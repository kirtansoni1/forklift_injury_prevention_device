# -*- coding: utf-8 -*-

import subprocess
import shutil
from pathlib import Path
import sys


def run_command(cmd: list, cwd: Path = None):
    """
    Executes a shell command and captures its output.
    Exits the script if the command fails.

    Args:
        cmd (list): Command to execute as list of strings.
        cwd (Path, optional): Directory to run the command in.
    """
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"Error:\n{result.stderr}")
        sys.exit(1)
    else:
        print(result.stdout)


def main():
    # Define paths
    model_pt = Path("yolo11n.pt")
    torchscript_file = Path("yolo11n.torchscript")
    export_dir = Path("yolo11n_ncnn_model")  # This will be created by Ultralytics CLI during NCNN export
    runs_dir = Path("runs")

    # Skip entire process if final NCNN model folder exists and is not empty
    if export_dir.exists() and any(export_dir.iterdir()):
        print(f"✅ Skipping setup: {export_dir} already exists and is populated.")
        return

    # Step 1: Download the .pt model via CLI if not already present
    if model_pt.exists():
        print("✅ Model already exists, skipping download.")
    else:
        print("📦 Downloading yolo11n.pt via Ultralytics CLI...")
        run_command(["yolo", "detect", "predict", "model=yolo11n.pt"])

    # Step 2: Export the model to NCNN format using Ultralytics CLI
    print("📤 Exporting yolo11n.pt to NCNN format...")
    run_command(["yolo", "export", "model=yolo11n.pt", "format=ncnn"])

    # Step 3: Validate the exported folder
    if not export_dir.exists():
        print("❌ Export folder not found. Aborting.")
        sys.exit(1)

    print(f"✅ NCNN model is available in: {export_dir.resolve()}")

    # Step 4: Cleanup temporary files
    if model_pt.exists():
        print(f"🧹 Removing {model_pt.name}")
        model_pt.unlink()

    if torchscript_file.exists():
        print(f"🧹 Removing {torchscript_file.name}")
        torchscript_file.unlink()

    if runs_dir.exists():
        print(f"🧹 Removing {runs_dir.name} directory")
        shutil.rmtree(runs_dir, ignore_errors=True)

    print("\n✅ NCNN model setup complete.")


if __name__ == "__main__":
    main()
