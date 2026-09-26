---
name: tarots-blog-publisher
description: Research a currently relevant esoteric / tarot topic (or the topic the operator names), write an SEO-optimized English article, generate its cover image with LitMedia, and publish it to the TAROTS chat blog through the site's REST API using every SEO field (keyword, meta title and description, slug, tags, FAQ, alt text). Use whenever asked to write, publish, schedule or post a blog article for TAROTS chat / tarots.chat, or to keep the blog fed with timely tarot, Thoth, Golden Dawn, astrology or cartomancy content.
---

# TAROTS chat blog publisher

Publishes one article at a time to the **TAROTS chat** blog (an AI reading service built on the Thoth Tarot) through
its REST API, and makes it as findable as it honestly can be. **International audience, English first**: the default
language is `en`; an Italian article is optional and separate.

Works for any agent that can run a shell command and read files (Hermes, OpenClaw, Claude Code, a cron job).
No dependency beyond Python 3.8+. The script is `scripts/tarots_blog.py` (path below is relative to this skill).

## Setup (once)

1. An editor creates a key in the console: **Blog → Keys**. The key is shown once. Permissions: `blog:write`
   (drafts) or `blog:write` + `blog:publish` (can publish). Ask the operator which one this agent should have.
2. Put it in the environment of the agent, **never in a file, an article, a prompt or a message**:
   ```
   TAROTS_API_URL=https://tarots.chat/api        # the API base of the site
   TAROTS_API_KEY=tk_live_…
   ```
3. Check: `python scripts/tarots_blog.py guide` prints what the key can do and the SEO thresholds.

If `guide` fails with `error: …`, read the message: it says what is wrong (URL, key, network). Do not work around it.

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
| `focus_keyword` | the one phrase; must appear in the SEO title, description, slug, first 100 words, one `##`, cover alt. |
| `secondary_keywords` | up to 10 related phrases, used naturally in the text. |
| `slug` | lowercase-hyphen, ≤ 75 chars and ≤ 9 words, contains the keyword. |
| `tags` | 2–6, reuse existing ones. |
| `section` | a slug from `sections` (or omit). |
| `faq` | 3–5 real questions with 1–3 sentence direct answers (`question`, `answer`); becomes FAQ structured data. |
| `cover_alt` | describes the image; the keyword only if it fits. |
| `language` | `en` (default). |
| `canonical_url` / `noindex` | leave unset unless the operator says the text lives elsewhere / must stay out of search. |

Put the article in a JSON file (see `assets/example-article.json`; friendly English keys are accepted). Put the
Markdown in a file next to it and reference it with `"body_file": "article.md"`, so no quoting problems.

### 6. Cover image with LitMedia
16:9, no text in the image. Follow `references/image-generation.md` (LitMedia skill: cost estimate and consent first,
prompt recipes, never bypass TLS errors). Save the result as a PNG/JPEG/WebP file. If image generation is not
possible, continue without a cover and say so in the report: an article without an image is better than a stalled one.

### 7. Check, fix, repeat
```
python scripts/tarots_blog.py check article.json
```
Prints a score 0–100 and a list `FIX` (errors), `WARN` (improvements). Fix the items and re-run. **Stop at ≥ 85 with
no `FIX`**, or after 4 rounds. The score measures good practice, not ranking: never stuff keywords or pad the text
to push a number. Meanings of each check: `references/seo-checklist.md`.

### 8. Publish
```
python scripts/tarots_blog.py post article.json --cover cover.png
```
`post` re-checks, refuses to save below 85, uploads the cover, creates the article, and prints the URL.
- `"status": "draft"` (the default) saves a draft an editor can publish. Use `"status": "published"` **only if the
  operator's instructions say to publish**. With a key that lacks `blog:publish` the server saves a draft anyway and
  prints a `note:`; report it, don't try to get around it.
- `"publish_at": "2026-10-12T08:00:00Z"` (with `published`) schedules the article for that time.
- On a network error or timeout **do not simply run `post` again**: run `mine` first, the article may exist.
- `--save-anyway` keeps a below-85 article as a draft for a human. Use it only when told to.

### 9. Report
Answer in a few lines: title, primary keyword, final SEO score, status, URL, cover yes/no, and anything an editor
must look at (`note:` lines, unverified claims you removed). Do not paste the key or the article body.

## Hard rules
- The key stays in the environment. Never print it, log it, commit it, or send it anywhere except `TAROTS_API_URL`.
- Never disable TLS verification and never follow a redirect with the key. Fix the URL instead.
- Publish only what you would put your name to: original, verified, no invented facts.
- One article per run unless asked. The key has a daily limit (`guide` shows it); a `429` means stop, not retry.
- Never edit or delete anything you did not create: the API refuses it, and you should not try.
- Do not mass-produce near-duplicate articles for keyword variants: one page per intent.

## Files
- `scripts/tarots_blog.py`: the CLI (`-h` for every command).
- `references/api.md`: the REST endpoints, fields and errors, if you would rather call the API directly.
- `references/keywords.md`: keyword clusters per page, competitors, topic calendar, on-page rules.
- `references/seo-checklist.md`: every check the server runs and how to satisfy it.
- `references/image-generation.md`: LitMedia commands and prompt recipes for the cover.
- `assets/example-article.json` + `assets/example-article.md`: the shape of an article (abridged, not a template
  to copy: a real article is 800+ words and its own).
