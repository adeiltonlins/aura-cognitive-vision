"""Provider-neutral orchestration for AURA's live perception loop.

The pipeline deliberately keeps model inference separate from temporal memory,
tracking, scene relations and presentation. A real camera/model adapter can
feed observations into `process_frame`.
"""

from scene_memory import SceneMemory
from scene_schema import Scene
from tracker import SimpleTracker
from scene_graph import SceneGraph


class CognitiveVisionPipeline:
    def __init__(self) -> None:
        self.memory = SceneMemory()
        self.tracker = SimpleTracker()
        self.graph = SceneGraph()
        self.frame_number = 0

    def process_frame(self, observations: list[dict]) -> dict:
        self.frame_number += 1
        tracked = self.tracker.update(observations)
        self.memory.update(tracked)

        # Keep graph construction intentionally conservative until a
        # relationship detector is connected.
        for item in tracked:
            entity_id = item.get("id") or item.get("label", "unknown")
            self.graph.upsert_entity(entity_id, item.get("label", "unknown"), item)

        return {
            "frame": self.frame_number,
            "observations": tracked,
            "memory": self.memory.snapshot(),
            "scene_graph": self.graph.snapshot(),
        }
