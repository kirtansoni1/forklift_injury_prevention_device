# -*- coding: utf-8 -*-

"""
Defines all constants and configuration values.
"""
import os
from pathlib import Path

# Camera settings
CAMERA_INDEX = 0
FRAME_WIDTH = 320
FRAME_HEIGHT = 320

# Detection thresholds
CONFIDENCE_THRESHOLD = 0.3  # General detection confidence threshold
CONFIDENCE_THRESHOLD_FACE = 0.45
CONFIDENCE_THRESHOLD_PHONE = 0.6
FACE_CLASS_ID = 0  # 'face'
PHONE_CLASS_ID = 1  # 'phone'

# NCNN model path
# Path to the NCNN model used by the detector. The original path contained a
# typo which prevented the model from loading, resulting in an empty video feed
# in the web interface.
NCNN_MODEL_PATH = Path("traning") / "runs" / "train" / "yolov11n_320_V3" / "weights" / "yolov11n_320_V3_ncnn_model"

# Serial settings
SERIAL_PORT = "COM3" if os.name == "nt" else "/dev/ttyAMA0"
SERIAL_BAUDRATE = 115200

# Drawing colors (BGR)
FACE_DETECTION_COLOR = (0, 255, 0)
PHONE_DETECTION_COLOR = (0, 0, 255)
FPS_COLOR = (0, 255, 0)
BOUND_LINE_COLOR = (255, 202, 40)
POINT_COLOR = (255, 0, 0)

# UI color palette
UI_PRIMARY_COLOR = "#ffca28"
UI_ALERT_COLOR = "#ff5252"
UI_INFO_COLOR = "#42a5f5"

# Notice display duration in seconds
NOTICE_DURATION = 3

# Detection settings
DRAW_POINT_OFFSET = 5  # Pixels below the top line of the bbox

# Phone detection scan window. After a phone is first detected the system
# samples the next N frames and requires at least half of them to contain a
# phone before confirming detection.
PHONE_SCAN_FRAMES = 30

# Number of frames to keep warnings active after confirmation. The default is
# twice the scan window for noticeable but not overly long alerts.
PHONE_DEBOUNCE_FRAMES = PHONE_SCAN_FRAMES * 2

# Safe-zone breach warning duration in frames.
SAFE_ZONE_DEBOUNCE_FRAMES = 30

# Serial command messages
PHONE_COMMAND = "phone_detected"
BREACH_COMMAND = "breach_detected"
