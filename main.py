# -*- coding: utf-8 -*-

import cv2
from threading import Thread, Event
from utils.camera_stream import CameraStream
from core.detector import AIDetector
# from comm.serial_comm import SerialComm
from utils.log import log_info, log_error
from utils.web_stream import start_web_streaming, update_frame
import time


def main():
    detector = AIDetector()
    camera = CameraStream().start()
    stop_event = Event()
    # comm = SerialComm()

    # Start Flask server on a separate thread
    Thread(target=start_web_streaming, daemon=True).start()

    def detection_loop():
        log_info("Detection thread started.")
        while not stop_event.is_set():
            frame = camera.read()
            if frame is None:
                time.sleep(0.005)
                continue

            detections = detector.detect_humans(frame)

            for (x1, y1, x2, y2, conf) in detections:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            update_frame(frame)

    Thread(target=detection_loop, daemon=True).start()

    log_info("System initialized. Detection loop running.")

    try:
        while True:
            time.sleep(1)
    except Exception as e:
        log_error(f"Exception occurred: {e}")
    finally:
        stop_event.set()
        camera.stop()
        # comm.close()
        log_info("System shutdown completed.")


if __name__ == "__main__":
    main()
