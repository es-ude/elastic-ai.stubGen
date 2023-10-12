from sys import argv

from stub import Stub
from stubbuilder import StubBuilder
from lexer import Lexer
from parser import Parser


#    sync predict_traffic_speed :
#       sync, onetime
#       in last_speeds : 6*int8
#       in keep_state  : bool
#       out            : int8

#    int8 predict_traffic_speed ( int8[6] inputs, bool more_inputs ) : sync
#    sync predict_traffic_speed(inputs : int8[6], more_inputs : bool) : int8


def _build_stub_from_text(input_text: str) -> Stub:
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(input_text)
    # for token in tokens:
    #     print(token)
    stub_builder = StubBuilder()
    parser = Parser(stub_builder).get_parser()
    parser.parse(tokens)
    return stub_builder.generate()


def _load_stub(reader) -> Stub:
    idl_text = reader.read()
    return _build_stub_from_text(idl_text)


def _save_stub_header(stub: Stub, file_name: str):
    with open(file_name, 'w') as writer:
        writer.write(stub.as_c_header())


def _save_stub_code(stub: Stub, file_name: str):
    with open(file_name, 'w') as writer:
        writer.write(stub.as_c_code())


def _get_filename_from_commandline_or_abort() -> str:
    if len(argv) < 2:
        print('Error: no filename given, aborting')
        exit(-1)
    return argv[1]


def _main() -> None:
    filename = _get_filename_from_commandline_or_abort()
    with open(f'{filename}.idl', 'r') as reader:
        stub = _load_stub(reader)
        _save_stub_header(stub, f'{filename}.h')
        _save_stub_code(stub, f'{filename}.c')
        print('Success: stub files generated successfully')


if __name__ == "__main__":
    _main()
