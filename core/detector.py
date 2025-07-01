import sys
sys.path.append('.')  # noqa

from ultralytics import YOLO
from utils.defines import NCNN_MODEL_PATH, CONFIDENCE_THRESHOLD, TARGET_CLASS


class YOLOv11Detector:
    """
    YOLOv11 detector using Ultralytics NCNN model.
    """

    def __init__(self):
        self.model = YOLO(NCNN_MODEL_PATH)

    def detect_humans(self, frame):
        results = self.model(frame, verbose=False)
        humans = []
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == TARGET_CLASS and float(box.conf[0]) > CONFIDENCE_THRESHOLD:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    humans.append((x1, y1, x2, y2, conf))
        return humans
