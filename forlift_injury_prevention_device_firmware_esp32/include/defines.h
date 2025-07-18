// =======================[ COM CONFIGURATION ]=========================
#define SERIAL_BAUD_RATE 115200 // Serial communication speed
// ======================================================================

// =======================[ USER CONFIGURATION ]=========================
// ESP32-S3 I²C Pin Configuration
#define I2C_SDA_PIN 9            // GPIO9 as SDA
#define I2C_SCL_PIN 10           // GPIO10 as SCL
#define I2C_FREQUENCY_HZ 1000000 // Max supported I2C speed for VL53L5CX

// Sensor I²C Addresses
#define VL53L5CX_ADDR_TOP 0x29
#define VL53L5CX_ADDR_LEFT 0x2A
#define VL53L5CX_ADDR_RIGHT 0x2B

#define NUM_SENSORS 3

// Grid resolution: choose 4x4 (16 zones) or 8x8 (64 zones)
#define GRID_RESOLUTION VL53L5CX_RESOLUTION_8X8

// Max range to display (for printing only)
#define MAX_DISTANCE_MM 2500

// Sensor configuration
#define RANGING_MODE SF_VL53L5CX_RANGING_MODE::AUTONOMOUS
#define INTEGRATION_TIME_MS 10 // 1-20 ms
#define SHARPENER_PERCENT 10   // 0-99%
#define TARGET_ORDER SF_VL53L5CX_TARGET_ORDER::CLOSEST
#define RANGING_FREQUENCY_HZ 15 // Max 15Hz

// Control flags
#define ENABLE_START_RANGING true
#define ENABLE_STOP_AFTER_ONE false
// =====================================================================
