from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any

PROMPT = (
    "Analyze this camera frame for AURA Cognitive Vision. "
    "Return ONLY valid JSON with keys summary, observations, uncertainty. "
    "Each observation must contain label, confidence (0-1), "
    "position {x,y,width,height} normalized to 0-1, and attributes. "
    "Do not identify people by name or infer sensitive personal attributes."
)


class GeminiPerception:
    """Converts a camera frame into structured AURA observations using Gemini."""

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        self.api_key = api_key
        self.model = model or os.getenv("AURA_GEMINI_MODEL", "gemini-2.5-flash-lite")

    def analyze(self, frame: Any) -> dict[str, Any]:
        ok, encoded = frame_to_jpeg(frame)
        if not ok:
            return {"status": "error", "error": "Could not encode frame", "provider": "gemini"}

        payload = {
            "contents": [{
                "parts": [
                    {"text": PROMPT},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(encoded).decode("ascii"),
                        }
                    },
                ]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1,
                "maxOutputTokens": 800,
            },
        }

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = response.read().decode("utf-8")
                result = json.loads(raw)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            return {
                "status": "error",
                "error": f"Gemini HTTP {exc.code}: {detail[:1200]}",
                "provider": "gemini",
            }
        except Exception as exc:
            return {
                "status": "error",
                "error": f"Gemini request failed: {type(exc).__name__}: {exc}",
                "provider": "gemini",
            }

        try:
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            return {
                "status": "error",
                "error": f"Gemini returned an unexpected response: {exc}",
                "raw": json.dumps(result)[:2000],
                "provider": "gemini",
            }

        if not text:
            return {"status": "error", "error": "Gemini returned an empty response", "provider": "gemini"}

        try:
            scene = json.loads(text)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "error": "Gemini returned invalid JSON",
                "raw": text[:2000],
                "provider": "gemini",
            }

        return {"status": "ok", "scene": scene, "provider": "gemini"}


def frame_to_jpeg(frame: Any) -> tuple[bool, bytes]:
    import cv2

    ok, encoded = cv2.imencode(".jpg", frame)
    return ok, encoded.tobytes() if ok else b""
