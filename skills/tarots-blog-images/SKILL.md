---
name: tarots-blog-images
description: Generate and swap the images of TAROTS chat (tarots.chat) blog articles — the cover and the pictures inside the text — with the LitMedia skill (litmedia-skill, API, Seedream 5.0 2K) through this skill's own `tarots_images.py generate`, one article at a time. Every picture is a scene written for that article, different in form from the previous ones (kind, shot, light and setting declared and checked), and never a picture of cards (one small card only in an article about that very card). Use when asked to replace, refresh, fix, vary or add images on TAROTS blog posts, to give an article a picture inside its text, or when tarots-blog-publisher needs a cover. Not browser-image-gen, not the agent's own image tool.
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
- **Fixed settings, nothing to choose**: the model is always **Seedream 5.0** (set in the script, not an option);
  `--aspect` is **3:2** for a cover (the default) and 4:3 or 1:1 inside the text; `--resolution` stays **2K**, the
  cheapest (10 credits: Seedream 5.0 has no 1K; 4K costs 20 and is never needed, the site shrinks every picture to
  1600 px). The LitMedia `quality` is derived by the script from the resolution: never pass it yourself.

## If LitMedia fails (problems already met and solved)
- **"Image generation failed" right after the task is created, with Seedream 5.0**: the installed `litmedia-skill`
  is an old copy. Its `scripts/ai_image.py` must send Seedream 5.0's model id (8) and `quality` in lowercase (`2k`),
  as the litmedia.ai website does (fix of 2026-09-30). `tarots_images.py` checks this before spending anything and
  stops with a message naming the folder to update; the up-to-date source is `E:\Projects\litmedia_skill`. Failed
  tasks are not charged.
- **`ModuleNotFoundError: requests`** (seen when the agent started this script with a bare Python, e.g. uv's): the
  script now finds a Python with LitMedia's dependencies by itself — `LITMEDIA_PYTHON` if set, then its own Python,
  `py -3.12`, `py -3`, `python3`, `python`, and on Windows `%LOCALAPPDATA%\Programs\Python\Python3*\python.exe`,
  newest first — and says which one in a `note:` line. If none has them it exits **5** naming the interpreter and the
  command (`<python> -m pip install -r <litmedia-skill>/scripts/requirements.txt`): install requirements.txt for
  the interpreter it names (ask the operator first), or report that line. The script never installs anything.
- **`ModuleNotFoundError: alibabacloud_oss_v2`** from `ai_image.py`: a dependency missing from LitMedia's
  requirements. Install it for the interpreter that runs the script: `python3 -m pip install alibabacloud_oss_v2`
  (on this Windows host `pip` alone installs into another Python).
- **Login or credits errors**: run `python scripts/tarots_images.py balance`; `litmedia-skill`'s
  `python scripts/auth.py status` tells whether the login is still valid, `auth.py login` renews it (it opens the
  LitMedia sign-in page for the operator: ask first, see its `SKILL.md`).
- **Nano Banana**: never through the API (accepted, then fails on LitMedia's side). This skill never uses it anyway.
- **A certificate / TLS error**: report it; never disable verification.
- After any failure: `balance`, then `show <id>` for the article, then at most **one** new attempt. Never a loop.

## Where the pictures go: the article's work folder
Every picture of an article lives in its work folder, the one `tarots_blog.py new "<slug>"` creates:
`~/.tarots-blog/work/<YYYY-MM-DD>-<slug>/foto/` (`TAROTS_WORK_DIR` moves the root).
- `generate --article <slug> …` saves there: `cover.jpg` for a 3:2 picture, `inline-1.jpg`, `inline-2.jpg`… for
  `--aspect 4:3` or `1:1`; `--out NAME` chooses the name. A bare `--out NAME` without `--article` goes in the newest
  work folder. An article with no work folder yet (an existing article whose pictures you redo) gets one for today.
- `generate` prints the full path of the file: use that path with `cover` and `inline`. An existing file is never
  overwritten (a picture already paid for).
- Never relative paths like `work/<slug>-cover.jpg`: they land in whatever folder the agent runs in, often this
  skill's, and get lost. Never search the disk for a picture: it is in `foto/` of its work folder.

## The picture rules (the script enforces them, with no option to skip)
- **Cards as context, never as the picture.** Refused: a card as the **subject** (the prompt starts with it, the
  word *card* is in the first clause or the first 8 content words, a close-up of a card, tarot artwork), **more than
  one card** (cards, a deck, a pile, a hand of cards, the arcana), a **spread or layout** (cards on a table, a
  reading, a fan of cards, cards face down, a Celtic Cross layout), **hands holding or turning a card**. Accepted:
  "tarot" as an adjective, the **names of the cards** as a world or a symbol, without the word *card* ("a lighthouse
  struck by lightning, the energy of the Tower"). An alt text describing a spread is refused; one mentioning a card
  gets a warning. Details and examples: `references/prompts.md`.
- **A card in the picture only for an article about that very card.** A prompt that draws one single small card
  (the word *card* later in the scene) needs `--article <slug or id>` (also on `prompt-check`), and is refused
  (exit 7) unless the article's **title or focus keyword names that card** (looked for in the work folder's
  article.json, then in the titles copy `~/.tarots-blog/titles-cache.json`, then through the API with the media
  key) and the prompt **names it in the same phrase**: "a single small card of the Tower". The card is drawn **in the
  style of the Thoth deck** (say it, or you get a warning; never a copy, never Rider-Waite or Marseille). Thoth and
  Rider-Waite names are the same card (Adjustment = Justice, Lust = Strength, Art = Temperance, Aeon = Judgement,
  Universe = World…). Accepted, for *The Tower tarot card meaning*: "…seen through the window, on the shelf a single
  small card of the Tower leaning on a cup, in the style of the Thoth deck". Refused, for *Tarot Meditation for
  Libra Season Balance* (an agent added a small Fool there "as context" and got a large Rider-Waite Fool): "…and
  beside it a single small card of the Fool" → *this article is not about a specific card: no card in its picture;
  show its world instead*. Not sure? Leave the card out: the world of the article is always the better picture.
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

`generate`, `prompt-check`, `catalog`, `progress` and `balance` need **no blog key** (only the LitMedia login of
`litmedia-skill`): a cover for a new article (tarots-blog-publisher) needs nothing from this section. A key with the
media permission is only for `list`, `show`, `cover` and `inline` on existing articles. Try the command first: if it
works, never ask the operator for a key.

**The recommended setup: ONE key for both skills.** A key's permissions are chosen only when it is created.
1. An admin creates in the console (**Blog → Keys**) **one** key with the three permissions **write + publish +
   media** (`blog:write`, `blog:publish`, `blog:media` — «Cambiare le immagini»). The media permission touches only
   pictures, but on **every** article: keep the key for these two skills alone.
2. It is saved once, for both skills, with the publisher:
   ```
   TAROTS_API_URL=https://tarots.chat/api
   TAROTS_API_KEY=tk_live_…
   python ../tarots-blog-publisher/scripts/tarots_blog.py key save
   ```
   It goes in `~/.tarots-blog/credentials.json` (outside any repository). With **no media key** (neither
   `TAROTS_MEDIA_KEY` nor `~/.tarots-blog/media-credentials.json`), `tarots_images.py` uses that key, read as
   `tarots_blog.py` reads it (`TAROTS_API_KEY`, else the saved file), and says so in a `note:` line. A separate media
   key, if one is set or saved, still wins: `tarots_images.py key clear` forgets an old one; `key show` shows both.
3. Check: `python scripts/tarots_images.py list` and `python scripts/tarots_images.py balance`.

If the key in use lacks the media permission, the server answers **403** and the script says: *this key cannot change
pictures: create in the console (Blog → Keys) ONE key with the three permissions write + publish + media, and save it
with `tarots_blog.py key save`; both skills will use it*. Report that line to the operator: do not look for another
key. Never put a key in a file of a project, a prompt or a message; only its 12-character prefix may appear in output.

(`generate` and `prompt-check` need no key: `tarots-blog-publisher` uses them without one. Only for a prompt that
draws a card, and only when its article is neither in a work folder nor in the titles copy, do they read the article
through the API with the key above, if there is one.)

## Workflow

### 1. Decide the scope with the operator
- Which articles: all, only published, one language, or the ids the operator names. `list --todo` shows what this
  tool has not redone yet. Many covers (all the drafts, say): not in this session, but with the loop of
  "Redo many covers" below, which the operator starts.
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
  `python scripts/tarots_images.py prompt-check --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --alt "<alt>" --article <slug>`
  (`--article` is needed only when the prompt draws a card; giving it always does no harm).

### 4. Try it dry first
```
python scripts/tarots_images.py generate --article <slug> --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --dry-run
```
For the first run with an operator, show the prompts for **three** articles and wait for an ok before generating.

### 5. Generate and swap
```
python scripts/tarots_images.py generate --article <slug> --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --budget <left>
python scripts/tarots_images.py cover <id> <the path generate printed: …/foto/cover.jpg> --alt "<what the picture shows>"

python scripts/tarots_images.py generate --article <slug> --prompt "<prompt>" --kind <other kind> --shot <shot> --light <other light> --setting "<other setting>" --aspect 4:3 --budget <left>
python scripts/tarots_images.py inline <id> --replace 0 <the path generate printed: …/foto/inline-1.jpg> "<alt>"
```
(`cover <id> <file> --dry-run` shows what would change before the real swap.)
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

## Redo many covers: the loop
Each prompt has to be written by a model that read that article, and a model's work degrades over a long session
with many articles. So many covers are redone **only** with `scripts/redo_covers_loop.py`: a deterministic loop,
outside the agent, that starts the agent **once per article**, with a clean context and a short prompt about that
article alone. It is the **only** way allowed to work on many articles; an agent never loops over articles itself.
```
python scripts/redo_covers_loop.py --dry-run                 # the list, and the prompt of the first article
python scripts/redo_covers_loop.py --limit 10 --budget 200   # ten articles at most, 200 credits at most
```
- **What it takes**: `tarots_images.py list --status draft --todo --json` (drafts whose cover was not redone yet),
  minus what its log has as done (and as failed, unless `--retry-failed`).
- **For each article**: `balance` first (it stops if the article could pass `--budget`, or go below `--reserve`; each
  article counts `--cost` 20 credits: a cover and at most one new try), the cover on the site (`show`) and the
  progress record; then the agent, by default `hermes -z "<prompt>" --skills tarots-blog-images` (`--agent-cmd` for
  another one), stopped after `--timeout` minutes (default 15). The prompt (Italian, `--prompt-file` to change it)
  says: read the article with `show`, choose the form with `progress` / `catalog`, write the prompt from the text,
  `generate --article <id>` at 3:2 and 2K, `cover <id> <file> --alt "…"`; no questions, no other article, no script
  of its own; if a step fails, stop and say so.
- **The check, after each article**: the cover on the site must have changed **and** `tarots_images.py cover` must
  have recorded it; anything else (the agent's word included) is a failure. Each article is one line of
  `~/.tarots-blog/loop-covers-log.jsonl` (article, outcome, reason, seconds, credits before and after) and the
  agent's output is kept in `~/.tarots-blog/loop-covers/`.
- **Limits**: `--limit` articles per run (default 10); it stops after 2 failures in a row (`--max-failures`, exit 3).
- **Starting again** goes on from where it stopped: done articles leave `--todo` and are in the log. At the end it
  prints redone, failed and credits spent.
- **The agent inside the loop does one article**: the one in its prompt, cover only, with this skill's commands, and
  then it stops. It never starts the loop itself, never takes another article.
- The operator starts it by hand: `tools/rifai_copertine_bozze.ps1` in the repository (the default values, the
  output saved next to the log).

## Hard rules
- Only pictures: never try to change text, title, SEO fields or status (the key cannot, and should not try).
- **Never a picture of cards** (a card at most as a small detail, and only in an article about that very card). No text in pictures. No recognisable real people, no fake photos of real
  events, no copy of the Thoth deck's actual artwork (copyrighted).
- **Only `tarots_images.py generate`** makes pictures (through `litmedia-skill`). Never `browser-image-gen`, never a
  built-in image tool, never the LitMedia website.
- **Never write your own script** (a loop, a batch, a "publish_sequential" helper) to generate or swap pictures in
  series: one article at a time, with these commands, looking at each result. Many articles: only
  `scripts/redo_covers_loop.py`, started by the operator, one agent run per article.
- Never reuse a picture on two articles; never work around a refusal by renaming a file or padding a prompt.
- Spend only the credits the operator agreed to. Check `balance` when in doubt.
- Never disable TLS verification, never follow a redirect with the key, never send the key anywhere but
  `TAROTS_API_URL`, never send it to LitMedia.

## Files
- `scripts/tarots_images.py`: the CLI (`-h` on every command).
- `scripts/redo_covers_loop.py`: the loop for many covers, one agent run per article (`-h` for the options).
- `references/prompts.md`: cards as context and never as the picture, the four dimensions with their catalogs and
  rules, the house style, examples.
- `references/api.md`: the four endpoints, if you would rather call them directly.
- `tests/test_controlli.py`: offline tests of the picture rules (`python -m pytest tests -q`).
- `tests/test_cartella_e_python.py`: offline tests of the work folder (`--article`, `foto/`) and of the choice of
  the Python that runs LitMedia.
- `tests/test_carta_articolo.py`: offline tests of the card rule (a card only for an article about that very card).
- `tests/test_una_chiave.py`: offline tests of the one key for both skills (the publisher's key, the 403 message).
- `tests/test_ciclo_copertine.py`: offline tests of the loop (fake blog, fake agent: budget, limits, stops, restart,
  log).
