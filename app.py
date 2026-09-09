import os
import io
import wave

from flask import Flask, request, send_file, jsonify, Response
from flask_cors import CORS
from piper import PiperVoice

app = Flask(__name__)
CORS(app)  # allows botprana.netlify.app (or any origin) to call this server

TEST_PAGE_HTML = """
<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Her Voice — Test</title>
  <style>
    body { font-family: sans-serif; background: #1B1420; color: #F2E9E4; padding: 24px; max-width: 480px; margin: 0 auto; }
    h1 { font-size: 20px; }
    textarea { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid #444; background: #2A1F33; color: #F2E9E4; font-size: 15px; box-sizing: border-box; }
    button { width: 100%; padding: 14px; margin-top: 12px; border-radius: 10px; border: none; background: #E8A87C; color: #1B1420; font-weight: bold; font-size: 15px; }
    #status { margin-top: 12px; font-size: 13px; color: #C9B8C4; text-align: center; }
  </style>
</head>
<body>
  <h1>Test your cloned voice</h1>
  <p>This page talks directly to this server — no main app, no brain, no CORS involved. Good for isolating whether the voice itself works.</p>
  <textarea id="text" rows="3" placeholder="Type something to hear it...">வணக்கம், நான் நலமா இருக்கேன்.</textarea>
  <button onclick="speak()">Generate & Play</button>
  <div id="status"></div>
  <audio id="player" controls style="width:100%; margin-top:12px; display:none;"></audio>
  <script>
    async function speak() {
      const text = document.getElementById('text').value;
      const statusEl = document.getElementById('status');
      const player = document.getElementById('player');
      statusEl.textContent = 'Generating... (first request after idle may take 30-50s)';
      try {
        const res = await fetch('/synthesize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: text })
        });
        if (!res.ok) {
          const errText = await res.text();
          throw new Error('Server returned ' + res.status + ': ' + errText);
        }
        const blob = await res.blob();
        player.src = URL.createObjectURL(blob);
        player.style.display = 'block';
        player.play();
        statusEl.textContent = 'Done.';
      } catch (err) {
        statusEl.textContent = 'Error: ' + err.message;
      }
    }
  </script>
</body>
</html>
"""

MODEL_PATH = "my_voice.onnx"
CONFIG_PATH = "my_voice.onnx.json"

# Your model was uploaded to GitHub split into 3 parts (to stay under the 25MB
# mobile upload limit). Reassemble them into the real .onnx file before loading.
if not os.path.exists(MODEL_PATH):
    print("Reassembling model from split parts...")
    part_files = sorted([f for f in os.listdir(".") if f.startswith("my_voice_") and f.endswith(".part")])
    if not part_files:
        raise FileNotFoundError(
            "No my_voice.onnx and no my_voice_*.part files found. "
            "Make sure the split model parts were uploaded to this repo."
        )
    with open(MODEL_PATH, "wb") as out_file:
        for part in part_files:
            print(f"  joining {part}")
            with open(part, "rb") as pf:
                out_file.write(pf.read())
    print(f"Reassembled {MODEL_PATH} from {len(part_files)} parts.")

print("Loading voice model...")
voice = PiperVoice.load(MODEL_PATH, config_path=CONFIG_PATH)
print("Voice model loaded.")


@app.route("/", methods=["GET"])
def health():
    # Built-in test page — visit this URL directly in a browser to test the
    # voice with no dependency on the main app, CORS, or the brain at all.
    return Response(TEST_PAGE_HTML, mimetype="text/html")


@app.route("/synthesize", methods=["POST"])
def synthesize():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(voice.config.sample_rate)
        for audio_chunk in voice.synthesize_stream_raw(text):
            wav_file.writeframes(audio_chunk)

    buffer.seek(0)
    return send_file(buffer, mimetype="audio/wav")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
