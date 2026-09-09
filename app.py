import os
import io
import wave

from flask import Flask, request, send_file, jsonify
from piper import PiperVoice

app = Flask(__name__)

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
    return jsonify({"status": "ok", "message": "Her Assistant voice server is running."})


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
