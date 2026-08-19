"""Canonical schema for AURA visual observations."""

from typing import Any, TypedDict


class Position(TypedDict, total=False):
    x: float
    y: float
    width: float
    height: float


class Observation(TypedDict, total=False):
    label: str
    confidence: float
    position: Position
    attributes: dict[str, Any]


class Scene(TypedDict, total=False):
    summary: str
    observations: list[Observation]
    uncertainty: list[str]


def empty_scene() -> Scene:
    return {
        "summary": "",
        "observations": [],
        "uncertainty": [],
    }
