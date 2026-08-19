from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from gemini_perception import GeminiPerception
from openai_perception import OpenAIPerception

app = Flask(__name__)
MOBILE_DIR = Path(__file__).parent / "mobile"


def build_provider():
    """Use Gemini for normal perception and OpenAI only as a fallback."""
    gemini = None
    openai = None
    errors = []

    if os.getenv("GEMINI_API_KEY"):
        try:
            gemini = GeminiPerception()
        except Exception as exc:
            errors.append(f"Gemini unavailable: {exc}")

    if os.getenv("OPENAI_API_KEY"):
        try:
            openai = OpenAIPerception()
        except Exception as exc:
            errors.append(f"OpenAI unavailable: {exc}")

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

    if not gemini and not openai:
        return jsonify({
            "status": "error",
            "error": "No perception provider is configured",
            "details": provider_errors,
        }), 503

    if gemini:
        try:
            result = gemini.analyze(frame)
            if result.get("status") == "ok":
                return jsonify(result)
        except Exception as exc:
            provider_errors.append(f"Gemini request failed: {exc}")

    if openai:
        try:
            result = openai.analyze(frame)
            return jsonify(result)
        except Exception as exc:
            provider_errors.append(f"OpenAI fallback failed: {exc}")

    return jsonify({
        "status": "error",
        "error": "All perception providers failed",
        "details": provider_errors[-4:],
    }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
