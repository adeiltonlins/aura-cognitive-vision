from flask import Flask, jsonify, render_template_string, request

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
    <p>Primeiro protótipo: preparar o ciclo <b>ver → estruturar → contextualizar</b>.</p>
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
  const response = await fetch('/analyze', { method: 'POST', body: data });
  result.textContent = JSON.stringify(await response.json(), null, 2);
});
</script>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/analyze")
def analyze():
    image = request.files.get("image")
    if not image:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    # Provider-neutral placeholder. A multimodal model will populate this structure.
    return jsonify({
        "status": "received",
        "filename": image.filename,
        "pipeline": [
            "perception",
            "scene_model",
            "context_engine",
            "presentation"
        ],
        "observations": [],
        "message": "Imagem recebida. Conecte um provedor multimodal para habilitar a percepção real."
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
