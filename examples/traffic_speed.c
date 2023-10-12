/*
 * This is an autogenerated stub. 
 * Do not change it manually. 
 */

# include <stdint.h>
# include <stdbool.h>
# include "../middleware/middleware.h"
# include "traffic_speed.h"

# define ADDR_SKELETON_INPUTS 0

static void model_compute(bool enable);
static uint8_t get_id(void);

static uint64_t accelerator_id = 47;
static uint32_t accelerator_addr = 4000;

bool traffic_speed_deploy(void)
{
   middleware_init();
   middleware_configure_fpga(accelerator_addr);
   sleep_ms(200);
   bool is_deployed_successfully = (get_id() == accelerator_id);
   middleware_deinit();
   return is_deployed_successfully;
}

int8_t traffic_speed_predict(int8_t *inputs, bool more_inputs)
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

