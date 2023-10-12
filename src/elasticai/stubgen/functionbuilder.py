from enum import Enum
from typing import List

from function import Function, SyncFunction
from variable import Variable


class FunctionBuilder:

    class CallPattern(Enum):
        SYNC = 1
        ASYNC = 2

    def __init__(self) -> None:
        self.name: str = ''
        self.prefix: str = ''
        self.pattern = FunctionBuilder.CallPattern.SYNC  # sync call pattern is standard value
        self.parameters: List[Variable] = []
        self.returnType = Variable.Type('void')

    def set_call_pattern(self, pattern: CallPattern) -> None:
        if pattern != FunctionBuilder.CallPattern.SYNC:
            raise ValueError("Currently, we can generate only synchronous (i.e. blocking) functions.")
        else:
            self.pattern = pattern

    def set_name(self, name: str) -> None:
        if name is None:
            raise ValueError("Function name must be given.")
        else:
            self.name = name

    def set_name_prefix(self, prefix: str) -> None:
        self.prefix = prefix

    def set_return_type(self, ret_type: Variable.Type) -> None:
        self.returnType = ret_type

    def add_input_parameter(self, param_type: Variable.Type, param_name: str, param_elements: int = 1) -> None:
        parameter = Variable(param_type, param_name, param_elements, Variable.Scope.INPUT)
        # parameter = Parameter(param_type, param_name, is_input_arg=True)
        # if param_elements > 1:
        #     parameter.set_as_array(param_elements)
        self.parameters.append(parameter)

    def generate(self) -> Function:
        name: str = self._generate_prefixed_name()
        if self.pattern == FunctionBuilder.CallPattern.SYNC:
            return SyncFunction(name, self.returnType, self.parameters)

    def _generate_prefixed_name(self) -> str:
        return f'{self.prefix}_{self.name}'
