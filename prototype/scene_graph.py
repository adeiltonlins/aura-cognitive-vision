"""Semantic graph for entities and relationships in a visual scene."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Entity:
    entity_id: str
    label: str
    confidence: float = 0.0
    position: dict[str, float] | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Relation:
    source: str
    relation: str
    target: str
    confidence: float = 0.0


class SceneGraph:
    def __init__(self) -> None:
        self.entities: dict[str, Entity] = {}
        self.relations: list[Relation] = []

    def upsert_entity(self, entity: Entity) -> None:
        self.entities[entity.entity_id] = entity

    def add_relation(self, source: str, relation: str, target: str, confidence: float = 0.0) -> None:
        item = Relation(source, relation, target, confidence)
        if item not in self.relations:
            self.relations.append(item)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entities": [vars(entity) for entity in self.entities.values()],
            "relations": [vars(relation) for relation in self.relations],
        }
