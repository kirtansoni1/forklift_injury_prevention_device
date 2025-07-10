#include <main.h>

SparkFun_VL53L5CX imagers[NUM_SENSORS];
VL53L5CX_ResultsData measurementData[NUM_SENSORS];

const char *sensorNames[NUM_SENSORS] = {"TOP", "LEFT", "RIGHT"};
const uint8_t sensorAddrs[NUM_SENSORS] = {VL53L5CX_ADDR_TOP, VL53L5CX_ADDR_LEFT, VL53L5CX_ADDR_RIGHT};

int imageResolution = 0;
int imageWidth = 0;

void setup()
{
  Serial.begin(SERIAL_BAUD_RATE);
  while (!Serial)
    ; // Wait for Serial to be ready
  delay(1000);
  Serial.println(F("🔧 VL53L5CX + ESP32-S3 Configuration Starting..."));

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQUENCY_HZ);

  for (int i = 0; i < NUM_SENSORS; i++)
  {
    Serial.print(F("Initializing "));
    Serial.print(sensorNames[i]);
    Serial.print(F(" sensor at address 0x"));
    Serial.println(sensorAddrs[i], HEX);

    if (!imagers[i].begin(sensorAddrs[i], Wire))
    {
      Serial.print(F("❌ Sensor not detected: "));
      Serial.println(sensorNames[i]);
      while (1)
        ;
    }

    imagers[i].setResolution(GRID_RESOLUTION);

    if (!imagers[i].isConnected())
    {
      Serial.print(F("❌ Sensor disconnected after init: "));
      Serial.println(sensorNames[i]);
      while (1)
        ;
    }

    if (!imagers[i].setRangingMode(RANGING_MODE))
    {
      Serial.print(F("❌ Failed to set ranging mode for "));
      Serial.println(sensorNames[i]);
      while (1)
        ;
    }

    imagers[i].setPowerMode(SF_VL53L5CX_POWER_MODE::SLEEP);
    delay(500);
    imagers[i].setPowerMode(SF_VL53L5CX_POWER_MODE::WAKEUP);

    if (!imagers[i].setIntegrationTime(INTEGRATION_TIME_MS))
    {
      Serial.print(F("❌ Failed to set integration time for "));
      Serial.println(sensorNames[i]);
      while (1)
        ;
    }

    if (!imagers[i].setSharpenerPercent(SHARPENER_PERCENT))
    {
      Serial.print(F("❌ Failed to set sharpener value for "));
      Serial.println(sensorNames[i]);
      while (1)
        ;
    }

    if (!imagers[i].setTargetOrder(TARGET_ORDER))
    {
      Serial.print(F("❌ Failed to set target order for "));
      Serial.println(sensorNames[i]);
      while (1)
        ;
    }

    imagers[i].setRangingFrequency(RANGING_FREQUENCY_HZ);

    if (ENABLE_START_RANGING)
    {
      if (!imagers[i].startRanging())
      {
        Serial.print(F("❌ Failed to start ranging for "));
        Serial.println(sensorNames[i]);
        while (1)
          ;
      }
    }
  }

  imageResolution = imagers[0].getResolution();
  imageWidth = sqrt(imageResolution);
  Serial.print(F("✅ Resolution set: "));
  Serial.print(imageWidth);
  Serial.println("x" + String(imageWidth));

  Serial.println(F("📡 Ranging started on all sensors."));
}

void loop()
{
  bool ready = true;
  for (int i = 0; i < NUM_SENSORS; i++)
    ready &= imagers[i].isDataReady();

  if (ready)
  {
    for (int i = 0; i < NUM_SENSORS; i++)
      imagers[i].getRangingData(&measurementData[i]);

    Serial.println("==== Distance Grid (mm) ====");
    Serial.println("TOP\t\t\t\t| LEFT\t\t\t\t| RIGHT");

    for (int y = 0; y <= imageWidth * (imageWidth - 1); y += imageWidth)
    {
      for (int s = 0; s < NUM_SENSORS; s++)
      {
        for (int x = imageWidth - 1; x >= 0; x--)
        {
          uint16_t dist = measurementData[s].distance_mm[x + y];
          if (dist == 0 || dist > MAX_DISTANCE_MM)
            Serial.print("----\t");
          else
            Serial.print(String(dist) + "\t");
        }
        if (s < NUM_SENSORS - 1)
          Serial.print("| ");
      }
      Serial.println();
    }

    Serial.println("============================\n");

    if (ENABLE_STOP_AFTER_ONE)
    {
      for (int i = 0; i < NUM_SENSORS; i++)
        imagers[i].stopRanging();
      Serial.println(F("🛑 Ranging stopped."));
      while (1)
        ;
    }
  }

  delay(20); // Keep CPU load low
}
