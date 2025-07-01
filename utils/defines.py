"""
Defines all constants and configuration values.
"""

# Camera settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 30

# Detection thresholds
CONFIDENCE_THRESHOLD = 0.4
IOU_THRESHOLD = 0.45
TARGET_CLASS = 0  # 'person'

# NCNN model path
NCNN_MODEL_PATH = "model/yolov11n_ncnn"

# Serial settings
SERIAL_PORT = "/dev/ttyAMA0"
SERIAL_BAUDRATE = 115200
