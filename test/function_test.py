import pytest

from elasticai.stubgen.functionbuilder import FunctionBuilder
from elasticai.stubgen.variable import Variable


def test_generating_signature_for_sync_works():
    expected = 'void FOO_bar(int16_t *a);\n'
    builder = FunctionBuilder()
    builder.set_name('bar')
    builder.set_name_prefix('FOO')
    builder.add_input_parameter(Variable.Type('int16'), 'a', 2)
    assert builder.generate().as_c_prototype() == expected


def test_generating_syn_does_not_throw_exception():
    builder = FunctionBuilder()
    builder.generate()


def test_generating_asyn_fails_with_exception():
    builder = FunctionBuilder()
    with pytest.raises(ValueError):
        builder.set_call_pattern(FunctionBuilder.CallPattern.ASYNC)
