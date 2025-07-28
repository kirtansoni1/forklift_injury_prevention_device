#include "main.h"

// =======================[ GLOBAL SENSOR INSTANCES ]===================
SparkFun_VL53L5CX sensorTop;
SparkFun_VL53L5CX sensorLeft;
SparkFun_VL53L5CX sensorRight;

// =======================[ GLOBAL DATA BUFFERS ]=======================
VL53L5CX_ResultsData dataTop;
VL53L5CX_ResultsData dataLeft;
VL53L5CX_ResultsData dataRight;

// =======================[ SENSOR CONFIGURATIONS ]======================
SensorConfig topSensorConfig = {
    .sensor = &sensorTop,
    .data = &dataTop,
    .address = SEN_TOP_I2C_ADDR,
    .resetPin = SEN_TOP_RST_PIN,
    .lpPin = SEN_TOP_LP_PIN,
    .intPin = SEN_TOP_INT_PIN,
    .name = "Top Sensor"};

SensorConfig leftSensorConfig = {
    .sensor = &sensorLeft,
    .data = &dataLeft,
    .address = SEN_LEFT_I2C_ADDR,
    .resetPin = SEN_LEFT_RST_PIN,
    .lpPin = SEN_LEFT_LP_PIN,
    .intPin = SEN_LEFT_INT_PIN,
    .name = "Left Sensor"};

SensorConfig rightSensorConfig = {
    .sensor = &sensorRight,
    .data = &dataRight,
    .address = SEN_RIGHT_I2C_ADDR,
    .resetPin = SEN_RIGHT_RST_PIN,
    .lpPin = SEN_RIGHT_LP_PIN,
    .intPin = SEN_RIGHT_INT_PIN,
    .name = "Right Sensor"};

// =======================[ INITIALIZATION FUNCTIONS ]===================
bool initializeSystem()
{
  Serial.begin(SERIAL_BAUD_RATE);
  delay(200); // Minimal delay for Serial stability
  Serial.println("🚀 VL53L5CX - Three Sensor Configuration");
  Serial.println("========================================");

  return true;
}

bool setupSensors()
{
  // Initialize I2C
  if (!SensorManager::initializeI2C())
  {
    Serial.println("❌ I2C initialization failed");
    return false;
  }

  // Scan I2C bus for debugging
  SensorManager::scanI2C();

  // Configure pins
  SensorManager::configurePins();

  // Add sensors to manager (initialize non-default address sensors first)
  SensorManager::addSensor(&topSensorConfig);   // Custom address 0x44
  SensorManager::addSensor(&leftSensorConfig);  // Custom address 0x45
  SensorManager::addSensor(&rightSensorConfig); // Default address 0x29 (last)

  // Initialize all sensors
  if (!SensorManager::initializeAllSensors())
  {
    Serial.println("❌ Sensor initialization failed");
    return false;
  }

  // Run diagnostic to check sensor status
  SensorManager::diagnosticSensorStatus();

  Serial.println("✅ System initialization complete");
  Serial.println("========================================");
  return true;
}

void processAllSensors()
{
  SensorManager::processSensorData();
}

// =======================[ ARDUINO MAIN FUNCTIONS ]======================
void setup()
{
  if (!initializeSystem())
  {
    Serial.println("❌ System initialization failed!");
    while (1)
    {
      delay(1000);
    }
  }

  if (!setupSensors())
  {
    Serial.println("❌ Sensor setup failed!");
    while (1)
    {
      delay(1000);
    }
  }
}

void loop()
{
  processAllSensors();
  delay(LOOP_DELAY_MS);
}
