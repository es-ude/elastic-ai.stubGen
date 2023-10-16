from typing import List
from elasticai.stubgen.function import Function, DeployFunction, ModelComputeFunction, GetIdFunction
from elasticai.stubgen.variable import Variable


class Stub:

    def __init__(self, name: str, description: str = '') -> None:
        self._name: str = name
        self._body_comment: str = description
        self._relative_path_to_middleware_header = ''
        self.functions: List[Function] = []
        self._helper_functions: List[Function] = [ModelComputeFunction()]
        self._system_functions: List[Function] = []
        self.variables = dict()

    def set_description(self, comment: str) -> None:
        self._body_comment = comment

    def set_relative_path_to_middleware_header(self, path: str):
        self._relative_path_to_middleware_header = path

    def add_static_deploy_function(self, accel_addr: int, accel_id: int):
        id_var = Variable(Variable.Type('id'), 'accelerator_id', value=accel_id)
        addr_var = Variable(Variable.Type('address'), 'accelerator_addr', value=accel_addr)
        self.variables['accelerator_id'] = id_var
        self.variables['accelerator_addr'] = addr_var
        switch_function = DeployFunction(f'{self._name}_deploy', addr_var, id_var)
        self._system_functions.append(switch_function)
        self._helper_functions.append(GetIdFunction())

    def add_function(self, function: Function):
        self.functions.append(function)

    def as_c_code(self) -> str:
        result: str = self._generate_starting_comment()
        result += self._generate_includes()
        result += self._generate_defines()
        result += self._generate_helper_function_prototypes()
        result += self._generate_variables()
        result += self._generate_system_functions()
        result += self._generate_stub_functions()
        result += self._generate_helper_functions()
        return result

    def _generate_starting_comment(self) -> str:
        text = self._body_comment.replace('\n', '\n * ')
        return f'/*\n'\
               f' * {text} \n' \
               f' */\n\n'

    def _generate_includes(self) -> str:
        path = self._relative_path_to_middleware_header
        if len(path) > 0 and path[-1] != '/':
            path += '/'
        return f'#include "{path}middleware.h"\n' \
               f'#include "Sleep.h"\n' \
               f'#include "{self._name.lower()}.h"\n\n' \
               f'#include <stdint.h>\n' \
               f'#include <stdbool.h>\n\n' \


    def _generate_defines(self) -> str:
        path = self._relative_path_to_middleware_header
        if len(path) > 0 and path[-1] != '/':
            path += '/'
        return f'#define ADDR_SKELETON_INPUTS 0\n' \
               f'#define ADDR_COMPUTATION_ENABLE 100\n\n'

    def _generate_helper_function_prototypes(self) -> str:
        result = ''
        for function in self._helper_functions:
            result += f'{function.as_c_prototype()}'
        return f'{result}\n'

    def _generate_variables(self):
        result = ''
        for var in self.variables.values():
            result += var.as_initialization()
        if self.variables:
            result += '\n'
        return result

    def _generate_system_functions(self) -> str:
        result: str = ''
        for function in self._system_functions:
            result += f'{function.as_c_code()}'
        return result

    def _generate_stub_functions(self) -> str:
        result: str = ''
        for function in self.functions:
            result += function.as_c_code()
        return result

    def _generate_helper_functions(self) -> str:
        result = ''
        for function in self._helper_functions:
            result += f'{function.as_c_code()}'
        return result

    def as_c_header(self) -> str:
        return f'#ifndef {self._name.upper()}_STUB_H\n' \
               f'#define {self._name.upper()}_STUB_H\n' \
               f'\n' \
               f'#include <stdbool.h>\n' \
               f'#include <stdint.h>\n' \
               f'\n' \
               f'{self._generate_system_function_prototypes()}' \
               f'{self._generate_stub_function_prototypes()}' \
               f'\n' \
               f'#endif\n'

    def _generate_system_function_prototypes(self) -> str:
        result: str = ''
        for function in self._system_functions:
            result += function.as_c_prototype()
        return result

    def _generate_stub_function_prototypes(self) -> str:
        result: str = ''
        for function in self.functions:
            result += function.as_c_prototype()
        return result
