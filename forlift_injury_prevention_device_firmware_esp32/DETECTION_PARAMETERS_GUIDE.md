# 🔧 Forklift ADAS Detection Parameters Configuration Guide

## 📋 Overview
This document provides a comprehensive guide to all configurable parameters in the forklift ADAS safety detection system. These parameters control the sensitivity, reliability, and performance of the object detection algorithm that prevents collisions with humans and objects.

## 🎯 Detection Thresholds

### Primary Distance Thresholds
**Location:** `src/safety_detector.cpp` (Global variables)

| Parameter | Default Value | Description | Adjustment Impact |
|-----------|---------------|-------------|-------------------|
| `THRESHOLD_TOP_MM` | 1500mm (1.5m) | Distance threshold for top sensor | **Sensitivity Control**: Lower = more sensitive, Higher = less sensitive |
| `THRESHOLD_LEFT_MM` | 1000mm (1.0m) | Distance threshold for left sensor | **Side Protection**: Adjust based on platform width and clearance needs |
| `THRESHOLD_RIGHT_MM` | 1000mm (1.0m) | Distance threshold for right sensor | **Side Protection**: Should match left sensor for symmetric detection |

**Runtime Modification:** These can be changed during operation using `SafetyDetector::updateThresholds()`

---

## 🧠 Detection Algorithm Parameters

### Core Detection Logic
**Location:** `include/safety_detector.h`

| Parameter | Default Value | Description | Tuning Guidelines |
|-----------|---------------|-------------|-------------------|
| `MIN_VALID_READINGS` | 20 | Minimum valid readings required out of 64 matrix cells | **Noise Rejection**: Increase for noisier environments (max 64) |
| `DETECTION_CONSENSUS_PCT` | 25% | Percentage of valid readings that must be below threshold | **Sensitivity**: Lower = more sensitive, Higher = more robust |
| `CONSECUTIVE_DETECTIONS` | 2 | Required consecutive positive detections before triggering | **Stability**: Increase to reduce false positives, Decrease for faster response |

### Range Validation
**Location:** `include/safety_detector.h`

| Parameter | Default Value | Description | Adjustment Guidelines |
|-----------|---------------|-------------|-------------------|
| `MAX_SENSOR_RANGE_MM` | 4000mm (4.0m) | Maximum valid sensor reading | **Range Limit**: Should not exceed sensor specifications |
| `MIN_SENSOR_RANGE_MM` | 50mm | Minimum valid sensor reading (noise floor) | **Noise Floor**: Increase if seeing noise below this distance |
| `DETECTION_HYSTERESIS_MM` | 100mm | Hysteresis to prevent detection oscillation | **Stability**: Increase to reduce flutter around threshold |

---

## ⚡ System Timing Parameters

### Main Loop Timing
**Location:** `include/defines.h`

| Parameter | Default Value | Description | Performance Impact |
|-----------|---------------|-------------|-------------------|
| `LOOP_DELAY_MS` | 50ms | Main processing loop delay | **Response Time**: Lower = faster response but higher CPU usage |
| `RANGING_FREQUENCY_HZ` | 15Hz | Sensor measurement frequency | **Data Rate**: Higher = more data but increased power consumption |

### Sensor Communication
**Location:** `include/defines.h`

| Parameter | Default Value | Description | Reliability Impact |
|-----------|---------------|-------------|-------------------|
| `I2C_FREQUENCY_HZ` | 100000 (100kHz) | I2C bus communication speed | **Stability**: Lower for better reliability, Higher for speed |
| `I2C_TIMEOUT_MS` | 50ms | I2C communication timeout | **Error Recovery**: Lower for faster recovery, Higher for reliability |

---

## 🎛️ Sensitivity Adjustment Guidelines

### Increasing Sensitivity (More Responsive)
To make the system more sensitive to objects:
1. **Decrease** `THRESHOLD_*_MM` values (detect objects further away)
2. **Decrease** `DETECTION_CONSENSUS_PCT` (require fewer cells for detection)
3. **Decrease** `CONSECUTIVE_DETECTIONS` (trigger faster)
4. **Decrease** `MIN_VALID_READINGS` (accept more noisy data)

### Decreasing Sensitivity (More Robust)
To make the system less prone to false positives:
1. **Increase** `THRESHOLD_*_MM` values (only detect closer objects)
2. **Increase** `DETECTION_CONSENSUS_PCT` (require more cells for detection)
3. **Increase** `CONSECUTIVE_DETECTIONS` (require more confirmations)
4. **Increase** `MIN_VALID_READINGS` (require cleaner data)

---

## 🔧 Parameter Modification Methods

### 1. Compile-Time Configuration
Edit values directly in header files:
- **Thresholds**: Modify defaults in `src/safety_detector.cpp`
- **Algorithm parameters**: Modify `#define` values in `include/safety_detector.h`
- **System timing**: Modify `#define` values in `include/defines.h`

### 2. Runtime Configuration
Use provided functions for dynamic adjustment:
```cpp
// Update thresholds during operation
SafetyDetector::updateThresholds(1200, 800, 800);

// Available in main.cpp
updateSafetyThresholds(1200, 800, 800);
```

### 3. Serial Commands (Future Enhancement)
Consider implementing serial commands for real-time tuning:
```cpp
// Example implementation needed
void processSerialCommands() {
    if (Serial.available()) {
        // Parse commands like "SET_THRESHOLD_TOP 1200"
        // Update parameters dynamically
    }
}
```

---

## 📊 Monitoring and Debugging

### Debug Output Control
**Location:** `src/safety_detector.cpp`

Uncomment `#define DEBUG_DETECTION` to enable detailed detection analysis output.

### Status Monitoring Functions
**Location:** `src/main.cpp` and `safety_detector.cpp`

| Function | Purpose | Usage |
|----------|---------|-------|
| `printSystemStatus()` | Complete system overview | Call for comprehensive diagnostics |
| `SafetyDetector::printSafetyStatus()` | Detection state details | Monitor current safety status |
| `isSafetyTriggered()` | Check current state | Quick status check for external systems |

---

## ⚠️ Critical Safety Considerations

### Parameter Constraints
1. **Never set thresholds below 200mm** - Too close for safe operation
2. **CONSECUTIVE_DETECTIONS should be ≥ 2** - Prevents single-sample false triggers
3. **MIN_VALID_READINGS should be ≥ 15** - Ensures sufficient data for reliable detection
4. **DETECTION_CONSENSUS_PCT should be 15-50%** - Balance between sensitivity and reliability

### Testing Protocol
When adjusting parameters:
1. **Test in controlled environment first**
2. **Verify with known objects at known distances**
3. **Test edge cases** (reflective surfaces, thin objects, etc.)
4. **Validate emergency stop response time**
5. **Document all changes and their effects**

---

## 📝 Change Log Template

When modifying parameters, document changes:

```
Date: [Date]
Modified by: [Name]
Parameters Changed:
- THRESHOLD_TOP_MM: [old] → [new] 
- [Parameter]: [old] → [new]
Reason: [Why the change was made]
Test Results: [Observed behavior changes]
Environment: [Where tested]
```

---

## 🔗 Related Files

- **Configuration**: `include/defines.h`, `include/safety_detector.h`
- **Implementation**: `src/safety_detector.cpp`, `src/main.cpp`
- **Examples**: `examples/safety_system_example.cpp`
- **Hardware**: Pin assignments in `include/defines.h`

---
