# -*- coding: utf-8 -*-
"""Test the :class:`AIDetector` using a sample image.

Run ``python ncnn_model_test.py`` to load ``test_images/sample1.jpg`` and display
the detection results.

Author: Kirtan Soni
"""
import cv2
import sys
import time
import matplotlib.pyplot as plt

sys.path.append('.')  # noqa

from core.detector import AIDetector


def main():
    image_path = "test_images/sample1.jpg"  # Path to test image
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"❌ Failed to load image: {image_path}")
        return

    detector = AIDetector()

    # Start timer
    start_time = time.time()

    detections = detector.detect_humans(frame)

    # End timer and calculate inference time
    inference_time_ms = (time.time() - start_time) * 1000
    print(f"✅ Inference Time: {inference_time_ms:.2f} ms")

    for (x1, y1, x2, y2, conf) in detections:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0))

    # Convert BGR (OpenCV format) to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    plt.imshow(rgb_frame)
    plt.title("Detection Result")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
