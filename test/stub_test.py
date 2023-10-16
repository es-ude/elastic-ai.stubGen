from elasticai.stubgen.stub import Stub


def test_stub_creation():
    expected = """/*
 *  
 */

# include <stdint.h>
# include <stdbool.h>
# include "middleware.h"
# include "test.h"

# define ADDR_SKELETON_INPUTS 0
# define ADDR_COMPUTATION_ENABLE 100

static void model_compute(bool enable);

static void model_compute(bool enable)
{
   uint8_t cmd = (enable ? 1 : 0);
   middlewareWriteBlocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);
}

"""
    the_stub = Stub("test")
    assert the_stub.as_c_code() == expected
