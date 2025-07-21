#include "sensor_manager.h"
#include "defines.h"

bool initVL53L5CX(SparkFun_VL53L5CX &sensor, uint8_t lpnPin, uint8_t newAddress, TwoWire &wire)
{
    digitalWrite(lpnPin, HIGH);
    delay(10); // Allow sensor to boot up

    // 1. Initialize with default address
    if (!sensor.begin(SEN_DEFAULT_I2C_ADDR, wire))
    {
        Serial.print("❌ Sensor at LP pin ");
        Serial.print(lpnPin);
        Serial.println(" failed to respond at 0x29");
        return false;
    }

    // 2. Skip Address Check
    if (sensor.getAddress() == newAddress)
    {
        Serial.print("⚠️ Sensor already at address 0x");
        Serial.println(newAddress, HEX);
        Serial.println("Skipping address change.");
        return true;
    }

    // 2. Set new I2C address
    if (!sensor.setAddress(newAddress))
    {
        Serial.print("❌ Failed to assign new address: 0x");
        Serial.println(newAddress, HEX);
        return false;
    }

    // 3. Confirm address was correctly applied
    if (sensor.getAddress() != newAddress)
    {
        Serial.print("❌ Address mismatch. Expected 0x");
        Serial.print(newAddress, HEX);
        Serial.print(", got 0x");
        Serial.println(sensor.getAddress(), HEX);
        return false;
    }

    Serial.print("✅ Sensor ready at 0x");
    Serial.println(sensor.getAddress(), HEX);

    powerDownAllSensors(); // optional: clean state for next sensor
    return true;
}

void powerDownAllSensors()
{
    digitalWrite(SEN_TOP_LP_PIN, LOW);
    digitalWrite(SEN_LEFT_LP_PIN, LOW);
    digitalWrite(SEN_RIGHT_LP_PIN, LOW);
    delay(10); // Allow sensors to power down
    Serial.println("🔌 All sensors powered down.");
}

void powerUpAllSensors()
{
    digitalWrite(SEN_TOP_LP_PIN, HIGH);
    digitalWrite(SEN_LEFT_LP_PIN, HIGH);
    digitalWrite(SEN_RIGHT_LP_PIN, HIGH);
    delay(10); // Allow sensors to power up
    Serial.println("🔌 All sensors powered up.");
}