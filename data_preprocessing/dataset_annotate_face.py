import os
from pathlib import Path
import cv2
from ultralytics import YOLO
from tqdm import tqdm

# ---------------------- CONFIGURATION ----------------------
INPUT_FOLDER = Path(r"G:\Work\ForkLift_Safety_System\Dataset\FACEANDPHONE.v2i.yolov11")
MODEL_PATH = r"G:\MasterThesis\final_code_base\models\yolov8m_FINAL_DATA.pt"
FACE_CLASS = 0
CONF_THRESHOLD = 0.4
SAVE_LIMIT = 2500
IOU_THRESHOLD = 0.5
IMG_EXTENSIONS = [".jpg", ".jpeg", ".png"]
DEVICE = 'cuda'
DATA_SPLITS = ['train', 'valid', 'test']
# ----------------------------------------------------------

# Load YOLOv8 model
model = YOLO(MODEL_PATH)
model.to(DEVICE)

# Utility: Calculate IoU


def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = area1 + area2 - inter_area
    return inter_area / union_area if union_area > 0 else 0


# Process each split
for split in DATA_SPLITS:
    print(f"Processing split: {split.upper()}")

    # Set paths for split
    image_folder = INPUT_FOLDER / split / "images"
    label_folder = INPUT_FOLDER / split / "labels"
    check_face_folder = INPUT_FOLDER / split / "check_faces"
    missing_face_folder = INPUT_FOLDER / split / "missing_faces"
    overlap_face_folder = INPUT_FOLDER / split / "overlapping_faces"

    check_face_folder.mkdir(parents=True, exist_ok=True)
    missing_face_folder.mkdir(parents=True, exist_ok=True)
    overlap_face_folder.mkdir(parents=True, exist_ok=True)

    image_paths = sorted([
        p for p in image_folder.glob("*")
        if p.suffix.lower() in IMG_EXTENSIONS
    ])

    saved_count = 0

    for img_path in tqdm(image_paths, desc=f"\uD83D\uDD04 {split} images", ncols=100):
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"\n❌ Failed to read image: {img_path.name}")
            continue

        height, width = img.shape[:2]
        results = model.predict(source=img, conf=CONF_THRESHOLD, verbose=False, device=DEVICE)[0]

        if results.boxes is None or results.boxes.shape[0] == 0:
            output_path = missing_face_folder / img_path.name
            cv2.imwrite(str(output_path), img)
            print(f"\n🔍 No face detected in: {img_path.name}")
            continue

        boxes_xyxy = [box.xyxy[0].tolist() for box in results.boxes]

        overlapping = False
        for i in range(len(boxes_xyxy)):
            for j in range(i + 1, len(boxes_xyxy)):
                if calculate_iou(boxes_xyxy[i], boxes_xyxy[j]) > IOU_THRESHOLD:
                    overlapping = True
                    break
            if overlapping:
                break

        if overlapping:
            output_path = overlap_face_folder / img_path.name
            cv2.imwrite(str(output_path), img)
            print(f"\n⚠️ Overlapping faces: {img_path.name}")
            continue

        face_labels = []
        for box in boxes_xyxy:
            x1, y1, x2, y2 = box
            x_center = (x1 + x2) / 2.0 / width
            y_center = (y1 + y2) / 2.0 / height
            w = (x2 - x1) / width
            h = (y2 - y1) / height
            face_labels.append(f"{FACE_CLASS} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")

        label_file = label_folder / f"{img_path.stem}.txt"
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

        if saved_count < SAVE_LIMIT:
            for x1, y1, x2, y2 in boxes_xyxy:
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, f"face {FACE_CLASS}", (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            output_path = check_face_folder / img_path.name
            cv2.imwrite(str(output_path), img)
            saved_count += 1
            print(f"   ✅ Saved to check_faces/{img_path.name}")

    print(f"✅ Done with {split.upper()}: {saved_count} detection preview image(s) saved.")
