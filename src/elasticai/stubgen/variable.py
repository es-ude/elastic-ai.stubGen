from enum import Enum


class Variable:

    class Type(Enum):
        BOOL = 'bool'
        UINT8 = 'uint8'
        INT8 = 'int8'
        INT16 = 'int16'
        INT32 = 'int32'
        INT64 = 'int64'
        VOID = 'void'
        ADDRESS = 'address'
        ID = 'id'

        @staticmethod
        def from_string(as_string: str):
            return Variable.Type(as_string)

        def __init__(self, as_string: str):
            self.var_type: str = ''
            self.length: int

            if as_string == 'bool':
                self.var_type = 'bool'
                self.length = 1
            elif as_string == 'uint8':
                self.var_type = 'uint8_t'
                self.length = 1
            elif as_string == 'int8':
                self.var_type = 'int8_t'
                self.length = 1
            elif as_string == 'int16':
                self.var_type = 'int16_t'
                self.length = 2
            elif as_string == 'int32':
                self.var_type = 'int32_t'
                self.length = 4
            elif as_string == 'int64':
                self.var_type = 'int64_t'
                self.length = 8
            elif as_string == 'void':
                self.var_type = 'void'
                self.length = 0
            elif as_string == 'address':
                self.var_type = 'uint32_t'
                self.length = 4
            elif as_string == 'id':
                self.var_type = 'uint64_t'
                self.length = 8
            else:
                raise ValueError("UNKNOWN TYPE")

        def as_c_code(self):
            return self.var_type

        def get_length_in_byte(self) -> int:
            return self.length

    class Scope(Enum):
        INPUT = 1
        OUTPUT = 2
        LOCAL = 3
        STUB = 4
        RETURN = 5

    def __init__(self, v_type: Type, name: str, elements=1, scope=Scope.STUB, value=None) -> None:
        self.type: Variable.Type = v_type
        self.identifier: str = name
        self.elements: int = elements
        self.scope: Variable.Scope = scope
        self.value = value

    def get_length_in_byte(self) -> int:
        return self.elements * self.type.get_length_in_byte()

    def as_initialization(self) -> str:
        result = self._prefix()
        result += f'{self._as_typed_var()} = {self.value};\n'
        return result

    def as_definition(self) -> str:
        result = self._prefix()
        result += f'{self._as_typed_var()};\n'
        return result

    def as_parameter_in_signature(self) -> str:
        return self._as_typed_var()

    def as_pass_by_reference(self) -> str:
        if self._is_array():
            return self.identifier
        else:
            return f'&{self.identifier}'

    def _is_array(self) -> bool:
        return self.elements > 1

    def _as_typed_var(self) -> str:
        if self._is_array():
            return f'{self.type.as_c_code()} *{self.identifier}'
        else:
            return f'{self.type.as_c_code()} {self.identifier}'

    def _prefix(self) -> str:
        if self.scope == Variable.Scope.STUB:
            return 'static '
        elif (self.scope == Variable.Scope.LOCAL) or (self.scope == Variable.Scope.RETURN):
            return '   '
        else:
            raise TypeError(self.scope.name)
