import os
import shutil
from pathlib import Path

# -------------------- CONFIGURATION --------------------
# Must contain train/, valid/, test/
INPUT_DATASET_DIR = Path(os.environ.get("INPUT_DATASET_DIR", "dataset/Test2.v1i.yolov11"))
OUTPUT_BASE_DIR = Path(os.environ.get("OUTPUT_BASE_DIR", "dataset/data"))  # Will create class_x_y/... folders
# -------------------------------------------------------

SPLITS = ['train', 'valid', 'test']


def extract_class_combination(label_path: Path):
    """Return sorted tuple of unique class IDs found in label file."""
    class_ids = set()
    try:
        with label_path.open('r') as f:
            for line in f:
                parts = line.strip().split()
                if parts and parts[0].isdigit():
                    class_ids.add(int(parts[0]))
    except Exception as e:
        print(f"[ERROR] Reading {label_path}: {e}")
    return tuple(sorted(class_ids))


def get_combination_folder_name(class_ids_tuple):
    """Generate folder name like class_0_2 from tuple (0, 2)."""
    return "class_" + "_".join(str(cid) for cid in class_ids_tuple)


def segregate_dataset():
    for split in SPLITS:
        image_dir = INPUT_DATASET_DIR / split / "images"
        label_dir = INPUT_DATASET_DIR / split / "labels"

        if not image_dir.exists() or not label_dir.exists():
            print(f"[WARN] Skipping '{split}' – missing images or labels folder.")
            continue

        for label_file in label_dir.glob("*.txt"):
            stem = label_file.stem
            image_file = next((f for f in image_dir.glob(f"{stem}.*")), None)

            if not image_file:
                print(f"[WARN] No image found for label: {label_file.name}")
                continue

            class_ids = extract_class_combination(label_file)
            if not class_ids:
                continue

            combo_folder_name = get_combination_folder_name(class_ids)
            combo_dir = OUTPUT_BASE_DIR / combo_folder_name
            image_out_dir = combo_dir / "images"
            label_out_dir = combo_dir / "labels"

            image_out_dir.mkdir(parents=True, exist_ok=True)
            label_out_dir.mkdir(parents=True, exist_ok=True)

            shutil.copy2(image_file, image_out_dir / image_file.name)
            shutil.copy2(label_file, label_out_dir / label_file.name)

    print("✅ Dataset segregation by class combinations complete.")


if __name__ == "__main__":
    segregate_dataset()
