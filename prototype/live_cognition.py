from __future__ import annotations

from typing import Any

from live_pipeline import CognitiveVisionPipeline


class LiveCognition:
    """Adapter that turns multimodal model output into persistent scene state."""

    def __init__(self) -> None:
        self.pipeline = CognitiveVisionPipeline()

    def consume(self, result: dict[str, Any]) -> dict[str, Any]:
        if result.get("status") != "ok":
            return self.pipeline.state()

        scene = result.get("scene") or {}
        observations = scene.get("observations") or []
        return self.pipeline.process_frame(observations, scene)
