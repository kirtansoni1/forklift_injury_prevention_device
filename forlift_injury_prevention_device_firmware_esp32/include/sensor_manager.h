#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include <SparkFun_VL53L5CX_Library.h>

// Initializes a sensor, sets I2C address, and returns true on success
bool initVL53L5CX(SparkFun_VL53L5CX &sensor, uint8_t lpnPin, uint8_t newAddress, TwoWire &wire);

// Powers down all VL53L5CX sensors
void powerDownAllSensors();

// Powers up all VL53L5CX sensors
void powerUpAllSensors();

#endif
