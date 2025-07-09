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
TARGET_FPS = 7

# Detection thresholds
CONFIDENCE_THRESHOLD = 0.7
IOU_THRESHOLD = 0.45
FACE_CLASS_ID = 0  # 'person'
PHONE_CLASS_ID = 1  # 'cell phone'

# NCNN model path
# Path to the NCNN model used by the detector. The original path contained a
# typo which prevented the model from loading, resulting in an empty video feed
# in the web interface.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
NCNN_MODEL_PATH = PROJECT_ROOT / "traning" / "runs" / "train" / \
    "yolov11n_320_V2" / "weights" / "yolov11n_320_V2_ncnn_model"

# Serial settings
SERIAL_PORT = "COM3" if os.name == "nt" else "/dev/ttyAMA0"
SERIAL_BAUDRATE = 115200
