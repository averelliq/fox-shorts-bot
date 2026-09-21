# Fox Shorts Bot V2 — free review-first prototype 🦊

This repository creates **original, directed 2D cartoon Shorts** on GitHub's standard Ubuntu runner. It is not the same as a paid AI video generator, and it does **not** publish to YouTube automatically. The fox is procedurally drawn consistently across four distinct story beats: office paycheck, exposed Wi-Fi notice and phone, angry boss, and rent-day twist. Arms, head, tail, legs and mouth move independently. Final MP4 is 1080×1920 with English narration and embedded captions.

## Run in your browser (no local install)
1. Open **Actions → Render Fox Short V2 → Run workflow**. Editing `stories/episode.json` also triggers a new run.
2. Open the finished run and download the **fox-short-v2-review** artifact. It contains `short.mp4` and `metadata.json`.
3. **Watch the video and listen to the voice yourself**. Automated checks catch resolution, duration, an audio stream, minimum scene count and measurable frame changes; they do not certify artistic quality, pronunciation or YouTube performance.
4. After approval, upload `short.mp4` through [YouTube Studio](https://studio.youtube.com/). Nothing in this repo uploads a video automatically.

## Voice / cost / reliability
The default voice is `en-US-GuyNeural` via the free community Python package `edge-tts`. It contacts an external online speech service without an API key. **That service is not guaranteed to stay free, available or suitable for every commercial use; check its applicable terms yourself.** If access fails, the workflow fails explicitly: there is no silent robotic eSpeak fallback. A fully offline permissively licensed neural voice is a separate, not-yet-implemented improvement.

The workflow uses a **standard public-repository GitHub-hosted runner**, not a paid larger runner, GPU or API. GitHub Actions still has abuse limits, concurrent job limits and artifact storage/retention limits. Artifact retention is 3 days. Do not publish account keys, OAuth credentials or private media in this public repository.

## Files
- `scripts/render_v2.py`: V2 character motion, scene drawing, neural TTS, FFmpeg encoding and technical checks.
- `stories/episode.json`: English story/title/description and per-beat stage directions.
- `.github/workflows/render.yml`: browser-triggered cloud rendering and review artifact.
- `scripts/render.py`: older V1 reference, **not** used by the current workflow.

## Optional local execution
On Ubuntu install `ffmpeg` and `fonts-dejavu-core`, then run `python -m pip install -r requirements.txt && python scripts/render_v2.py` (requires internet access for speech). Check `output/short.mp4` and `output/metadata.json`.

## Not implemented
Automatically generated fresh story concepts, truly studio-level character rigging, offline neural voice, YouTube OAuth setup, automatic upload, thumbnail generation and subjective video assessment. These are future work, not V2 features. Do not claim this generator makes AI content undetectable or guarantees distribution.
