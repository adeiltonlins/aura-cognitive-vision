# Mobile perception contract

The mobile client sends a JPEG frame as multipart field `frame` to `POST /api/perception`.

The server should return JSON in this shape:

```json
{
  "status": "ok",
  "scene": {
    "summary": "Uma pessoa próxima de uma mesa.",
    "observations": [
      {
        "label": "person",
        "confidence": 0.96,
        "position": {"x": 0.2, "y": 0.1, "width": 0.3, "height": 0.7},
        "attributes": {}
      }
    ],
    "uncertainty": []
  }
}
```

The API key stays on the server. The browser never receives it.
