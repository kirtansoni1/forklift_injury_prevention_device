import shutil
from pathlib import Path

# -------------------- CONFIGURATION --------------------
# Must contain train/, valid/, test/
INPUT_DATASET_DIR = Path(r"G:\Work\ForkLift_Safety_System\Dataset\Test2.v1i.yolov11")
OUTPUT_BASE_DIR = Path(r"G:\Work\ForkLift_Safety_System\Dataset\data")  # Will create class_0/, class_1/, etc.
# -------------------------------------------------------

SPLITS = ['train', 'valid', 'test']


def extract_classes_from_label(label_path: Path):
    """Extract all class IDs from a YOLO label file."""
    class_ids = set()
    try:
        with label_path.open('r') as f:
            for line in f:
                parts = line.strip().split()
                if parts and parts[0].isdigit():
                    class_ids.add(int(parts[0]))
    except Exception as e:
        print(f"[ERROR] Failed reading {label_path}: {e}")
    return class_ids


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
                print(f"[WARN] No image found for label {label_file.name}")
                continue

            class_ids = extract_classes_from_label(label_file)

            for class_id in class_ids:
                class_dir = OUTPUT_BASE_DIR / f"class_{class_id}"
                class_images = class_dir / "images"
                class_labels = class_dir / "labels"

                class_images.mkdir(parents=True, exist_ok=True)
                class_labels.mkdir(parents=True, exist_ok=True)

                shutil.copy2(image_file, class_images / image_file.name)
                shutil.copy2(label_file, class_labels / label_file.name)

    print("✅ YOLO dataset segregation complete.")


if __name__ == "__main__":
    segregate_dataset()
