"""Short-term semantic memory for AURA 2.0.

Stores structured observations instead of raw camera frames. This prototype
keeps state in the running process; persistent memory can be added later.
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
    status: str = "present"


class SceneMemory:
    """Keeps lightweight state for entities observed across frames."""

    def __init__(self, max_entities: int = 100) -> None:
        self.entities: dict[str, SceneObservation] = {}
        self.max_entities = max_entities

    @staticmethod
    def _moved(old: dict[str, float] | None, new: dict[str, float] | None) -> bool:
        if not old or not new:
            return False
        return any(abs(float(new.get(k, 0)) - float(old.get(k, 0))) > 0.12 for k in ("x", "y"))

    def update(self, observations: list[dict[str, Any]]) -> list[dict[str, str]]:
        now = datetime.now(timezone.utc).isoformat()
        seen: set[str] = set()
        events: list[dict[str, str]] = []

        for item in observations:
            label = str(item.get("label", "unknown")).strip().lower()
            if not label:
                continue
            seen.add(label)
            position = item.get("position")
            existing = self.entities.get(label)

            if existing is None:
                self.entities[label] = SceneObservation(
                    label=label,
                    confidence=float(item.get("confidence", 0.0)),
                    position=position,
                    attributes=item.get("attributes", {}),
                    first_seen=now,
                    last_seen=now,
                )
                events.append({"type": "new", "label": label})
                continue

            was_missing = existing.status == "missing"
            moved = self._moved(existing.position, position)
            existing.confidence = float(item.get("confidence", existing.confidence))
            existing.position = position or existing.position
            existing.attributes.update(item.get("attributes", {}))
            existing.last_seen = now
            existing.observations += 1
            existing.status = "present"

            if was_missing:
                events.append({"type": "returned", "label": label})
            elif moved:
                events.append({"type": "moved", "label": label})

        for label, entity in self.entities.items():
            if label not in seen and entity.status == "present":
                entity.status = "missing"
                events.append({"type": "missing", "label": label})

        if len(self.entities) > self.max_entities:
            oldest = sorted(self.entities.items(), key=lambda pair: pair[1].last_seen)
            for label, _ in oldest[: len(self.entities) - self.max_entities]:
                self.entities.pop(label, None)

        return events

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
                "status": entity.status,
            }
            for entity in self.entities.values()
        ]

    def reset(self) -> None:
        self.entities.clear()
