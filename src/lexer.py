from rply import LexerGenerator


class Lexer:

    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('STUB', r'stub')
        self.lexer.add('SYNC', r'sync')
        self.lexer.add('ASYNC', r'async')
        self.lexer.add('ASYNC', r'async')
        self.lexer.add('PATH', r'path')
        self.lexer.add('ADDRESS', r'address')
        self.lexer.add('DEPLOY', r'deploy')
        self.lexer.add('BOOL', r'bool')
        self.lexer.add('INT8', r'int8')
        self.lexer.add('INT16', r'int16')
        self.lexer.add('INT32', r'int32')
        self.lexer.add('INT64', r'int64')
        self.lexer.add('VOID', r'void')
        self.lexer.add('OPEN_SQUARE_BRACKET', r'\[')
        self.lexer.add('CLOSE_SQUARE_BRACKET', r'\]')
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')
        self.lexer.add('COMMA', r'\,')
        self.lexer.add('COLON', r'\:')
        self.lexer.add('NUMBER', r'\d+')
        self.lexer.add('STRING', r'[a-zA-Z]\w*')
        self.lexer.add('PATH_STRING', r'.*[a-zA-Z/]\w*')
        # Ignore spaces
        self.lexer.ignore(r'\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
