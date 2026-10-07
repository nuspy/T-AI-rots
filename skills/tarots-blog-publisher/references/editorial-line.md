# The editorial line: a plan of series and articles for expert readers

The operator (7/10/2026): the blog must not be filled with «banalità da lettura della domenica». The blog is fed
from an **editorial plan that you make yourself**: series of 3–10 articles and single articles, about **100
articles** in all. A **daily session** writes about **5** of them, in order, and publishes them. When the plan runs
out, the session makes a new one before writing. The operator can also ask at any time for one article or one
series on a topic he gives: it goes ahead of the plan.

The reader is someone who already knows the Thoth deck, the Golden Dawn attributions and the Tree of Life, and reads
to learn something they did not know: a scholar of Western esotericism, a practitioner of twenty years, a historian
of the occult. Write for them. An article they would skim in ten seconds is a failed article, whatever its score.

## The three ways in

| The operator asks | You do |
|---|---|
| «make the plan» (or `plan session` exits 14: PLAN EMPTY) | research, then `plan add <file.json>` with about 100 articles: section «The plan» |
| the daily job | `plan session`, then `plan next` → write → `post --publish`, until `plan next` says the session is done: section «The daily session» |
| «write an article / a series about X» | the same file format with that one item, `plan add <file.json> --now`, then `plan next` until it is written: it goes ahead of the plan |

## What a series is, what an article is

- A **series** is **3–10 articles** around one question that matters, with a **thesis**: a claim the series argues,
  not a topic it surveys. «The Sefer Yetzirah tarot» is a topic; «The letter attributions of the Thoth deck are a
  reading of a 3rd–6th century text, and the disputes about them are disputes about that text» is a thesis. Every
  part answers one precise question, stands on its own and builds on the previous part (it links it).
- A **single article** answers one precise question that does not need a series: one disputed attribution, one
  document, one painting, one scholar's argument.
- Both rest on **sources you can name**: primary texts (with edition or translation), scholars, museum or library
  pages. Never invent a source, a quotation, a date or a manuscript.
- The **titles** are real titles: a phrase with a point, a question, or a name and a subtitle after a colon. Never
  keywords in a row: `plan add` and `check` refuse them.

## Where good topics come from

Directions, not a list to copy: what you plan must come from your research.

- **History, with its disputes**: the Visconti-Sforza and Milanese decks; the game of tarocchi and its rules; the
  Marseille pattern; Court de Gébelin (1781) and the Egyptian myth; Etteilla; Éliphas Lévi's letter attributions
  (1856) and why they differ from the Golden Dawn's; the Cipher Manuscripts; Mathers, Westcott, Book T; Waite and
  Smith; Crowley and Frieda Harris (1938–1944), their letters and the paintings' changes. Scholars: Michael Dummett,
  Ronald Decker, Thierry Depaulis, Helen Farley, Robert Place, Ronald Hutton.
- **Kabbalah explained to the tarot reader**: the Sefer Yetzirah (mother, double and simple letters; the Cube of
  Space; the 32 paths and their different trees: Kircher, the Gra, Isaac Luria); the Zohar's Partzufim and the court
  cards; the Four Worlds and the four suits; Tzimtzum and the Fool; Da'at and the card that is missing. Scholars:
  Gershom Scholem, Moshe Idel, Aryeh Kaplan (translator), Peter Hayman (critical edition), Marla Segol.
- **The Hermetic sciences in the deck**: the 36 decans of the minors (Picatrix, Agrippa, Liber 777), the 72 Shem
  angels, alchemy in Art (XIV) and in the court cards, geomancy, Enochian traces, the numerology of the ten small
  cards and the Pythagorean tetractys.
- **Interdisciplinary readings**: the Renaissance art of memory (Frances Yates, Giordano Bruno) and the deck as a
  memory palace; Jung, synchronicity and the I Ching; semiotics and narrative (Calvino's *The Castle of Crossed
  Destinies*, Umberto Eco); Neoplatonism and Ficino; Western esotericism as an academic field (Antoine Faivre,
  Wouter Hanegraaff, the Aries and Correspondences journals).
- **Structure and number**: why 22 = 3 + 7 + 12, 78 as a triangular number, the combinatorics of a spread, the deck
  as a finite system of symbols.
- **Close readings**: Crowley's *The Book of Thoth* chapter by chapter; one Atu through all its sources; one
  disputed attribution traced from its first appearance.

## What is never a topic

`plan add` and `ideas add` refuse them by themselves, but do not even propose them: <sign> season articles; moon
phases, eclipses, Mercury retrograde; seasonal spreads and rituals (equinox, Samhain, new year); beginner's guides,
«how to read tarot», cheat sheets; love readings, soulmates, twin flames; horoscopes, manifesting, self-care,
«witchy» lifestyle; yes/no and daily-card pieces. Also never: a card meaning repeated in a different costume, a
spread invented to fit a season, a list of «10 ways to…».

## How to research (and not research twice)

1. **Read the record first**: `tarots_blog.py ideas list` and `tarots_blog.py plan status`. They hold the topics
   already proposed, rejected, planned and written, and the notes of earlier research. Do not search again what is
   there; do not propose what was rejected. `tarots_blog.py titles` lists every article already on the blog.
2. **Search the web**. Prefer pages you can open and cite: university and museum pages, the Warburg Institute,
   archive.org scans of primary texts, Sefaria for Hebrew sources, the Hermetic Library for Crowley and the Golden
   Dawn, JSTOR and academia.edu abstracts, Wikipedia only as a map to the real sources. Useful searches:
   `<subject> scholarship history`, `<subject> primary source edition`, `<subject> dispute attribution`,
   `"Book of Thoth" <atu> letter`, `Sefer Yetzirah <letter> commentary`.
3. **Record what you found** after each useful search:
   `tarots_blog.py ideas research "<what you searched>" --why "<what you learned, one or two lines>" --source <url>`.
4. **Record each candidate** with `ideas add "<title>" --why "<the thesis, and why an expert would read it>"
   --source <url>`; drop the weak ones with `ideas reject "<title>" --why "<reason>"`.

## Sources that exist

Every source of the plan is looked up by `plan add` (and by `tarots_blog.py sources-check "<source>" …`, which you
run first): a book in the Open Library catalogue, a Wikipedia page in Wikipedia, a link by opening it. **What is not
found is refused** (7/10/2026: the first plan cited books that do not exist and wrong years). Write them like this:

- a book: `Author, Title (Year)` — the year of the edition you cite: `Michael Dummett, The Game of Tarot (1980)`;
- a translation: `Work, tr. Translator (Year)` — `Sefer Yetzirah, tr. Aryeh Kaplan (1990)`;
- a Wikipedia page, with its exact title: `Visconti–Sforza Tarot, Wikipedia`;
- a page you opened: its URL.

When a source is refused, the message says what exists instead: the author's real books on that subject, the real
years of the editions, the closest Wikipedia pages. Use them; never keep a refused source. A real book the catalogue
does not know (it happens: Scholem's *Origins of the Kabbalah*) is replaced by one it knows, or by the page you read.
Never cite this blog as a source.

## The plan

Make it in one go: research, then one JSON file with **about 100 articles** in all, as series (3–10 parts each) and
single articles, mixed so that a day's ~5 articles are varied (a series of 3 and two single articles; a series of 5;
a long series alone). Put the items in the order they should be written. Then:

```
tarots_blog.py plan add <file.json>
```

The file:

```json
{"items": [
  {"kind": "series",
   "title": "The Letters Before the Cards: The Sefer Yetzirah and the Tarot",
   "thesis": "The letter attributions of the Thoth deck are a reading of a 3rd-6th century text, and the disputes about them are disputes about that text.",
   "why": "Experts know the attributions; few know their source, its versions and the choices the Golden Dawn made.",
   "section": "kabbalah",
   "sources": ["Sefer Yetzirah, tr. Aryeh Kaplan (1990)", "Peter Hayman, Sefer Yesira (2004)"],
   "parts": [
     {"title": "Three Mothers and the Breath Between Them",
      "question": "Why do Aleph, Mem and Shin carry the elements, and what does that make of the Fool, the Hanged Man and the Aeon?",
      "sources": ["Sefer Yetzirah ch. 3", "Crowley, The Book of Thoth (1944)"],
      "keyword": "sefer yetzirah tarot"},
     {"title": "…", "question": "…", "sources": ["…"], "keyword": "…"},
     {"title": "…", "question": "…", "sources": ["…"], "keyword": "…"}
   ]},
  {"kind": "single",
   "title": "What Frieda Harris Changed in the Last Drafts",
   "question": "Which cards did Harris repaint after 1942, and what did Crowley ask her to change?",
   "why": "The correspondence is rarely read; it explains details every Thoth reader sees.",
   "section": "thoth-tarot",
   "sources": ["Richard Kaczynski, Perdurabo (2010)", "…"],
   "keyword": "frieda harris thoth tarot"}
]}
```

`section` is a slug from `tarots_blog.py sections` (type «articoli»: `kabbalah`, `thoth-tarot`, `symbolism`,
`spirituality`…). `plan add` checks every item: title, thesis or question, why, section, at least two sources; a
series has 3–10 parts, each with a title, a question and sources; no popular genre, no keyword-string title, nothing
already on the blog (TAKEN), nothing that repeats an item of the plan. **It keeps the good items and refuses the bad
ones** (printed with the reason, and recorded among the rejected ideas): fix the refused ones and add them again, or
replace them. `plan status` shows how many articles are queued.

## The daily session

```
tarots_blog.py guide
tarots_blog.py plan session            # exit 14 (PLAN EMPTY): make a new plan first (section «The plan»), then again
tarots_blog.py plan next               # the part to write now: its brief and the exact `new` command
   … new … --series <id> --part <n>   # write, check, cover, then:
tarots_blog.py post <slug> --publish   # published; the part is marked written
tarots_blog.py plan next               # again, after every post, until it says the session is done
tarots_blog.py run-report --hours 24   # the SAVED lines, and INCOMPLETE / STUCK lines if any: in the report
```

- `plan session` opens, in order, the items of the plan until about 5 articles are to be written. **The items an
  earlier session left incomplete come first**, always. A series is never split: a series of 8 is the whole session.
- `plan next` gives the parts **in order**: part 2 of a series before part 3, never skipped.
- **A failure is never abandoned.** A STOP of `check` or a `post` refused by the API is recorded on the part by the
  script itself. `plan next` then gives the same part again, with `RETRY` and the reason, and a new work folder
  (`…-retry2`): write it again, better. After 3 failed attempts in one day it goes on to the next item; the part
  stays open, the next session starts from it, and every `run-report` shows it (`INCOMPLETE`, or `STUCK` after 3
  failures). Never mark a part written yourself, never skip it: only the operator may (`plan skip`).
- If the session stops halfway (a crash, a timeout), nothing is lost: the next `plan session` starts from the parts
  left.

## How to write one part

1. Read the brief of `plan next` and open its sources.
2. `new … --series <id> --part <n>` (the command printed by `plan next`) fills the title, the slug, the section, the
   series' tag and the `series` block of article.json.
3. Write:
   - **1,500–3,000 words**, in English, for the expert reader;
   - the **first paragraph states the question and the thesis** (and contains the focus keyword in a natural
     sentence);
   - the **evidence**: what the primary sources say, quoted briefly and attributed (edition, chapter, page or link);
     what the scholars say, by name;
   - **the counter-reading**: the strongest objection, a different tradition, an attribution that disagrees;
   - **what it changes for a reader of the Thoth deck**: concrete, card by card where it applies;
   - in a series: the **link to the previous part** in a sentence (`[[post:<slug>]]`, the brief prints it; `post`
     refuses part 2 onwards without it) and one line saying «Part n of N of the series «…»»;
   - internal links to the cards and spreads you discuss (`[[card:…]]`), at least two external sources you opened.
4. The focus keyword goes in the SEO title, the description, the slug and the first paragraph — not necessarily in
   the title.
5. `check`, the cover with `tarots_images.py generate --article <slug>`, `post <slug> --publish`. Then `plan next`.
