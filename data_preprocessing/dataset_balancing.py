"""
YOLO Label Cleaner Script

This script scans a YOLO dataset and removes all non-bounding box annotations (e.g., segmentation masks).
It preserves only proper 5-column bounding box entries per label file.

Removed label files (or filtered lines) are saved into a separate directory.
Visualizations are also generated for the removed labels with bounding boxes drawn.

Configuration parameters are defined at the top of the script.

Author: Kirtan Soni
Version: 1.0
"""

from pathlib import Path
import shutil
import cv2

# -------------------- CONFIGURATION --------------------
DATASET_DIR = Path(r"G:\Work\ForkLift_Safety_System\Dataset\Forklift_Dataset")  # 🔁 Path to the YOLO dataset directory
# 🔁 Cleaned dataset with only bounding boxes
OUTPUT_DIR = Path(r"G:\Work\ForkLift_Safety_System\Dataset\cleaned_data")
# 🔁 Removed files with non-bbox data
REMOVED_DIR = Path(r"G:\Work\ForkLift_Safety_System\Dataset\cleaned_data\removed")
IMG_FORMATS = [".jpg", ".png"]                     # Accepted image formats
VISUALIZE_REMOVED = True                            # Draw and save bounding boxes for removed files

# -------------------- FUNCTION TO CLEAN LABEL --------------------


def is_valid_bbox_line(line):
    parts = line.strip().split()
    return len(parts) == 5 and all(p.replace('.', '', 1).isdigit() or p.isdigit() for p in parts)


def draw_boxes(image_path, label_lines, output_path):
    img = cv2.imread(str(image_path))
    if img is None:
        return
    h, w = img.shape[:2]
    for line in label_lines:
        parts = list(map(float, line.strip().split()))
        class_id, cx, cy, bw, bh = parts
        x1 = int((cx - bw / 2) * w)
        y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w)
        y2 = int((cy + bh / 2) * h)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, str(int(class_id)), (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.imwrite(str(output_path), img)

# -------------------- MAIN FUNCTION --------------------


def clean_yolo_labels():
    print("[INFO] Starting label cleanup...")
    total_cleaned = 0
    total_removed = 0
    removal_log = []

    for split in ["train", "valid", "test"]:
        img_dir = DATASET_DIR / split / "images"
        lbl_dir = DATASET_DIR / split / "labels"
        out_img_dir = OUTPUT_DIR / split / "images"
        out_lbl_dir = OUTPUT_DIR / split / "labels"
        rem_lbl_dir = REMOVED_DIR / split / "labels"
        rem_img_dir = REMOVED_DIR / split / "images"
        vis_img_dir = REMOVED_DIR / split / "visuals"

        out_img_dir.mkdir(parents=True, exist_ok=True)
        out_lbl_dir.mkdir(parents=True, exist_ok=True)
        rem_lbl_dir.mkdir(parents=True, exist_ok=True)
        rem_img_dir.mkdir(parents=True, exist_ok=True)
        vis_img_dir.mkdir(parents=True, exist_ok=True)

        image_files = [f for f in img_dir.glob("*") if f.suffix.lower() in IMG_FORMATS]

        for img_path in image_files:
            label_path = lbl_dir / (img_path.stem + ".txt")

            if not label_path.exists():
                continue

            with open(label_path, 'r') as f:
                lines = f.readlines()

            bbox_lines = [l for l in lines if is_valid_bbox_line(l)]

            if len(bbox_lines) == len(lines):
                # All lines are valid bbox
                shutil.copy(img_path, out_img_dir / img_path.name)
                shutil.copy(label_path, out_lbl_dir / label_path.name)
                total_cleaned += 1
            else:
                # File contains non-bbox data
                with open(rem_lbl_dir / label_path.name, 'w') as f:
                    f.writelines(lines)
                shutil.copy(img_path, rem_img_dir / img_path.name)
                if VISUALIZE_REMOVED:
                    draw_boxes(img_path, bbox_lines, vis_img_dir / img_path.name)
                total_removed += 1
                removal_log.append({
                    "split": split,
                    "file": label_path.name,
                    "total_lines": len(lines),
                    "bbox_lines": len(bbox_lines),
                    "removed_lines": len(lines) - len(bbox_lines)
                })

    print("\n✅ Cleanup complete. Cleaned and removed files are separated.")
    print("\n--- Removal Summary ---")
    print(f"Total cleaned label files: {total_cleaned}")
    print(f"Total removed label files (non-bbox entries): {total_removed}")

    if removal_log:
        print("\nDetailed removed files:")
        for entry in removal_log:
            print(f"[{entry['split'].upper()}] {entry['file']}: total={entry['total_lines']} | valid={entry['bbox_lines']} | removed={entry['removed_lines']}")


if __name__ == "__main__":
    clean_yolo_labels()
