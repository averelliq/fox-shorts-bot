# Fox Shorts Bot — honest free starter

Original, hand-drawn procedural 2D fox animation with independent tail/arms/head/eye/mouth motion, English eSpeak NG voice, subtitles, scene switching, 1080×1920 MP4, FFprobe quality checks, and GitHub Actions artifact delivery. **This is an MVP, not photorealistic generative video and not natural neural TTS.** No automatic AI script generation; edit `stories/episode.json` with your own original English script.

## Set up on GitHub, no PC installation
1. Open **Actions → Render Fox Short → Run workflow**. On first upload, Actions might ask you to enable workflows.
2. After the job ends, download `fox-short-review` under **Artifacts**. Watch `short.mp4` and read `metadata.json` before publishing.
3. For another video, change the English text, title, description and scene/emotion in `stories/episode.json`, commit and run again.

## YouTube publishing (deliberately manual approval)
Open YouTube Studio https://studio.youtube.com/ → Create → Upload videos; upload your reviewed `short.mp4`, paste title and description from `metadata.json`, choose audience, and publish after watching. Automated YouTube API upload is **not implemented** in this MVP: it requires user-owned Google OAuth authorization, token storage and potential API project verification. Never commit credentials to GitHub. There is no built-in promise of views or monetization.

## Local optional test
On Ubuntu: `sudo apt-get install ffmpeg espeak-ng fonts-dejavu-core`; `python -m pip install -r requirements.txt`; `python scripts/render.py`.

## Troubleshooting
If duration check fails, shorten the JSON story or increase `--max-seconds` up to an appropriate platform limit. If FFmpeg, font or eSpeak fails, inspect GitHub Actions logs. eSpeak is intentionally a basic **robotic** fallback; natural neural TTS is a later phase pending an actually tested CPU-compatible open model and redistribution/license checks. Source artwork and dialogue are original; do not substitute unlicensed media.