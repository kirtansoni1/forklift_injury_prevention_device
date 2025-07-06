"""
YOLO Dataset Count Script

This script counts the number of image and label files in a YOLO-format dataset
organized into `train`, `valid`, and `test` splits.

It reports:
- Total images and labels per split
- Total counts across the dataset

Usage:
- Update `DATASET_DIR` with the path to your YOLO dataset.
- Run the script.

Author: Kirtan Soni
Version: 1.0
"""

from pathlib import Path

# -------------------- CONFIGURATION --------------------
DATASET_DIR = Path(r"G:\Work\ForkLift_Safety_System\Dataset\Forklift_Dataset")  # Replace with your YOLO dataset path

# -------------------- MAIN SCRIPT --------------------


def count_yolo_dataset():
    splits = ["train", "valid", "test"]
    totals = {"images": 0, "labels": 0}

    for split in splits:
        img_dir = DATASET_DIR / split / "images"
        lbl_dir = DATASET_DIR / split / "labels"

        num_images = len(list(img_dir.glob("*.*"))) if img_dir.exists() else 0
        num_labels = len(list(lbl_dir.glob("*.txt"))) if lbl_dir.exists() else 0

        totals["images"] += num_images
        totals["labels"] += num_labels

        print(f"[INFO] Split: {split}")
        print(f"        Images: {num_images}")
        print(f"        Labels: {num_labels}\n")

    print("[SUMMARY] Total across dataset")
    print(f"          Images: {totals['images']}")
    print(f"          Labels: {totals['labels']}")


if __name__ == "__main__":
    count_yolo_dataset()
