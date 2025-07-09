import subprocess
from pathlib import Path
import sys


def export_ncnn(pt_model_path: str):
    pt_model = Path(pt_model_path).resolve()

    if not pt_model.exists():
        print(f"❌ Error: .pt model not found: {pt_model}")
        sys.exit(1)

    print(f"🔁 Exporting NCNN from: {pt_model}")

    # Run the export command
    result = subprocess.run(
        ["yolo", "export", f"model={str(pt_model)}", "format=ncnn"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        print("❌ NCNN export failed.")
        sys.exit(1)

    # Confirm the expected output folder exists
    expected_ncnn_dir = pt_model.parent / "best_ncnn_model"
    if expected_ncnn_dir.exists():
        print(f"✅ NCNN model exported to: {expected_ncnn_dir}")
    else:
        print("⚠️ Export completed, but expected output folder not found. Check above logs.")


if __name__ == "__main__":
    # Example usage — just change this line
    export_ncnn(Path("traning") / "runs" / "train" / "yolov11n_320" / "weights" / "yolov11n_320.pt")
