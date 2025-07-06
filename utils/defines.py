# -*- coding: utf-8 -*-

"""
Defines all constants and configuration values.
"""

# Camera settings
CAMERA_INDEX = 0
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
TARGET_FPS = 7

# Detection thresholds
CONFIDENCE_THRESHOLD = 0.7
IOU_THRESHOLD = 0.45
TARGET_CLASS = 0  # 'person'

# NCNN model path
NCNN_MODEL_PATH = r"traning\runs\train\yolov11n_320\weights\best.pt"

# Serial settings
SERIAL_PORT = "/dev/ttyAMA0"
SERIAL_BAUDRATE = 115200
