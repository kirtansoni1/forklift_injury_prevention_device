#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include <Arduino.h>
#include <SparkFun_VL53L5CX_Library.h>
#include "defines.h"

// =======================[ SENSOR STRUCTURE ]============================
struct SensorConfig
{
    SparkFun_VL53L5CX *sensor;
    VL53L5CX_ResultsData *data;
    uint8_t address;
    uint8_t resetPin;
    uint8_t lpPin;
    uint8_t intPin;
    const char *name;
};

// =======================[ SENSOR MANAGER CLASS ]========================
class SensorManager
{
private:
    static SensorConfig *sensors[3];
    static int sensorCount;
    static int imageResolution;
    static int imageWidth;

    static void resetSensor(uint8_t rstPin);

public:
    // Initialization functions
    static bool initializeI2C();
    static bool initializeAllSensors();
    static void configurePins();

    // Sensor management
    static bool addSensor(SensorConfig *config);
    static void holdAllInReset();
    static void releaseAllFromReset();

    // Data processing
    static void processSensorData();
    static void printSensorMatrix(const char *label, VL53L5CX_ResultsData &data, int sensorId);
    static void diagnosticSensorStatus();
    static void scanI2C(); // Add I2C scanner for debugging

    // Getters
    static int getImageResolution() { return imageResolution; }
    static int getImageWidth() { return imageWidth; }
};

// =======================[ UTILITY FUNCTIONS ]===========================
// Individual sensor control functions (legacy support)
bool initVL53L5CX(SparkFun_VL53L5CX &sensor, uint8_t rstPin, uint8_t lpPin, uint8_t newAddress);
void holdSensorInReset(uint8_t rstPin);
void releaseSensorFromReset(uint8_t rstPin);
void holdSensorInLPState(uint8_t lpPin);
void releaseSensorFromLPState(uint8_t lpPin);

#endif // SENSOR_MANAGER_H
