# -*- coding: utf-8 -*-

from flask import Flask, Response, render_template, request, jsonify
from flask import Flask, Response, render_template, request, jsonify
import cv2
import threading
import time
from pathlib import Path
from utils.defines import (
    FRAME_WIDTH,
    UI_PRIMARY_COLOR,
    UI_ALERT_COLOR,
    UI_INFO_COLOR,
    NOTICE_DURATION,
)

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
_status = {"phone": False, "operator": "Not Present", "count": 0, "fps": 0.0}
_notice = {"message": "", "level": "info", "time": 0.0}


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
    return render_template(
        "index.html",
        primary_color=UI_PRIMARY_COLOR,
        alert_color=UI_ALERT_COLOR,
        info_color=UI_INFO_COLOR,
    )


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
    try:
        x1 = max(0.0, min(float(data['x1']), 1.0))
        x2 = max(0.0, min(float(data['x2']), 1.0))
    except (TypeError, ValueError):
        return jsonify({'status': 'error'}), 400
    # Determine the width of the most recent frame if available. This ensures
    # that the bounding line positions match the actual streamed frame even if
    # the camera resolution differs from the configured FRAME_WIDTH constant.
    with _lock:
        frame_width = (_current_frame.shape[1]
                       if _current_frame is not None else FRAME_WIDTH)

    _bounds = (int(x1 * frame_width), int(x2 * frame_width))
    return jsonify({'status': 'ok'})


@app.route('/reset_bounds', methods=['POST'])
def reset_bounds():
    """Clear any existing bounding lines."""
    global _bounds
    _bounds = None
    return jsonify({'status': 'ok'})


def get_bounds():
    """Return the currently configured bounding lines."""
    return _bounds


def update_status(phone: bool, operator: str, count: int, fps: float):
    """Update live status values for the web UI."""
    global _status
    _status.update(phone=phone, operator=operator, count=count, fps=fps)


def set_notice(message: str, level: str = "info"):
    """Display a transient notice overlay on the web UI."""
    global _notice
    _notice = {"message": message, "level": level, "time": time.time()}


def get_notice():
    """Return the current notice if not expired."""
    global _notice
    if _notice["message"] and time.time() - _notice["time"] > NOTICE_DURATION:
        _notice = {"message": "", "level": "info", "time": 0.0}
    return {"message": _notice["message"], "level": _notice["level"]}


@app.route('/status')
def status():
    """Provide detection status for the web UI."""
    return jsonify({**_status, "notice": get_notice()})


def start_web_streaming():
    """Start Flask server (non-blocking)."""
    # Disable the reloader when running inside a thread to avoid spawning
    # additional processes.
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True,
            use_reloader=False)
