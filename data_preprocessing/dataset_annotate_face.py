import os
from pathlib import Path
import cv2
from ultralytics import YOLO
from tqdm import tqdm
import torch

# ---------------------- CONFIGURATION ----------------------
INPUT_FOLDER = Path(r"G:\Work\ForkLift_Safety_System\Dataset\data\class_2")
IMAGE_FOLDER = INPUT_FOLDER / "images"
LABEL_FOLDER = INPUT_FOLDER / "labels"
MODEL_PATH = r"G:\MasterThesis\final_code_base\models\yolov8m_FINAL_DATA.pt"
CHECK_FACE_FOLDER = INPUT_FOLDER / "check_faces"
MISSING_FACE_FOLDER = INPUT_FOLDER / "missing_faces"
OVERLAP_FACE_FOLDER = INPUT_FOLDER / "overlapping_faces"

FACE_CLASS = 0
CONF_THRESHOLD = 0.4
SAVE_LIMIT = 2500
IOU_THRESHOLD = 0.5
IMG_EXTENSIONS = [".jpg", ".jpeg", ".png"]
DEVICE = 'cuda'
# ----------------------------------------------------------

# Create output directories
CHECK_FACE_FOLDER.mkdir(parents=True, exist_ok=True)
MISSING_FACE_FOLDER.mkdir(parents=True, exist_ok=True)
OVERLAP_FACE_FOLDER.mkdir(parents=True, exist_ok=True)

# Load YOLOv8 model
model = YOLO(MODEL_PATH)
model.to(DEVICE)

# Utility: Calculate IoU


def calculate_iou(box1, box2):
    """Calculate IoU between two boxes [x1, y1, x2, y2]"""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = area1 + area2 - inter_area

    return inter_area / union_area if union_area > 0 else 0


# Collect image paths
image_paths = sorted([
    p for p in IMAGE_FOLDER.glob("*")
    if p.suffix.lower() in IMG_EXTENSIONS
])

saved_count = 0

for img_path in tqdm(image_paths, desc="🔄 Processing Images", ncols=100):

    img = cv2.imread(str(img_path))
    if img is None:
        print(f"\n❌ Failed to read image: {img_path.name}")
        continue

    height, width = img.shape[:2]

    # Run inference
    results = model.predict(source=img, conf=CONF_THRESHOLD, verbose=False, device=DEVICE)[0]

    if results.boxes is None or results.boxes.shape[0] == 0:
        output_path = MISSING_FACE_FOLDER / img_path.name
        cv2.imwrite(str(output_path), img)
        print(f"\n🔍 No face detected in: {img_path.name}")
        print(f"   ⚠️ Saved to missing_faces/{img_path.name}")
        continue

    # Extract boxes and check for overlaps
    boxes_xyxy = [box.xyxy[0].tolist() for box in results.boxes]

    overlapping = False
    for i in range(len(boxes_xyxy)):
        for j in range(i + 1, len(boxes_xyxy)):
            iou = calculate_iou(boxes_xyxy[i], boxes_xyxy[j])
            if iou > IOU_THRESHOLD:
                overlapping = True
                break
        if overlapping:
            break

    if overlapping:
        output_path = OVERLAP_FACE_FOLDER / img_path.name
        cv2.imwrite(str(output_path), img)
        print(f"\n⚠️ Overlapping/Nested faces in: {img_path.name} → moved to overlapping_faces/")
        continue

    # Format YOLO face labels
    face_labels = []
    for box in boxes_xyxy:
        x1, y1, x2, y2 = box
        x_center = (x1 + x2) / 2.0 / width
        y_center = (y1 + y2) / 2.0 / height
        w = (x2 - x1) / width
        h = (y2 - y1) / height
        face_labels.append(f"{FACE_CLASS} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")

    print(f"\n🖼️ {img_path.name} → {len(face_labels)} face(s) detected")
    for idx, label in enumerate(face_labels):
        print(f"   [{idx+1}] {label}")

    # Label file: Remove old class 0 and update
    label_file = LABEL_FOLDER / f"{img_path.stem}.txt"
    existing_labels = []
    if label_file.exists():
        with open(label_file, "r") as f:
            existing_labels = [
                line.strip() for line in f.readlines()
                if not line.strip().startswith(f"{FACE_CLASS} ")
            ]

    updated_labels = existing_labels + face_labels
    with open(label_file, "w") as f:
        for label in updated_labels:
            f.write(label + "\n")

    # Save visual image if under limit
    if saved_count < SAVE_LIMIT:
        for x1, y1, x2, y2 in boxes_xyxy:
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"face {FACE_CLASS}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        output_path = CHECK_FACE_FOLDER / img_path.name
        cv2.imwrite(str(output_path), img)
        saved_count += 1
        print(f"   ✅ Saved to check_faces/{img_path.name}")

print(f"\n🎯 Completed. Saved {saved_count} image(s) with face detection preview.")
