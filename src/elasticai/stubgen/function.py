from typing import List

from elasticai.stubgen.variable import Variable


def _formatted_body_line(line: str) -> str:
    return f'   {line};\n'


class WriterC:

    def signature(self, static: bool, identifier: str, result_var: Variable, parameters: List[Variable]) -> None:
        result: str = ''
        if static:
            result += 'static '
        result += f'{result_var.type.as_c_code()} {identifier}'
        result += f'({self._parameter_list_as_c(parameters)})'
        print(result)

    @staticmethod
    def _parameter_list_as_c(parameters: List[Variable]) -> str:
        if not parameters:
            return Variable.Type.VOID.as_c_code()
        else:
            result: str = ''
            for param in parameters:
                result += param.as_parameter_in_signature() + ', '
            result = result[:-2]
            return result

    @staticmethod
    def open_block():
        print('{\n')

    @staticmethod
    def close_block():
        print('}\n\n')


class Function:

    def __init__(self, identifier: str, return_type: Variable.Type, arguments=None, is_private=False) -> None:
        if arguments is None:
            arguments = []
        self._identifier = identifier
        self._result_var = Variable(return_type, '_result', scope=Variable.Scope.RETURN)
        self._input_variables: List[Variable] = arguments
        self.is_private = is_private

    def as_c_code(self) -> str:
        result: str = f'{self._signature_as_c()}\n' \
                      f'{{\n' \
                      f'{self._body_as_c()}' \
                      f'}}\n\n'
        # self.as_c_code_()
        return result

    def as_c_code_(self) -> None:
        writer = WriterC()
        writer.signature(self.is_private, self._identifier, self._result_var, self._input_variables)
        # self._write_body(writer)
        writer.open_block()
        writer.close_block()

    def as_c_prototype(self) -> str:
        return f'{self._signature_as_c()};\n'

    def _signature_as_c(self) -> str:
        result: str = ''
        if self.is_private:
            result += 'static '
        result += f'{self._result_var.type.as_c_code()} {self._identifier}'
        result += f'({self._parameter_list_as_c()})'
        return result

    def _parameter_list_as_c(self) -> str:
        if not self._input_variables:
            return Variable.Type.VOID.as_c_code()
        else:
            result: str = ''
            for param in self._input_variables:
                result += param.as_parameter_in_signature() + ', '
            result = result[:-2]
            return result

    def _body_as_c(self) -> str:
        raise NotImplementedError


class SyncFunction(Function):

    def _body_as_c(self) -> str:
        target_address = 0
        return self._define_local_vars() + \
            self._enable_fpga() + \
            self._run_accelerator() + \
            self._block_until_ready() + \
            self._retrieve_result(target_address) + \
            self._stop_fpga() + \
            self._return_result()

    def _define_local_vars(self):
        if self._is_returning_result():
            return f'{self._result_var.as_definition()}\n'
        else:
            return ''

    def _run_accelerator(self) -> str:
        return self._send_data_to_fpga() + \
               self._start_computation() + \
               '\n'

    @staticmethod
    def _enable_fpga() -> str:
        return _formatted_body_line('middlewareInit()') + _formatted_body_line('middlewareUserlogicEnable()')

    def _send_data_to_fpga(self) -> str:
        result = ''
        target_address = 0
        for parameter in self._input_variables:
            identifier = parameter.as_pass_by_reference()
            length = parameter.get_length_in_byte()
            result += f'{self._pass_parameter(target_address, f"{identifier}", length)}'
            target_address += length
        return result

    @staticmethod
    def _start_computation() -> str:
        return _formatted_body_line('modelCompute(true)')

    @staticmethod
    def _pass_parameter(target_addr: int, name: str, length: int) -> str:
        return _formatted_body_line(f'middlewareWriteBlocking('
                                    f'ADDR_SKELETON_INPUTS+{target_addr}, (uint8_t*)({name}), {length})')

    def _get_input_length(self) -> int:
        input_length = 0
        for param in self._input_variables:
            input_length += param.get_length_in_byte()
        return input_length

    @staticmethod
    def _block_until_ready() -> str:
        return _formatted_body_line(f'while( middlewareUserlogicGetBusyStatus() )')+'\n'

    def _is_returning_result(self) -> bool:
        return self._result_var.type.get_length_in_byte() > 0

    def _retrieve_result(self, target_addr: int) -> str:
        if self._is_returning_result():
            res = self._result_var.identifier
            length = self._result_var.type.get_length_in_byte()
            return _formatted_body_line(f'middlewareReadBlocking('
                                        f'ADDR_SKELETON_INPUTS+{target_addr}, (uint8_t *)(&{res}), {length})') + \
                   _formatted_body_line(f'middlewareReadBlocking('
                                        f'ADDR_SKELETON_INPUTS+{target_addr}, (uint8_t *)(&{res}), {length})')
        else:
            return ''

    def _return_result(self) -> str:
        if self._is_returning_result():
            return _formatted_body_line(f'return {self._result_var.identifier}')
        else:
            return ''

    @staticmethod
    def _stop_fpga() -> str:
        return f'   modelCompute(false);\n' \
               f'   middlewareUserlogicDisable();\n' \
               f'   middlewareDeinit();\n'


class DeployFunction(Function):

    def __init__(self, identifier: str, address_var: Variable, id_var: Variable) -> None:
        super().__init__(identifier, Variable.Type.BOOL)
        self.address_var_name: str = address_var.identifier
        self.id_var = id_var

    def _body_as_c(self) -> str:
        return f'   middlewareInit();\n' \
               f'   middlewareConfigureFpga({self.address_var_name});\n' \
               f'   sleep_for_ms(200);\n' \
               f'   bool is_deployed_successfully = (get_id() == accelerator_id);\n' \
               f'   middlewareDeinit();\n' \
               f'   return is_deployed_successfully;\n'


class ModelComputeFunction(Function):

    def __init__(self) -> None:
        arg = Variable(Variable.Type.BOOL, 'enable', scope=Variable.Scope.LOCAL)
        super().__init__('modelCompute', Variable.Type.VOID, [arg], is_private=True)

    def _body_as_c(self) -> str:
        return self._shorter_body_as_c()

    @staticmethod
    def _original_body_as_c() -> str:
        return '   uint8_t cmd[1] = {0x01};\n' \
               '   if (enable)\n' \
               '      cmd[0] = 1;\n' \
               '   else\n' \
               '      cmd[0] = 0;\n' \
               '   middlewareWriteBlocking(ADDR_COMPUTATION_ENABLE, cmd, 1);\n'

    @staticmethod
    def _shorter_body_as_c() -> str:
        return '   uint8_t cmd = (enable ? 1 : 0);\n' \
               '   middlewareWriteBlocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);\n'


class GetIdFunction(Function):

    def __init__(self) -> None:
        super().__init__('get_id', Variable.Type.UINT8, is_private=True)

    def _body_as_c(self) -> str:
        return '   middlewareUserlogicEnable();\n' \
               '   uint8_t id = middlewareGetDesignId();\n' \
               '   middlewareUserlogicDisable();\n' \
               '   return id;\n'
