---
name: tarots-blog-images
description: Generate and swap the images of TAROTS chat (tarots.chat) blog articles — the cover and the pictures inside the text — with the LitMedia skill (litmedia-skill, API, Seedream 5.0 2K) through this skill's own `tarots_images.py generate`, one article at a time. Every picture is a scene written for that article, different in form from the previous ones (kind, shot, light and setting declared and checked), and never a picture of cards (a card may only be context). Use when asked to replace, refresh, fix, vary or add images on TAROTS blog posts, to give an article a picture inside its text, or when tarots-blog-publisher needs a cover. Not browser-image-gen, not the agent's own image tool.
---

# TAROTS chat blog images

The blog's covers went wrong twice: first every article had tarot cards laid out on a table; then an agent made
about fifty covers from one fixed prompt per section, with cards in almost all of them, the same picture again and
again, sometimes the same file on two articles. This skill gives every article **its own** picture — a scene, a
place, a person, a season, an object or a metaphor from what the article is actually about, **never a picture of
cards** — in a form (kind, shot, light, setting) that differs from the last pictures, and replaces cover and inline
pictures through the REST API, without touching the text, the SEO fields or the status.

Works for any agent that can run a shell command (Hermes, OpenClaw, Codex, Claude Code). Python 3.8+, standard
library only. The script is `scripts/tarots_images.py` (paths below are relative to this skill). It is also the
**only** way `tarots-blog-publisher` generates its covers and inline pictures.

## How pictures are made: only LitMedia, only through this script
- `python scripts/tarots_images.py generate …` calls the separate **`litmedia-skill`** (LitMedia API, Seedream 5.0,
  2K; its own login and credits: read its `SKILL.md` once). That is the only way to make a blog picture.
- **Never** `browser-image-gen`, never the LitMedia website in a browser, never the agent's own built-in image tool,
  never `litmedia-skill`'s `ai_image.py` called directly (it would skip every check below).
- If LitMedia does not answer, fails or the credits are not enough: **no picture**. Say so in the report; do not
  look for another way to make one.

## The picture rules (the script enforces them, with no option to skip)
- **Cards as context, never as the picture.** Refused: a card as the **subject** (the prompt starts with it, the
  word *card* is in the first clause or the first 8 content words, a close-up of a card, tarot artwork), **more than
  one card** (cards, a deck, a pile, a hand of cards, the arcana), a **spread or layout** (cards on a table, a
  reading, a fan of cards, cards face down, a Celtic Cross layout), **hands holding or turning a card**. Accepted:
  "tarot" as an adjective, the **names of the cards** as a world or a symbol ("a lighthouse struck by lightning, the
  energy of the Tower"), **one single small card later in the scene**. An alt text describing a spread is refused;
  one mentioning a card gets a warning. Details and examples: `references/prompts.md`.
- **A concrete scene from this article**: at least 12 content words once the house style and the empty words
  ("mystical", "ethereal", "professional photography"…) are out.
- **A new form**: `generate` and `prompt-check` require `--kind` (17 values), `--shot` (12), `--light` (10) and
  `--setting` (a place, culture or era in free text); `catalog` lists them. Refused: a kind of the **last 3**
  pictures, a kind+shot pair of the **last 20**, a light of the **last 2** (firelight: of the **last 10**), a
  setting of the **last 10**. The prompt must contain a word of the declared light and shot (the setting is recorded for variety; it does not
  have to appear in the prompt).
  Each refusal says what to change and lists what is free.
- **A new scene**: a prompt sharing 45% or more of its content words with any prompt already generated is refused,
  with the closest one shown. Change the scene, not three words.
- **A new file**: `cover` and `inline` refuse a picture (same bytes, whatever the name) already used for another
  article.
- These checks run on `generate`, on `generate --dry-run` and on `prompt-check`; refusals exit with code **7**
  (a value outside the catalogs: code 2). Everything is recorded in `~/.tarots-blog/images-progress.json` (prompts,
  the four dimensions, files, sha256, dates). The publisher's `tarots_blog.py post --cover` / `upload` read and
  write the same record: they accept only pictures made by `generate` (or explicitly supplied by the operator) and
  never one already used by another article.

## Setup (once)

1. An admin creates a key in the console: **Blog → Keys**, permission **«Cambiare le immagini» (`blog:media`)**.
   That permission touches only pictures, but on **every** article: keep the key for this job alone.
2. For the first run only:
   ```
   TAROTS_API_URL=https://tarots.chat/api
   TAROTS_MEDIA_KEY=tk_live_…
   ```
   The key is then remembered in `~/.tarots-blog/media-credentials.json` (outside any repository). Never put it in a
   file of a project, a prompt or a message; only its 12-character prefix may appear in output.
3. Check: `python scripts/tarots_images.py list` and `python scripts/tarots_images.py balance`.

(`generate` and `prompt-check` need no key: `tarots-blog-publisher` uses them without one.)

## Workflow

### 1. Decide the scope with the operator
- Which articles: all, only published, one language, or the ids the operator names. `list --todo` shows what this
  tool has not redone yet.
- Cover only, or cover **and** pictures in the text (the operator's standing choice for this blog: both).
- **Budget**: each picture costs **10 credits** (Seedream 5.0, 2K; there is no 1K). Tell the operator:
  *N articles × (1 cover + k inline) × 10 = total*, and the current `balance`. Get a yes before spending. If the
  operator already set a budget, keep to it with `--budget` (credits still allowed) and `--reserve` (credits that
  must stay on the account).

### 2. One article at a time: read before you imagine
```
python scripts/tarots_images.py show <id>
python scripts/tarots_images.py progress
```
Read title, subtitle, keyword, section, tags and **the whole text**. Find what the article is really about: the
human situation it speaks to (grief, a new love, a decision, a change of season), the world of its card, the place
or the time. Note where the text already has pictures (`immagini_nel_testo`, numbered from 0) and what their alt
text says. `progress` shows the last 20 pictures with their kind, shot, light and setting, and what is free next.

### 3. Write the prompt (the heart of the job)
Follow `references/prompts.md`. In short:
- The **subject comes from the article**: name **one concrete element of its text**. Never a prompt per section,
  never a template, never the candlelit table, the open book with a candle or the desk as a default scene.
- Then choose its **form** among the free values (`catalog`, `progress`): `--kind` (what it shows), `--shot` (the
  framing), `--light`, `--setting` (a place, culture or era, from the article when it has one). Write the light, the
  framing and the setting into the prompt with their own words.
- Append the house style line unchanged; covers are **3:2**, pictures in the text **4:3** (or 1:1 for a close-up).
- Check it for free:
  `python scripts/tarots_images.py prompt-check --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --alt "<alt>"`.

### 4. Try it dry first
```
python scripts/tarots_images.py generate --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --out work/<slug>-cover.jpg --dry-run
python scripts/tarots_images.py cover <id> work/<slug>-cover.jpg --alt "<alt>" --dry-run
```
For the first run with an operator, show the prompts for **three** articles and wait for an ok before generating.

### 5. Generate and swap
```
python scripts/tarots_images.py generate --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --out work/<slug>-cover.jpg --budget <left>
python scripts/tarots_images.py cover <id> work/<slug>-cover.jpg --alt "<what the picture shows>"

python scripts/tarots_images.py generate --prompt "<prompt>" --kind <other kind> --shot <shot> --light <other light> --setting "<other setting>" --aspect 4:3 --out work/<slug>-1.jpg --budget <left>
python scripts/tarots_images.py inline <id> --replace 0 work/<slug>-1.jpg "<alt>"
```
- **Look at every picture before swapping it in** (open the file). Reject it if it is a picture of cards anyway (a
  card filling the frame, a spread, a deck, cards in a hand), has text or letters, a malformed hand or face, or has
  nothing to do with the article. A second try is a **rewritten** prompt with a new form (the same prompt and the
  same dimensions are refused as a repeat), and at most one.
- `inline` also takes `--add <after paragraph> <file> <alt>` (0 = after the first paragraph; paragraphs are blocks
  separated by a blank line) and `--remove <n>`. Add a picture only where it serves the text, not at the top (that is
  the cover) and not after the last paragraph. One or two per article is plenty, each a different kind from the cover.
- Alt text: describe what is **in the new picture**, 8–125 characters, the keyword only if it fits naturally.
- The server makes the list thumbnail of every uploaded picture by itself: nothing to do.
- A timeout from LitMedia: run `balance` and check the article with `show` before trying again. Never resubmit in a
  loop. `429` from the API: stop and wait.
- Then the next article, from step 2.

### 6. Report
A short table: article, what changed (cover / inline n), the subject and the form (kind · shot · light · setting)
of each picture, credits spent,
balance left, and anything the operator should look at (a picture you rejected, a prompt the script refused and
why, an article whose text made a good picture hard, LitMedia failing).

## Hard rules
- Only pictures: never try to change text, title, SEO fields or status (the key cannot, and should not try).
- **Never a picture of cards** (a card at most as a small detail in the context). No text in pictures. No recognisable real people, no fake photos of real
  events, no copy of the Thoth deck's actual artwork (copyrighted).
- **Only `tarots_images.py generate`** makes pictures (through `litmedia-skill`). Never `browser-image-gen`, never a
  built-in image tool, never the LitMedia website.
- **Never write your own script** (a loop, a batch, a "publish_sequential" helper) to generate or swap pictures in
  series: one article at a time, with these commands, looking at each result.
- Never reuse a picture on two articles; never work around a refusal by renaming a file or padding a prompt.
- Spend only the credits the operator agreed to. Check `balance` when in doubt.
- Never disable TLS verification, never follow a redirect with the key, never send the key anywhere but
  `TAROTS_API_URL`, never send it to LitMedia.

## Files
- `scripts/tarots_images.py`: the CLI (`-h` on every command).
- `references/prompts.md`: cards as context and never as the picture, the four dimensions with their catalogs and
  rules, the house style, examples.
- `references/api.md`: the four endpoints, if you would rather call them directly.
- `tests/test_controlli.py`: offline tests of the picture rules (`python -m pytest tests -q`).
