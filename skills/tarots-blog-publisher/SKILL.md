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
| **`tarots-blog-publisher`** (this one) | researches, writes and publishes the article on the blog of tarots.chat, through the site's REST API and `scripts/tarots_blog.py`; edits and deletes the articles the operator names (any draft; published ones with `blog:publish`) |
| **`tarots-blog-images`** | generates every picture of the blog — this skill's cover and inline pictures too — with `tarots_images.py generate`, and swaps the pictures of existing articles |
| **`litmedia-skill`** | the image engine (LitMedia API, Seedream 5.0). It is called **by** `tarots_images.py`: never call it directly for the blog |
| Postiz, SocialClaw, `browser-image-gen` | **not used for the blog**, ever. Postiz and SocialClaw post to social networks (their "posts" on WordPress or Medium are not this blog); `browser-image-gen` drives a browser and is meant for the tarot-deck skill only |

If the operator asks to "post", "publish" or "schedule" an article for TAROTS chat, it means this skill and this
script: there is no other target to choose or ask about.

## Setup: run `guide` first, never ask for a key
**Start every run with `python scripts/tarots_blog.py guide`, before asking anything.** If it prints the key's
permissions (`note: using the saved key (prefix tk_live_…)`), the key and the URL are already saved: everything is
set, go on and **never ask the operator for a key or a URL**. `guide` (and `new`) also print the two scripts'
**absolute paths** (`BLOG = "<python>" "<…>/tarots_blog.py"`, `IMAGES = "<python>" "<…>/tarots_images.py"`): use
them for **every** command, from any folder (the work folder too). The `scripts/…` paths in this file are only
short names for those: **never search the disk for a script** (`os.walk`, `dir /s`, `find`). `guide` also prints today's date (`note: today is …`):
use it for every "timely" decision. Only if `guide` fails with a message about a missing key, follow
`references/setup.md` (first setup, and what to do when a different key is offered). The recommended key is **one
key with the three permissions write + publish + media**, saved with `key save`: `tarots-blog-images` uses the same
key, so there is nothing else to set up for pictures.

## The work folder: the only place for this article's files
```
python scripts/tarots_blog.py new "samhain tarot spread"
```
creates `~/.tarots-blog/work/<YYYY-MM-DD>-<slug>/` (or under `TAROTS_WORK_DIR`) and prints its absolute paths:
- `article.json` — the fields, with every SEO field, `section` and `subject` empty, `"status": "draft"`,
  `"body_file": "article.md"`;
- `article.md` — the text, empty;
- `foto/` — every picture of this article (cover and inline), where `tarots_images.py generate --article <slug>`
  saves them, each with a name of its own (`cover-20261005-143012.jpg`, `inline-20261005-144501.jpg`);
- `.checks` — written by `check`: its rounds (do not edit it).

Rules:
- The article's files live **only** there: **never** in this skill's folder, never in a repository, never in the
  current directory. `check` and `post` refuse an article.json inside the skill's folder.
- Every command takes the **slug** (or the folder, or the path) instead of a path: `check samhain-tarot-spread`,
  `post samhain-tarot-spread`. A bare picture name (`--cover cover-20261005-143012.jpg`) is looked for in `foto/`,
  and `post` without `--cover` takes by itself the **last cover generated for this slug** (the record of
  `tarots_images.py` says which file is the cover of which article) and names it in a `note:` line.
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
python scripts/tarots_blog.py catalog --grep death                          # 5. link shortcuts (and the id for "subject")
python scripts/tarots_blog.py tags                                          #    tags to reuse
python scripts/tarots_blog.py check samhain-tarot-spread                    # 6. score + NEXT; fix only NEXT; at most 4 rounds
python ../tarots-blog-images/scripts/tarots_images.py progress              # 7. pictures: what form is free
python ../tarots-blog-images/scripts/tarots_images.py generate --article samhain-tarot-spread --kind landscape --shot wide --light blue-hour --setting "Irish hillside" --prompt "…"
#                                         → foto/cover-<YYYYMMDD-HHMMSS>.jpg, and the exact `post` command to run
python scripts/tarots_blog.py post samhain-tarot-spread                     # 8. re-check, upload that cover, save (draft)
```
Then the report (step 9). `post` without `--cover` uses the last cover generated for the slug (a `note:` line names
the file); with none it **stops with exit 11** and saves nothing, naming the file that is missing if one was
recorded and then deleted: generate the cover (step 7) and run `post` again. `--no-cover` saves without one,
**only** when the generation failed (LitMedia error, no credits): say why in the report.

## Workflow

### 1. Learn what exists
- `titles` lists the **whole blog** (every key and the console), one line each: `slug | title | keyword | lang |
  status | date`, newest first. Filter it (`--grep TEXT`, `--lang en`, `--section SLUG`, `--status draft`); it keeps
  a local copy and fetches only what changed. `sections` and `tags` list what to reuse.
- `list-posts` lists **every** article with its **id** (the id `update` takes), page by page; `mine` (= `list-posts
  --mine`) only those this key created. One key can change any draft: which one is the operator's choice.
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
| `subject` | what the article is about: `{"type": "card", "ref": "maj-16"}` or `{"type": "spread", "ref": "croce-celtica"}` (the id or slug from `catalog --grep <word>`). Leave `{"type": "", "ref": ""}` and the server works it out from the title and the keyword; `null` only for an article that names a card without being about it. |
| `section` | **an article about one card goes in the section of that card**: `major-arcana`, or its suit under «By suit» (`wands`, `cups`, `swords`, `disks`); one about a spread in a section of spreads (`tarot-spreads`); any other in a section of articles. A slug from `sections`, or empty: the server then puts an article on a card or a spread in its section. `check` warns (`WARN [subject]`) when subject and section do not match: fix article.json. |
| `faq` | 3–5 real questions with 1–3 sentence direct answers (`question`, `answer`). |
| `cover_alt` | what is in the picture; never a spread; a card only if the picture really shows one. |
| `language` | `en` (default). |
| `canonical_url` / `noindex` | leave unset unless the operator says so. |

`assets/example-article.json` + `.md` show the shape (abridged, not a template to copy).

### 6. Pictures: cover and inline
3:2 cover, no text in the image, **never a picture of cards** (one single small card, as context, is admitted in
any picture; never more than one, never a copy of a deck's artwork), its own subject from this article, in a form
that differs from the last pictures. **One small card is allowed in any article, not only its own** (relaxed
6/10/2026): write it small ("a single small card of the Tower") and "in the style of the Thoth deck", or get a
warning instead of a refusal; a card that is not the one the article's title, focus keyword or `subject` names
(*Tarot Meditation for Libra Season Balance*, an article about no card, still admits a small Fool "as context") is
a warning too, not exit 7. Made **only** by the `tarots-blog-images` skill:
```
python ../tarots-blog-images/scripts/tarots_images.py progress
python ../tarots-blog-images/scripts/tarots_images.py prompt-check --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>" --alt "<cover alt>" --article <slug>
python ../tarots-blog-images/scripts/tarots_images.py generate --article <slug> --prompt "<prompt>" --kind <kind> --shot <shot> --light <light> --setting "<setting>"
```
`--article <slug>` saves into the work folder's `foto/` with **a name of its own, never used before**:
`cover-<YYYYMMDD-HHMMSS>.jpg` for a 3:2 picture, `inline-<YYYYMMDD-HHMMSS>.jpg` for `--aspect 4:3` or `1:1`
(`--role cover|inline` says it explicitly); it never overwrites a file, records the article (slug, and id when
known) and the role, and **prints the exact command that uses that file**: copy it. Then `post <slug>` takes the
last cover generated for the slug by itself (`--cover NAME` for another file of `foto/`), and for an inline picture
`upload <the inline file> --for <slug>` (prints the url for `![alt](url)`). A second cover for the same article is
simply generated again: the newer one wins, the older stays on disk, unused. Prompt rules, the four dimensions,
what `post` and `upload` refuse (exit 7), cost and consent:
`references/image-generation.md`. If the other skill is not next to this one, find its folder `tarots-blog-images`
among the agent's skills; if it is not installed, or LitMedia fails, say so (attended run: `post <slug> --no-cover`;
unattended: see below). Never another image tool.

### 7. Check: fix only what NEXT says, at most 4 rounds
```
python scripts/tarots_blog.py check <slug>
```
It prints the score 0–100, the open items (`FIX` errors, `WARN` improvements) and then
**`NEXT — fix only these, do not rewrite the rest`**: one instruction per item, with the real values, e.g.
`seo_title is 76 chars: cut it to ≤ 60, keyword first: current = "…"`, `the keyword "…" is not in the first 100
words: edit ONLY the first paragraph and put the exact phrase in it`, `no internal links: run catalog --grep <word>
and put 2 of the printed shortcuts in sentences`. Items under "No action needed now" (no cover yet, keyword in the
alt) are left as they are. A `WARN [subject]` line says that the subject and the section do not match (an article
about the Tower in `love`): set the section it names in article.json; a `note [subject]` line needs nothing.
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
python scripts/tarots_blog.py post <slug>
```
`post` re-checks, refuses to save below 85 or with a `FIX` (and prints NEXT), uploads the cover, creates the article
and prints the URL.
- **The cover**: without `--cover`, `post` takes the **last cover recorded for this slug** by `tarots_images.py
  generate --article <slug>` whose file is still in `foto/`, names it in a `note:` line, and prints `cover: <file>`
  after saving; every check of the record still applies (made by `generate`, not used by another article, never two
  cards or a copy of a deck's artwork). A work folder from before the pictures had their own names: its `foto/cover.*`, with a
  `warning:` line. With no cover it **stops (exit 11)**, nothing saved, naming the recorded file that is missing if
  there is one: generate it with `tarots_images.py generate --article <slug> …`, then `post` again. `--no-cover`
  saves without a cover **only if the generation failed**: write the reason in the report. The `WARN immagine` of
  `check` is not a reason to skip it.
- `"status": "draft"` (the default) saves a draft an editor can publish. `"status": "published"` **only if the
  operator's (or the job's) instructions say to publish**; `"publish_at": "2026-10-12T08:00:00Z"` schedules it. With
  a key that lacks `blog:publish` the server saves a draft anyway and prints a `note:`: report it.
- On a network error or timeout **do not simply run `post` again**: run `mine` (or `titles --grep <word>
  --refresh`) first, the article may exist.
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
- **The key is the one saved key**: ONE key with write + publish + media, saved once by the operator with `key
  save` in `~/.tarots-blog/credentials.json`. Both skills read it by themselves (`note: using the saved key (prefix
  tk_live_…)`): set no variable, look for no other key, never print it. A `403` on a picture command means that key
  lacks the media permission: report the line, do not work around it.
- **Topic**: chosen with `topic-check`, preferring this week's events (dates verified on a page you open, within
  the next 14 days) or an evergreen; never one `TAKEN`.
- **One article per run.** Status `draft`, unless the job's instructions say `published`.
- The job's instructions are the operator's standing ok for this article's pictures: a cover and at most one inline
  picture (10 credits each); pass the job's budget with `--budget` if it sets one.
- **The cover is part of the article.** Run `generate --article <slug>` before `post`; `post <slug>` takes the
  last cover generated for the slug by itself (or run the exact `post` command `generate` printed). A post without a
  cover is saved **only with `--no-cover`, and only if the generation failed** (LitMedia error, credits, exit 5/6 of
  `tarots_images.py`): the report says so, with the error line. If `post` stops with exit 11 (no cover for the
  slug), the cover was forgotten or its file deleted: generate it, then `post` again.
- **The section**: an article about one card goes in that card's section (fill `subject` and `section`, or leave
  both empty and let the server place it); `check` must show no `WARN [subject]` line before `post`.
- **If a step fails, nothing is saved**: `guide` errors, `topic-check` leaves no free topic, the keyword is refused,
  `check` says `STOP` (exit 10), `post` refuses. Do not retry in a loop, do not use `--save-anyway`; write the report
  with the reason and the work folder path.
- `ModuleNotFoundError: requests` from LitMedia: `tarots_images.py` now finds a Python that has LitMedia's
  dependencies by itself; if there is none it exits 5 naming the `pip install -r …requirements.txt` command and the
  interpreter: report that line, do not install anything.
- The final report is the one of step 9, with the work folder path.

## Exit codes of `tarots_blog.py`
`0` ok · `2` usage, article file missing/unfilled/in the skill folder · `3` below the score or a `FIX` left (nothing
saved) · `4` the API refused · `5` configuration (key, URL) · `7` a picture rule refused the file · `8` topic or
keyword TAKEN · `9` the focus keyword is not a search phrase (> 6 words, a repeated word) · `10` STOP after 4 rounds · `11` `post` found no cover
generated for the slug and no `--cover` / `--no-cover` was given (nothing saved).

## Edit an existing article
`list-posts` (every article, with ids), `mine` (this key's), `update <id> patch.json`, `delete-draft <id>`. One key
reads, changes and deletes **any draft** of the blog (`blog:write`), whoever wrote it, and a published one too with
`blog:publish`: **only the article the operator (or the job) names**, never one chosen by you. Details and limits:
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
- Edit or delete only the article the operator (or the job) names: the key can touch every draft (and, with
  `blog:publish`, every published article), so the limit is yours. Never delete a published article unless the
  operator asked for that very one.
- One page per search intent: every topic goes through `topic-check` first (`TAKEN` = do not write it).
- Postiz, SocialClaw and other social or scheduling tools are not part of this job.

## Files
- `scripts/tarots_blog.py`: the CLI (`-h` for every command).
- `references/setup.md`: first setup of the key, a new key when one is saved.
- `references/writing.md`: links, inline picture, captions, video, coloured text.
- `references/seo-checklist.md`: every check the server runs and how to satisfy it.
- `references/keywords.md`: keyword clusters, competitors, topic calendar, on-page rules.
- `references/image-generation.md`: how the cover and inline pictures are made (only through `tarots-blog-images`).
- `references/editing.md`: `list-posts`, `update` and `delete-draft`.
- `references/api.md`: the REST endpoints, fields and errors.
- `assets/example-article.json` + `assets/example-article.md`: the shape of an article (abridged).
- `../tarots-blog-images/`: the picture skill (`scripts/tarots_images.py`, `references/prompts.md`).
- `tests/`: offline tests (pictures, titles and topic-check, work folder, NEXT, keyword, rounds, the cover of the
  slug, subject and section).
