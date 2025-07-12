"""Utility to replace class IDs in YOLO label files.

Configure ``INPUT_FOLDER`` to point at a dataset and set ``OLD_CLASS`` and
``NEW_CLASS`` to remap labels. Run with ``python dataset_change_class.py``.

Author: Kirtan Soni
"""

import os
from pathlib import Path

# --------- CONFIGURATION ---------
# Path can be overridden with the INPUT_FOLDER environment variable
INPUT_FOLDER = Path(os.environ.get("INPUT_FOLDER", "dataset/data/class_2"))
OLD_CLASS = 2
NEW_CLASS = 1
EXT = ".txt"
# ---------------------------------


def replace_class_in_labels(input_dir: Path, old_class: int, new_class: int):
    for file in input_dir.rglob(f'*{EXT}'):
        with open(file, 'r') as f:
            lines = f.readlines()

        updated_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            if int(parts[0]) == old_class:
                parts[0] = str(new_class)
            updated_lines.append(' '.join(parts) + '\n')

        with open(file, 'w') as f:
            f.writelines(updated_lines)
        print(f"Updated: {file}")


if __name__ == "__main__":
    replace_class_in_labels(INPUT_FOLDER, OLD_CLASS, NEW_CLASS)
