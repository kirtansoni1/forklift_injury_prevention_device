# -*- coding: utf-8 -*-

"""Main application entry point.

This script initializes the camera, AI detector and web server to provide a
real-time view of the forklift area. Detected faces and phone usage are
highlighted on the stream and notices are exposed through a small Flask
interface.

Run this script with Python 3.11 after installing the requirements::

    python main.py

Author: Kirtan Soni
"""

import cv2
from threading import Thread
from utils.camera_stream import CameraStream
from core.detector import AIDetector
# from comm.serial_comm import SerialComm
from utils.log import log_info, log_error
from utils.web_stream import (
    start_web_streaming,
    update_frame,
    get_bounds,
    update_status,
    set_notice,
    hold_notice,
)
from utils.defines import (
    FACE_CLASS_ID,
    PHONE_CLASS_ID,
    FACE_DETECTION_COLOR,
    PHONE_DETECTION_COLOR,
    FPS_COLOR,
    POINT_COLOR,
    BOUND_LINE_COLOR,
    DRAW_POINT_OFFSET,
    PHONE_COMMAND,
    BREACH_COMMAND,
    PHONE_SCAN_FRAMES,
    SAFE_ZONE_SCAN_FRAMES,
    PHONE_DEBOUNCE_FRAMES,
    SAFE_ZONE_DEBOUNCE_FRAMES,
    CONFIDENCE_THRESHOLD_FACE,
    CONFIDENCE_THRESHOLD_PHONE,
)
import time
from collections import deque


def main():
    detector = AIDetector()
    camera = CameraStream().start()
    # comm = SerialComm()
    phone_timer = 0
    safe_zone_timer = 0
    phone_history = deque(maxlen=PHONE_SCAN_FRAMES)
    safe_history = deque(maxlen=SAFE_ZONE_SCAN_FRAMES)
    prev_time = time.time()

    # Start Flask server on a separate thread
    Thread(target=start_web_streaming, daemon=True).start()

    log_info("System initialized. Starting detection loop.")

    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue

            now = time.time()
            fps = 1.0 / (now - prev_time)
            prev_time = now

            detections = detector.detect_humans(frame)

            bounds = get_bounds()
            # Debugging: Uncomment to visualize bounds------------------------------------------
            # if bounds is not None:
            #     height = frame.shape[0]
            #     cv2.line(frame, (bounds[0], 0), (bounds[0], height), BOUND_LINE_COLOR, 2)
            #     cv2.line(frame, (bounds[1], 0), (bounds[1], height), BOUND_LINE_COLOR, 2)
            # -----------------------------------------------------------------------------------

            phone_present = False
            operator_count = 0
            any_inside = False
            any_outside = False

            for (x1, y1, x2, y2, conf, cls_id) in detections:
                if cls_id == PHONE_CLASS_ID and conf > CONFIDENCE_THRESHOLD_PHONE:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), PHONE_DETECTION_COLOR, 2)
                    phone_present = True

                if cls_id == FACE_CLASS_ID and conf > CONFIDENCE_THRESHOLD_FACE:
                    operator_count += 1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), FACE_DETECTION_COLOR, 2)
                    mid_x = (x1 + x2) // 2
                    mid_y = y1 + DRAW_POINT_OFFSET
                    cv2.circle(frame, (mid_x, mid_y), 3, POINT_COLOR, -1)

                if bounds is not None:
                    left, right = sorted(bounds)
                    in_safe = left <= mid_x <= right
                    if in_safe:
                        any_inside = True
                    else:
                        any_outside = True

                if bounds is None:
                    # If no bounds are set, consider all faces as inside
                    any_inside = True

            # Phone detection smoothing using a detection window and hold timer
            phone_history.append(1 if phone_present else 0)
            if len(phone_history) == PHONE_SCAN_FRAMES:
                if sum(phone_history) >= PHONE_SCAN_FRAMES // 2:
                    if phone_timer == 0:
                        # comm.send(PHONE_COMMAND)
                        set_notice("Phone detected", "warning")
                    phone_timer = PHONE_DEBOUNCE_FRAMES
                phone_history.clear()
            else:
                if phone_timer > 0 and not phone_present:
                    phone_timer -= 1

            if phone_timer > 0:
                hold_notice("Phone detected")
            phone_active = phone_timer > 0

            # Safe zone breach smoothing using detection window and hold timer
            safe_history.append(1 if any_outside else 0)
            if len(safe_history) == SAFE_ZONE_SCAN_FRAMES:
                if sum(safe_history) >= SAFE_ZONE_SCAN_FRAMES // 2:
                    if safe_zone_timer == 0:
                        # comm.send(BREACH_COMMAND)
                        set_notice("Return to safe zone", "critical")
                    safe_zone_timer = SAFE_ZONE_DEBOUNCE_FRAMES
                safe_history.clear()
            else:
                if safe_zone_timer > 0 and not any_outside:
                    safe_zone_timer -= 1

            if safe_zone_timer > 0:
                hold_notice("Return to safe zone")
            breach_active = safe_zone_timer > 0

            operator_status = "Not Present"
            if operator_count > 0:
                if breach_active:
                    operator_status = "Outside safe zone"
                elif any_inside or not any_outside:
                    operator_status = "Inside safe zone"

            if operator_count > 1:
                set_notice("Too many operators", "warning")


            # Draw FPS on frame
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, FPS_COLOR, 2)

            # Update status for UI
            update_status(phone_active, operator_status, operator_count, round(fps, 1))

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
