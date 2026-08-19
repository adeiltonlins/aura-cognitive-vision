from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from gemini_perception import GeminiPerception
from openai_perception import OpenAIPerception
from scene_memory import SceneMemory

app = Flask(__name__)
MOBILE_DIR = Path(__file__).parent / "mobile"
scene_memory = SceneMemory()


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
        "version": "2.0",
        "primary_provider": "gemini" if gemini else None,
        "fallback_provider": "openai" if openai else None,
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "gemini_model": os.getenv("AURA_GEMINI_MODEL", "gemini-3.5-flash-lite") if gemini else None,
        "memory_objects": len(scene_memory.entities),
    })


@app.post("/api/memory/reset")
def reset_memory():
    scene_memory.reset()
    return jsonify({"status": "ok", "message": "AURA visual memory reset"})


@app.get("/api/memory")
def get_memory():
    return jsonify({
        "status": "ok",
        "version": "2.0",
        "objects": scene_memory.snapshot(),
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
                scene = result.get("scene") or {}
                observations = scene.get("observations") or []
                events = scene_memory.update(observations)
                return jsonify({
                    **result,
                    "memory": {
                        "version": "2.0",
                        "objects": scene_memory.snapshot(),
                        "events": events,
                    },
                })
            failures.append({"provider": "gemini", "error": result.get("error", "unknown error")})
        except Exception as exc:
            failures.append({"provider": "gemini", "error": f"{type(exc).__name__}: {exc}"})

    if openai:
        try:
            result = openai.analyze(frame)
            if result.get("status") == "ok":
                scene = result.get("scene") or {}
                observations = scene.get("observations") or []
                events = scene_memory.update(observations)
                return jsonify({
                    **result,
                    "memory": {
                        "version": "2.0",
                        "objects": scene_memory.snapshot(),
                        "events": events,
                    },
                })
            failures.append({"provider": "openai", "error": result.get("error", "unknown error")})
        except Exception as exc:
            failures.append({"provider": "openai", "error": f"{type(exc).__name__}: {exc}"})

    details = failures[-4:] or provider_errors[-4:]
    app.logger.error("AURA perception failed: %s", details)
    return jsonify({
        "status": "error",
        "error": details[0]["error"] if details and isinstance(details[0], dict) else "All perception providers failed",
        "details": details,
    }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
