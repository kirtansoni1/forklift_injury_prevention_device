#include <main.h>

SparkFun_VL53L5CX myImager;
VL53L5CX_ResultsData measurementData;

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

  Serial.print(F("Initializing VL53L5CX at address 0x"));
  Serial.println(VL53L5CX_I2C_ADDR, HEX);

  if (!myImager.begin(VL53L5CX_I2C_ADDR, Wire))
  {
    Serial.println(F("❌ Sensor not detected. Check wiring and power."));
    while (1)
      ;
  }

  // Resolution setup
  myImager.setResolution(GRID_RESOLUTION);
  imageResolution = myImager.getResolution();
  imageWidth = sqrt(imageResolution);
  Serial.print(F("✅ Resolution set: "));
  Serial.print(imageWidth);
  Serial.println("x" + String(imageWidth));

  // Confirm sensor connectivity
  if (!myImager.isConnected())
  {
    Serial.println(F("❌ Sensor disconnected after init."));
    while (1)
      ;
  }

  // Ranging Mode: CONTINUOUS or AUTONOMOUS
  if (!myImager.setRangingMode(RANGING_MODE))
  {
    Serial.println(F("❌ Failed to set ranging mode."));
    while (1)
      ;
  }

  // Power Mode: sleep → wakeup
  myImager.setPowerMode(SF_VL53L5CX_POWER_MODE::SLEEP);
  delay(500);
  myImager.setPowerMode(SF_VL53L5CX_POWER_MODE::WAKEUP);

  // Integration Time
  if (!myImager.setIntegrationTime(INTEGRATION_TIME_MS))
  {
    Serial.println(F("❌ Failed to set integration time."));
    while (1)
      ;
  }
  Serial.print(F("✅ Integration time set to "));
  Serial.print(INTEGRATION_TIME_MS);
  Serial.println(F("ms"));

  // Sharpener
  if (!myImager.setSharpenerPercent(SHARPENER_PERCENT))
  {
    Serial.println(F("❌ Failed to set sharpener value."));
    while (1)
      ;
  }
  Serial.print(F("✅ Sharpener set to "));
  Serial.print(SHARPENER_PERCENT);
  Serial.println(F("%"));

  // Target Order
  if (!myImager.setTargetOrder(TARGET_ORDER))
  {
    Serial.println(F("❌ Failed to set target order."));
    while (1)
      ;
  }
  Serial.print(F("✅ Target order set to: "));
  Serial.println((TARGET_ORDER == SF_VL53L5CX_TARGET_ORDER::CLOSEST) ? "CLOSEST" : "STRONGEST");

  // Ranging Frequency
  myImager.setRangingFrequency(RANGING_FREQUENCY_HZ);
  Serial.print(F("✅ Ranging frequency: "));
  Serial.print(RANGING_FREQUENCY_HZ);
  Serial.println(" Hz");

  // Start Ranging
  if (ENABLE_START_RANGING)
  {
    if (!myImager.startRanging())
    {
      Serial.println(F("❌ Failed to start ranging."));
      while (1)
        ;
    }
    Serial.println(F("📡 Ranging started."));
  }
}

void loop()
{
  // Poll for new data
  if (myImager.isDataReady())
  {
    if (myImager.getRangingData(&measurementData))
    {
      Serial.println("==== Distance Grid (mm) ====");

      // Print in matrix format, reverse X to match real layout
      for (int y = 0; y <= imageWidth * (imageWidth - 1); y += imageWidth)
      {
        for (int x = imageWidth - 1; x >= 0; x--)
        {
          uint16_t dist = measurementData.distance_mm[x + y];
          if (dist == 0 || dist > MAX_DISTANCE_MM)
            Serial.print("----\t");
          else
            Serial.print(String(dist) + "\t");
        }
        Serial.println();
      }

      Serial.println("============================\n");

      if (ENABLE_STOP_AFTER_ONE)
      {
        myImager.stopRanging();
        Serial.println(F("🛑 Ranging stopped."));
        while (1)
          ;
      }
    }
  }

  delay(20); // Keep CPU load low
}
