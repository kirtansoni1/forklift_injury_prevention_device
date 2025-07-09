# -*- coding: utf-8 -*-

import cv2
from threading import Thread
from utils.camera_stream import CameraStream
from core.detector import AIDetector
from comm.serial_comm import SerialComm
from utils.log import log_info, log_error
from utils.web_stream import (
    start_web_streaming,
    update_frame,
    get_bounds,
    update_status,
    set_notice,
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
    FRAME_HEIGHT,
    PHONE_DETECT_FRAMES,
    CONFIDENCE_THRESHOLD_FACE,
    CONFIDENCE_THRESHOLD_PHONE
)
import time


def main():
    detector = AIDetector()
    camera = CameraStream().start()
    # comm = SerialComm()
    face_was_safe = False
    phone_frames = 0
    phone_detections = 0
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
            if bounds is not None:
                cv2.line(frame, (bounds[0], 0), (bounds[0], FRAME_HEIGHT), BOUND_LINE_COLOR, 2)
                cv2.line(frame, (bounds[1], 0), (bounds[1], FRAME_HEIGHT), BOUND_LINE_COLOR, 2)

            phone_present = False
            operator_count = 0
            any_inside = False
            any_outside = False

            for (x1, y1, x2, y2, conf, cls_id) in detections:
                if cls_id == PHONE_CLASS_ID:
                    phone_present = True

                if cls_id == FACE_CLASS_ID and conf > CONFIDENCE_THRESHOLD_FACE:
                    operator_count += 1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), FACE_DETECTION_COLOR, 2)
                    mid_x = (x1 + x2) // 2
                    mid_y = y1 + DRAW_POINT_OFFSET
                    cv2.circle(frame, (mid_x, mid_y), 3, POINT_COLOR, -1)

                if cls_id == PHONE_CLASS_ID and conf > CONFIDENCE_THRESHOLD_PHONE:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), PHONE_DETECTION_COLOR, 2)

                    if bounds is not None:
                        left, right = sorted(bounds)
                        in_safe = left <= mid_x <= right
                        if in_safe:
                            any_inside = True
                        else:
                            any_outside = True

            # Phone detection majority check
            if phone_present:
                phone_detections += 1
            phone_frames += 1
            if phone_frames >= PHONE_DETECT_FRAMES:
                if phone_detections > PHONE_DETECT_FRAMES / 2:
                    # comm.send(PHONE_COMMAND)
                    set_notice("Phone detected", "warning")
                phone_frames = 0
                phone_detections = 0

            operator_status = "Not Present"
            if operator_count > 0:
                if any_outside:
                    operator_status = "Outside safe zone"
                elif any_inside:
                    operator_status = "Inside safe zone"

            if operator_count > 1:
                set_notice("Too many operators", "warning")

            if bounds is not None and any_outside and face_was_safe:
                # comm.send(BREACH_COMMAND)
                set_notice("Return to safe zone", "critical")
                face_was_safe = False
            elif any_inside:
                face_was_safe = True

            # Draw FPS on frame
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, FPS_COLOR, 2)

            # Update status for UI
            update_status(phone_present, operator_status, operator_count, round(fps, 1))

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
