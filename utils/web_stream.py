# -*- coding: utf-8 -*-

from flask import Flask, Response, render_template
import cv2
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "web" / "templates"),
    static_folder=str(BASE_DIR / "web" / "static"),
)

# Global frame buffer and lock
_lock = threading.Lock()
_current_frame = None


def update_frame(frame):
    """Update the global frame to be streamed."""
    global _current_frame
    with _lock:
        _current_frame = frame.copy()


def generate():
    """Generate frames as JPEG stream."""
    global _current_frame
    while True:
        with _lock:
            if _current_frame is None:
                continue
            success, jpeg = cv2.imencode('.jpg', _current_frame)
            if not success:
                continue
            frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Render the main video stream page."""
    return render_template("index.html")


@app.route('/video_feed')
def video_feed():
    """Stream the frame via MJPEG."""
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def start_web_streaming():
    """Start Flask server (non-blocking)."""
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
