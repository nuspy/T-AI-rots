---
name: tarots-blog-publisher
description: Write one SEO-optimized English article and publish it on the TAROTS chat (tarots.chat) site's OWN blog, through the site's own REST API with this skill's script `tarots_blog.py` (draft, publish, schedule, update or delete a draft), using every SEO field (keyword, meta title and description, slug, tags, FAQ, alt text). Pictures come from the tarots-blog-images skill (LitMedia, never cards). Use whenever asked to write, publish, schedule, edit or post an article on the TAROTS chat blog, or to keep that blog fed with timely tarot, Thoth, Golden Dawn or astrology content. This is not a social media or scheduling tool; it does not post to Postiz, SocialClaw, WordPress, Medium or any social network, and those tools never publish this blog.
---

# TAROTS chat blog publisher

Publishes one article at a time to the **TAROTS chat** blog (an AI reading service built on the Thoth Tarot) through
its REST API, and makes it as findable as it honestly can be. **International audience, English first**: the default
language is `en`; an Italian article is optional and separate.

Works for any agent that can run a shell command and read files (Hermes, OpenClaw, Claude Code, a cron job).
No dependency beyond Python 3.8+. The script is `scripts/tarots_blog.py` (path below is relative to this skill).

## Which skill does what
| Skill | Its job for the blog |
|---|---|
| **`tarots-blog-publisher`** (this one) | researches, writes and publishes the article on the blog of tarots.chat, through the site's REST API and `scripts/tarots_blog.py`; edits and deletes the drafts it created |
| **`tarots-blog-images`** | generates every picture of the blog — this skill's cover and inline pictures too — with `tarots_images.py generate`, and swaps the pictures of existing articles |
| **`litmedia-skill`** | the image engine (LitMedia API, Seedream 5.0). It is called **by** `tarots_images.py`: never call it directly for the blog |
| Postiz, SocialClaw, `browser-image-gen` | **not used for the blog**, ever. Postiz and SocialClaw post to social networks (their "posts" on WordPress or Medium are not this blog); `browser-image-gen` drives a browser and is meant for the tarot-deck skill only |

If the operator asks to "post", "publish" or "schedule" an article for TAROTS chat, it means this skill and this
script: there is no other target to choose or ask about.

## Setup (once per key, not once per run)

1. An editor creates a key in the console: **Blog → Keys**. The key is shown once. Permissions: `blog:write`
   (drafts) or `blog:write` + `blog:publish` (can publish). Ask the operator which one this agent should have.
2. Put it in the environment for this run only:
   ```
   TAROTS_API_URL=https://tarots.chat/api        # the API base of the site
   TAROTS_API_KEY=tk_live_…
   ```
   The **first** run with nothing saved yet remembers both, in `~/.tarots-blog/credentials.json` — a file
   outside any repository, never inside this project, `chmod 600` where the OS supports it. Every run after
   that needs neither variable: omit them and the saved ones are used automatically (a one-line `note:` on
   stderr says so, every time, so it is never silently invisible).
3. Check: `python scripts/tarots_blog.py guide` prints what the key can do and the SEO thresholds.

If `guide` fails with `error: …`, read the message: it says what is wrong (URL, key, network). Do not work around it.

### Given a new key when one is already saved

Never swapped in silently. If `TAROTS_API_KEY` is set to a key that differs from the one already saved, every
command refuses with an error naming both by prefix and asks for one of three explicit choices:
- `python scripts/tarots_blog.py key show` — compare the saved key's prefix against the new one first.
- `python scripts/tarots_blog.py key save` — replace the saved key with the one in `TAROTS_API_KEY` now.
- unset `TAROTS_API_KEY` — keep using the saved key, untouched.

`python scripts/tarots_blog.py key clear` forgets the saved key entirely (a bare `guide` or any other command then
falls back to needing `TAROTS_API_KEY` set, as on a first run). Only the 12-character prefix is ever shown or
printed — never the full key — matching how the console lists keys.

## Workflow

Do the steps in order. Nothing is public until step 8, and only if the operator wants it published.

### 1. Learn what exists
```
python scripts/tarots_blog.py sections      # slug of a section for the article
python scripts/tarots_blog.py tags          # reuse tags, don't invent near-duplicates
python scripts/tarots_blog.py mine          # what this key already wrote: no repeated topic or keyword
python scripts/tarots_blog.py catalog --grep tower   # link shortcuts for cards and spreads
```

### 2. Choose the topic
- **The operator named a topic** → use it exactly, and find the keyword around it.
- **Otherwise** pick something esoteric that is timely *now*: an astronomical or seasonal moment (equinox, solstice,
  full/new moon, eclipse, retrograde), a cultural moment, a trend people are searching (shadow work, tarot
  journaling, pick-a-card vs real spreads), or a Thoth / Golden Dawn evergreen. `references/keywords.md` has the
  keyword map and a calendar to start from.
- **Verify every date and astronomical claim** with a source you actually opened before writing it. If you cannot
  verify it, drop the claim or the topic.
- One primary keyword per article, not used by anything in `mine`. Prefer a specific, answerable phrase
  ("The Tower tarot card meaning in the Thoth deck") over a head term ("tarot").

### 3. Outline for search intent
- The first 100 words answer the question directly and contain the primary keyword.
- 3–6 `##` sections, at least one with the keyword or a close variant; question-style headings when natural.
- Plan 2–5 internal links (cards, spreads, other posts), at least one reputable external source, 3–5 FAQ items.

### 4. Write the article (original, expert, useful)
- English, **800+ words** (300 is the hard minimum), short sentences (average ≤ 24 words), Markdown, no HTML.
  Do **not** write an `# H1`: the page title is the H1. Sections start at `##`.
- Write it yourself from what you know and verified. Never copy or closely paraphrase another site; never invent a
  quote, statistic, source, or "study". Attribute Crowley, Harris, the Golden Dawn correctly, and say when something
  is a modern interpretation.
- Internal links inside sentences with shortcuts: `[[card:the-tower]]`, `[[spread:celtic-cross]]`,
  `[[post:some-existing-slug]]` (a card or spread on its own line becomes a card with its picture). Take the exact
  shortcut from `catalog`. An unknown reference disappears silently, so copy, don't guess.
- **Inline images — decide explicitly, don't silently skip**: for every article, actively decide whether a scene
  from the text, an abstract picture of a spread's positions (lights, stones, a constellation: never cards) or a
  close-up of a symbol would genuinely help — most articles about a spread or a specific symbol do benefit from one.
  If yes, generate it with `tarots_images.py generate --aspect 4:3` (step 6; a different kind of picture from the
  cover), upload it with `python scripts/tarots_blog.py upload work/<slug>-1.jpg --for <slug>`, then paste the
  printed `url` into the body as ordinary Markdown: `![alt text](url)`. One is normally enough, not one per paragraph. State the decision either
  way in the step 9 report.
- **Inline video**: a line on its own with `[[video:youtube:VIDEO_ID]]` (11-character id from the URL, e.g.
  `dQw4w9WgXcQ`) or `[[video:vimeo:VIDEO_ID]]` (the number in the Vimeo URL) embeds that video. No other host —
  the site doesn't run its own video hosting. Use only a real, relevant, existing video (a tradition's own
  explainer, a museum/library recording) — never invent one.
- **Image captions**: put the caption in the image title — `![alt text](url "The caption under the picture")`.
  Alt describes the picture for who can't see it; the caption says why it is there.
- **Rich text (sparingly)**: `:text[a phrase]{color=brass}` / `{color=plum}` / `{color=verdigris}` /
  `{color=muted}`, `:text[bigger]{size=large}` (`small`, `large`, `title`), both together
  `:text[…]{color=plum size=large}`, and `:underline[…]`. Only these values exist (the site's palette): anything
  else is ignored, and no HTML ever runs. One or two highlights per article at most — emphasis that is everywhere
  is emphasis nowhere; `**bold**` is still the default.
- Voice: warm and precise, reflective rather than prophetic. Tarot is a tool for reflection here: no promises about
  the future, no health, legal, money or "he will/won't love you" verdicts, no fear-mongering. For relationship
  topics offer questions and perspectives, never a verdict on a person or a couple.
- Mention the service only where it is really useful (a spread the reader can try), once or twice, no hard sell.

### 5. Fill the SEO fields
| Field | Rule |
|---|---|
| `title` | ≤ 200; the page H1. Clear and specific. |
| `seo_title` | **30–60 chars**, keyword near the start. |
| `seo_description` | **120–160 chars**, keyword once, a promise and a reason to click. |
| `focus_keyword` | the one phrase; must appear in the SEO title, description, slug, first 100 words, one `##`; in the cover alt only if the picture really shows it (otherwise accept that one warning). |
| `secondary_keywords` | up to 10 related phrases, used naturally in the text. |
| `slug` | lowercase-hyphen, ≤ 75 chars and ≤ 9 words, contains the keyword. |
| `tags` | 2–6, reuse existing ones. |
| `section` | a slug from `sections` (or omit). |
| `faq` | 3–5 real questions with 1–3 sentence direct answers (`question`, `answer`); becomes FAQ structured data. |
| `cover_alt` | describes what is in the picture; the keyword only if it fits; never "tarot cards" (there are none). |
| `language` | `en` (default). |
| `canonical_url` / `noindex` | leave unset unless the operator says the text lives elsewhere / must stay out of search. |

Put the article in a JSON file (see `assets/example-article.json`; friendly English keys are accepted). Put the
Markdown in a file next to it and reference it with `"body_file": "article.md"`, so no quoting problems.

### 6. Cover image (and the inline picture)
3:2, no text in the image, **no card of any kind** — not a spread, not a deck, not one small card as a detail.
**Its own subject, taken from this article's text**, and a different kind of picture from the last ones on the blog.
The blog's covers had to be redone twice for breaking this. Read `tarots-blog-images/references/prompts.md` (the
rules, the kinds of picture, the house style, examples) and write the prompt after the article, naming something
concrete from it.

Generate **only** with the `tarots-blog-images` skill's script, which calls `litmedia-skill` (Seedream 5.0, 2K,
10 credits a picture) and checks the prompt first (no cards, a concrete scene, not a repeat of an earlier picture):
```
python ../tarots-blog-images/scripts/tarots_images.py prompt-check --prompt "<prompt>" --alt "<cover alt>"
python ../tarots-blog-images/scripts/tarots_images.py generate --prompt "<prompt>" --out work/<slug>-cover.jpg
python ../tarots-blog-images/scripts/tarots_images.py generate --prompt "<other prompt>" --aspect 4:3 --out work/<slug>-1.jpg
```
- The path is relative to this skill's folder: the two skills are normally installed side by side (`skills/`,
  `~/.claude/skills/`, `~/.agents/skills/`, `%LOCALAPPDATA%/hermes/skills/`). If they are not, find the other one
  by its folder name `tarots-blog-images` in the agent's skills directories and use its `scripts/tarots_images.py`.
  If it is not installed, say so and publish without pictures: do not make them another way.
- Then the file goes to `tarots_blog.py post article.json --cover work/<slug>-cover.jpg` (the cover) or
  `tarots_blog.py upload work/<slug>-1.jpg --for <slug>` (an inline picture, step 4).
- `post --cover` and `upload` check the picture against the same record as `tarots_images.py`
  (`~/.tarots-blog/images-progress.json`, or `TAROTS_IMAGES_PROGRESS`) **before uploading anything**, and refuse it
  (exit 7) if:
  - it was **not made by `tarots_images.py generate`** — unless the operator supplied this very picture: then add
    `--operator-image` (accepted with a warning; never for a picture you made some other way);
  - it is **already used by another article** (same bytes, whatever the file name);
  - the prompt it was generated from asks for a card.
- After a successful `post` the cover is recorded with the new article; after `upload` the picture is recorded
  with the `--for` slug or id (without `--for` it is tied to that upload alone and can never be used again). Always
  pass `--for`.
- **Never** `browser-image-gen`, never the LitMedia website, never the agent's own image tool, never `ai_image.py`
  of `litmedia-skill` called directly.
- Cost and consent first (10 credits a picture). Never bypass TLS errors. Look at every picture before using it.
- If a picture cannot be made (LitMedia down, no credits, the prompt keeps being refused), continue without it and
  say so in the report: an article without an image is better than a stalled one, or than a card picture.

To change the pictures of articles that already exist (yours or others'), use the **`tarots-blog-images`** skill:
it has its own key with the `blog:media` permission.

### 7. Check, fix, repeat
```
python scripts/tarots_blog.py check article.json
```
Prints a score 0–100 and a list `FIX` (errors), `WARN` (improvements). Fix the items and re-run. **Stop at ≥ 85 with
no `FIX`**, or after 4 rounds. The score measures good practice, not ranking: never stuff keywords or pad the text
to push a number. Meanings of each check: `references/seo-checklist.md`.

### 8. Publish
**The publishing target is always the TAROTS chat blog itself, through this one script and its REST API — never a
social platform, a CMS, or any other publishing/scheduling tool you may also have available** (Postiz, SocialClaw,
WordPress, Medium, a social scheduler, a generic "publish" skill). If you have such a tool loaded, ignore it for
this task: it does not apply here, and there is no other target to ask the operator about.
```
python scripts/tarots_blog.py post article.json --cover cover.png
```
`post` re-checks, refuses to save below 85, uploads the cover, creates the article, and prints the URL.
- `"status": "draft"` (the default) saves a draft an editor can publish. Use `"status": "published"` **only if the
  operator's instructions say to publish**. With a key that lacks `blog:publish` the server saves a draft anyway and
  prints a `note:`; report it, don't try to get around it.
- `"publish_at": "2026-10-12T08:00:00Z"` (with `published`) schedules the article for that time.
- On a network error or timeout **do not simply run `post` again**: run `mine` first, the article may exist.
- `--save-anyway` keeps a below-85 article as a draft for a human. Use it **only when the operator asked for it
  for this very article**; never as a habit, never for a series. A low score means: fix the article (step 7).

### 9. Report
Answer in a few lines: title, primary keyword, final SEO score, status, URL, cover yes/no, **inline image yes/no and
why**, and anything an editor must look at (`note:` lines, unverified claims you removed). Do not paste the key or
the article body.

## Edit an existing article
`tarots_blog.py` can change and delete **only the articles this key created** (`mine` lists them; for any other
article the API answers `404`, the same as "does not exist").

```
python scripts/tarots_blog.py mine                       # find the id
python scripts/tarots_blog.py update <id> patch.json     # change some fields
python scripts/tarots_blog.py delete-draft <id>          # delete a draft
```
- `patch.json` holds **only the fields to change**, with the same names as an article file (`title`, `subtitle`,
  `body` or `body_file`, `language`, `section`, `tags`, `slug`, `seo_title`, `seo_description`, `focus_keyword`,
  `secondary_keywords`, `faq`, `cover_alt`, `cover_image_id`, `canonical_url`, `noindex`, `status`
  (`draft|published|archived`), `publish_at`, `featured`). An unknown field is an error. `body`/`body_file`
  replaces the **whole** text; `tags`, `faq` and `secondary_keywords` replace the whole list.
- There is **no dry run and no score gate** on `update`: the change is saved, then the SEO report is printed. Run
  `check` on the full article first. A `dry_run` field in the patch is refused (the server would ignore it and
  save).
- Without `blog:publish`: an article that is already published or archived cannot be changed (`403`), and
  `status: published|archived`, `publish_at` or `featured` in the patch are ignored with a `note:`.
- `delete-draft` deletes **drafts only** (`409` otherwise); a published article is archived from the console.
- Pictures of an existing article (cover or inline): use the **`tarots-blog-images`** skill (`cover`, `inline`),
  not `update` with a new `cover_image_id`, so the picture rules and the record of used pictures apply.

## Hard rules
- The key lives in the environment or in the local cache file described above — **never** in a project file, an
  article, a prompt or a message. Never print the full key, log it, commit it, or send it anywhere except
  `TAROTS_API_URL`; only its 12-character prefix (`tk_live_ab12…`) may ever appear in output.
- Never disable TLS verification and never follow a redirect with the key. Fix the URL instead.
- Publish only what you would put your name to: original, verified, no invented facts.
- **One article per run**, unless the operator explicitly asks for more; even then, one after the other with this
  skill's commands, each one researched, written, checked and illustrated on its own. The key has a daily limit
  (`guide` shows it); a `429` means stop, not retry.
- **Never write your own script** (a loop, a batch, a "publish_sequential" or "generate_articles" helper) that
  writes, generates pictures for or publishes articles in series. Run this skill's commands by hand.
- **No card of any kind in any picture.** Pictures only from `tarots_images.py generate` (LitMedia), never from
  `browser-image-gen` or a built-in image tool. **Never reuse the cover (or any picture) of another article.**
  `--operator-image` only for a picture the operator supplied; never to get around a refusal.
- `--save-anyway` only when the operator asked for it for that article.
- Never edit or delete anything you did not create: the API refuses it, and you should not try.
- Do not mass-produce near-duplicate articles for keyword variants: one page per intent.
- Postiz, SocialClaw and other social or scheduling tools are not part of this job.

## Files
- `scripts/tarots_blog.py`: the CLI (`-h` for every command).
- `references/api.md`: the REST endpoints, fields and errors, if you would rather call the API directly.
- `references/keywords.md`: keyword clusters per page, competitors, topic calendar, on-page rules.
- `references/seo-checklist.md`: every check the server runs and how to satisfy it.
- `references/image-generation.md`: how the cover and inline pictures are made (only through `tarots-blog-images`).
- `assets/example-article.json` + `assets/example-article.md`: the shape of an article (abridged, not a template
  to copy: a real article is 800+ words and its own).
- `../tarots-blog-images/`: the picture skill (`scripts/tarots_images.py`, `references/prompts.md`).
- `tests/test_immagini.py`: offline tests of the picture checks of `post --cover` and `upload`.
