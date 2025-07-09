import cv2
import time
from pathlib import Path
from datetime import datetime


def get_start_index(output_path: Path):
    """Return next frame index based on existing images."""
    image_files = sorted(output_path.glob("frame_*.jpg"))
    if not image_files:
        return 0
    last_file = image_files[-1]
    last_index = int(last_file.stem.split("_")[1])
    return last_index + 1


def capture_dataset(
    camera_index=0,
    frame_width=640,
    frame_height=480,
    capture_fps=2,
    total_new_frames=100,
    output_dir="dataset/images",
    preview=True
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"❌ Failed to open camera at index {camera_index}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    start_index = get_start_index(output_path)
    print(f"📁 Saving images starting at frame index: {start_index}")
    print(f"🎥 Target: {total_new_frames} new frames @ {capture_fps} FPS")

    delay = 1.0 / capture_fps
    count = 0

    # Read and discard first black frame
    print("⚠️ Discarding first frame (usually black)...")
    cap.read()

    while count < total_new_frames:
        start_time = time.time()
        ret, frame = cap.read()

        if not ret:
            print("⚠️ Failed to read frame.")
            continue

        # Save image with next available index
        frame_id = start_index + count
        filename = output_path / f"frame_{frame_id:04d}.jpg"
        cv2.imwrite(str(filename), frame)

        # Show preview
        if preview:
            preview_frame = frame.copy()
            timestamp = datetime.now().strftime("%H:%M:%S")
            cv2.putText(preview_frame, f"Frame: {frame_id}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(preview_frame, f"Time: {timestamp}", (10, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            cv2.imshow("📸 Capturing Dataset", preview_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("🛑 Capture interrupted by user.")
                break

        count += 1
        elapsed = time.time() - start_time
        time.sleep(max(0, delay - elapsed))

    cap.release()
    if preview:
        cv2.destroyAllWindows()

    print(f"✅ Finished. Captured {count} new frames starting from frame_{start_index:04d}.")


if __name__ == "__main__":
    capture_dataset(
        camera_index=0,
        frame_width=320,
        frame_height=320,
        capture_fps=3,
        total_new_frames=500,
        output_dir="dataset/images",
        preview=True
    )
