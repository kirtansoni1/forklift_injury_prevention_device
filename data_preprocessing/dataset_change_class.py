import os
from pathlib import Path

# --------- CONFIGURATION ---------
INPUT_FOLDER = Path(r"G:\Work\ForkLift_Safety_System\Dataset\data\class_2")  # replace with your folder path
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
