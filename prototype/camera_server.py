from __future__ import annotations

import base64
import io
import os
import threading
import time

from flask import Flask, Response, jsonify, render_template_string

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

from live_pipeline import LivePipeline

app = Flask(__name__)
pipeline = LivePipeline()
camera = None
camera_lock = threading.Lock()

PAGE = """
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AURA Live Vision</title>
<style>
body{margin:0;background:#050812;color:#eef3ff;font-family:system-ui,sans-serif}
main{max-width:1100px;margin:auto;padding:24px}.hud{position:relative;border:1px solid #263354;border-radius:18px;overflow:hidden;background:#0b1020}
img{display:block;width:100%;min-height:420px;object-fit:cover}.panel{position:absolute;top:16px;left:16px;padding:14px 16px;border-radius:12px;background:rgba(5,8,18,.82);backdrop-filter:blur(8px)}
.status{color:#83e6ac}.title{font-weight:700;font-size:20px}.small{font-size:13px;opacity:.75;margin-top:6px}
</style></head><body><main><div class="hud"><img src="/video_feed"><div class="panel"><div class="title">👁️ AURA</div><div class="status">● LIVE PERCEPTION</div><div class="small">Camera → tracking → scene memory → scene graph</div></div></div></main></body></html>
"""


def get_camera():
    global camera
    if cv2 is None:
        return None
    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(int(os.getenv("AURA_CAMERA_INDEX", "0")))
        return camera


def frames():
    cam = get_camera()
    if cam is None:
        yield b""
        return

    while True:
        ok, frame = cam.read()
        if not ok:
            time.sleep(0.2)
            continue

        # The frame is intentionally kept provider-neutral here.
        # A future perception worker will populate pipeline state from frames.
        pipeline.process_frame([])

        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            continue
        payload = encoded.tobytes()
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + payload + b"\r\n")


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.get("/video_feed")
def video_feed():
    return Response(frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.get("/state")
def state():
    return jsonify(pipeline.state())


if __name__ == "__main__":
    if cv2 is None:
        raise SystemExit("Instale opencv-python para usar a câmera ao vivo.")
    app.run(host="0.0.0.0", port=8000, debug=True)
