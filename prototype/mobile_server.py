from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from openai_perception import OpenAIPerception

app = Flask(__name__)
perception = OpenAIPerception()
MOBILE_DIR = Path(__file__).parent / "mobile"


@app.get("/")
def mobile_app():
    return send_from_directory(MOBILE_DIR, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "aura-mobile-perception"})


@app.post("/api/perception")
def mobile_perception():
    upload = request.files.get("frame")
    if upload is None:
        return jsonify({"status": "error", "error": "Missing multipart field 'frame'"}), 400

    import cv2
    import numpy as np

    data = upload.read()
    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({"status": "error", "error": "Invalid JPEG frame"}), 400

    result = perception.analyze(frame)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
