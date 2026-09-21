# Fox Shorts Bot V3 🦊

A free **review-first 2D animation prototype**, running on standard GitHub Actions Ubuntu runners. It draws the same fox across four directed beats, adds a teal vest/badge, phone interaction, boss/landlord reactions, small camera pushes, 2–3-word caption groups and original synthesized notification/reaction tones. English narration is produced with `edge-tts`. The finished MP4 is checked for 1080×1920 dimensions, audio, duration and scene frame changes.

**This is still procedural 2D cartoon artwork, not studio character animation or generative text-to-video.** Caption timing uses estimated word positions within each spoken sentence, not true forced alignment. The cartoon's acting, pronunciation, comedy, and music/SFX balance require human inspection. SFX are synthesized tones, not realistic recorded Foley.

## Browser-only use
1. Open **Actions → Render Fox Short V3 → Run workflow** (editing `stories/episode.json` also triggers rendering).
2. Open the successful run, download **fox-short-v3-review**, and extract `short.mp4` and `metadata.json`.
3. Watch and listen to the entire MP4; do not interpret automated QC as creative approval.
4. There is **no automatic YouTube publishing** or Google OAuth in this repo. After your approval, manually upload through YouTube Studio if desired.

## Architecture and constraints
- `scripts/render_v2.py`: original tested drawing/voice/encoding engine.
- `scripts/render_v3.py`: overlays consistent costume, props, moving captions, shot variants and original sound cues.
- `scripts/run_v3.py`: compatibility entrypoint for V2's dynamically looked-up frame function; **run this file** rather than invoking `render_v3.py` directly.
- `stories/episode.json`: original English dialogue and staging for four scenes.
- `.github/workflows/render.yml`: preview-only workflow with 3-day artifacts and concurrency cancellation.

On Ubuntu, install `ffmpeg` and `fonts-dejavu-core`; then `python -m pip install -r requirements.txt && python scripts/run_v3.py`. English speech requires the external `edge-tts` service (no API key), whose free availability and commercial-use suitability are **not guaranteed**; assess applicable terms before monetization. No paid API, private credential, YouTube upload or large/GPU runner is configured. Standard GitHub limits and artifact storage limits still apply.

## Still not implemented
Truly sophisticated skeletal animation, voice pronunciation/acting evaluated by human hearing, accurate forced-aligned word subtitles, fully autonomous original story generation, OAuth-based YouTube uploads, thumbnails or a verified royalty-free recorded Foley library. Do not promise undetectable AI or YouTube reach.
