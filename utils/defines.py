# -*- coding: utf-8 -*-

"""Central configuration for the detection system.

All tunable parameters used across the project are collected here so that they
can be easily modified from one place.

Author: Kirtan Soni
"""
import os
from pathlib import Path

# Camera settings -----------------------------------------------------------
# Index passed to ``cv2.VideoCapture``
CAMERA_INDEX = 0
# Width of captured frames in pixels
FRAME_WIDTH = 320
# Height of captured frames in pixels
FRAME_HEIGHT = 320

# Detection thresholds ------------------------------------------------------
# Minimum confidence for any detection
CONFIDENCE_THRESHOLD = 0.3
# Threshold specifically for face detections
CONFIDENCE_THRESHOLD_FACE = 0.45
# Threshold specifically for phone detections
CONFIDENCE_THRESHOLD_PHONE = 0.6
# Class IDs as they appear in the YOLO model
FACE_CLASS_ID = 0  # class name "face"
PHONE_CLASS_ID = 1  # class name "phone"

# NCNN model path -----------------------------------------------------------
# Path to the NCNN model used by :class:`AIDetector`
NCNN_MODEL_PATH = Path("traning") / "runs" / "train" / "yolov11n_320_V3" / "weights" / "yolov11n_320_V3_ncnn_model"

# Serial settings -----------------------------------------------------------
# Default port for UART communication with the ESP32
SERIAL_PORT = "COM3" if os.name == "nt" else "/dev/ttyAMA0"
# UART speed in bits per second
SERIAL_BAUDRATE = 115200

# Drawing colors (BGR) -----------------------------------------------------
# Color used for face bounding boxes
FACE_DETECTION_COLOR = (0, 255, 0)
# Color used for phone bounding boxes
PHONE_DETECTION_COLOR = (0, 0, 255)
# Color used when printing FPS on the frame
FPS_COLOR = (0, 255, 0)
# Color of the safe zone boundary lines drawn on the frame
BOUND_LINE_COLOR = (255, 202, 40)
# Color of the small point drawn on detected faces
POINT_COLOR = (255, 0, 0)

# UI color palette ---------------------------------------------------------
# Primary theme color for the web UI
UI_PRIMARY_COLOR = "#ffca28"
# Used for critical warnings
UI_ALERT_COLOR = "#ff5252"
# Used for informational notices
UI_INFO_COLOR = "#42a5f5"

# Notice display duration in seconds --------------------------------------
NOTICE_DURATION = 1

# Detection settings -------------------------------------------------------
# Offset for drawing the face point indicator
DRAW_POINT_OFFSET = 5

# Debounce settings -------------------------------------------------------
# Size of the rolling window used to smooth detections
PHONE_SCAN_FRAMES = 150
SAFE_ZONE_SCAN_FRAMES = 30
# How long to keep a warning active after detection triggers
PHONE_DEBOUNCE_FRAMES = PHONE_SCAN_FRAMES * 2
SAFE_ZONE_DEBOUNCE_FRAMES = SAFE_ZONE_SCAN_FRAMES * 2

# Serial command messages --------------------------------------------------
PHONE_COMMAND = "phone_detected"
BREACH_COMMAND = "breach_detected"
