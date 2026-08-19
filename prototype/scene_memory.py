"""Temporal scene memory for AURA 2.0."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SceneObservation:
    label: str
    confidence: float
    position: dict[str, float] | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    first_seen: str = field(default_factory=now_iso)
    last_seen: str = field(default_factory=now_iso)
    observations: int = 1
    present: bool = True


class SceneMemory:
    """Keeps semantic state for entities observed across camera frames."""

    def __init__(self) -> None:
        self.entities: dict[str, SceneObservation] = {}
        self.last_events: list[dict[str, Any]] = []

    @staticmethod
    def _distance(a: dict[str, float] | None, b: dict[str, float] | None) -> float:
        if not a or not b:
            return 0.0
        ax, ay = float(a.get("x", 0)), float(a.get("y", 0))
        bx, by = float(b.get("x", 0)), float(b.get("y", 0))
        return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

    def update(self, observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        now = now_iso()
        events: list[dict[str, Any]] = []
        seen: set[str] = set()

        for item in observations:
            label = str(item.get("label", "unknown")).strip().lower()
            if not label:
                continue
            seen.add(label)
            confidence = float(item.get("confidence", 0.0))
            position = item.get("position")
            attributes = item.get("attributes", {}) or {}
            existing = self.entities.get(label)

            if existing is None:
                self.entities[label] = SceneObservation(label, confidence, position, attributes, now, now)
                events.append({"type": "new", "label": label, "message": f"Novo objeto: {label}"})
                continue

            if not existing.present:
                events.append({"type": "returned", "label": label, "message": f"{label} voltou à cena"})
            elif self._distance(existing.position, position) >= 0.18:
                events.append({"type": "moved", "label": label, "message": f"{label} mudou de posição"})

            existing.confidence = confidence
            existing.position = position or existing.position
            existing.attributes.update(attributes)
            existing.last_seen = now
            existing.observations += 1
            existing.present = True

        for label, entity in self.entities.items():
            if entity.present and label not in seen:
                entity.present = False
                events.append({"type": "left", "label": label, "message": f"{label} saiu da cena"})

        self.last_events = events
        return events

    def snapshot(self) -> list[dict[str, Any]]:
        return [{
            "label": e.label, "confidence": e.confidence, "position": e.position,
            "attributes": e.attributes, "first_seen": e.first_seen, "last_seen": e.last_seen,
            "observations": e.observations, "present": e.present,
        } for e in self.entities.values()]

    def reset(self) -> None:
        self.entities.clear()
        self.last_events = []
