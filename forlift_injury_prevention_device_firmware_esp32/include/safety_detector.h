#ifndef SAFETY_DETECTOR_H
#define SAFETY_DETECTOR_H

#include <Arduino.h>
#include <SparkFun_VL53L5CX_Library.h>
#include "defines.h"

// =======================[ DETECTION CONFIGURATION ]===================
// Global threshold distances (mm) - can be modified by external logic
extern uint16_t THRESHOLD_TOP_MM;   // Top sensor threshold
extern uint16_t THRESHOLD_LEFT_MM;  // Left sensor threshold
extern uint16_t THRESHOLD_RIGHT_MM; // Right sensor threshold

// Detection algorithm parameters
#define MIN_VALID_READINGS 5 // Minimum valid readings required (out of 64)
                             // 📖 TUNING GUIDE: Increase (25-30) for noisy environments,
                             //    decrease (15-18) for cleaner conditions.
                             //    Higher values = more robust, lower = more sensitive
                             // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

#define DETECTION_CONSENSUS_PCT 10 // Percentage of valid readings needed for detection
                                   // 📖 TUNING GUIDE: Core sensitivity control!
                                   //    Lower (15-20%) = more sensitive to small objects
                                   //    Higher (30-40%) = more robust against false positives
                                   //    Recommended range: 15-50%
                                   // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

#define MAX_SENSOR_RANGE_MM 4000 // Maximum valid sensor range
                                 // 📖 TUNING GUIDE: Should not exceed sensor specifications.
                                 //    Readings above this are considered invalid/noise
                                 // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

#define MIN_SENSOR_RANGE_MM 50 // Minimum valid sensor range (noise floor)
                               // 📖 TUNING GUIDE: Increase (100-150mm) if seeing noise
                               //    at very close distances. This filters out sensor noise.
                               // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

#define DETECTION_HYSTERESIS_MM 100 // Hysteresis to prevent oscillation
                                    // 📖 TUNING GUIDE: Increase (150-200mm) if detection
                                    //    flickers on/off rapidly. Provides stability buffer.
                                    // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

#define CONSECUTIVE_DETECTIONS 2 // Required consecutive detections for trigger
                                 // 📖 TUNING GUIDE: Critical stability parameter!
                                 //    2 = fast response, 3-4 = more stable
                                 //    Higher values reduce false positives but slow response
                                 // 📍 CONFIG GUIDE: See DETECTION_PARAMETERS_GUIDE.md

// =======================[ DETECTION RESULTS STRUCTURE ]===============
struct DetectionResult
{
    bool objectDetected;        // Final detection result
    uint8_t validReadings;      // Number of valid readings in matrix
    uint16_t closestDistance;   // Closest valid distance found
    uint16_t averageDistance;   // Average of readings below threshold
    uint8_t detectionsInMatrix; // Number of readings below threshold
    float detectionConfidence;  // Confidence percentage (0-100)
    uint32_t timestamp;         // Detection timestamp
};

// =======================[ SAFETY STATE STRUCTURE ]====================
struct SafetyState
{
    bool topSensorTriggered;          // Top sensor detection state
    bool leftSensorTriggered;         // Left sensor detection state
    bool rightSensorTriggered;        // Right sensor detection state
    bool emergencyStop;               // Overall emergency stop state
    uint32_t lastTriggerTime;         // Last trigger timestamp
    uint8_t consecutiveTopDetections; // Consecutive detection counter
    uint8_t consecutiveLeftDetections;
    uint8_t consecutiveRightDetections;
};

// =======================[ SAFETY DETECTOR CLASS ]======================
class SafetyDetector
{
private:
    static SafetyState currentState;

    // Internal detection functions
    static bool isValidReading(uint16_t distance);
    static DetectionResult analyzeMatrix(const VL53L5CX_ResultsData &data, uint16_t threshold);
    static bool applyConsensusFilter(const DetectionResult &result);
    static void updateConsecutiveDetections(bool detected, uint8_t &counter);
    static void printDetectionDetails(const char *sensorName, const DetectionResult &result);

public:
    // =======================[ INITIALIZATION ]=========================
    /**
     * @brief Initialize the safety detection system
     * @details Sets up default thresholds and initializes safety state
     */
    static void initialize();

    // =======================[ MAIN DETECTION FUNCTION ]================
    /**
     * @brief Process all sensor data and update safety state
     * @param topData Top sensor 8x8 distance matrix
     * @param leftData Left sensor 8x8 distance matrix
     * @param rightData Right sensor 8x8 distance matrix
     * @return true if emergency stop should be activated
     */
    static bool processAllSensors(const VL53L5CX_ResultsData &topData,
                                  const VL53L5CX_ResultsData &leftData,
                                  const VL53L5CX_ResultsData &rightData);

    // =======================[ INDIVIDUAL SENSOR DETECTION ]=============
    /**
     * @brief Analyze single sensor for object detection
     * @param data Sensor 8x8 distance matrix
     * @param threshold Distance threshold in millimeters
     * @param sensorName Name for logging purposes
     * @return DetectionResult structure with analysis details
     */
    static DetectionResult detectObject(const VL53L5CX_ResultsData &data,
                                        uint16_t threshold,
                                        const char *sensorName);

    // =======================[ RELAY CONTROL ]==========================
    /**
     * @brief Control safety relays based on detection state
     * @param emergencyStop true to activate emergency stop (open relays)
     */
    static void controlSafetyRelays(bool emergencyStop);

    /**
     * @brief Initialize relay pins and set safe state
     */
    static void initializeRelays();

    // =======================[ THRESHOLD MANAGEMENT ]===================
    /**
     * @brief Update detection thresholds
     * @param topThreshold Top sensor threshold (mm)
     * @param leftThreshold Left sensor threshold (mm)
     * @param rightThreshold Right sensor threshold (mm)
     */
    static void updateThresholds(uint16_t topThreshold,
                                 uint16_t leftThreshold,
                                 uint16_t rightThreshold);

    // =======================[ STATUS AND DIAGNOSTICS ]=================
    /**
     * @brief Get current safety state
     * @return Current SafetyState structure
     */
    static SafetyState getSafetyState() { return currentState; }

    /**
     * @brief Print detailed safety status
     */
    static void printSafetyStatus();

    /**
     * @brief Reset safety state (clear consecutive detections)
     */
    static void resetSafetyState();

    /**
     * @brief Check if system is in emergency stop state
     * @return true if emergency stop is active
     */
    static bool isEmergencyStopActive() { return currentState.emergencyStop; }
};

// =======================[ UTILITY FUNCTIONS ]==========================
/**
 * @brief Convert 8x8 matrix coordinates to linear index
 * @param x X coordinate (0-7)
 * @param y Y coordinate (0-7)
 * @return Linear index (0-63)
 */
inline uint8_t matrixToIndex(uint8_t x, uint8_t y)
{
    return y * 8 + x;
}

/**
 * @brief Convert linear index to 8x8 matrix coordinates
 * @param index Linear index (0-63)
 * @param x Reference to store X coordinate
 * @param y Reference to store Y coordinate
 */
inline void indexToMatrix(uint8_t index, uint8_t &x, uint8_t &y)
{
    x = index % 8;
    y = index / 8;
}

#endif // SAFETY_DETECTOR_H
