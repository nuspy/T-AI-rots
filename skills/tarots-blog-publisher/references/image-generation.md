# Cover image: two alternatives, pick one per run

**Do not use your own agent framework's built-in image-generation tool for this** (a native
`image_generate`/`generate_image`/similar capability some agents ship with) — it is a third,
different mechanism, has no `nano-banana`/free option, and defeats the cost or free-method choice
below. This skill's cover always comes from one of the two named skills' own CLI scripts, run as a
shell command via your terminal/bash tool — never from an image tool built into your own runtime.

Two independent ways to get the cover (and any inline image) file to hand to `tarots_blog.py upload`
or `post --cover`. Same downstream steps either way — only how the file is produced differs.

| | `litmedia-skill` (API) | `browser-image-gen` (browser) |
|---|---|---|
| Cost | Paid, per generation | Free for `nano-banana` and `flux` (verify `Credits Required` each time — the site can change this without notice) |
| Speed | Fast, can batch | Slow, ~60-90s, one at a time |
| Setup | OAuth device grant once | One interactive browser login once (`login_una_tantum.py`) |
| Command | `ai_image.py run ...` | `genera_immagine.py --model ... --prompt ...` |

**Default to `litmedia-skill`** unless the operator's instructions say to use the free/browser
method, or explicitly name "Nano Banana", "Flux", or "the browser one". When they do, use
`browser-image-gen` instead for this run — both skills are meant to be trusted/installed side by
side, this is a per-run choice via the prompt, not a permanent switch.

## Option A: LitMedia (API, paid)

The cover is generated with the **LitMedia** skill (`litmedia-skill`, script `scripts/ai_image.py`) and then uploaded
with `tarots_blog.py`. LitMedia is a separate skill with its own login and credits: read its `SKILL.md` first.

## Rules that apply here

1. **Cost and consent.** LitMedia spends credits. Before the first generation of a session: run `estimate-cost`,
   tell the operator the model, aspect ratio, resolution and the cost, and get a yes. If the operator has already
   said to proceed without asking (a standing "auto-proceed"), go ahead. Ask again if the parameters change.
2. **Use the script, not raw HTTP.** `ai_image.py run …` submits and polls until done; do not resubmit a task that is
   still running.
3. **TLS errors are not to be bypassed.** If LitMedia fails with a certificate error (`SSLCertVerificationError`),
   do not disable verification, set `verify=False`, or use another certificate store trick. Report it, and either use
   an image the operator supplied or publish without a cover.
4. **Never send the blog key to LitMedia** (or anything else). The two tools do not share credentials.
5. **The image is illustration, not evidence.** Don't generate fake photos of real people, fake screenshots, fake
   "old manuscripts" presented as real, or a reproduction of the actual Thoth deck's cards (copyrighted artwork).
   Symbolic, atmospheric imagery is right.

## Commands

```
python <litmedia-skill>/scripts/ai_image.py list-models --type text2image
python <litmedia-skill>/scripts/ai_image.py estimate-cost --type text2image --model "Nano Banana 2" --resolution 1K --count 1
python <litmedia-skill>/scripts/ai_image.py run --type text2image --model "Nano Banana 2" \
    --prompt "<prompt>" --aspect-ratio 3:2 --resolution 1K --count 1 --output-dir ./cover
```

**Resolution: always `1K`, never `2K` or `4K`, for a cover.** The page never actually displays the cover wider than
~800 px (checked against the live site) — generating at `2K` (~2048 px) or higher only spends more credits for
detail nobody sees, the browser downscales it either way. `1K` (~1024 px) is the smallest tier the API exposes and
is already above what the page shows. If the model has no `--resolution` parameter at all (e.g. plain "Nano
Banana"), that is fine too — do not add one. Generate **one** image; a second only if the first is unusable. The
result is downloaded into `--output-dir`; pass that file to `tarots_blog.py post … --cover <file>`.

## Option B: browser-image-gen (free/browser)

The `browser-image-gen` skill is installed at `/c/Users/atain/AppData/Local/hermes/skills/browser-image-gen/`.
Read its `SKILL.md` first — it covers one-time login setup and honest limitations (slower, fragile to site changes,
one image at a time). Once the session is logged in:

```
python /c/Users/atain/AppData/Local/hermes/skills/browser-image-gen/scripts/genera_immagine.py \
    --model nano-banana --prompt "<prompt>" --aspect 3:2 --output cover.png
```

`--model nano-banana` at `3:2` (confirmed by the operator as the standing setting for posts, no
resolution/quality forced — the script's own default resolution `1K` applies) is the confirmed free
(0 credits) combination as of 2026-09-29 — the script prints the actual `Credits Required` before
generating either way, so trust that over this note if they disagree. Same prompt recipe as Option A
below. The downloaded file is automatically converted to WebP by the script (PNG/JPEG → WebP via PIL). 
The output will always be `.webp` even if you pass `--output cover.png`. Pass it straight to 
`tarots_blog.py upload` / `post --cover` like any other file.

### Critical notes for browser-image-gen reliability

- **Domain**: The main site is `litmedia.ai`. Generated images are served from two of their CDN subdomains — 
  `resource.soulvid.ai` (smaller assets, ~100KB) and `app-images.litvid.org` (the large generated results, typically 
  1-2MB PNG). The script's internal `DOMINI_RISULTATI` checks for both `"soulvid"` and `"litvid"`. Do not change it.
- **Session expiry**: Playwright sessions expire after ~3 minutes. If a generation fails with "nessuna immagine trovata", 
  re-run `login_una_tantum.py` first, then retry the generation. Do NOT let more than 3 minutes pass between login 
  and the generation command.
- **DOM fallback**: The script now has a DOM extraction fallback — if no large network responses are captured (which 
  happens when litmedia.ai serves images as `<img>` tags in the page), it extracts URLs directly from the DOM by 
  querying `document.querySelectorAll('img[src]')` and filtering for both `soulvid` and `litvid`. This is reliable but 
  requires the session to still be alive at extraction time.
- **Timeout**: nano-banana typically takes 60–120 seconds to generate. Use `--timeout 600` (default) or higher if the 
  queue is long. The script polls every 10 seconds and stops when "Processing" disappears from the page.
- **WebP conversion**: Litmedia.ai generates images in PNG or JPEG format (often 1–2MB). The script automatically 
  converts them to WebP using PIL (`quality=85, method=6`) after download — this reduces file size by 60–80% with no 
  visible quality loss. The output file will always be `.webp` even if you pass `--output cover.png`. If conversion 
  fails for any reason, the script falls back to saving the original format. Always check that the final file is WebP 
  before passing it to `tarots_blog.py post --cover`.

## Prompt recipe (English)

`<subject/symbol> + <scene or composition> + <mood and light> + <style> + <constraints>`

- Subject from the article: the card's symbols (a tower struck by lightning, a starry night sky with a kneeling
  figure and water, the moon over two towers), the season (equinox balance, winter solstice candlelight), the practice
  (a journal, candles and cards on a table).
- Composition for 3:2: leave calm space, one clear focal point, nothing important at the far edges.
- Mood: contemplative, mystical, warm candlelight or deep indigo night with gold accents (the brand palette is indigo,
  night violet and gold).
- Style: painterly, or an elegant esoteric illustration; consistent across articles.
- Constraints, always: `no text, no letters, no watermark, no logo, no recognizable real person`.

Examples:

- *"A lone stone tower on a cliff struck by a golden lightning bolt at night, storm clouds in deep indigo and violet,
  sparks falling, dramatic but symbolic, esoteric painterly illustration, calm dark space on the left, no text, no
  letters, no watermark"* (article: The Tower)
- *"A wooden table at dusk with a Thoth-style tarot spread of cards face down, a burning candle, a brass astrolabe
  and dried flowers, warm candlelight against deep indigo shadows, contemplative mood, painterly, no
  text, no readable card faces, no watermark"* (article: how to start a tarot journal)

## Alt text and file

Write `cover_alt` yourself, describing what is really in the image, 8+ characters, ideally ≤ 125:
`"A stone tower on a cliff struck by golden lightning under a violet night sky"`. Include the keyword only if it
fits without sounding forced. PNG, JPEG or WebP up to 8 MB.

## Images inside the body, not just the cover

**Checked against the live blog (2026-09-28): none of the sampled published articles had a real inline image —
only a cover, sometimes not even that.** The instruction below was being treated as optional and skipped every
time. It is not optional: a genuinely useful inline image (a diagram, a spread layout, a close-up of a symbol
discussed in the text) is part of a normal article, the same way a cover is. Decide explicitly for every article
whether one belongs, and say so in the step 9 report either way ("inline image: yes, showing X" / "inline image:
none, the topic didn't call for one") — never just silently skip the decision.

Either option above works for it (LitMedia or browser-image-gen), same choice logic as the cover:
generate the same way, then `python scripts/tarots_blog.py upload picture.png` on its own (no
`post`/`--cover`) to get back a URL, and write `![alt text](url)` at the right point in the
Markdown body — not at the very top (that is what the cover is for) and not inside the closing
paragraph.

**Resolution: the smallest the model allows.** This is a small illustration inside a column of text, not a hero
image — never `2K` or `4K`. Use `--resolution "1K"` if the model requires one, or prefer a fixed-price model with no
resolution parameter at all (e.g. plain "Nano Banana" — also the cheapest option, see `list-models`). Same
cost-and-consent rule as the cover: each inline image is a separate generation, counted and consented to like any
other. One inline image is normally enough; a second only if the article genuinely covers two distinct visual
ideas — a wall of decorative images hurts more than it helps.
