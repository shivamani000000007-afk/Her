# Her Voice — Render Deployment (split-file, mobile, no Hugging Face)

Your model is split into 3 parts, each under GitHub's 25MB mobile upload limit.
The server automatically glues them back together the moment it starts up —
you don't need to do anything about that part, it just works.

## Files in this download
- `Dockerfile`
- `app.py`
- `requirements.txt`
- `README.md`
- `my_voice_00.part`
- `my_voice_01.part`
- `my_voice_02.part`
- `my_voice.onnx.json` (small, uploads normally)

## Step 1 — Upload everything to a new GitHub repo (from your phone)

1. github.com → **New repository** → name it e.g. `her-voice-server`
2. **Add file → Upload files**
3. Upload all 7 files listed above, straight into the root (no subfolders)
   — each `.part` file is ~20MB, safely under the 25MB limit
4. Commit

## Step 2 — Deploy on Render

1. render.com → sign up free
2. **New → Web Service** → connect GitHub → pick `her-voice-server`
3. It auto-detects the Dockerfile — leave settings default
4. Instance type: **Free**
5. **Create Web Service**
6. Watch the build logs — you should see lines like:
   ```
   Reassembling model from split parts...
     joining my_voice_00.part
     joining my_voice_01.part
     joining my_voice_02.part
   Reassembled my_voice.onnx from 3 parts.
   Loading voice model...
   Voice model loaded.
   ```
   That confirms the split file was rebuilt correctly.

## Step 3 — Test it

Visit the Render URL it gives you — you should see:
```json
{"status": "ok", "message": "Her Assistant voice server is running."}
```

## Step 4 — Wire it into the assistant

1. botprana.netlify.app → gear icon
2. Paste into **Cloned-voice endpoint**:
   `https://your-render-url.onrender.com/synthesize`
3. Save, send a message, listen

## Notes
- Free Render services sleep after ~15 min idle — first message after a gap
  takes ~30-50s to wake up, that's normal
- If the build log shows "No my_voice.onnx and no my_voice_*.part files found,"
  double-check all 3 `.part` files actually uploaded — mobile uploads sometimes
  drop one if the connection hiccups mid-upload
