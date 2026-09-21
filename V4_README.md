# Fox Shorts Bot V4 — original hand-inked cartoon 🦊

V4 replaces the simple geometric drawings with an original thick-ink-outlined fox, stable emerald costume, expressive faces, sketchbook-style locations, individually staged phone and boss interactions, camera framing changes, a landlord and visible door-slam ending. The user-supplied image is a stylistic reference, NOT an asset and not copied. This is procedural SVG animation, not a full professional hand-drawn production.

## One-time browser setup
1. Open the `scripts` folder on GitHub and select **Add file → Upload files**.
2. Upload the prepared `render_v4.py` file into `scripts/` and commit to `main`. Do not upload the ZIP, MP4, or artwork into the public source repository.
3. Open **Actions → Render Fox Short V4 (Review Only) → Run workflow → Run workflow**.
4. After success, download the `fox-short-v4-review` artifact, unzip and watch `short.mp4`. See `metadata.json` for mechanical checks.
5. Listen to English pronunciation, check poses and continuity yourself. No automatic YouTube upload is included.

V4 story is separate at `stories/episode_v4.json`; the original V3 story and workflow are unchanged. GitHub standard CPU runners have finite use/storage limits. The natural voice is generated using `edge-tts` which depends on external network access and terms; if it fails, production fails explicitly, never silently substitutes robotic audio. An optional `FOX_OFFLINE_TEST=1` mode uses eSpeak ONLY for local testing; it should never be used as release narration. No credentials are stored in source control. Technical QC does not certify artistry or virality.
