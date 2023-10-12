from rply import ParserGenerator
from elasticai.stubgen.stubbuilder import StubBuilder


class Parser:

    def __init__(self, builder: StubBuilder):
        self.pg = ParserGenerator(
            # A list of all token names accepted by the parser.
            ['STUB', 'OPEN_PAREN', 'CLOSE_PAREN', 'COLON', 'NUMBER',
             'SYNC', 'ASYNC', 'OPEN_SQUARE_BRACKET', 'CLOSE_SQUARE_BRACKET',
             'STRING', 'COMMA', 'VOID', 'BOOL', 'INT8', 'INT16', 'INT32',
             'INT64', 'PATH', 'PATH_STRING', 'ADDRESS', 'DEPLOY']
        )
        self.builder = builder
        self.add_production_rules()

    def add_production_rules(self) -> None:

        @self.pg.production('stub : STUB STRING attr function')
        @self.pg.production('stub : STUB STRING function')
        def stub(p):
            name: str = p[1].value
            self.builder.set_name(name)

        @self.pg.production('id : NUMBER')
        def accel_id(p):
            the_id = int(p[0].value)
            self.builder.set_accelerator_id(the_id)

        @self.pg.production('address : NUMBER')
        def accel_addr(p):
            address = int(p[0].value)
            self.builder.set_accelerator_address(address)

        @self.pg.production('attr : attr2')
        @self.pg.production('attr : attr attr2')
        def attributes(p):
            pass

        @self.pg.production('attr2 : PATH PATH_STRING')
        def path_attr(p):
            path = p[1].value
            self.builder.set_middleware_path(path)

        @self.pg.production('attr2 : ADDRESS address')
        def address_attr(p):
            pass

        @self.pg.production('attr2 : DEPLOY id address')
        def switch_attr(p):
            pass

        @self.pg.production('function : function2')
        @self.pg.production('function : function function2')
        def functions(p):
            pass

        @self.pg.production('function2 : pattern STRING OPEN_PAREN parameter CLOSE_PAREN COLON return_type')
        @self.pg.production('function2 : pattern STRING OPEN_PAREN CLOSE_PAREN COLON return_type')
        def function(p):
            name = p[1]
            self.builder.set_function_name(name.value)

        @self.pg.production('pattern : SYNC')
        @self.pg.production('pattern : ASYNC')
        def pattern(p):
            the_pattern = p[0]
            if the_pattern.gettokentype() == 'SYNC':
                self.builder.add_synchronous_function()

        @self.pg.production('return_type : INT8')
        @self.pg.production('return_type : VOID')
        def return_type(p):
            ret_type: str = p[0].value
            self.builder.set_function_return_type(ret_type)

        @self.pg.production('parameter : parameter2 COMMA parameter')
        @self.pg.production('parameter : parameter2')
        def parameters(p):
            pass

        @self.pg.production('parameter2 : BOOL STRING')
        @self.pg.production('parameter2 : INT8 STRING')
        @self.pg.production('parameter2 : INT16 STRING')
        @self.pg.production('parameter2 : INT32 STRING')
        @self.pg.production('parameter2 : INT64 STRING')
        def parameter(p):
            name: str = p[1].value
            p_type: str = p[0].value
            self.builder.add_function_input_parameter(name, p_type, 1)

        @self.pg.production('parameter2 : BOOL OPEN_SQUARE_BRACKET NUMBER CLOSE_SQUARE_BRACKET STRING')
        @self.pg.production('parameter2 : INT8 OPEN_SQUARE_BRACKET NUMBER CLOSE_SQUARE_BRACKET STRING')
        @self.pg.production('parameter2 : INT16 OPEN_SQUARE_BRACKET NUMBER CLOSE_SQUARE_BRACKET STRING')
        @self.pg.production('parameter2 : INT32 OPEN_SQUARE_BRACKET NUMBER CLOSE_SQUARE_BRACKET STRING')
        @self.pg.production('parameter2 : INT64 OPEN_SQUARE_BRACKET NUMBER CLOSE_SQUARE_BRACKET STRING')
        def array_parameter(p):
            p_type = p[0].value
            length = int(p[2].value)
            name = p[4].value
            self.builder.add_function_input_parameter(name, p_type, length)

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
