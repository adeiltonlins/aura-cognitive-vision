"""Lightweight tracker that assigns stable IDs to nearby observations."""

from math import hypot
from typing import Any


class EntityTracker:
    def __init__(self, max_distance: float = 0.15) -> None:
        self.max_distance = max_distance
        self._next_id = 1
        self._tracks: dict[str, dict[str, Any]] = {}

    def update(self, observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        updated: list[dict[str, Any]] = []
        used: set[str] = set()

        for observation in observations:
            label = str(observation.get("label", "unknown")).lower()
            position = observation.get("position") or {}
            x = float(position.get("x", 0.0))
            y = float(position.get("y", 0.0))

            best_id = None
            best_distance = self.max_distance
            for entity_id, track in self._tracks.items():
                if entity_id in used or track["label"] != label:
                    continue
                distance = hypot(x - track["x"], y - track["y"])
                if distance <= best_distance:
                    best_id = entity_id
                    best_distance = distance

            if best_id is None:
                best_id = f"{label}_{self._next_id:03d}"
                self._next_id += 1

            self._tracks[best_id] = {"label": label, "x": x, "y": y}
            used.add(best_id)
            item = dict(observation)
            item["entity_id"] = best_id
            updated.append(item)

        return updated

    def snapshot(self) -> list[dict[str, Any]]:
        return [
            {"entity_id": entity_id, **track}
            for entity_id, track in self._tracks.items()
        ]
