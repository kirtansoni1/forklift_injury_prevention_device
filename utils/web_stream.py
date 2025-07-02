# -*- coding: utf-8 -*-

from flask import Flask, Response, render_template_string
import cv2
import threading

app = Flask(__name__)

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
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Forklift Injury Prevention Device</title>
        <style>
            body {
                background-color: #121212;
                color: #f5f5f5;
                font-family: 'Segoe UI', sans-serif;
                text-align: center;
                padding-top: 30px;
            }
            h1 {
                font-size: 2em;
                margin-bottom: 0.5em;
                color: #ffca28;
            }
            p {
                font-size: 1.1em;
                margin-bottom: 1.5em;
            }
            .stream-container {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .stream {
                border: 3px solid #ffca28;
                border-radius: 12px;
                box-shadow: 0 0 20px rgba(255, 202, 40, 0.3);
                width: 80vw;
                max-width: 960px;
            }
        </style>
    </head>
    <body>
        <h1>Forklift Injury Prevention Device Live Stream</h1>
        <p>Streaming from Raspberry Pi</p>
        <div class="stream-container">
            <img class="stream" src="/video_feed" alt="Live Stream Unavailable">
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/video_feed')
def video_feed():
    """Stream the frame via MJPEG."""
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def start_web_streaming():
    """Start Flask server (non-blocking)."""
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
