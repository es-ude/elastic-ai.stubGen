import string

from elasticai.stubgen.lexer import Lexer
from elasticai.stubgen.parser import Parser
from elasticai.stubgen.stub import Stub
from elasticai.stubgen.stubbuilder import StubBuilder


def compare_without_whitespaces(s1: str, s2: str):
    remove = string.whitespace
    mapping = {ord(c): None for c in remove}
    assert s1.translate(mapping) == s2.translate(mapping)


def _strip_indention(text: str) -> str:
    original_lines = text.strip('\n').split('\n')
    stripped_lines = []
    for line in original_lines:
        stripped_lines.append(line.strip())
    return "\n".join(stripped_lines).rstrip('\n')


def compare(actual: str, expected: str):
    assert _strip_indention(actual) == _strip_indention(expected)


def build_stub_from_text(input_text: str) -> Stub:
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(input_text)
    stub_builder = StubBuilder()
    parser = Parser(stub_builder).get_parser()
    parser.parse(tokens)
    return stub_builder.generate()


def test_basic_stub_header_can_be_generated_from_string() -> None:
    input_text = """
    stub test
    sync function () : void         
    """
    expected = """
    # ifndef TEST_STUB_H
    # define TEST_STUB_H
    
    # include <stdbool.h>
    # include <stdint.h>
    
    void test_function(void);

    # endif
    """
    stub = build_stub_from_text(input_text)
    compare(stub.as_c_header(), expected)


def test_basic_stub_code_can_be_generated_from_string() -> None:
    input_text = """
    stub test
    sync function () : void         
    """
    expected = """
    /* 
     * This is an autogenerated stub.
     * Do not change it manually. 
     */
     
    # include <stdint.h>
    # include <stdbool.h>
    # include "middleware.h"
    # include "test.h"
    
    # define ADDR_SKELETON_INPUTS 0
    
    static void model_compute(bool enable);
    
    void test_function(void)
    {
       middleware_init();
       middleware_userlogic_enable();
       model_compute(true);
       
       while( middleware_userlogic_get_busy_status() );
          
       model_compute(false);
       middleware_userlogic_disable();
       middleware_deinit();
    }
    
    static void model_compute(bool enable)
    {
       uint8_t cmd = (enable ? 1 : 0);
       middleware_write_blocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);
    }
    """
    stub = build_stub_from_text(input_text)
    compare(stub.as_c_code(), expected)


def test_can_generate_deployable_stub_code() -> None:
    input_text = """
    stub another_test
    
    path ../middleware
    deploy 47 4000
    
    sync doSomething () : void
    sync predict ( int8[6] inputs, bool more_inputs ) : int8
    """
    expected = """
    /* 
     * This is an autogenerated stub.
     * Do not change it manually. 
     */

    # include <stdint.h>
    # include <stdbool.h>
    # include "../middleware/middleware.h"
    # include "another_test.h"

    # define ADDR_SKELETON_INPUTS 0

    static void model_compute(bool enable);
    static uint8_t get_id(void);

    static uint64_t accelerator_id = 47;
    static uint32_t accelerator_addr = 4000;

    bool another_test_deploy(void)
    {
       middleware_init();
       middleware_configure_fpga(accelerator_addr);
       sleep_ms(200);
       bool is_deployed_successfully = (get_id() == accelerator_id);
       middleware_deinit();
       return is_deployed_successfully;
    }

    void another_test_doSomething(void)
    {
       middleware_init();
       middleware_userlogic_enable();
       model_compute(true);
    
       while( middleware_userlogic_get_busy_status() );
    
       model_compute(false);
       middleware_userlogic_disable();
       middleware_deinit();
    }
    
    int8_t another_test_predict(int8_t *inputs, bool more_inputs)
    {
       int8_t _result;
    
       middleware_init();
       middleware_userlogic_enable();
       middleware_write_blocking(ADDR_SKELETON_INPUTS+0, (uint8_t*)(inputs), 6);
       middleware_write_blocking(ADDR_SKELETON_INPUTS+6, (uint8_t*)(&more_inputs), 1);
       model_compute(true);
       
       while( middleware_userlogic_get_busy_status() );

       middleware_read_blocking(1, (uint8_t *)(&_result), 1);
       middleware_read_blocking(1, (uint8_t *)(&_result), 1);
       model_compute(false);
       middleware_userlogic_disable();
       middleware_deinit();
       return _result;
    }
    
    static void model_compute(bool enable)
    {
       uint8_t cmd = (enable ? 1 : 0);
       middleware_write_blocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);
    }
    
    static uint8_t get_id(void)
    {
       middleware_userlogic_enable();
       uint8_t id = middleware_userlogic_get_design_id();
       middleware_userlogic_disable();
       return id;
    }
    """
    stub = build_stub_from_text(input_text)
    compare(stub.as_c_code(), expected)
