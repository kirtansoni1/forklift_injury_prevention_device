"""
YOLO Webcam Detection Script for Windows

This script opens a webcam stream on a Windows machine and runs YOLO object detection
on each frame in real-time using the Ultralytics YOLOv8/Yolov11 model.

Make sure:
- You have a compatible CUDA setup
- You have installed ultralytics: `pip install ultralytics`
- Your webcam works with OpenCV

Author: Kirtan Soni
Version: 1.0
"""

import cv2
from ultralytics import YOLO

# -------------------- CONFIGURATION --------------------
# 🔁 Change to yolov11n.pt or your trained model path
MODEL_PATH = r"traning\runs\train\yolov11n_320_V2\weights\best_ncnn_model"
CONFIDENCE_THRESHOLD = 0.3     # 🔁 Minimum confidence to show detection
WEBCAM_INDEX = 0               # 🔁 Index for cv2.VideoCapture

# -------------------- MAIN SCRIPT --------------------


def run_webcam_detection():
    print("[INFO] Loading model...")
    model = YOLO(MODEL_PATH)

    print("[INFO] Starting webcam stream...")
    cap = cv2.VideoCapture(WEBCAM_INDEX)

    if not cap.isOpened():
        print("[ERROR] Cannot access webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run detection
        results = model.predict(source=frame, device='cpu', conf=CONFIDENCE_THRESHOLD, verbose=False, task='detect')

        # Draw bounding boxes manually
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                label = f"{model.names[cls]} {conf:.2f}"

                # Draw box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Draw label
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Show the frame
        cv2.imshow("YOLO Webcam Detection", frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("[INFO] Shutting down...")
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_webcam_detection()
