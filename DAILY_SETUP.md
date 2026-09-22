# Rusty: daily draft workflow (REVIEW ONLY)

This is a prototype, not an automatic AI cartoon studio. V6 still uses a small low-resolution fox sprite atlas and has NO genuine frame-by-frame walk cycle. DO NOT publish drafts without watching and approving them.

## Schedule

The workflow `.github/workflows/daily-rusty-drafts.yml` runs at **09:17 and 19:17 Turkey time** (06:17 and 16:17 UTC). GitHub may delay/drop scheduled runs; public repository schedules can be disabled after 60 days without repo activity. Every run generates **one** separate review-only video and a `review.json` report. Thus the target is two drafts per day, *not* two guaranteed public YouTube uploads. Output artifacts expire after three days.

Open GitHub repository → Actions → `Rusty Daily Drafts — Review Only` → choose run → Artifacts → download `rusty-review-...` to view the MP4 and report. `Run workflow` supports morning/evening manual runs. Choose `offline_test` only to exercise the robotic eSpeak fallback for engineering checks; normal scheduled runs use edge-tts and will fail rather than secretly substitute a robot voice if it is unavailable.

## Optional API accounts (never put keys in chat or repository files)

Go to repository **Settings → Secrets and variables → Actions → New repository secret**. Add:

- `GEMINI_API_KEY`: Google AI Studio Gemini key. With a key, the bot requests a four-line script from `gemini-2.5-flash`, then checks length and visual compatibility. Without a key, or if the response is invalid/unavailable, it labels the result `curated_template_...` and uses one of six prewritten scripts. Six variants do NOT provide 60 unique story concepts; do not treat them as production-ready unique videos.
- `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`: Workers AI account ID and token. Both are required; the bot requests **at most one** `@cf/black-forest-labs/flux-1-schnell` background per run, with **4 steps**, and falls back to its built-in office if the service fails. An AI background is not a new animation. Cloudflare free plan has a daily quota and some account/model restrictions.

No paid API or credit card required by the workflow itself. Check your provider's current plan before enabling the associated API. GitHub standard public runners have other limits. All generated media stays as a private-to-the-run GitHub Actions artifact (your repository itself is public); do not add any personal/secret information to story prompts.

## Safety and accuracy

- No YouTube upload code; no OAuth token or publish permissions.
- No API key printing; GitHub Secrets are passed as environment variables.
- Story must fit four existing poses: boss/exposure reaction → Wi-Fi phone → sharing → exit/rent joke.
- Each scheduled run gets a separate dated filename and `review.json` containing source, fallback status, technical QC, and honest animation limitations.
- Narration uses edge-tts service, not Kokoro. Kokoro has NOT been integrated, and speech quality has NOT been human-reviewed.
- Cloudflare, Gemini and daily schedule must be tested with connected credentials and actual scheduled executions before claiming 60 outputs/month.
