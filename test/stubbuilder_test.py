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
    original_lines = text.strip("\n").split("\n")
    stripped_lines = []
    for line in original_lines:
        stripped_lines.append(line.strip())
    return "\n".join(stripped_lines).rstrip("\n")


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
    #ifndef TEST_STUB_H
    #define TEST_STUB_H
    
    #include <stdbool.h>
    #include <stdint.h>
    
    void test_function(void);

    #endif
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
     
    #include "middleware.h"
    #include "Sleep.h"
    #include "test.h"
     
    #include <stdint.h>
    #include <stdbool.h>
    
    #define ADDR_SKELETON_INPUTS 0
    #define ADDR_COMPUTATION_ENABLE 100
    
    static void modelCompute(bool enable);
    
    void test_function(void)
    {
       middlewareInit();
       middlewareUserlogicEnable();
       modelCompute(true);
       
       while( middlewareUserlogicGetBusyStatus() );
       modelCompute(false);
       middlewareUserlogicDisable();
       middlewareDeinit();
    }
    
    static void modelCompute(bool enable)
    {
       uint8_t cmd = (enable ? 1 : 0);
       middlewareWriteBlocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);
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

    #include "../middleware/middleware.h"
    #include "Sleep.h"
    #include "another_test.h"

    #include <stdint.h>
    #include <stdbool.h>

    #define ADDR_SKELETON_INPUTS 0
    #define ADDR_COMPUTATION_ENABLE 100

    static void modelCompute(bool enable);
    static uint8_t get_id(void);

    static uint64_t accelerator_id = 47;
    static uint32_t accelerator_addr = 4000;

    bool another_test_deploy(void)
    {
       middlewareInit();
       middlewareConfigureFpga(accelerator_addr);
       sleep_for_ms(200);
       bool is_deployed_successfully = (get_id() == accelerator_id);
       middlewareDeinit();
       return is_deployed_successfully;
    }

    void another_test_doSomething(void)
    {
       middlewareInit();
       middlewareUserlogicEnable();
       modelCompute(true);
    
       while( middlewareUserlogicGetBusyStatus() );
       modelCompute(false);
       middlewareUserlogicDisable();
       middlewareDeinit();
    }
    
    int8_t another_test_predict(int8_t *inputs, bool more_inputs)
    {
       int8_t _result;
    
       middlewareInit();
       middlewareUserlogicEnable();
       middlewareWriteBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t*)(inputs), 6);
       middlewareWriteBlocking(ADDR_SKELETON_INPUTS+6, (uint8_t*)(&more_inputs), 1);
       modelCompute(true);
       
       while( middlewareUserlogicGetBusyStatus() );
       modelCompute(false);
       for(int i = 0; i < 1; i++){
          middlewareReadBlocking(ADDR_SKELETON_INPUTS+0+i, (uint8_t *)(&_result)+i, 1);
          middlewareReadBlocking(ADDR_SKELETON_INPUTS+0+i, (uint8_t *)(&_result)+i, 1); 
       }
       modelCompute(false);
       middlewareUserlogicDisable();
       middlewareDeinit();
       return _result;
    }
    
    static void modelCompute(bool enable)
    {
       uint8_t cmd = (enable ? 1 : 0);
       middlewareWriteBlocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);
    }
    
    static uint8_t get_id(void)
    {
       middlewareUserlogicEnable();
       uint8_t id = middlewareGetDesignId();
       middlewareUserlogicDisable();
       return id;
    }
    """
    stub = build_stub_from_text(input_text)
    compare(stub.as_c_code(), expected)


def test_can_generate_deployable_stub_code_with_output_parameter() -> None:
    input_text = """
    stub test
    
    path ../middleware
    deploy 47 4000
    
    sync predict ( int8[6] inputs, int8[10] outputs ) : void
    """
    expected = """
    /* 
     * This is an autogenerated stub.
     * Do not change it manually. 
     */

    #include "../middleware/middleware.h"
    #include "Sleep.h"
    #include "test.h"

    #include <stdint.h>
    #include <stdbool.h>

    #define ADDR_SKELETON_INPUTS 0
    #define ADDR_COMPUTATION_ENABLE 100

    static void modelCompute(bool enable);
    static uint8_t get_id(void);

    static uint64_t accelerator_id = 47;
    static uint32_t accelerator_addr = 4000;

    bool test_deploy(void)
    {
       middlewareInit();
       middlewareConfigureFpga(accelerator_addr);
       sleep_for_ms(200);
       bool is_deployed_successfully = (get_id() == accelerator_id);
       middlewareDeinit();
       return is_deployed_successfully;
    }
    
    void test_predict(int8_t *inputs, int8_t *outputs)
    {
       middlewareInit();
       middlewareUserlogicEnable();
       middlewareWriteBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t*)(inputs), 6);
       modelCompute(true);
       
       while( middlewareUserlogicGetBusyStatus() );
       modelCompute(false);
       for(int i = 0; i < 10; i++){
          middlewareReadBlocking(ADDR_SKELETON_INPUTS+0+i, (uint8_t *)(outputs)+i, 1);
          middlewareReadBlocking(ADDR_SKELETON_INPUTS+0+i, (uint8_t *)(outputs)+i, 1); 
       }
       modelCompute(false);
       middlewareUserlogicDisable();
       middlewareDeinit();
    }
    
    static void modelCompute(bool enable)
    {
       uint8_t cmd = (enable ? 1 : 0);
       middlewareWriteBlocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);
    }
    
    static uint8_t get_id(void)
    {
       middlewareUserlogicEnable();
       uint8_t id = middlewareGetDesignId();
       middlewareUserlogicDisable();
       return id;
    }
    """
    stub = build_stub_from_text(input_text)
    compare(stub.as_c_code(), expected)
