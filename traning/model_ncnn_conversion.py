import subprocess
from pathlib import Path
import sys


def convert_to_ncnn(pt_model_path: str, output_dir: str = None):
    pt_model = Path(pt_model_path).resolve()

    if not pt_model.exists():
        print(f"❌ Model file not found: {pt_model}")
        sys.exit(1)

    # Create output directory
    out_dir = Path(output_dir) if output_dir else pt_model.parent / f"{pt_model.stem}_ncnn_model_V2"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Prepare YOLO CLI command
    cmd = [
        "yolo",
        "export",
        f"model={str(pt_model)}",
        "format=ncnn",
        f"name={out_dir.name}"
    ]

    # Run export
    print(f"🔁 Exporting {pt_model.name} to NCNN format...")
    result = subprocess.run(cmd, cwd=out_dir.parent, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Conversion failed:")
        print(result.stderr)
        sys.exit(1)
    else:
        print(f"✅ Conversion successful. Files saved in: {out_dir}")
        print(result.stdout)


if __name__ == "__main__":
    # Example usage
    convert_to_ncnn(r"traning\runs\train\yolov11n_320_V2\weights\best.pt")  # Replace with your .pt path
