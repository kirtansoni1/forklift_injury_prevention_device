#ifndef MAIN_H
#define MAIN_H

#include <Arduino.h>
#include <Wire.h>
#include <math.h>
#include <SparkFun_VL53L5CX_Library.h>

#include "defines.h"
#include "sensor_manager.h"

// === Global Sensor Instances ===
extern SparkFun_VL53L5CX sensorTop;
extern SparkFun_VL53L5CX sensorLeft;
extern SparkFun_VL53L5CX sensorRight;

// === Global Data Buffers ===
extern VL53L5CX_ResultsData dataTop;
extern VL53L5CX_ResultsData dataLeft;
extern VL53L5CX_ResultsData dataRight;

// === Global Configuration Parameters ===
extern int imageResolution;
extern int imageWidth;

// === Function Prototypes ===
void printSensorMatrix(const char *label, VL53L5CX_ResultsData &data);

#endif // MAIN_H
