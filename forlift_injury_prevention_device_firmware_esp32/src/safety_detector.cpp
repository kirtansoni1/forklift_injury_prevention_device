#include "safety_detector.h"

// =======================[ GLOBAL THRESHOLD VARIABLES ]==================
uint16_t THRESHOLD_TOP_MM = 1500; // Default: 1.5 meters for top sensor
                                  // 📖 TUNING GUIDE: Primary sensitivity control for overhead detection
                                  //    Lower (1000-1200mm) = detect objects further away (more sensitive)
                                  //    Higher (1800-2000mm) = only detect closer objects (less sensitive)
                                  //    Recommended range: 1000-2500mm based on platform height
                                  // 📍 CONFIG GUIDE: Can be changed at runtime via updateThresholds()
                                  //    See DETECTION_PARAMETERS_GUIDE.md for complete guide

uint16_t THRESHOLD_LEFT_MM = 1000; // Default: 1.0 meter for left sensor
                                   // 📖 TUNING GUIDE: Side detection sensitivity control
                                   //    Lower (600-800mm) = wider safety zone, more sensitive
                                   //    Higher (1200-1500mm) = narrower safety zone, less sensitive
                                   //    Should consider platform width + safety margin
                                   // 📍 CONFIG GUIDE: Usually matches RIGHT sensor for symmetry
                                   //    See DETECTION_PARAMETERS_GUIDE.md for environment-specific tuning

uint16_t THRESHOLD_RIGHT_MM = 1000; // Default: 1.0 meter for right sensor
                                    // 📖 TUNING GUIDE: Side detection sensitivity control
                                    //    Should typically match LEFT_MM for symmetric protection
                                    //    Adjust both together unless asymmetric environment requires different values
                                    // 📍 CONFIG GUIDE: Runtime adjustable via updateThresholds()
                                    //    See DETECTION_PARAMETERS_GUIDE.md for optimization guidelines

// =======================[ STATIC MEMBER INITIALIZATION ]================
SafetyState SafetyDetector::currentState = {
    .topSensorTriggered = false,
    .leftSensorTriggered = false,
    .rightSensorTriggered = false,
    .emergencyStop = false,
    .lastTriggerTime = 0,
    .consecutiveTopDetections = 0,
    .consecutiveLeftDetections = 0,
    .consecutiveRightDetections = 0};

// =======================[ INITIALIZATION ]==============================
void SafetyDetector::initialize()
{
    // Initialize relay control
    initializeRelays();

    // Reset safety state
    resetSafetyState();

    Serial.println("🛡️ Safety Detection System Initialized");
    Serial.println("========================================");
    Serial.print("📏 Top Sensor Threshold: ");
    Serial.print(THRESHOLD_TOP_MM);
    Serial.println("mm");
    Serial.print("📏 Left Sensor Threshold: ");
    Serial.print(THRESHOLD_LEFT_MM);
    Serial.println("mm");
    Serial.print("📏 Right Sensor Threshold: ");
    Serial.print(THRESHOLD_RIGHT_MM);
    Serial.println("mm");
    Serial.println("========================================");
}

// =======================[ RELAY CONTROL ]===============================
void SafetyDetector::initializeRelays()
{
    // Configure relay pins as outputs
    pinMode(RELAY1_PIN, OUTPUT);
    pinMode(RELAY2_PIN, OUTPUT);

    // Set relays to safe state (HIGH = relay open = motors stopped)
    digitalWrite(RELAY1_PIN, HIGH);
    digitalWrite(RELAY2_PIN, HIGH);

    Serial.println("🔌 Safety relays initialized in SAFE state (motors stopped)");
}

void SafetyDetector::controlSafetyRelays(bool emergencyStop)
{
    if (emergencyStop)
    {
        // Emergency stop: Open relays (HIGH) to cut motor power
        digitalWrite(RELAY1_PIN, HIGH);
        digitalWrite(RELAY2_PIN, HIGH);
        Serial.println("🚨 EMERGENCY STOP ACTIVATED - Motors stopped");
    }
    else
    {
        // Normal operation: Close relays (LOW) to allow motor power
        digitalWrite(RELAY1_PIN, LOW);
        digitalWrite(RELAY2_PIN, LOW);
        Serial.println("✅ Normal operation - Motors enabled");
    }
}

// =======================[ VALIDATION FUNCTIONS ]========================
bool SafetyDetector::isValidReading(uint16_t distance)
{
    // Filter out noise and invalid readings
    return (distance >= MIN_SENSOR_RANGE_MM && distance <= MAX_SENSOR_RANGE_MM);
}

// =======================[ CORE DETECTION ALGORITHM ]====================
DetectionResult SafetyDetector::analyzeMatrix(const VL53L5CX_ResultsData &data, uint16_t threshold)
{
    DetectionResult result = {0};
    result.timestamp = millis();
    result.closestDistance = MAX_SENSOR_RANGE_MM;

    uint16_t validDistanceSum = 0;
    uint8_t belowThresholdCount = 0;

    // Analyze all 64 zones in the 8x8 matrix
    for (int i = 0; i < 64; i++)
    {
        uint16_t distance = data.distance_mm[i];

        // Check if reading is valid
        if (isValidReading(distance))
        {
            result.validReadings++;
            validDistanceSum += distance;

            // Update closest distance
            if (distance < result.closestDistance)
            {
                result.closestDistance = distance;
            }

            // Check if this reading is below threshold
            if (distance < threshold)
            {
                belowThresholdCount++;
            }
        }
    }

    // Calculate detection metrics
    result.detectionsInMatrix = belowThresholdCount;

    if (result.validReadings > 0)
    {
        result.averageDistance = validDistanceSum / result.validReadings;
        result.detectionConfidence = (float)belowThresholdCount / result.validReadings * 100.0;
    }

    // Apply consensus-based detection logic
    result.objectDetected = applyConsensusFilter(result);

    return result;
}

bool SafetyDetector::applyConsensusFilter(const DetectionResult &result)
{
    // Minimum valid readings check
    if (result.validReadings < MIN_VALID_READINGS)
    {
        return false; // Not enough valid data
    }

    // Consensus percentage check
    float detectionPercentage = (float)result.detectionsInMatrix / result.validReadings * 100.0;
    if (detectionPercentage < DETECTION_CONSENSUS_PCT)
    {
        return false; // Not enough consensus for detection
    }

    // Additional robustness checks

    // 1. Cluster analysis: Check if detections are clustered (not scattered noise)
    // This is a simplified cluster check - could be enhanced with spatial analysis
    if (result.detectionsInMatrix > 0 && result.closestDistance < (result.averageDistance - DETECTION_HYSTERESIS_MM))
    {
        return true; // Strong signal with clear closest object
    }

    // 2. High confidence detection
    if (detectionPercentage > 50.0)
    {
        return true; // Very high confidence
    }

    return false;
}

// =======================[ CONSECUTIVE DETECTION MANAGEMENT ]=============
void SafetyDetector::updateConsecutiveDetections(bool detected, uint8_t &counter)
{
    if (detected)
    {
        counter = min(counter + 1, 255); // Prevent overflow
    }
    else
    {
        counter = 0; // Reset on no detection
    }
}

// =======================[ MAIN DETECTION FUNCTIONS ]====================
DetectionResult SafetyDetector::detectObject(const VL53L5CX_ResultsData &data,
                                             uint16_t threshold,
                                             const char *sensorName)
{
    DetectionResult result = analyzeMatrix(data, threshold);

// Optional: Print detailed analysis for debugging
#ifdef DEBUG_DETECTION
    printDetectionDetails(sensorName, result);
#endif

    return result;
}

bool SafetyDetector::processAllSensors(const VL53L5CX_ResultsData &topData,
                                       const VL53L5CX_ResultsData &leftData,
                                       const VL53L5CX_ResultsData &rightData)
{
    bool previousEmergencyState = currentState.emergencyStop;

    // Analyze each sensor
    DetectionResult topResult = detectObject(topData, THRESHOLD_TOP_MM, "TOP");
    DetectionResult leftResult = detectObject(leftData, THRESHOLD_LEFT_MM, "LEFT");
    DetectionResult rightResult = detectObject(rightData, THRESHOLD_RIGHT_MM, "RIGHT");

    // Update consecutive detection counters
    updateConsecutiveDetections(topResult.objectDetected, currentState.consecutiveTopDetections);
    updateConsecutiveDetections(leftResult.objectDetected, currentState.consecutiveLeftDetections);
    updateConsecutiveDetections(rightResult.objectDetected, currentState.consecutiveRightDetections);

    // Apply consecutive detection requirement for stability
    currentState.topSensorTriggered = (currentState.consecutiveTopDetections >= CONSECUTIVE_DETECTIONS);
    currentState.leftSensorTriggered = (currentState.consecutiveLeftDetections >= CONSECUTIVE_DETECTIONS);
    currentState.rightSensorTriggered = (currentState.consecutiveRightDetections >= CONSECUTIVE_DETECTIONS);

    // Determine overall emergency state
    bool anyTrigger = currentState.topSensorTriggered ||
                      currentState.leftSensorTriggered ||
                      currentState.rightSensorTriggered;

    currentState.emergencyStop = anyTrigger;

    // Update timestamp if state changed
    if (currentState.emergencyStop != previousEmergencyState)
    {
        currentState.lastTriggerTime = millis();

        if (currentState.emergencyStop)
        {
            Serial.println("🚨 OBJECT DETECTED - EMERGENCY STOP TRIGGERED!");
            Serial.print("🔍 Triggered by: ");
            if (currentState.topSensorTriggered)
                Serial.print("TOP ");
            if (currentState.leftSensorTriggered)
                Serial.print("LEFT ");
            if (currentState.rightSensorTriggered)
                Serial.print("RIGHT ");
            Serial.println();
        }
        else
        {
            Serial.println("✅ All clear - Emergency stop deactivated");
        }
    }

    // Control relays based on safety state
    controlSafetyRelays(currentState.emergencyStop);

    // Print status every 1 second when triggered
    static uint32_t lastStatusPrint = 0;
    if (currentState.emergencyStop && (millis() - lastStatusPrint > 1000))
    {
        printSafetyStatus();
        lastStatusPrint = millis();
    }

    return currentState.emergencyStop;
}

// =======================[ THRESHOLD MANAGEMENT ]========================
void SafetyDetector::updateThresholds(uint16_t topThreshold,
                                      uint16_t leftThreshold,
                                      uint16_t rightThreshold)
{
    THRESHOLD_TOP_MM = topThreshold;
    THRESHOLD_LEFT_MM = leftThreshold;
    THRESHOLD_RIGHT_MM = rightThreshold;

    Serial.println("📏 Detection thresholds updated:");
    Serial.print("   Top: ");
    Serial.print(THRESHOLD_TOP_MM);
    Serial.println("mm");
    Serial.print("   Left: ");
    Serial.print(THRESHOLD_LEFT_MM);
    Serial.println("mm");
    Serial.print("   Right: ");
    Serial.print(THRESHOLD_RIGHT_MM);
    Serial.println("mm");
}

// =======================[ STATUS AND DIAGNOSTICS ]======================
void SafetyDetector::printSafetyStatus()
{
    Serial.println("🛡️ SAFETY STATUS REPORT");
    Serial.println("========================");
    Serial.print("🚨 Emergency Stop: ");
    Serial.println(currentState.emergencyStop ? "ACTIVE" : "inactive");
    Serial.print("📡 Top Sensor: ");
    Serial.print(currentState.topSensorTriggered ? "TRIGGERED" : "clear");
    Serial.print(" (");
    Serial.print(currentState.consecutiveTopDetections);
    Serial.println(" consecutive)");
    Serial.print("📡 Left Sensor: ");
    Serial.print(currentState.leftSensorTriggered ? "TRIGGERED" : "clear");
    Serial.print(" (");
    Serial.print(currentState.consecutiveLeftDetections);
    Serial.println(" consecutive)");
    Serial.print("📡 Right Sensor: ");
    Serial.print(currentState.rightSensorTriggered ? "TRIGGERED" : "clear");
    Serial.print(" (");
    Serial.print(currentState.consecutiveRightDetections);
    Serial.println(" consecutive)");

    if (currentState.emergencyStop)
    {
        uint32_t triggerDuration = millis() - currentState.lastTriggerTime;
        Serial.print("⏱️ Trigger Duration: ");
        Serial.print(triggerDuration);
        Serial.println("ms");
    }
    Serial.println("========================");
}

void SafetyDetector::resetSafetyState()
{
    currentState.topSensorTriggered = false;
    currentState.leftSensorTriggered = false;
    currentState.rightSensorTriggered = false;
    currentState.emergencyStop = false;
    currentState.lastTriggerTime = 0;
    currentState.consecutiveTopDetections = 0;
    currentState.consecutiveLeftDetections = 0;
    currentState.consecutiveRightDetections = 0;

    Serial.println("🔄 Safety state reset");
}

void SafetyDetector::printDetectionDetails(const char *sensorName, const DetectionResult &result)
{
    Serial.print("🔍 ");
    Serial.print(sensorName);
    Serial.print(" Analysis: ");
    Serial.print("Valid:");
    Serial.print(result.validReadings);
    Serial.print("/64, Detections:");
    Serial.print(result.detectionsInMatrix);
    Serial.print(", Closest:");
    Serial.print(result.closestDistance);
    Serial.print("mm, Confidence:");
    Serial.print(result.detectionConfidence, 1);
    Serial.print("%, Result:");
    Serial.println(result.objectDetected ? "DETECTED" : "clear");
}
