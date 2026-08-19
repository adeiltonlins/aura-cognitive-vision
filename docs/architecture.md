# AURA Architecture

## Cognitive vision loop

AURA is organized as a pipeline with explicit boundaries between perception, cognition and presentation.

```text
Input
  ↓
Perception
  ↓
Scene Model
  ↓
Context Engine
  ↓
Reasoning / Agents
  ↓
Spatial Semantics
  ↓
Presentation
  ↓
Human feedback
```

## 1. Perception

Inputs may include:

- images;
- video frames;
- camera streams;
- depth information;
- future wearable sensors.

The perception layer should output structured observations rather than raw model prose.

Example:

```json
{
  "objects": [
    {
      "label": "person",
      "confidence": 0.97,
      "position": {"x": 0.42, "y": 0.31}
    }
  ]
}
```

## 2. Scene model

The scene model represents entities, relationships and observations over time. This eventually becomes a scene graph capable of answering questions such as:

- What is present?
- Where is it?
- What changed?
- What is related to what?
- How confident are we?

## 3. Context engine

The context engine combines the current scene with user intent, recent observations and available knowledge.

A key research question is how much context should be retained and when it should be discarded.

## 4. Cognitive engine

The cognitive layer can combine multimodal models with deterministic software and specialized agents.

Possible agents include:

- perception verifier;
- context researcher;
- reasoning agent;
- safety verifier;
- action planner.

The system should avoid treating model output as automatically correct. Verification and uncertainty are first-class concepts.

## 5. Spatial semantics

The spatial layer translates semantic understanding into coordinates and persistent anchors so information can eventually be placed relative to physical objects.

## 6. Presentation

The same cognitive output should be usable by different interfaces:

- browser simulation;
- phone screen;
- AR headset;
- smart glasses;
- future optical interfaces.

This separation keeps the intelligence independent from hardware.

## Research direction

The long-term question is not simply whether a machine can recognize an object. It is whether a system can maintain a useful, uncertain, contextual model of the user's environment and present only information that meaningfully assists the user.
