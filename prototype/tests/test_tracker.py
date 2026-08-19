from tracker import EntityTracker


def test_tracker_keeps_identity_when_object_moves_slightly():
    tracker = EntityTracker(max_distance=0.2)

    first = tracker.update([
        {"label": "person", "confidence": 0.9, "position": {"x": 0.2, "y": 0.3}}
    ])
    second = tracker.update([
        {"label": "person", "confidence": 0.92, "position": {"x": 0.25, "y": 0.31}}
    ])

    assert first[0]["entity_id"] == second[0]["entity_id"]
