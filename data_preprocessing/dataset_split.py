import os
import shutil
import random
from pathlib import Path

# ---------------- CONFIGURATION ----------------
# Path to folder containing 'images/' and 'labels/'
INPUT_DIR = Path(os.environ.get("INPUT_DIR", "dataset/data/class_2"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "dataset/DATA"))  # Output base directory

SPLIT_RATIO = {
    'train': 0.7,
    'val': 0.2,
    'test': 0.1
}

IMAGE_EXTS = [".jpg", ".jpeg", ".png"]
# ------------------------------------------------


def get_image_files(image_dir):
    return [f for f in image_dir.iterdir() if f.suffix.lower() in IMAGE_EXTS]


def ensure_dir(path):
    if not path.exists():
        path.mkdir(parents=True)


def split_dataset(image_files, ratios):
    total = len(image_files)
    random.shuffle(image_files)

    train_end = int(ratios['train'] * total)
    val_end = train_end + int(ratios['val'] * total)

    return {
        'train': image_files[:train_end],
        'val': image_files[train_end:val_end],
        'test': image_files[val_end:]
    }


def copy_files(image_list, subset_name, image_dir, label_dir):
    out_img_dir = OUTPUT_DIR / subset_name / 'images'
    out_lbl_dir = OUTPUT_DIR / subset_name / 'labels'

    ensure_dir(out_img_dir)
    ensure_dir(out_lbl_dir)

    for img_path in image_list:
        label_path = label_dir / (img_path.stem + ".txt")

        shutil.copy(img_path, out_img_dir / img_path.name)
        if label_path.exists():
            shutil.copy(label_path, out_lbl_dir / label_path.name)


def main():
    image_dir = INPUT_DIR / "images"
    label_dir = INPUT_DIR / "labels"

    if not image_dir.exists() or not label_dir.exists():
        raise FileNotFoundError("Ensure 'images/' and 'labels/' folders exist in the input directory.")

    image_files = get_image_files(image_dir)

    splits = split_dataset(image_files, SPLIT_RATIO)

    for split_name, files in splits.items():
        copy_files(files, split_name, image_dir, label_dir)

    print("✅ Dataset split completed successfully.")
    for k, v in splits.items():
        print(f"{k}: {len(v)} images")


if __name__ == "__main__":
    main()
