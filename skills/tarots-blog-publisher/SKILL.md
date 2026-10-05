---
name: tarots-blog-publisher
description: Write one SEO-optimized English article and publish it on the TAROTS chat (tarots.chat) site's OWN blog, through the site's own REST API with this skill's script `tarots_blog.py` (draft, publish, schedule, update or delete a draft), using every SEO field (keyword, meta title and description, slug, tags, FAQ, alt text). Pictures come from the tarots-blog-images skill (LitMedia, never a picture of cards). Use whenever asked to write, publish, schedule, edit or post an article on the TAROTS chat blog, or to keep that blog fed with timely tarot, Thoth, Golden Dawn or astrology content. This is not a social media or scheduling tool; it does not post to Postiz, SocialClaw, WordPress, Medium or any social network, and those tools never publish this blog.
---

# TAROTS chat blog publisher

Publishes one article at a time to the **TAROTS chat** blog (an AI reading service built on the Thoth Tarot) through
its REST API, and makes it as findable as it honestly can be. **International audience, English first**: the default
language is `en`; an Italian article is optional and separate.

Works for any agent that can run a shell command and read files (Hermes, OpenClaw, Claude Code, a cron job), also
through `execute_code` with `subprocess`. No dependency beyond Python 3.8+. The script is `scripts/tarots_blog.py`
(paths below are relative to this skill's folder).

## Which skill does what
| Skill | Its job for the blog |
|---|---|
| **`tarots-blog-publisher`** (this one) | researches, writes and publishes the article on the blog of tarots.chat, through the site's REST API and `scripts/tarots_blog.py`; edits and deletes the drafts it created |
| **`tarots-blog-images`** | generates every picture of the blog — this skill's cover and inline pictures too — with `tarots_images.py generate`, and swaps the pictures of existing articles |
| **`litmedia-skill`** | the image engine (LitMedia API, Seedream 5.0). It is called **by** `tarots_images.py`: never call it directly for the blog |
| Postiz, SocialClaw, `browser-image-gen` | **not used for the blog**, ever. Postiz and SocialClaw post to social networks (their "posts" on WordPress or Medium are not this blog); `browser-image-gen` drives a browser and is meant for the tarot-deck skill only |

If the operator asks to "post", "publish" or "schedule" an article for TAROTS chat, it means this skill and this
script: there is no other target to choose or ask about.

## Setup: run `guide` first, never ask for a key
**Start every run with `python scripts/tarots_blog.py guide`, before asking anything.** If it prints the key's
permissions (`note: using the saved key (prefix tk_live_…)`), the key and the URL are already saved: everything is
set, go on and **never ask the operator for a key or a URL**. `guide` also prints today's date (`note: today is …`):
use it for every "timely" decision. Only if `guide` fails with a message about a missing key, follow
`references/setup.md` (first setup, and what to do when a different key is offered).

## The work folder: the only place for this article's files
```
python scripts/tarots_blog.py new "samhain tarot spread"
```
creates `~/.tarots-blog/work/<YYYY-MM-DD>-<slug>/` (or under `TAROTS_WORK_DIR`) and prints its absolute paths:
- `article.json` — the fields, with every SEO field empty, `"status": "draft"`, `"body_file": "article.md"`;
- `article.md` — the text, empty;
- `foto/` — every picture of this article (cover and inline), where `tarots_images.py generate --article <slug>`
  saves them;
- `.checks` — written by `check`: its rounds (do not edit it).

Rules:
- The article's files live **only** there: **never** in this skill's folder, never in a repository, never in the
  current directory. `check` and `post` refuse an article.json inside the skill's folder.
- Every command takes the **slug** (or the folder, or the path) instead of a path: `check samhain-tarot-spread`,
  `post samhain-tarot-spread --cover cover.jpg`. A bare picture name is looked for in `foto/`.
- If a command says the article is not found, its message names the work folder and lists the newest ones.
  **Never search the disk** (`os.walk`, `dir /s`, `find /`) for an article file.

## The whole run, command by command
This is the sequence for one article. Follow it in this order.
```
python scripts/tarots_blog.py guide                                        # 1. key ok? today's date
python scripts/tarots_blog.py titles --grep samhain                         # 2. what exists around the topic
python scripts/tarots_blog.py topic-check "samhain tarot spread" --lang en  #    the keyword: FREE / CLOSE ok, TAKEN = choose another
python scripts/tarots_blog.py new "samhain tarot spread"                     # 3. the work folder (prints the paths)
#  4. write article.md and fill article.json, in the folder printed by `new`
python scripts/tarots_blog.py catalog --grep death                          # 5. link shortcuts for the cards/spreads named
python scripts/tarots_blog.py tags                                          #    tags to reuse
python scripts/tarots_blog.py check samhain-tarot-spread                    # 6. score + NEXT; fix only NEXT; at most 4 rounds
python ../tarots-blog-images/scripts/tarots_images.py progress              # 7. pictures: what form is free
python ../tarots-blog-images/scripts/tarots_images.py generate --article samhain-tarot-spread --kind landscape --shot wide --light blue-hour --setting "Irish hillside" --prompt "…"
#                                                                              → foto/cover.jpg
python scripts/tarots_blog.py post samhain-tarot-spread --cover cover.jpg   # 8. re-check, upload the cover, save (draft)
```
Then the report (step 9).

## Workflow

### 1. Learn what exists
- `titles` lists the **whole blog** (every key and the console), one line each: `slug | title | keyword | lang |
  status | date`, newest first. Filter it (`--grep TEXT`, `--lang en`, `--section SLUG`, `--status draft`); it keeps
  a local copy and fetches only what changed. `sections` and `tags` list what to reuse.
- `mine` lists only what **this key** created, with ids: use it to find an article to `update`.
- **Never download or read whole articles to choose a topic**: titles, slugs and keywords are enough.

### 2. Choose the topic and the focus keyword — before writing a word
- **The operator named a topic** → use it exactly, and find the keyword around it.
- **Otherwise** something esoteric that is timely *now*: an astronomical or seasonal moment, a cultural moment, a
  trend, or a Thoth / Golden Dawn evergreen (`references/keywords.md` has the keyword map and a calendar).
- **Timely means within the next 14 days of today's date** (`guide` prints it). A date that has passed is not a hook:
  an "autumn equinox" article two weeks after the equinox is late. **Verify every date and astronomical claim**
  with a page you actually open (an observatory, an almanac, an encyclopedia). If you cannot verify it, drop it.
- **The focus keyword** is the phrase a person would really type into a search engine, in natural word order,
  **2–5 words**, specific and answerable. It is the phrase you pass to `topic-check`; the text is then written
  around it. Never paste it into a title or at the end of a sentence only to make it appear.
  - Bad (seen): topic "autumn equinox", keyword `balance tarot meditation autumn` — nobody searches that word salad;
    it never appeared in the text, so it was pasted into the H1 ("…Balance: balance tarot meditation autumn"):
    keyword stuffing.
  - Good: `mabon tarot spread`, chosen first, checked with `topic-check`, and the opening written around it: "A
    Mabon tarot spread is a five-card reading for the autumn equinox, when day and night are equal…".
  - `check` and `post` refuse a keyword of more than 6 words or with a repeated word (exit 9), and one another
    article already has (exit 8, the `topic-check` comparison).
- **Check the keyword (and the proposed title) against the whole blog**:
  `python scripts/tarots_blog.py topic-check "mabon tarot spread" --lang en`. It prints the 5 closest articles and:
  - `TAKEN` (exit 8): the same slug, keyword or title, or score ≥ 0.88. **Do not write it.** Choose another topic;
    if the operator named this one, tell them it exists (they may want it updated).
  - `CLOSE` (0.40–0.88): write it **only if the search intent is really different** (a different question, reader
    or use), and say so in the report, naming the close article.
  - `FREE` (< 0.40): go ahead.
  On a server without `GET /titles` both commands warn that only this key's articles are compared: say so.

### 3. Outline for search intent
- The first 100 words answer the question directly and contain the focus keyword.
- 3–6 `##` sections, one with the keyword; question-style headings when natural.
- Plan 2–5 internal links, at least one reputable external source, 3–5 FAQ items.

### 4. Write the article (original, expert, useful)
- In `article.md` of the work folder. English, **800+ words** (300 is the hard minimum), short sentences (average
  ≤ 24 words), Markdown, no HTML. **No `# H1`**: sections start at `##`.
- Write it yourself from what you know and verified. Never copy or closely paraphrase another site; never invent a
  quote, statistic, source or "study". Attribute Crowley, Harris, the Golden Dawn correctly, and say when something
  is a modern interpretation.
- Internal links inside sentences with the exact shortcuts from `catalog`: `[[card:the-tower]]`,
  `[[spread:celtic-cross]]`, `[[post:slug]]`. Inline picture (decide explicitly, say it in the report), captions,
  video and coloured text: `references/writing.md`.
- Voice: warm and precise, reflective rather than prophetic. No promises about the future, no health, legal, money
  or "he will/won't love you" verdicts, no fear-mongering. Mention the service once or twice where useful, no hard sell.

### 5. Fill the SEO fields (article.json)
| Field | Rule |
|---|---|
| `title` | ≤ 200; the page H1. Clear and specific. |
| `seo_title` | **30–60 chars**, keyword at the start. |
| `seo_description` | **120–160 chars**, keyword once, a promise and a reason to click. |
| `focus_keyword` | the phrase of step 2; in the SEO title, description, slug, first 100 words, one `##`; in the cover alt only if the picture really shows it. |
| `secondary_keywords` | up to 10 related phrases, used naturally in the text. |
| `slug` | lowercase-hyphen, ≤ 75 chars and ≤ 9 words, contains the keyword. |
| `tags` | 2–6, reuse existing ones (`tags`). |
| `section` | a slug from `sections` (or leave it out). |
| `faq` | 3–5 real questions with 1–3 sentence direct answers (`question`, `answer`). |
| `cover_alt` | what is in the picture; never a spread; a card only if the picture really shows one. |
| `language` | `en` (default). |
| `canonical_url` / `noindex` | leave unset unless the operator says so. |

`assets/example-article.json` + `.md` show the shape (abridged, not a template to copy).

### 6. Pictures: cover and inline
3:2 cover, no text in the image, **never a picture of cards** (cards only as context), its own subject from this
article, in a form that differs from the last pictures. Made **only** by the `tarots-blog-images` skill:
```
python ../tarots-blog-images/scripts/tarots_images.py progress
python ../tarots-blog-images/scripts/tarots_images.py prompt-check --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --alt "<cover alt>"
python ../tarots-blog-images/scripts/tarots_images.py generate --article <slug> --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>"
```
`--article <slug>` saves into the work folder's `foto/`: `cover.jpg` for a 3:2 picture, `inline-1.jpg`… for
`--aspect 4:3`; it never overwrites a file. Then `post <slug> --cover cover.jpg`, and for an inline picture
`upload inline-1.jpg --for <slug>` (prints the url for `![alt](url)`). Prompt rules, the four dimensions, what
`post --cover` and `upload` refuse (exit 7), cost and consent: `references/image-generation.md`. If the other skill
is not next to this one, find its folder `tarots-blog-images` among the agent's skills; if it is not installed, or
LitMedia fails, say so (attended run: publish without pictures; unattended: see below). Never another image tool.

### 7. Check: fix only what NEXT says, at most 4 rounds
```
python scripts/tarots_blog.py check <slug>
```
It prints the score 0–100, the open items (`FIX` errors, `WARN` improvements) and then
**`NEXT — fix only these, do not rewrite the rest`**: one instruction per item, with the real values, e.g.
`seo_title is 76 chars: cut it to ≤ 60, keyword first: current = "…"`, `the keyword "…" is not in the first 100
words: edit ONLY the first paragraph and put the exact phrase in it`, `no internal links: run catalog --grep <word>
and put 2 of the printed shortcuts in sentences`. Items under "No action needed now" (no cover yet, keyword in the
alt) are left as they are.
- **Change only the lines NEXT names** (one field in article.json, one paragraph or one heading in article.md).
  **Never rewrite or regenerate the whole text**: what passed stays as it is.
- `PASS` (score ≥ 85 and no `FIX`): stop polishing and go on.
- The rounds are counted (`.checks`). Rounds 1–4 below the score exit 3 with NEXT. **The 5th `check` still below
  85 prints `STOP` and exits 10**: do not save, no `post`, no `--save-anyway`, no other rewrite; end the run and
  report it. From then on `check` and `post` refuse that article (only the operator can reopen it).
- The score measures good practice, not ranking: never stuff keywords or pad the text. Meanings of each check:
  `references/seo-checklist.md`.

### 8. Publish
The target is always the TAROTS chat blog through this script — never a social platform, a CMS or another
publishing tool you may have loaded.
```
python scripts/tarots_blog.py post <slug> --cover cover.jpg
```
`post` re-checks, refuses to save below 85 or with a `FIX` (and prints NEXT), uploads the cover, creates the article
and prints the URL.
- `"status": "draft"` (the default) saves a draft an editor can publish. `"status": "published"` **only if the
  operator's (or the job's) instructions say to publish**; `"publish_at": "2026-10-12T08:00:00Z"` schedules it. With
  a key that lacks `blog:publish` the server saves a draft anyway and prints a `note:`: report it.
- On a network error or timeout **do not simply run `post` again**: run `mine` first, the article may exist.
- `--save-anyway` keeps a below-85 article as a draft for a human: **only when the operator asked for it for this
  very article**, never after a STOP, never as a habit.

### 9. Report
A few lines: title, focus keyword, the `topic-check` verdict (for `CLOSE`: the close article and why the intent
differs), final SEO score and number of `check` rounds, status, URL, cover yes/no, **inline image yes/no and why**,
the **work folder path**, and anything an editor must look at (`note:` lines, claims you removed). Never the key,
never the article body.

## Unattended runs (a scheduled job, no operator watching)
- **Ask nothing.** `guide` gives the key's state and today's date; the job's instructions give the rest. A missing
  key is a failure to report, not a question.
- **Topic**: chosen with `topic-check`, preferring this week's events (dates verified on a page you open, within
  the next 14 days) or an evergreen; never one `TAKEN`.
- **One article per run.** Status `draft`, unless the job's instructions say `published`.
- The job's instructions are the operator's standing ok for this article's pictures: a cover and at most one inline
  picture (10 credits each); pass the job's budget with `--budget` if it sets one.
- **If a step fails, nothing is saved**: `guide` errors, `topic-check` leaves no free topic, LitMedia fails (no
  cover), the keyword is refused, `check` says `STOP` (exit 10), `post` refuses. Do not retry in a loop, do not use
  `--save-anyway`; write the report with the reason and the work folder path.
- `ModuleNotFoundError: requests` from LitMedia: `tarots_images.py` now finds a Python that has LitMedia's
  dependencies by itself; if there is none it exits 5 naming the `pip install -r …requirements.txt` command and the
  interpreter: report that line, do not install anything.
- The final report is the one of step 9, with the work folder path.

## Exit codes of `tarots_blog.py`
`0` ok · `2` usage, article file missing/unfilled/in the skill folder · `3` below the score or a `FIX` left (nothing
saved) · `4` the API refused · `5` configuration (key, URL) · `7` a picture rule refused the file · `8` topic or
keyword TAKEN · `9` the focus keyword is not a search phrase (> 6 words, a repeated word) · `10` STOP after 4 rounds.

## Edit an existing article
`mine`, `update <id> patch.json`, `delete-draft <id>`: only articles this key created. Details and limits:
`references/editing.md`. Pictures of existing articles: the `tarots-blog-images` skill.

## Hard rules
- The key lives in the environment or in the local cache file — **never** in a project file, an article, a prompt
  or a message. Only its 12-character prefix may ever appear in output. Never disable TLS verification, never follow
  a redirect with the key.
- Article files only in the work folder made by `new`; never in the skill's folder or a repository; never search
  the disk for them.
- Publish only what you would put your name to: original, verified, no invented facts.
- **One article per run**, unless the operator explicitly asks for more; even then one after the other, each
  researched, written, checked and illustrated on its own. A `429` means stop, not retry.
- **Never write your own script** (a loop, a batch, a "publish_sequential" or "generate_articles" helper) that
  writes, illustrates or publishes articles in series. Running this skill's commands through `execute_code` /
  `subprocess` one at a time is fine.
- **Never a picture of cards**; pictures only from `tarots_images.py generate`; never reuse a picture of another
  article; `--operator-image` only for a picture the operator supplied.
- `--save-anyway` only when the operator asked for it for that article; never after a STOP.
- Never edit or delete anything you did not create.
- One page per search intent: every topic goes through `topic-check` first (`TAKEN` = do not write it).
- Postiz, SocialClaw and other social or scheduling tools are not part of this job.

## Files
- `scripts/tarots_blog.py`: the CLI (`-h` for every command).
- `references/setup.md`: first setup of the key, a new key when one is saved.
- `references/writing.md`: links, inline picture, captions, video, coloured text.
- `references/seo-checklist.md`: every check the server runs and how to satisfy it.
- `references/keywords.md`: keyword clusters, competitors, topic calendar, on-page rules.
- `references/image-generation.md`: how the cover and inline pictures are made (only through `tarots-blog-images`).
- `references/editing.md`: `update` and `delete-draft`.
- `references/api.md`: the REST endpoints, fields and errors.
- `assets/example-article.json` + `assets/example-article.md`: the shape of an article (abridged).
- `../tarots-blog-images/`: the picture skill (`scripts/tarots_images.py`, `references/prompts.md`).
- `tests/`: offline tests (pictures, titles and topic-check, work folder, NEXT, keyword, rounds).
