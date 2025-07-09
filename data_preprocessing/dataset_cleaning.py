"""
YOLO Dataset Cleaning Script

This script processes a YOLO-format object detection dataset by performing the following actions:

1. **Input/Output Configuration**:
   - Accepts a dataset directory structured with `train`, `valid`, and `test` subfolders.
   - Saves the cleaned dataset to a new directory following YOLO folder structure.
   - Saves invalid or removed images (with reasons) to a separate folder with bounding boxes drawn.

2. **Filtering Logic**:
   - Removes images with:
     - No label file.
     - More than the allowed number of detections (default = 2).
     - Zero detections.
     - Very small bounding boxes (area below a defined threshold).
     - Duplicate images (determined by base filename pattern, e.g., `helm_000115`).

3. **Visualization**:
   - Draws bounding boxes on removed images and stores them under the `removed/` directory with reason prefixes.

4. **Train/Valid/Test Split**:
   - After cleaning, it randomly splits the dataset into training, validation, and testing sets using user-defined ratios.

5. **Logging and Statistics**:
   - Prints informative logs for each step.
   - Displays a detailed summary of how many images were processed, removed, and retained per category.

6. **Parameters You Can Modify**:
   - `INPUT_DATASET_DIR`: Path to the raw YOLO dataset.
   - `OUTPUT_DATASET_DIR`: Where cleaned dataset will be saved.
   - `MIN_BBOX_AREA`: Bounding box area threshold.
   - `MAX_OBJECTS_ALLOWED`: Maximum number of allowed detections per image.
   - `TRAIN_SPLIT`, `VALID_SPLIT`, `TEST_SPLIT`: Ratios for dataset splitting.
   - `SEED`: Ensures reproducible splits.

Usage:
    - Place your dataset in the correct YOLO folder structure.
    - Update the `INPUT_DATASET_DIR` and `OUTPUT_DATASET_DIR` paths.
    - Run the script with Python 3 and OpenCV installed.

Author: Kirtan Soni
Version: 1.0
"""
import os
import shutil
from pathlib import Path
import random
import cv2

# -------------------- CONFIGURATION PARAMETERS --------------------
# Input dataset directory in YOLO format
INPUT_DATASET_DIR = Path(os.environ.get("INPUT_DATASET_DIR", "dataset/fullModel.v1i.yolov11"))

# Output directory where cleaned dataset will be saved
OUTPUT_DATASET_DIR = Path(os.environ.get("OUTPUT_DATASET_DIR", "dataset/Cleaned_Dataset"))

# Output directory for removed images with visual bounding boxes
REMOVED_DIR = OUTPUT_DATASET_DIR / "removed"

# Bounding box area threshold (width * height); any box smaller than this is considered 'too small'
MIN_BBOX_AREA = 0.0001

# Max number of objects allowed in one image (inclusive)
MAX_OBJECTS_ALLOWED = 5

# Split percentages
TRAIN_SPLIT = 0.7
VALID_SPLIT = 0.2
TEST_SPLIT = 0.1

# Random seed for reproducibility
SEED = 42

# -------------------- UTILITY FUNCTIONS --------------------


def read_label_file(label_path):
    with open(label_path, 'r') as f:
        lines = f.readlines()
    return [list(map(float, line.strip().split())) for line in lines if line.strip()]  # class_id cx cy w h


def is_valid_annotation(annotations):
    if len(annotations) == 0:
        return False, "no_detection"
    if len(annotations) > MAX_OBJECTS_ALLOWED:
        return False, "too_many_detections"
    for ann in annotations:
        _, _, _, w, h = ann
        if w * h < MIN_BBOX_AREA:
            return False, "bbox_too_small"
    return True, "valid"


def collect_image_label_pairs(split_dir):
    images_dir = split_dir / "images"
    labels_dir = split_dir / "labels"
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
    return [(img, labels_dir / (img.stem + ".txt")) for img in image_files]


def create_yolo_structure(base_dir):
    for split in ["train", "valid", "test"]:
        (base_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (base_dir / split / "labels").mkdir(parents=True, exist_ok=True)
    REMOVED_DIR.mkdir(parents=True, exist_ok=True)


def draw_and_save_removed_image(img_path, annotations, reason):
    img = cv2.imread(str(img_path))
    if img is None:
        return
    h, w, _ = img.shape
    for ann in annotations:
        class_id, cx, cy, bw, bh = ann
        x1 = int((cx - bw / 2) * w)
        y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w)
        y2 = int((cy + bh / 2) * h)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, f"{int(class_id)}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    dest = REMOVED_DIR / f"{reason}_{img_path.name}"
    cv2.imwrite(str(dest), img)

# -------------------- MAIN SCRIPT --------------------


def main():
    random.seed(SEED)
    OUTPUT_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    create_yolo_structure(OUTPUT_DATASET_DIR)

    all_pairs = []
    seen_base_names = set()
    duplicate_images_removed = 0

    for split in ["train", "valid", "test"]:
        split_dir = INPUT_DATASET_DIR / split
        split_pairs = collect_image_label_pairs(split_dir)
        for img_path, label_path in split_pairs:
            base_name = "_".join(img_path.stem.split("_")[:2])  # e.g., helm_000115
            if base_name in seen_base_names:
                duplicate_images_removed += 1
                continue
            seen_base_names.add(base_name)
            all_pairs.append((img_path, label_path))
        print(f"Collected {len(split_pairs)} image-label pairs from '{split}' split.")

    print(f"\n[INFO] Total image-label pairs after removing duplicates: {len(all_pairs)}")
    print(f"[INFO] Duplicate images removed: {duplicate_images_removed}")

    valid_pairs = []
    removed_due_to_no_label = 0
    removed_due_to_small_area = 0
    removed_due_to_too_many = 0
    removed_due_to_empty = 0

    for img_path, label_path in all_pairs:
        if not label_path.exists():
            removed_due_to_no_label += 1
            continue
        annotations = read_label_file(label_path)
        is_valid, reason = is_valid_annotation(annotations)
        if is_valid:
            valid_pairs.append((img_path, label_path))
        else:
            if reason == "no_detection":
                removed_due_to_empty += 1
            elif reason == "too_many_detections":
                removed_due_to_too_many += 1
            elif reason == "bbox_too_small":
                removed_due_to_small_area += 1
            draw_and_save_removed_image(img_path, annotations, reason)

    print(f"\n[INFO] Valid cleaned pairs retained: {len(valid_pairs)}")
    print(f"[INFO] Removed due to missing label file: {removed_due_to_no_label}")
    print(f"[INFO] Removed due to no detection: {removed_due_to_empty}")
    print(f"[INFO] Removed due to >{MAX_OBJECTS_ALLOWED} detections: {removed_due_to_too_many}")
    print(f"[INFO] Removed due to small bounding box area: {removed_due_to_small_area}")

    random.shuffle(valid_pairs)

    train_end = int(len(valid_pairs) * TRAIN_SPLIT)
    valid_end = train_end + int(len(valid_pairs) * VALID_SPLIT)

    split_map = {
        "train": valid_pairs[:train_end],
        "valid": valid_pairs[train_end:valid_end],
        "test": valid_pairs[valid_end:]
    }

    for split, pairs in split_map.items():
        print(f"\n[INFO] Copying {len(pairs)} items to '{split}' split...")
        for img_path, label_path in pairs:
            dest_img = OUTPUT_DATASET_DIR / split / "images" / img_path.name
            dest_lbl = OUTPUT_DATASET_DIR / split / "labels" / label_path.name
            shutil.copy(img_path, dest_img)
            shutil.copy(label_path, dest_lbl)

    print("\n✅ Dataset cleaning and splitting complete.")
    print("\n--- Final Summary ---")
    print(f"Original total: {len(all_pairs) + duplicate_images_removed}")
    print(f"Duplicates removed: {duplicate_images_removed}")
    print(f"Valid images retained: {len(valid_pairs)}")
    print(f"Removed (missing label): {removed_due_to_no_label}")
    print(f"Removed (no detection): {removed_due_to_empty}")
    print(f"Removed (too many detections): {removed_due_to_too_many}")
    print(f"Removed (small bounding box): {removed_due_to_small_area}")
    print(f"Train split: {len(split_map['train'])}")
    print(f"Valid split: {len(split_map['valid'])}")
    print(f"Test split:  {len(split_map['test'])}")


if __name__ == "__main__":
    main()
