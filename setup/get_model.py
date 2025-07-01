# setup/get_model.py
import subprocess
import shutil
from pathlib import Path
import sys


def run_command(cmd: list, cwd: Path = None):
    """Runs a shell command and checks for errors."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"Error:\n{result.stderr}")
        sys.exit(1)
    else:
        print(result.stdout)


def main():
    model_pt = Path("yolo11n.pt")
    torchscript_file = Path("yolo11n.torchscript")
    export_dir = Path("yolo11n_ncnn_model")
    runs_dir = Path("runs")
    target_dir = Path("model/yolov11n_ncnn")

    # Skip entire process if final model folder exists and is not empty
    if target_dir.exists() and any(target_dir.iterdir()):
        print(f"✅ Skipping setup: {target_dir} already exists and is populated.")
        return

    target_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Download the model via CLI if not present
    if model_pt.exists():
        print("✅ Model already exists, skipping download.")
    else:
        print("📦 Downloading yolo11n.pt via Ultralytics CLI...")
        run_command(["yolo", "detect", "predict", "model=yolo11n.pt"])

    # Step 2: Export model to NCNN using CLI
    print("📤 Exporting yolo11n.pt to NCNN format...")
    run_command(["yolo", "export", "model=yolo11n.pt", "format=ncnn"])

    # Step 3: Move exported NCNN files
    if not export_dir.exists():
        print("❌ Export folder not found. Aborting.")
        sys.exit(1)

    for file in export_dir.iterdir():
        dest = target_dir / file.name
        print(f"📁 Moving {file.name} → {dest}")
        shutil.move(str(file), dest)

    # Step 4: Cleanup
    shutil.rmtree(export_dir, ignore_errors=True)
    if model_pt.exists():
        print(f"🧹 Removing {model_pt.name}")
        model_pt.unlink()
    if torchscript_file.exists():
        print(f"🧹 Removing {torchscript_file.name}")
        torchscript_file.unlink()
    if runs_dir.exists():
        print(f"🧹 Removing {runs_dir.name} directory")
        shutil.rmtree(runs_dir, ignore_errors=True)

    print(f"\n✅ NCNN model is ready at: {target_dir.resolve()}")


if __name__ == "__main__":
    main()
