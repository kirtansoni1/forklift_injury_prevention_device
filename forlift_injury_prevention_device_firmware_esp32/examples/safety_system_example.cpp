/**
 * @file safety_system_example.cpp
 * @brief Example usage of the ADAS Safety Detection System
 * @details This file demonstrates how to use the safety detection system
 *          for industrial platform collision avoidance
 *
 * @author Forklift Safety Team
 * @date 2025
 */

#include "main.h"

// =======================[ EXAMPLE USAGE FUNCTIONS ]===================

/**
 * @brief Example: Basic safety system operation
 */
void exampleBasicOperation()
{
    Serial.println("🔧 Example: Basic Safety Operation");

    // The main loop already handles basic detection automatically
    // Just call processAllSensors() in your main loop

    // Check current safety status
    if (isSafetyTriggered())
    {
        Serial.println("⚠️ Safety system is currently triggered");
    }
    else
    {
        Serial.println("✅ All clear for operation");
    }
}

/**
 * @brief Example: Updating thresholds dynamically
 */
void exampleUpdateThresholds()
{
    Serial.println("🔧 Example: Dynamic Threshold Update");

    // Update thresholds based on operational requirements
    // For example, closer thresholds in tight spaces
    updateSafetyThresholds(800, 600, 600); // Tighter thresholds

    delay(5000); // Operate with tight thresholds

    // Return to normal thresholds
    updateSafetyThresholds(1500, 1000, 1000); // Normal thresholds
}

/**
 * @brief Example: Manual override for maintenance
 */
void exampleManualOverride()
{
    Serial.println("🔧 Example: Manual Override for Maintenance");

    // Disable safety system for maintenance (USE WITH EXTREME CAUTION!)
    manualEmergencyOverride(false); // Allow movement

    Serial.println("⚠️ CAUTION: Safety system overridden!");
    Serial.println("⚠️ Ensure area is clear before proceeding!");

    delay(1000);

    // Re-enable safety system
    manualEmergencyOverride(true); // Safety stop
    Serial.println("✅ Safety system re-enabled");
}

/**
 * @brief Example: System diagnostics and monitoring
 */
void exampleSystemDiagnostics()
{
    Serial.println("🔧 Example: System Diagnostics");

    // Print comprehensive system status
    printSystemStatus();

    // Get safety state for custom logic
    SafetyState state = SafetyDetector::getSafetyState();

    if (state.emergencyStop)
    {
        Serial.println("📊 Custom Analysis:");
        Serial.print("   - Top sensor: ");
        Serial.println(state.topSensorTriggered ? "TRIGGERED" : "OK");
        Serial.print("   - Left sensor: ");
        Serial.println(state.leftSensorTriggered ? "TRIGGERED" : "OK");
        Serial.print("   - Right sensor: ");
        Serial.println(state.rightSensorTriggered ? "TRIGGERED" : "OK");

        uint32_t triggerDuration = millis() - state.lastTriggerTime;
        Serial.print("   - Trigger duration: ");
        Serial.print(triggerDuration);
        Serial.println("ms");
    }
}

/**
 * @brief Example: Adaptive threshold based on platform speed
 */
void exampleAdaptiveThresholds()
{
    Serial.println("🔧 Example: Adaptive Thresholds");

    // Simulate different platform speeds
    float platformSpeed = 2.5; // m/s (example)

    // Calculate adaptive thresholds based on stopping distance
    // Stopping distance = speed² / (2 * deceleration)
    // Assuming 2 m/s² deceleration capability
    float stoppingDistance = (platformSpeed * platformSpeed) / (2 * 2.0);

    // Add safety margin (50% extra)
    uint16_t adaptiveThreshold = (uint16_t)((stoppingDistance * 1.5) * 1000); // Convert to mm

    // Apply speed-based thresholds
    updateSafetyThresholds(adaptiveThreshold, adaptiveThreshold, adaptiveThreshold);

    Serial.print("📏 Adaptive threshold for ");
    Serial.print(platformSpeed);
    Serial.print(" m/s: ");
    Serial.print(adaptiveThreshold);
    Serial.println("mm");
}

// =======================[ INTEGRATION EXAMPLES ]======================

/**
 * @brief Example: Integration with external control system
 */
void exampleExternalIntegration()
{
    Serial.println("🔧 Example: External System Integration");

    // Example: Send status to external system (Raspberry Pi, PLC, etc.)
    SafetyState state = SafetyDetector::getSafetyState();

    // Create status message for external system
    String statusMessage = "SAFETY_STATUS:";
    statusMessage += state.emergencyStop ? "STOP" : "GO";
    statusMessage += ",TOP:" + String(state.topSensorTriggered ? 1 : 0);
    statusMessage += ",LEFT:" + String(state.leftSensorTriggered ? 1 : 0);
    statusMessage += ",RIGHT:" + String(state.rightSensorTriggered ? 1 : 0);

    // Send via UART to Raspberry Pi (example)
    Serial2.println(statusMessage); // Assuming Serial2 is connected to Pi

    Serial.println("📡 Status sent to external system: " + statusMessage);
}

/**
 * @brief Example: Override button handling
 */
void exampleOverrideButton()
{
    static bool lastButtonState = HIGH;
    static uint32_t buttonPressTime = 0;
    static bool overrideActive = false;

    // Read override button (with debouncing)
    bool currentButtonState = digitalRead(OVRRD_BUTTON_PIN);

    if (currentButtonState != lastButtonState)
    {
        if (currentButtonState == LOW)
        { // Button pressed
            buttonPressTime = millis();
        }
        else
        { // Button released
            uint32_t pressDuration = millis() - buttonPressTime;

            // Require 3-second press for safety override
            if (pressDuration > 3000)
            {
                overrideActive = !overrideActive;
                manualEmergencyOverride(!overrideActive); // Invert logic

                Serial.print("🔘 Override button: ");
                Serial.println(overrideActive ? "ACTIVATED" : "DEACTIVATED");
            }
        }
        lastButtonState = currentButtonState;
    }

    // Automatic override timeout (safety feature)
    static uint32_t overrideStartTime = 0;
    if (overrideActive)
    {
        if (overrideStartTime == 0)
        {
            overrideStartTime = millis();
        }
        else if (millis() - overrideStartTime > 30000)
        { // 30-second timeout
            overrideActive = false;
            manualEmergencyOverride(true); // Return to safety mode
            Serial.println("⏰ Override timeout - returning to safety mode");
            overrideStartTime = 0;
        }
    }
    else
    {
        overrideStartTime = 0;
    }
}

// =======================[ USAGE NOTES ]================================
/*
 * INTEGRATION GUIDE:
 *
 * 1. Basic Integration:
 *    - Include safety_detector.h in your main file
 *    - Call SafetyDetector::initialize() in setup()
 *    - Call SafetyDetector::processAllSensors() in loop()
 *    - Monitor isSafetyTriggered() for safety state
 *
 * 2. Threshold Management:
 *    - Use updateSafetyThresholds() to adjust detection ranges
 *    - Consider platform speed, load, and environment
 *    - Implement adaptive thresholds for optimal safety
 *
 * 3. External Integration:
 *    - Use SafetyDetector::getSafetyState() for detailed status
 *    - Implement communication protocols for external systems
 *    - Consider redundant safety measures
 *
 * 4. Maintenance Mode:
 *    - Use manualEmergencyOverride() with extreme caution
 *    - Implement timeout mechanisms
 *    - Require operator confirmation
 *
 * 5. Monitoring and Diagnostics:
 *    - Use printSystemStatus() for comprehensive diagnostics
 *    - Monitor sensor health and calibration
 *    - Log safety events for analysis
 *
 * SAFETY CONSIDERATIONS:
 * - Always test thoroughly in controlled environment
 * - Implement redundant safety measures
 * - Regular calibration and maintenance required
 * - Train operators on emergency procedures
 * - Comply with industrial safety standards
 */
