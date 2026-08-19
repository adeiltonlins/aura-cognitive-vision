"""Small provider-independent temporal memory for AURA.

The memory intentionally stores observations rather than model prose. It can
later be connected to a tracker, database, or spatial scene graph.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SceneObservation:
    label: str
    confidence: float
    position: dict[str, float] | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    first_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    observations: int = 1


class SceneMemory:
    """Keeps lightweight state for entities observed across frames."""

    def __init__(self) -> None:
        self.entities: dict[str, SceneObservation] = {}

    def update(self, observations: list[dict[str, Any]]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        for item in observations:
            label = str(item.get("label", "unknown")).strip().lower()
            if not label:
                continue

            existing = self.entities.get(label)
            if existing is None:
                self.entities[label] = SceneObservation(
                    label=label,
                    confidence=float(item.get("confidence", 0.0)),
                    position=item.get("position"),
                    attributes=item.get("attributes", {}),
                    first_seen=now,
                    last_seen=now,
                )
            else:
                existing.confidence = float(item.get("confidence", existing.confidence))
                existing.position = item.get("position", existing.position)
                existing.attributes.update(item.get("attributes", {}))
                existing.last_seen = now
                existing.observations += 1

    def snapshot(self) -> list[dict[str, Any]]:
        return [
            {
                "label": entity.label,
                "confidence": entity.confidence,
                "position": entity.position,
                "attributes": entity.attributes,
                "first_seen": entity.first_seen,
                "last_seen": entity.last_seen,
                "observations": entity.observations,
            }
            for entity in self.entities.values()
        ]
