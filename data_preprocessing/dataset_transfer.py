"""
YOLO Dataset Transfer Script

This script transfers a YOLO-format object detection dataset from one directory to another,
maintaining the directory structure (`train/`, `valid/`, `test/`), including both `images/` and `labels/`.

Simply configure the source and destination paths.

Usage:
- Update `SOURCE_DIR` and `DESTINATION_DIR`
- Run the script

Author: Kirtan Soni
Version: 1.0
"""

import shutil
from pathlib import Path

# -------------------- CONFIGURATION --------------------
SOURCE_DIR = Path(r"G:\Work\ForkLift_Safety_System\Dataset\data")  # Replace with path to source dataset
DESTINATION_DIR = Path(r"G:\Work\ForkLift_Safety_System\Dataset\Forklift_Dataset")  # Replace with destination path

# -------------------- MAIN SCRIPT --------------------


def transfer_yolo_dataset():
    splits = ["train", "valid", "test"]
    subfolders = ["images", "labels"]

    print("[INFO] Starting dataset transfer...")

    for split in splits:
        for sub in subfolders:
            src_path = SOURCE_DIR / split / sub
            dst_path = DESTINATION_DIR / split / sub
            dst_path.mkdir(parents=True, exist_ok=True)

            if not src_path.exists():
                print(f"[WARNING] Missing directory: {src_path}")
                continue

            files = list(src_path.glob("*.*"))
            print(f"[INFO] Copying {len(files)} files from {src_path} to {dst_path}...")

            for file in files:
                shutil.copy(file, dst_path)

    print("\n✅ Dataset transfer complete.")


if __name__ == "__main__":
    transfer_yolo_dataset()
