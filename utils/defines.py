# -*- coding: utf-8 -*-

"""
Defines all constants and configuration values.
"""

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
NCNN_MODEL_PATH = r"traning\runs\train\yolov11n_320_V2\weights\best_ncnn_model"

# Serial settings
SERIAL_PORT = "/dev/ttyAMA0"
SERIAL_BAUDRATE = 115200
