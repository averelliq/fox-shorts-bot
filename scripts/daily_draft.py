"""Two distinct daily *review drafts* based on V6's limited four-scene artwork.
No YouTube API, no publishing. External API credentials are optional GitHub secrets.
"""
import asyncio
import base64
import datetime as dt
import io
import json
import os
import random
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image
import render_v6 as v6

ROOT = Path(__file__).resolve().parents[1]
SCENE_TEXT = (
    'My boss paid me in exposure.',
    'So I found his Wi-Fi password.',
    'I shared it with everyone.',
    'Now who is paying the rent?',
)
# All templates match ONLY the V6 artwork: shocked office fox, phone, Wi-Fi sharing, exit.
TEMPLATES = (
    ('My boss offered exposure instead of money.', 'I found the office Wi-Fi password.', 'I exposed it to the entire team.', 'Apparently the landlord prefers actual cash.'),
    ('My paycheck was replaced by free publicity.', 'So I checked the boss’s Wi-Fi settings.', 'The password became public information.', 'My rent is still surprisingly private.'),
    ('The boss said exposure would pay me.', 'I opened the office Wi-Fi menu.', 'Then everybody got free internet.', 'The landlord did not accept the joke.'),
    ('My boss called it a networking opportunity.', 'I found the actual office network.', 'And generously shared its password.', 'Now I need a different kind of connection.'),
    ('The boss promised unlimited visibility today.', 'I looked up his Wi-Fi password.', 'The whole office could finally see it.', 'My landlord wants to see my paycheck.'),
    ('I asked for wages and got exposure.', 'Then I opened the router settings.', 'I gave everyone the network password.', 'Sadly my rent has no exposure plan.'),
)


def selected_slot():
    slot = os.getenv('RUSTY_SLOT', 'auto').lower()
    if slot == 'auto':
        slot = 'morning' if dt.datetime.now(dt.timezone.utc).hour < 12 else 'evening'
    if slot not in ('morning', 'evening'):
        raise ValueError('RUSTY_SLOT must be morning or evening')
    return slot


def validate(lines):
    if not isinstance(lines, list) or len(lines) != 4:
        raise ValueError('Need four lines for four available storyboard beats')
    for line in lines:
        if not isinstance(line, str) or not 12 <= len(line) <= 115:
            raise ValueError('Caption length outside safe range')
        if not 3 <= len(line.split()) <= 15:
            raise ValueError('Caption word count outside safe range')
    if sum(len(x.split()) for x in lines) > 44:
        raise ValueError('Narration is too long for a short V6 proof')
    return [x.strip() for x in lines]


def post_json(url, data, headers, timeout=45):
    request = urllib.request.Request(url, json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json', **headers}, method='POST')
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def script_for(day, slot):
    seed = int(day.strftime('%Y%m%d')) * 2 + (slot == 'evening')
    fallback = list(TEMPLATES[seed % len(TEMPLATES)])
    key = os.getenv('GEMINI_API_KEY', '').strip()
    if not key:
        return validate(fallback), 'curated_template_no_gemini_key'
    prompt = ('Return ONLY a JSON array of exactly four short English voiceover lines. Write original, playful, family-friendly office comedy for an ORIGINAL orange fox named Rusty. '
              'CRITICAL visual continuity: line 1 Rusty reacts to a boss offering exposure instead of wages; '
              'line 2 Rusty checks the boss office Wi-Fi password on a phone; line 3 Rusty reveals the password to coworkers; '
              'line 4 Rusty walks out with a funny rent/paycheck punchline. Do not invent any other visual actions, objects or scenes. '
              'Use 3-12 words per line, maximum 44 words total, no hashtags, no real passwords. '
              f'Today is {day.isoformat()}, slot is {slot}; avoid copying this reference: {fallback}')
    try:
        result = post_json('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent',
                           {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseMimeType': 'application/json', 'temperature': 0.8, 'maxOutputTokens': 350, 'thinkingConfig': {'thinkingBudget': 0}}},
                           {'x-goog-api-key': key})
        text = ''.join(p.get('text', '') for p in result['candidates'][0]['content']['parts'])
        return validate(json.loads(text)), 'gemini_2_5_flash'
    except (ValueError, KeyError, IndexError, TypeError, urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
        print(f'Gemini unavailable or rejected; using prewritten storyboard: {type(error).__name__}')
        return validate(fallback), 'curated_template_gemini_unavailable'


def optional_office_background(day, slot):
    account = os.getenv('CLOUDFLARE_ACCOUNT_ID', '').strip()
    token = os.getenv('CLOUDFLARE_API_TOKEN', '').strip()
    if not (account and token):
        return None, 'built_in_background_no_cloudflare_credentials'
    prompt = ('Beautiful original hand-painted 2D cartoon OFFICE INTERIOR background only, no people, no animals, '
              'no fox, no lettering or logos. Cozy whimsical workplace with a big window, warm peach walls, wood desk, '
              'soft cream and teal palette, ink outlines and subtle paper texture, portrait 9:16 framing, '
              'open clear foreground and center for an animated character, consistent TV animation background art.')
    url = f'https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/black-forest-labs/flux-1-schnell'
    try:
        reply = post_json(url, {'prompt': prompt, 'steps': 4, 'seed': int(day.strftime('%Y%m%d')) % 999999 + (slot == 'evening')},
                          {'Authorization': f'Bearer {token}'}, timeout=100)
        image_bytes = base64.b64decode(reply['result']['image'], validate=True)
        if len(image_bytes) > 12_000_000:
            raise ValueError('Image response unexpectedly large')
        art = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
        return art.resize((v6.W, v6.H), Image.Resampling.LANCZOS), 'cloudflare_flux_1_schnell_one_image'
    except (ValueError, KeyError, TypeError, OSError, urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
        print(f'Cloudflare background unavailable; preserving built-in art: {type(error).__name__}')
        return None, 'built_in_background_cloudflare_unavailable'


def main():
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).date()
    slot = selected_slot()
    lines, story_source = script_for(today, slot)
    office, bg_source = optional_office_background(today, slot)
    replacements = dict(zip(SCENE_TEXT, lines))
    original_caption = v6.caption
    original_neural = v6.neural
    original_run = v6.run
    original_bg = v6.bg
    spoken = ' '.join(lines)

    def custom_caption(frame, text):
        return original_caption(frame, replacements.get(text, text))

    async def custom_neural(_text, path):
        return await original_neural(spoken, path)

    def custom_run(args):
        if args and args[0] == 'espeak' and os.getenv('FOX_OFFLINE_TEST') == '1':
            args = list(args)
            args[-1] = spoken
        return original_run(args)

    def custom_bg(kind):
        if kind == 'office' and office is not None:
            return office.copy()
        return original_bg(kind)

    v6.caption = custom_caption
    v6.neural = custom_neural
    v6.run = custom_run
    v6.bg = custom_bg
    v6.main()  # Raises on failed audio, invalid 1080x1920 MP4, or failed QC.

    folder = ROOT / 'output' / 'daily' / f'{today.isoformat()}-{slot}'
    folder.mkdir(parents=True, exist_ok=True)
    video = folder / 'rusty_review.mp4'
    shutil.copyfile(ROOT / 'output' / 'short_v6_proof.mp4', video)
    report = json.loads((ROOT / 'output' / 'metadata_v6.json').read_text())
    report.update({'date_trt': today.isoformat(), 'slot_trt': slot, 'voiceover_lines': lines,
                   'story_source': story_source, 'office_background_source': bg_source,
                   'youtube_uploaded': False, 'human_review_required': True,
                   'not_a_full_character_animation': True,
                   'scene_asset_limitations': 'V6 three low-resolution static character sprites; no real walk cycle'})
    (folder / 'review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print('REVIEW DRAFT READY', video, 'source=', story_source, 'background=', bg_source)


if __name__ == '__main__':
    main()
