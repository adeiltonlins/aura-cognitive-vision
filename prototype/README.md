# AURA v0.1 Prototype

This directory contains the first runnable proof-of-concept scaffold for the cognitive vision loop.

## Goal

`image → perception → structured scene → context → presentation`

The current implementation intentionally keeps the perception backend modular. A real multimodal provider can be connected through the `VISION_PROVIDER` interface later.

## Structure

- `app.py` — minimal local web server
- `requirements.txt` — Python dependencies
- `.env.example` — configuration template

## Run

```bash
cd prototype
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open the local address shown by the server.

## Next implementation

1. Connect a multimodal vision model.
2. Return structured JSON observations.
3. Draw confidence-aware annotations over the image.
4. Add video-frame processing.
