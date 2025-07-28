#ifndef MAIN_H
#define MAIN_H

#include <Arduino.h>
#include <Wire.h>
#include <math.h>
#include <SparkFun_VL53L5CX_Library.h>

#include "defines.h"
#include "sensor_manager.h"

// =======================[ GLOBAL SENSOR INSTANCES ]===================
extern SparkFun_VL53L5CX sensorTop;
extern SparkFun_VL53L5CX sensorLeft;
extern SparkFun_VL53L5CX sensorRight;

// =======================[ GLOBAL DATA BUFFERS ]=======================
extern VL53L5CX_ResultsData dataTop;
extern VL53L5CX_ResultsData dataLeft;
extern VL53L5CX_ResultsData dataRight;

// =======================[ GLOBAL SENSOR CONFIGURATIONS ]===============
extern SensorConfig topSensorConfig;
extern SensorConfig leftSensorConfig;
extern SensorConfig rightSensorConfig;

// =======================[ FUNCTION PROTOTYPES ]========================
// System initialization
bool initializeSystem();
bool setupSensors();

// Main application loop
void processAllSensors();

#endif // MAIN_H
