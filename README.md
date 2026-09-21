# Fox Shorts Bot — Rusty V5 🦊

The current **V5 proof** uses the original Rusty character drawings approved by the user, rather than drawing the fox from procedural SVG shapes as earlier versions did. It prepares a 3–5 second 1080×1920 review MP4 with three distinct artwork-based poses, English narration and subtitles. **It does not upload to YouTube.** This is an acting/visual-style proof, not a finished Shorts episode or studio-quality frame-by-frame animation.

**[V5 documentation and limitations](V5_README.md)** · [V5 sprite engine](scripts/render_v5.py) · [V5 GitHub Actions](../../actions/workflows/render-v5.yml)

In your browser go to **Actions → Render Rusty V5 Sprite Proof (Review Only) → Run workflow**. When the run succeeds, download the `rusty-v5-sprite-proof` artifact. It contains `short_v5_proof.mp4` and `metadata_v5.json`. Artifacts expire in three days.

V1–V4 source and workflows are retained for reference. The old [V4 documentation](V4_README.md) applies only to V4. The new atlas is reconstructed from four small text chunks in `assets/` and SHA-256 validated before rendering. Automated tests verify basic technical conditions, not artistic quality, naturalness of the English voice or popularity.

Costs: standard GitHub runner plus free software; the online voice service may have availability/terms restrictions. Public repositories must not contain private account credentials or unlicensed media. **Publishing remains manual and requires review/approval.**
