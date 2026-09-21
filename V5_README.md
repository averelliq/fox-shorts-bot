# Rusty V5 — approved artwork / short animation proof 🦊

V5 is a **different character-rendering approach** from V1–V4: `scripts/render_v5.py` does not draw a procedural fox. It decodes a checked, transparent sprite atlas extracted from the original Rusty expression/action artwork approved in chat. Three distinct real drawings (shocked face, phone-use pose, walking pose) are used in a **3–5 second acting/staging proof** with a 1080×1920 MP4, English neural narration and captions. Artwork is committed as four base64 chunks (`assets/v5_atlas_part_*.txt`); the SHA-256 in `assets/rusty_atlas.json` checks exact reconstruction. No external expiring art URLs or paid image API are required.

**Watch and approve the short proof BEFORE attempting a full Shorts episode.** This is NOT professional frame-by-frame animation. It moves/cuts between rigid drawn poses and changes camera/staging; limbs, lips, and tail are not yet independently drawn/inbetweened. The art atlas is also relatively low resolution because poses were cropped from a single full design sheet. A production series would need individually exported high-res transparent pose drawings, matched mouth and limb layers, and a real 2D rig/tween pipeline. Do not claim that a normal GitHub CPU produces unlimited, studio-quality AI animation.

## Browser workflow (no installation or manual code upload)
Open **Actions → Render Rusty V5 Sprite Proof (Review Only)**. The first run is triggered by committing the workflow; on later occasions press **Run workflow**. Download the **rusty-v5-sprite-proof** artifact and open `short_v5_proof.mp4`; inspect `metadata_v5.json` for mechanical QC. Artifacts expire after three days, so save useful proofs. There are no YouTube upload steps, OAuth credentials, or automatic publishing in V5.

Speech uses network-dependent `edge-tts` neural narration (availability and usage terms not guaranteed). If it fails, the GitHub run fails rather than substituting robotic speech. `FOX_OFFLINE_TEST=1` permits eSpeak **only** in local smoke tests, not release-ready narration. Automated QC verifies dimensions, audio stream, duration, three distinct poses and art hash; it does not certify voice naturalness or animation quality.

Legacy V1–V4 files remain in the repository for reference and are not the V5 renderer.
