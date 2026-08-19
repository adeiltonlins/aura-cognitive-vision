import base64
import json
import os

from flask import Flask, jsonify, render_template_string, request
from openai import OpenAI

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>AURA Cognitive Vision</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 0; background: #0b1020; color: #f4f7ff; }
    main { max-width: 900px; margin: 0 auto; padding: 48px 20px; }
    .card { background: #121a2e; border: 1px solid #273252; border-radius: 18px; padding: 24px; }
    h1 { margin-top: 0; }
    .status { color: #8fe3b1; }
    button { padding: 12px 18px; border: 0; border-radius: 10px; cursor: pointer; }
    pre { white-space: pre-wrap; background: #080c17; padding: 16px; border-radius: 12px; }
  </style>
</head>
<body>
<main>
  <div class="card">
    <h1>👁️ AURA Cognitive Vision</h1>
    <p class="status">● Cognitive Vision v0.1 — online</p>
    <p>Primeiro ciclo: <b>ver → estruturar → contextualizar</b>.</p>
    <form id="visionForm">
      <input id="image" type="file" accept="image/*" required>
      <button type="submit">Analisar cena</button>
    </form>
    <pre id="result">Aguardando uma imagem...</pre>
  </div>
</main>
<script>
const form = document.getElementById('visionForm');
const result = document.getElementById('result');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = new FormData();
  data.append('image', document.getElementById('image').files[0]);
  result.textContent = 'Processando percepção...';
  try {
    const response = await fetch('/analyze', { method: 'POST', body: data });
    result.textContent = JSON.stringify(await response.json(), null, 2);
  } catch (error) {
    result.textContent = JSON.stringify({error: error.message}, null, 2);
  }
});
</script>
</body>
</html>
"""


def get_client():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY não configurada no ambiente.")
    return OpenAI()


def analyze_with_openai(image_bytes: bytes, mime_type: str):
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    client = get_client()

    prompt = """
You are the perception layer of AURA Cognitive Vision.
Analyze the supplied image and return ONLY valid JSON with this shape:
{
  "scene_summary": "short description",
  "observations": [
    {
      "label": "object/entity",
      "confidence": 0.0,
      "location": "relative location in the image",
      "attributes": ["..."],
      "relevance": "why this may matter"
    }
  ],
  "context": ["useful contextual inferences"],
  "uncertainties": ["things that may be wrong or ambiguous"]
}
Do not invent details that cannot reasonably be inferred from the image.
"""

    response = client.responses.create(
        model=os.getenv("AURA_VISION_MODEL", "gpt-5.6-luna"),
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:{mime_type};base64,{encoded}",
                },
            ],
        }],
    )

    text = response.output_text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "scene_summary": text,
            "observations": [],
            "context": [],
            "uncertainties": ["Model output was not valid JSON."]
        }


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/analyze")
def analyze():
    image = request.files.get("image")
    if not image:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    try:
        result = analyze_with_openai(
            image.read(),
            image.mimetype or "image/jpeg",
        )
        return jsonify({
            "status": "analyzed",
            "pipeline": [
                "perception",
                "scene_model",
                "context_engine",
                "presentation"
            ],
            **result,
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "error": str(exc),
            "hint": "Configure OPENAI_API_KEY no ambiente antes de analisar imagens."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
