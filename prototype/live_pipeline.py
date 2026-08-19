"""Orchestration for AURA's live perception loop."""

from scene_memory import SceneMemory
from tracker import EntityTracker
from scene_graph import SceneGraph


class CognitiveVisionPipeline:
    def __init__(self) -> None:
        self.memory = SceneMemory()
        self.tracker = EntityTracker()
        self.graph = SceneGraph()
        self.frame_number = 0
        self.latest_scene: dict = {"summary": "waiting", "uncertainty": []}

    def process_frame(self, observations: list[dict], scene: dict | None = None) -> dict:
        self.frame_number += 1
        tracked = self.tracker.update(observations)
        self.memory.update(tracked)

        for item in tracked:
            entity_id = item.get("entity_id") or item.get("label", "unknown")
            self.graph.upsert_entity(entity_id, item.get("label", "unknown"), item)

        if scene:
            self.latest_scene = scene

        return self.state(tracked)

    def state(self, observations: list[dict] | None = None) -> dict:
        return {
            "frame": self.frame_number,
            "observations": observations or [],
            "memory": self.memory.snapshot(),
            "scene_graph": self.graph.snapshot(),
            "scene": self.latest_scene,
        }
