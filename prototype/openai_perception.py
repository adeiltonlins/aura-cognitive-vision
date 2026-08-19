from __future__ import annotations

import base64
import json
import os
from typing import Any

from openai import OpenAI


class OpenAIPerception:
    """Converts a camera frame into structured AURA observations."""

    def __init__(self, model: str | None = None) -> None:
        self.client = OpenAI()
        self.model = model or os.getenv("AURA_VISION_MODEL", "gpt-4.1-mini")

    def analyze(self, frame: Any) -> dict[str, Any]:
        ok, encoded = frame_to_jpeg(frame)
        if not ok:
            return {"status": "error", "error": "Could not encode frame"}

        image_data = base64.b64encode(encoded).decode("ascii")
        response = self.client.responses.create(
            model=self.model,
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze this camera frame for AURA Cognitive Vision. "
                            "Return ONLY valid JSON with keys summary, observations, "
                            "uncertainty. Each observation must contain label, "
                            "confidence (0-1), position {x,y,width,height} normalized "
                            "to 0-1, and attributes. Do not identify people by name "
                            "or infer sensitive personal attributes."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_data}",
                        "detail": "low",
                    },
                ],
            }],
        )

        text = response.output_text.strip()
        try:
            return {"status": "ok", "scene": json.loads(text)}
        except json.JSONDecodeError:
            return {"status": "error", "error": "Vision model returned invalid JSON", "raw": text}


def frame_to_jpeg(frame: Any) -> tuple[bool, bytes]:
    import cv2

    ok, encoded = cv2.imencode(".jpg", frame)
    return ok, encoded.tobytes() if ok else b""
