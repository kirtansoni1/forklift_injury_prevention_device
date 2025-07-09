# -*- coding: utf-8 -*-

import os
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
        # Select appropriate backend based on operating system
        backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_V4L2
        self.cap = cv2.VideoCapture(CAMERA_INDEX, backend)
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
