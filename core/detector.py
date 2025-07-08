# -*- coding: utf-8 -*-

import sys
sys.path.append('.')  # noqa

from ultralytics import YOLO
import torch
from utils.defines import NCNN_MODEL_PATH, CONFIDENCE_THRESHOLD


class AIDetector:
    """
    YOLOv11 detector using Ultralytics NCNN model.
    """

    def __init__(self, device: str | None = None):
        """Load the YOLO NCNN model on the optimal device."""
        if device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.model = YOLO(NCNN_MODEL_PATH, task='detect')

    def detect_humans(self, frame):
        """Run inference and return detected humans as bounding boxes."""
        results = self.model(frame, verbose=False, device=self.device)
        humans = []
        for result in results:
            for box in result.boxes:
                if float(box.conf[0]) > CONFIDENCE_THRESHOLD:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    humans.append((x1, y1, x2, y2, conf))
        return humans
