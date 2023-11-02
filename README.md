## IDL Specification v1.0 (2023-10-31)

The stub generator needs some information about the stub it should generate
and the stub's functions. To provide this information to it
the developer creates an .idl file and passes it to the generator
as a command line argument. The contents of the file are written
using an Interface Definition Language (IDL) that we define for our
stub generator. The used IDL is specified in the next paragraphs. 

---

But first, a short explanation of some terms used in our description:

**must** : this information is mandatory and must be included in the IDL file.\
**can** : this information is optional and can be omitted in the IDL file.

**HWA** : a hardware accelerator is a bitfile that can be deployed on the FPGA. 
It provides some accelerated implementation of a complex functionality, e.g.
a neural network, etc. Our stub uses a HWA by sending it data and
retrieving results from it. The HWA can be designed by a hardware engineer or
generated using our *elastic AI.creator* tool. 

**Stub Function** : a stub function is a autogenerated C function that is used 
by the C application developer to execute a HWA. The stub function is
responsible for sending data to the HWA, waiting for results, retrieving them
and providing them to the C application. 

---

### IDL Commands

#### Stub Name

First the generator needs to know how the stub will be called. For this, 
we *must* specify the stub name with

`stub <stub_name>`

The stub name will be used as a prefix for all generated C function names. It must
be a valid C identifier, e.g., no spaces, not starting with a digit, etc. 
As an example, `stub my_stub` specifies that all generated functions will be 
prefixed with `my_stub`, leading to function names like `my_stub_deploy`, etc. 

#### Middleware Path

Next, we *can* provide a relative path for specifying where the middleware
header file `middleware.h` will be located relatively to our generated stub
at compile time (i.e., when we will use our generated stub, not while generating it). 
For this we can use: 

`path <pathname>`

As an example, `path ../middleware` specifies that `middleware.h` will be 
located in `./../middleware` relative to our stub when compiling our application later.

A stub can include a special function to deploy its HWA before using it. 
If this function should be generated for us, we should specify this. We can use:

`deploy <id> <addr>`

The first parameter <id> specifies the (globally unique?) identifier of the HWA to deploy. 
This id is X byte long. Refer to your HWA specification to find the right ID.

The second parameter <addr> specifies where in the on-board flash memory your HWA is stored.
More specifically, this is the  starting address in byte of your HWA in flash. This can be
used to store multiple HWAs and to switch between them dynamically using different
generated stubs. One stub can never use multiple HWAs. It is always bound to 
exactly one HWA. 

If such a line is included, a stub function <stub_name>_generate will be automatically 
generated for us. If it is omitted, no such function will be generated and we need to 
use a different way to deploy our HWA, e.g., by calling middleware functions
directly in our application code. 

#### Stub Functions

Next, we can specify arbitrary number of generated stub functions. 
A stub can also contain zero functions but it will not be useful. 

A stub function can be synchronous or asynchronous. A synchronous function
will block when called until the execution of the HWA is finished, its 
result is available and can be returned directly. 
An asynchronous function will return immediately when called, before the 
execution on the HWA is finished. Results must be retrieved using a provided callback 
function. Currently, we only support synchronous functions. Support for asynchronous 
functions may be added in the future.  

To specify a synchronous stub function, we can write:

`sync <function_name> ( <parameters> ) : <return_type>`

<return_type> can be one of `void, bool, int8, int16, int32, int64`\
To specify that a function does not return a result, use the return type `void`.

Parameters are specified as zero to n `<param_type> <param_name>` pairs, separated by comma. \
<param_type> can be one of `bool, int8, int16, int32, int64`\
To specify that a function takes no parameters, leave the parameter list empty (do not use void).\
Parameter types can also be array types. Return types currently cannot.

As an example,

`sync predict ( int8[6] inputs, bool more_inputs ) : int8`

specifies a stub function called `predict` that takes as its input an array `ìnputs` with 
six elements of type `ìnt8` (an integer type with 8bit length) and an additional
parameter `more_inputs` of type `bool`. Note that a boolean is specified as an 8bit type.
The function returns a result of type `ìnt8`.

### Example

In this section we want to give a short illustrative example for an IDL and
the corresponding generated code. Note that more examples can be found in
the unit tests in the `test` subdirectory. The unit tests provide the actual
normative specification. In other words, if they specify a different behaviour 
that we do in this document, then the tests are right!

Using the IDL commands, we can, e.g., specify a stub in an IDL file (e.g., called 
`traffic_speed.idl`) as follows:

> stub traffic_speed
>
> path ../middleware \
> deploy 47 4000
> 
> sync predict ( int8[6] inputs, bool more_inputs ) : int8

This will lead to the following code being generated in a file `traffic_speed.h`: 

> #ifndef TRAFFIC_SPEED_STUB_H\
> #define TRAFFIC_SPEED_STUB_H
> 
> #include <stdbool.h>\
> #include <stdint.h>
> 
> bool traffic_speed_deploy(void);\
> int8_t traffic_speed_predict(int8_t *inputs, bool more_inputs);
> 
> #endif


The stub generator will furthermore generate the following code in a file `traffic_speed.c`:

> /*
>  * This is an autogenerated stub. 
>  * Do not change it manually. \
>  */
> 
> #include "../middleware/middleware.h"\
> #include "Sleep.h"\
> #include "traffic_speed.h"
> 
> #include <stdint.h>\
> #include <stdbool.h>
> 
> #define ADDR_SKELETON_INPUTS 0\
> #define ADDR_COMPUTATION_ENABLE 100
> 
> static void modelCompute(bool enable);\
> static uint8_t get_id(void);
> 
> static uint64_t accelerator_id = 47;\
> static uint32_t accelerator_addr = 4000;
> 
> bool traffic_speed_deploy(void)\
> {\
>    middlewareInit();\
>    middlewareConfigureFpga(accelerator_addr);\
>    sleep_for_ms(200);\
>    bool is_deployed_successfully = (get_id() == accelerator_id);\
>    middlewareDeinit();\
>    return is_deployed_successfully;\
> }
> 
> int8_t traffic_speed_predict(int8_t *inputs, bool more_inputs)\
> {\
>    int8_t _result;
> 
>    middlewareInit();\
>    middlewareUserlogicEnable();\
>    middlewareWriteBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t*)(inputs), 6);\
>    middlewareWriteBlocking(ADDR_SKELETON_INPUTS+6, (uint8_t*)(&more_inputs), 1);\
>    modelCompute(true);
> 
>    while( middlewareUserlogicGetBusyStatus() );\
>    modelCompute(false);\
>    for(int i = 0; i < 1; i++){\
>       middlewareReadBlocking(ADDR_SKELETON_INPUTS+0+i, (uint8_t *)(&_result)+i, 1);\
>       middlewareReadBlocking(ADDR_SKELETON_INPUTS+0+i, (uint8_t *)(&_result)+i, 1);\
>    }\
>    modelCompute(false);\
>    middlewareUserlogicDisable();\
>    middlewareDeinit();\
>    return _result;
> }
> 
> static void modelCompute(bool enable)\
> {\
>    uint8_t cmd = (enable ? 1 : 0);\
>    middlewareWriteBlocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);\
> }
> 
> static uint8_t get_id(void)\
> {\
>    middlewareUserlogicEnable();\
>    uint8_t id = middlewareGetDesignId();\
>    middlewareUserlogicDisable();\
>    return id;\
> }