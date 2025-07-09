# -*- coding: utf-8 -*-

import cv2
import threading
import sys
sys.path.append('.')  # noqa

from utils.defines import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT


class CameraStream:
    """
    Threaded camera stream reader.
    """

    def __init__(self):
        # Explicitly select the V4L2 backend so the USB/CSI camera works
        # reliably across different Linux environments. Without this, OpenCV
        # may pick an incompatible backend and no frames will be captured.
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        # self.cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self._update, daemon=True).start()
        return self

    def _update(self):
        while not self.stopped:
            if self.cap.grab():
                _, frame = self.cap.retrieve()
                with self.lock:
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.stopped = True
        self.cap.release()
