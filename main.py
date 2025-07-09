# -*- coding: utf-8 -*-

import cv2
from threading import Thread
from utils.camera_stream import CameraStream
from core.detector import AIDetector
from comm.serial_comm import SerialComm
from utils.log import log_info, log_error
from utils.web_stream import start_web_streaming, update_frame, get_bounds
from utils.defines import (
    FACE_CLASS_ID,
    PHONE_CLASS_ID,
    BOX_COLOR,
    POINT_COLOR,
    BOUND_LINE_COLOR,
    DRAW_POINT_OFFSET,
    PHONE_COMMAND,
    BREACH_COMMAND,
    FRAME_HEIGHT,
)
import time


def main():
    detector = AIDetector()
    camera = CameraStream().start()
    comm = SerialComm()
    face_was_safe = False

    # Start Flask server on a separate thread
    Thread(target=start_web_streaming, daemon=True).start()

    log_info("System initialized. Starting detection loop.")

    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue

            detections = detector.detect_humans(frame)

            bounds = get_bounds()
            if bounds is not None:
                cv2.line(frame, (bounds[0], 0), (bounds[0], FRAME_HEIGHT), BOUND_LINE_COLOR, 2)
                cv2.line(frame, (bounds[1], 0), (bounds[1], FRAME_HEIGHT), BOUND_LINE_COLOR, 2)

            for (x1, y1, x2, y2, conf, cls_id) in detections:
                if cls_id == PHONE_CLASS_ID:
                    comm.send(PHONE_COMMAND)

                if cls_id == FACE_CLASS_ID:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOR, 2)
                    mid_x = (x1 + x2) // 2
                    mid_y = y1 + DRAW_POINT_OFFSET
                    cv2.circle(frame, (mid_x, mid_y), 3, POINT_COLOR, -1)

                    if bounds is not None:
                        left, right = sorted(bounds)
                        in_safe = left <= mid_x <= right
                        if not in_safe and face_was_safe:
                            comm.send(BREACH_COMMAND)
                            face_was_safe = False
                        elif in_safe:
                            face_was_safe = True

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
