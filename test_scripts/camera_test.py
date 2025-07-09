# -*- coding: utf-8 -*-

import os
import cv2
import time


def main():
    # Use the correct camera index (0 is default USB cam)
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_V4L2
    cap = cv2.VideoCapture(0, backend)

    # Set camera resolution (choose based on camera capability & FPS tradeoff)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Confirm actual settings
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Camera initialized: {width}x{height} @ {fps} FPS")

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Optional: flip frame if needed
        # frame = cv2.flip(frame, 1)

        # Show frame
        cv2.imshow("USB Camera Feed", frame)

        # Display FPS in console
        curr_time = time.time()
        print(f"FPS: {1/(curr_time - prev_time):.2f}", end="\r")
        prev_time = curr_time

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
