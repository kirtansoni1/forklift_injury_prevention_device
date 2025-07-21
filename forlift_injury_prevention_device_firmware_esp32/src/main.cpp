#include "main.h"

SparkFun_VL53L5CX sensorTop;
SparkFun_VL53L5CX sensorLeft;
SparkFun_VL53L5CX sensorRight;

VL53L5CX_ResultsData dataTop;
VL53L5CX_ResultsData dataLeft;
VL53L5CX_ResultsData dataRight;

int imageResolution = 0;
int imageWidth = 0;

void setup()
{
  Serial.begin(SERIAL_BAUD_RATE);
  while (!Serial)
    ;
  delay(1000);

  Serial.println(F("🔧 Initializing I2C and Sensors..."));
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQUENCY_HZ);

  // Setup LPn pins
  pinMode(SEN_TOP_LP_PIN, OUTPUT);
  pinMode(SEN_LEFT_LP_PIN, OUTPUT);
  pinMode(SEN_RIGHT_LP_PIN, OUTPUT);

  powerDownAllSensors();

  if (!initVL53L5CX(sensorTop, SEN_TOP_LP_PIN, SEN_TOP_I2C_ADDR, Wire))
    while (1)
      ;
  if (!initVL53L5CX(sensorLeft, SEN_LEFT_LP_PIN, SEN_LEFT_I2C_ADDR, Wire))
    while (1)
      ;
  if (!initVL53L5CX(sensorRight, SEN_RIGHT_LP_PIN, SEN_RIGHT_I2C_ADDR, Wire))
    while (1)
      ;

  powerUpAllSensors(); // Power up all sensors after initialization

  SparkFun_VL53L5CX *sensors[] = {&sensorTop, &sensorLeft, &sensorRight};
  const char *names[] = {"TOP", "LEFT", "RIGHT"};

  for (int i = 0; i < 3; i++)
  {
    sensors[i]->setResolution(GRID_RESOLUTION);
    imageResolution = sensors[i]->getResolution();
    imageWidth = sqrt(imageResolution);

    sensors[i]->setPowerMode(SF_VL53L5CX_POWER_MODE::SLEEP);
    delay(500);
    sensors[i]->setPowerMode(SF_VL53L5CX_POWER_MODE::WAKEUP);

    sensors[i]->setIntegrationTime(INTEGRATION_TIME_MS);
    sensors[i]->setSharpenerPercent(SHARPENER_PERCENT);
    sensors[i]->setTargetOrder(TARGET_ORDER);
    sensors[i]->setRangingFrequency(RANGING_FREQUENCY_HZ);

    if (ENABLE_START_RANGING)
    {
      if (!sensors[i]->startRanging())
      {
        Serial.print(F("❌ Failed to start "));
        Serial.println(names[i]);
        while (1)
          ;
      }
      Serial.print("📡 ");
      Serial.print(names[i]);
      Serial.println(" Ranging started.");
    }
  }

  Serial.print(F("✅ Sensor resolution: "));
  Serial.print(imageWidth);
  Serial.println("x" + String(imageWidth));
}

void printSensorMatrix(const char *label, VL53L5CX_ResultsData &data)
{
  Serial.print("==== ");
  Serial.print(label);
  Serial.println(" Distance Grid (mm) ====");

  for (int y = 0; y <= imageWidth * (imageWidth - 1); y += imageWidth)
  {
    for (int x = imageWidth - 1; x >= 0; x--)
    {
      uint16_t dist = data.distance_mm[x + y];
      if (dist == 0 || dist > MAX_DISTANCE_MM)
        Serial.print("----\t");
      else
        Serial.print(String(dist) + "\t");
    }
    Serial.println();
  }

  Serial.println("=====================================\n");
}

void loop()
{
  if (sensorTop.isDataReady())
  {
    if (sensorTop.getRangingData(&dataTop))
    {
      printSensorMatrix("TOP", dataTop);
    }
  }

  if (sensorLeft.isDataReady())
  {
    if (sensorLeft.getRangingData(&dataLeft))
    {
      printSensorMatrix("LEFT", dataLeft);
    }
  }

  if (sensorRight.isDataReady())
  {
    if (sensorRight.getRangingData(&dataRight))
    {
      printSensorMatrix("RIGHT", dataRight);
    }
  }

  delay(20); // Lower CPU usage
}
