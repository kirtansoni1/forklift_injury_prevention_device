# -*- coding: utf-8 -*-

from flask import Flask, Response, render_template, request, jsonify
import cv2
import threading
import time
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
_bounds = None


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
            frame = None if _current_frame is None else _current_frame.copy()

        if frame is None:
            time.sleep(0.01)
            continue

        success, jpeg = cv2.imencode('.jpg', frame)
        if not success:
            time.sleep(0.01)
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


@app.route('/set_bounds', methods=['POST'])
def set_bounds():
    """Receive bounding line coordinates from the web UI."""
    global _bounds
    data = request.get_json(force=True)
    if not data or 'x1' not in data or 'x2' not in data:
        return jsonify({'status': 'error'}), 400
    _bounds = (int(data['x1']), int(data['x2']))
    return jsonify({'status': 'ok'})


def get_bounds():
    """Return the currently configured bounding lines."""
    return _bounds


def start_web_streaming():
    """Start Flask server (non-blocking)."""
    # Disable the reloader when running inside a thread to avoid spawning
    # additional processes.
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True,
            use_reloader=False)
