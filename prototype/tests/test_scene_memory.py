from scene_memory import SceneMemory


def test_scene_memory_persists_entities_across_updates():
    memory = SceneMemory()
    memory.update([
        {"label": "person", "confidence": 0.91, "position": {"x": 0.2, "y": 0.3}}
    ])
    memory.update([
        {"label": "person", "confidence": 0.95, "position": {"x": 0.25, "y": 0.32}}
    ])

    snapshot = memory.snapshot()
    assert len(snapshot) == 1
    assert snapshot[0]["label"] == "person"
    assert snapshot[0]["observations"] == 2
    assert snapshot[0]["confidence"] == 0.95
