# Cover image with LitMedia

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
python <litmedia-skill>/scripts/ai_image.py estimate-cost --type text2image --model "Nano Banana 2" --resolution 2K --count 1
python <litmedia-skill>/scripts/ai_image.py run --type text2image --model "Nano Banana 2" \
    --prompt "<prompt>" --aspect-ratio 16:9 --resolution 2K --count 1 --output-dir ./cover
```

Default model recommended by LitMedia: **Nano Banana** (no resolution parameter, lowest cost). `2K` at 16:9 is enough:
the site scales covers to 1600 px wide and serves WebP. Generate **one** image; a second only if the first is unusable.
The result is downloaded into `--output-dir`; pass that file to `tarots_blog.py post … --cover <file>`.

## Prompt recipe (English)

`<subject/symbol> + <scene or composition> + <mood and light> + <style> + <constraints>`

- Subject from the article: the card's symbols (a tower struck by lightning, a starry night sky with a kneeling
  figure and water, the moon over two towers), the season (equinox balance, winter solstice candlelight), the practice
  (a journal, candles and cards on a table).
- Composition for 16:9: leave calm space, one clear focal point, nothing important at the far edges.
- Mood: contemplative, mystical, warm candlelight or deep indigo night with gold accents (the brand palette is indigo,
  night violet and gold).
- Style: painterly, or an elegant esoteric illustration; consistent across articles.
- Constraints, always: `no text, no letters, no watermark, no logo, no recognizable real person`.

Examples:

- *"A lone stone tower on a cliff struck by a golden lightning bolt at night, storm clouds in deep indigo and violet,
  sparks falling, dramatic but symbolic, esoteric painterly illustration, wide cinematic composition, calm dark
  space on the left, no text, no letters, no watermark"* (article: The Tower)
- *"A wooden table at dusk with a Thoth-style tarot spread of cards face down, a burning candle, a brass astrolabe
  and dried flowers, warm candlelight against deep indigo shadows, contemplative mood, painterly, wide 16:9, no
  text, no readable card faces, no watermark"* (article: how to start a tarot journal)

## Alt text and file

Write `cover_alt` yourself, describing what is really in the image, 8+ characters, ideally ≤ 125:
`"A stone tower on a cliff struck by golden lightning under a violet night sky"`. Include the keyword only if it
fits without sounding forced. PNG, JPEG or WebP up to 8 MB.

## Images inside the body, not just the cover

The same LitMedia flow works for an extra image placed inside the article (a diagram, a close-up of a symbol
discussed in the text) — generate it the same way, then `python scripts/tarots_blog.py upload picture.png` on its
own (no `post`/`--cover`) to get back a URL, and write `![alt text](url)` at the right point in the Markdown body.
Same cost-and-consent rule as the cover: each inline image is a separate generation, counted and consented to like
any other. Use it only where it genuinely helps the reader — a wall of decorative images hurts more than it helps.
