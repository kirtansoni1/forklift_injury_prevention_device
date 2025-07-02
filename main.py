# -*- coding: utf-8 -*-

import cv2
from threading import Thread
from utils.camera_stream import CameraStream
from core.detector import AIDetector
from comm.serial_comm import SerialComm
from utils.log import log_info, log_error
from utils.web_stream import start_web_streaming, update_frame
import time


def main():
    detector = AIDetector()
    camera = CameraStream().start()
    # comm = SerialComm()

    # Start Flask server on a separate thread
    Thread(target=start_web_streaming, daemon=True).start()

    log_info("System initialized. Starting detection loop.")

    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue

            detections = detector.detect_humans(frame)

            for (x1, y1, x2, y2, conf) in detections:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Optional: send/receive logic (currently commented)
            # if detections:
            #     comm.send("human_detected")
            # msg = comm.receive()
            # if msg:
            #     log_info(f"Received from ESP32-S3: {msg}")

            # Update the stream frame for web viewing
            update_frame(frame)

    except Exception as e:
        log_error(f"Exception occurred: {e}")
    finally:
        camera.stop()
        # comm.close()
        log_info("System shutdown completed.")


if __name__ == "__main__":
    main()
