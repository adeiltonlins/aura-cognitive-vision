from __future__ import annotations

import base64
import json
import os
from typing import Any

from google import genai
from google.genai import types

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
        self.client = genai.Client(api_key=api_key)
        # Lite is a good default for frequent camera perception and low cost.
        self.model = model or os.getenv("AURA_GEMINI_MODEL", "gemini-2.5-flash-lite")

    def analyze(self, frame: Any) -> dict[str, Any]:
        ok, encoded = frame_to_jpeg(frame)
        if not ok:
            return {"status": "error", "error": "Could not encode frame", "provider": "gemini"}

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_text(text=PROMPT),
                types.Part.from_bytes(data=encoded, mime_type="image/jpeg"),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        text = (response.text or "").strip()
        if not text:
            return {"status": "error", "error": "Gemini returned an empty response", "provider": "gemini"}

        try:
            return {"status": "ok", "scene": json.loads(text), "provider": "gemini"}
        except json.JSONDecodeError:
            return {
                "status": "error",
                "error": "Gemini returned invalid JSON",
                "raw": text[:2000],
                "provider": "gemini",
            }


def frame_to_jpeg(frame: Any) -> tuple[bool, bytes]:
    import cv2

    ok, encoded = cv2.imencode(".jpg", frame)
    return ok, encoded.tobytes() if ok else b""
