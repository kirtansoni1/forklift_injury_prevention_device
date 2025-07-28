// =======================[ SYSTEM CONFIGURATION ]=========================
#define SERIAL_BAUD_RATE 115200 // Serial communication speed
#define LOOP_DELAY_MS 10        // Main loop delay (faster response)
                                // 📖 TUNING GUIDE: Critical real-time parameter!
                                //    Lower (20-30ms) = faster response, higher CPU usage
                                //    Higher (100-200ms) = slower response, lower CPU usage
                                //    50ms = ~20Hz update rate, good balance for safety systems
                                // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

#define INIT_TIMEOUT_MS 15000 // Initialization timeout (increased)
// ======================================================================

// =======================[ I2C CONFIGURATION ]===========================
#define I2C_SDA_PIN 4           // GPIO4 as SDA
#define I2C_SCL_PIN 5           // GPIO5 as SCL
#define I2C_FREQUENCY_HZ 850000 // Reduced to 850kHz for stability
                                // 📖 TUNING GUIDE: Communication reliability vs speed
                                //    400kHz = stable, good for 3 sensors
                                //    800kHz = faster but may cause communication errors
                                //    Lower if experiencing I2C timeouts or errors
                                // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

#define I2C_TIMEOUT_MS 50 // Reduced timeout for faster recovery
                          // 📖 TUNING GUIDE: Error recovery vs reliability
                          //    Lower (30-40ms) = faster recovery from errors
                          //    Higher (100-200ms) = more tolerance for slow sensors
                          // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md
// ======================================================================

// =======================[ SENSOR CONFIGURATION ]========================
// Sensor I²C Addresses
#define SEN_DEFAULT_I2C_ADDR 0x29
#define SEN_TOP_I2C_ADDR 0x44   // Top sensor address
#define SEN_LEFT_I2C_ADDR 0x45  // Left sensor address
#define SEN_RIGHT_I2C_ADDR 0x29 // Right sensor address (keep default)

// Sensor Settings
#define SENSOR_RESOLUTION 64    // 8x8 = 64 zones
#define SENSOR_GRID_WIDTH 8     // 8x8 grid
#define RANGING_FREQUENCY_HZ 30 // Sensor ranging frequency
                                // 📖 TUNING GUIDE: Data acquisition rate control
                                //    Higher (20-60Hz) = more data, faster detection, higher power
                                //    Lower (5-10Hz) = less data, slower detection, lower power
                                //    15Hz = good balance for safety applications
                                // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

#define MAX_DISTANCE_MM 2500 // Max range to display

// Timing Configuration
#define SENSOR_RESET_DELAY_MS 5  // Minimal reset delay
#define SENSOR_INIT_DELAY_MS 10  // Minimal initialization delay
#define SENSOR_CONFIG_DELAY_MS 2 // Minimal configuration delay
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
