// =======================[ COM CONFIGURATION ]=========================
#define SERIAL_BAUD_RATE 115200 // Serial communication speed
// ======================================================================

// =======================[ USER CONFIGURATION ]=========================
// ESP32-S3 I²C Pin Configuration
#define I2C_SDA_PIN 4            // GPIO4 as SDA
#define I2C_SCL_PIN 5            // GPIO5 as SCL
#define I2C_FREQUENCY_HZ 1000000 // Max supported I2C speed for VL53L5CX

// Sensor I²C Address
#define SEN_DEFAULT_I2C_ADDR 0x29
#define SEN_TOP_I2C_ADDR 0x29
#define SEN_RIGHT_I2C_ADDR 0x2A
#define SEN_LEFT_I2C_ADDR 0x2B

// Grid resolution: choose 4x4 (16 zones) or 8x8 (64 zones)
#define GRID_RESOLUTION VL53L5CX_RESOLUTION_8X8

// Max range to display (for printing only)
#define MAX_DISTANCE_MM 2500

// Sensor configuration
#define RANGING_MODE SF_VL53L5CX_RANGING_MODE::AUTONOMOUS
#define INTEGRATION_TIME_MS 10 // 1–20 ms
#define SHARPENER_PERCENT 10   // 0–99%
#define TARGET_ORDER SF_VL53L5CX_TARGET_ORDER::CLOSEST
#define RANGING_FREQUENCY_HZ 15 // Max 15 Hz

// Control flags
#define ENABLE_START_RANGING true
#define ENABLE_STOP_AFTER_ONE false
// ======================================================================

// =======================[ PIN ASSIGNMENTS ]============================
// Sensor Pins
#define SEN_TOP_LP_PIN 6   // GPIO6
#define SEN_TOP_RST_PIN 7  // GPIO7
#define SEN_TOP_INT_PIN 21 // GPIO21

#define SEN_LEFT_LP_PIN 8   // GPIO8
#define SEN_LEFT_RST_PIN 9  // GPIO9
#define SEN_LEFT_INT_PIN 14 // GPIO14

#define SEN_RIGHT_LP_PIN 10  // GPIO10
#define SEN_RIGHT_RST_PIN 11 // GPIO11
#define SEN_RIGHT_INT_PIN 15 // GPIO15

// Relay Outputs
#define RELAY1_PIN 12 // GPIO12
#define RELAY2_PIN 13 // GPIO13

// User Interface
#define OVRRD_BUTTON_PIN 16 // GPIO16

// UART Interface to Raspberry Pi
#define RPI_RX_PIN 17 // GPIO17
#define RPI_TX_PIN 18 // GPIO18
// ======================================================================
