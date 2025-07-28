#include "sensor_manager.h"
#include <Arduino.h>

// =======================[ STATIC MEMBER INITIALIZATION ]================
SensorConfig *SensorManager::sensors[3] = {nullptr, nullptr, nullptr};
int SensorManager::sensorCount = 0;
int SensorManager::imageResolution = SENSOR_RESOLUTION;
int SensorManager::imageWidth = SENSOR_GRID_WIDTH;

// =======================[ PRIVATE METHODS ]=============================
void SensorManager::resetSensor(uint8_t rstPin)
{
    pinMode(rstPin, OUTPUT);
    digitalWrite(rstPin, HIGH); // Hold in reset
    delay(SENSOR_RESET_DELAY_MS);
    digitalWrite(rstPin, LOW); // Release from reset
    delay(SENSOR_RESET_DELAY_MS);
    Serial.print("🔄 Reset sequence completed for sensor on pin ");
    Serial.println(rstPin);
}

// =======================[ PUBLIC METHODS ]==============================
bool SensorManager::initializeI2C()
{
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQUENCY_HZ);
    Wire.setTimeout(I2C_TIMEOUT_MS); // Set I2C timeout for faster recovery
    Wire.setClock(I2C_FREQUENCY_HZ); // Ensure clock speed is set
    delay(10);                       // Brief settling time for stable communication
    Serial.println("🔌 I2C initialized with 100kHz frequency for stability");
    return true;
}

void SensorManager::configurePins()
{
    // Configure all reset pins
    pinMode(SEN_TOP_RST_PIN, OUTPUT);
    pinMode(SEN_LEFT_RST_PIN, OUTPUT);
    pinMode(SEN_RIGHT_RST_PIN, OUTPUT);

    // Configure all LP pins
    pinMode(SEN_TOP_LP_PIN, OUTPUT);
    pinMode(SEN_LEFT_LP_PIN, OUTPUT);
    pinMode(SEN_RIGHT_LP_PIN, OUTPUT);

    // Configure all interrupt pins
    pinMode(SEN_TOP_INT_PIN, INPUT);
    pinMode(SEN_LEFT_INT_PIN, INPUT);
    pinMode(SEN_RIGHT_INT_PIN, INPUT);

    Serial.println("📌 All sensor pins configured");
}

bool SensorManager::addSensor(SensorConfig *config)
{
    if (sensorCount >= 3)
    {
        Serial.println("❌ Maximum sensor count reached");
        return false;
    }

    sensors[sensorCount] = config;
    sensorCount++;

    Serial.print("➕ Added sensor: ");
    Serial.println(config->name);
    return true;
}

void SensorManager::holdAllInReset()
{
    digitalWrite(SEN_TOP_RST_PIN, HIGH);
    digitalWrite(SEN_LEFT_RST_PIN, HIGH);
    digitalWrite(SEN_RIGHT_RST_PIN, HIGH);
    delay(SENSOR_RESET_DELAY_MS);
    Serial.println("🔌 All sensors held in reset");
}

void SensorManager::releaseAllFromReset()
{
    digitalWrite(SEN_TOP_RST_PIN, LOW);
    digitalWrite(SEN_LEFT_RST_PIN, LOW);
    digitalWrite(SEN_RIGHT_RST_PIN, LOW);
    delay(SENSOR_RESET_DELAY_MS);
    Serial.println("🔌 All sensors released from reset");
}

bool SensorManager::initializeAllSensors()
{
    Serial.println("🚀 Starting optimized sensor initialization...");
    unsigned long startTime = millis();

    // Quick reset cycle for all sensors
    holdAllInReset();
    delay(SENSOR_INIT_DELAY_MS); // Reduced delay

    // Initialize sensors in optimal order (non-default addresses first)
    for (int i = 0; i < sensorCount; i++)
    {
        if (sensors[i] != nullptr)
        {
            unsigned long sensorStartTime = millis();

            Serial.print("🔧 Initializing ");
            Serial.print(sensors[i]->name);
            Serial.print(" (0x");
            Serial.print(sensors[i]->address, HEX);
            Serial.println(")");

            // Release this sensor from reset
            digitalWrite(sensors[i]->resetPin, LOW);
            delay(SENSOR_INIT_DELAY_MS);

            // Initialize sensor with optimized retry
            bool initialized = false;
            for (int retry = 0; retry < 5 && !initialized; retry++)
            {
                // Check individual sensor timeout (5 seconds per sensor)
                if (millis() - sensorStartTime > 5000)
                {
                    Serial.print("❌ Timeout during ");
                    Serial.print(sensors[i]->name);
                    Serial.println(" initialization");
                    return false;
                }

                if (sensors[i]->sensor->begin())
                {
                    initialized = true;
                }
                else
                {
                    Serial.print("⚠️ Retry ");
                    Serial.print(retry + 1);
                    Serial.print(" for ");
                    Serial.println(sensors[i]->name);
                    delay(SENSOR_INIT_DELAY_MS); // Reduced retry delay
                }
            }

            if (!initialized)
            {
                Serial.print("❌ ");
                Serial.print(sensors[i]->name);
                Serial.println(" initialization failed after retries");
                return false;
            }

            // Change address if needed
            if (sensors[i]->address != SEN_DEFAULT_I2C_ADDR)
            {
                bool addressSet = false;
                for (int addrRetry = 0; addrRetry < 3 && !addressSet; addrRetry++)
                {
                    if (sensors[i]->sensor->setAddress(sensors[i]->address))
                    {
                        addressSet = true;
                    }
                    else
                    {
                        delay(SENSOR_INIT_DELAY_MS);
                    }
                }

                if (!addressSet)
                {
                    Serial.print("❌ Address change failed for ");
                    Serial.println(sensors[i]->name);
                    return false;
                }
                Serial.print("✅ Address set to 0x");
                Serial.println(sensors[i]->address, HEX);
            }

            // Quick sensor configuration
            sensors[i]->sensor->setResolution(SENSOR_RESOLUTION);
            sensors[i]->sensor->setRangingFrequency(RANGING_FREQUENCY_HZ);

            delay(SENSOR_CONFIG_DELAY_MS); // Minimal delay

            sensors[i]->sensor->startRanging();
            Serial.print("✅ ");
            Serial.print(sensors[i]->name);
            Serial.println(" ready");
        }
    }

    unsigned long totalTime = millis() - startTime;
    Serial.print("✅ All sensors initialized in ");
    Serial.print(totalTime);
    Serial.println("ms");
    return true;
}

void SensorManager::processSensorData()
{
    for (int i = 0; i < sensorCount; i++)
    {
        if (sensors[i] != nullptr && sensors[i]->sensor->isConnected())
        {
            if (sensors[i]->sensor->isDataReady())
            {
                if (sensors[i]->sensor->getRangingData(sensors[i]->data))
                {
                    printSensorMatrix(sensors[i]->name, *sensors[i]->data, i + 1);
                }
                else
                {
                    Serial.print("⚠️ Data retrieval failed for ");
                    Serial.println(sensors[i]->name);
                }
            }
        }
        else if (sensors[i] != nullptr)
        {
            // Sensor disconnected - try to reconnect
            static unsigned long lastReconnectAttempt[3] = {0, 0, 0};
            if (millis() - lastReconnectAttempt[i] > 5000) // Try every 5 seconds
            {
                Serial.print("🔌 Attempting to reconnect ");
                Serial.println(sensors[i]->name);
                lastReconnectAttempt[i] = millis();

                // Quick reconnection attempt
                if (sensors[i]->sensor->begin())
                {
                    Serial.print("✅ ");
                    Serial.print(sensors[i]->name);
                    Serial.println(" reconnected");
                }
            }
        }
    }
}

void SensorManager::printSensorMatrix(const char *label, VL53L5CX_ResultsData &data, int sensorId)
{
    for (int y = 0; y <= imageWidth * (imageWidth - 1); y += imageWidth)
    {
        for (int x = imageWidth - 1; x >= 0; x--)
        {
            Serial.print("\t");
            Serial.print(sensorId);
            Serial.print(":");
            Serial.print(data.distance_mm[x + y]);
        }
        Serial.println();
    }
    Serial.println();
}

void SensorManager::diagnosticSensorStatus()
{
    Serial.println("🔍 Sensor Diagnostic Status:");
    Serial.println("============================");

    for (int i = 0; i < sensorCount; i++)
    {
        if (sensors[i] != nullptr)
        {
            Serial.print("Sensor ");
            Serial.print(i + 1);
            Serial.print(" (");
            Serial.print(sensors[i]->name);
            Serial.print("): ");

            // Check I2C connection
            Wire.beginTransmission(sensors[i]->address);
            uint8_t error = Wire.endTransmission();

            if (error == 0)
            {
                Serial.print("✅ I2C OK at 0x");
                Serial.print(sensors[i]->address, HEX);

                if (sensors[i]->sensor->isConnected())
                {
                    Serial.print(" | Connected | Data Ready: ");
                    Serial.println(sensors[i]->sensor->isDataReady() ? "Yes" : "No");
                }
                else
                {
                    Serial.println(" | Sensor Not Ready");
                }
            }
            else
            {
                Serial.print("❌ I2C Error ");
                Serial.print(error);
                Serial.print(" at 0x");
                Serial.println(sensors[i]->address, HEX);
            }
        }
    }
    Serial.println("============================");
}

void SensorManager::scanI2C()
{
    Serial.println("🔍 Scanning I2C bus...");
    Serial.println("     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f");

    for (int i = 0; i < 8; i++)
    {
        Serial.print(i * 16, HEX);
        Serial.print(": ");
        for (int j = 0; j < 16; j++)
        {
            int address = i * 16 + j;
            if (address < 0x08 || address > 0x77)
            {
                Serial.print("   ");
            }
            else
            {
                Wire.beginTransmission(address);
                uint8_t error = Wire.endTransmission();
                if (error == 0)
                {
                    if (address < 16)
                        Serial.print("0");
                    Serial.print(address, HEX);
                }
                else
                {
                    Serial.print("--");
                }
                Serial.print(" ");
            }
        }
        Serial.println();
    }
    Serial.println("🔍 I2C scan complete");
}

// =======================[ LEGACY UTILITY FUNCTIONS ]====================
bool initVL53L5CX(SparkFun_VL53L5CX &sensor, uint8_t rstPin, uint8_t lpPin, uint8_t newAddress)
{
    // Reset sequence
    pinMode(rstPin, OUTPUT);
    digitalWrite(rstPin, HIGH);
    delay(100);
    digitalWrite(rstPin, LOW);
    delay(10);

    // Initialize sensor
    if (!sensor.begin())
    {
        Serial.print("❌ Sensor failed to initialize at default address: 0x");
        Serial.println(SEN_DEFAULT_I2C_ADDR, HEX);
        return false;
    }

    // Set new address
    if (!sensor.setAddress(newAddress))
    {
        Serial.print("❌ Failed to assign new address: 0x");
        Serial.println(newAddress, HEX);
        return false;
    }

    // Verify address
    if (sensor.getAddress() != newAddress)
    {
        Serial.print("❌ Address verification failed");
        return false;
    }

    Serial.print("✅ Sensor ready at 0x");
    Serial.println(sensor.getAddress(), HEX);
    return true;
}

void holdSensorInReset(uint8_t rstPin)
{
    digitalWrite(rstPin, HIGH);
    delay(10);
}

void releaseSensorFromReset(uint8_t rstPin)
{
    digitalWrite(rstPin, LOW);
    delay(10);
}

void holdSensorInLPState(uint8_t lpPin)
{
    digitalWrite(lpPin, LOW);
    delay(10);
}

void releaseSensorFromLPState(uint8_t lpPin)
{
    digitalWrite(lpPin, HIGH);
    delay(10);
}
