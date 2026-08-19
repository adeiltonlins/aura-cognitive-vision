from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from gemini_perception import GeminiPerception
from openai_perception import OpenAIPerception

app = Flask(__name__)
MOBILE_DIR = Path(__file__).parent / "mobile"


def build_provider():
    gemini = None
    openai = None
    errors = []

    if os.getenv("GEMINI_API_KEY"):
        try:
            gemini = GeminiPerception()
        except Exception as exc:
            errors.append(f"Gemini initialization failed: {type(exc).__name__}: {exc}")
    else:
        errors.append("GEMINI_API_KEY is not configured")

    if os.getenv("OPENAI_API_KEY"):
        try:
            openai = OpenAIPerception()
        except Exception as exc:
            errors.append(f"OpenAI initialization failed: {type(exc).__name__}: {exc}")
    else:
        errors.append("OPENAI_API_KEY is not configured")

    return gemini, openai, errors


gemini, openai, provider_errors = build_provider()


@app.get("/")
def mobile_app():
    return send_from_directory(MOBILE_DIR, "index.html")


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "aura-mobile-perception",
        "primary_provider": "gemini" if gemini else None,
        "fallback_provider": "openai" if openai else None,
        "gemini_model": os.getenv("AURA_GEMINI_MODEL", "gemini-2.5-flash-lite") if gemini else None,
    })


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

    failures = []

    if gemini:
        try:
            result = gemini.analyze(frame)
            if result.get("status") == "ok":
                return jsonify(result)
            failures.append({"provider": "gemini", "error": result.get("error", "unknown error")})
        except Exception as exc:
            failures.append({"provider": "gemini", "error": f"{type(exc).__name__}: {exc}"})

    if openai:
        try:
            result = openai.analyze(frame)
            if result.get("status") == "ok":
                return jsonify(result)
            failures.append({"provider": "openai", "error": result.get("error", "unknown error")})
        except Exception as exc:
            failures.append({"provider": "openai", "error": f"{type(exc).__name__}: {exc}"})

    return jsonify({
        "status": "error",
        "error": "All perception providers failed",
        "details": failures[-4:] or provider_errors[-4:],
    }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
