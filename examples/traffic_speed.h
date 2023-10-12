# ifndef TRAFFIC_SPEED_STUB_H
# define TRAFFIC_SPEED_STUB_H

# include <stdint.h>

bool traffic_speed_deploy(void);
int8_t traffic_speed_predict(int8_t *inputs, bool more_inputs);

# endif
