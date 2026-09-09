# Her Voice — Render Deployment

A small Flask server that loads your trained Piper voice model and serves it as a
real, always-reachable API — free, on Render.

## Files needed in this folder
- `Dockerfile`
- `app.py`
- `requirements.txt`
- `my_voice.onnx` (your trained model — copy it in here)
- `my_voice.onnx.json` (your model's config — copy it in here)

## Step 1 — Put this on GitHub
1. Create a new GitHub repo (can be separate from your main assistant repo)
2. Upload all 5 files above into it (root of the repo, no subfolders)

## Step 2 — Deploy on Render
1. Go to https://render.com → sign up free (no card required)
2. **New → Web Service**
3. Connect your GitHub, pick this repo
4. Render will detect the `Dockerfile` automatically — leave settings default
5. Instance type: **Free**
6. Click **Create Web Service** — first build takes a few minutes (installing
   espeak-ng + piper-tts)

## Step 3 — Test it
Once deployed, Render gives you a URL like `https://her-voice-xxxx.onrender.com`.
Visit it directly in a browser — you should see:
```json
{"status": "ok", "message": "Her Assistant voice server is running."}
```
That confirms it's alive.

## Step 4 — Wire it into the assistant
1. Go to https://botprana.netlify.app/
2. Tap the gear icon (Settings)
3. Paste this into **Cloned-voice endpoint**:
   `https://her-voice-xxxx.onrender.com/synthesize`
   (note the `/synthesize` at the end — that's the actual generation route)
4. Save, send a message — it should reply in your voice.

## Honest free-tier notes
- Render's free web services **sleep after ~15 min of no traffic**. The first
  request after sleeping takes ~30-50 seconds to wake up (you'll see a delay,
  not an error) — after that it's fast again.
- If she messages it after it's been idle a while, the first reply will just take
  a bit longer to arrive — normal, not broken.
