# The editorial line: series for expert readers

The operator (7/10/2026): the blog must not be filled with «banalità da lettura della domenica». An unattended run
writes **one part of a series** each evening. **You design the series yourself**: you research it, you plan it, you
record it, and then you write one part per run until it is complete; then you design the next one.

The reader is someone who already knows the Thoth deck, the Golden Dawn attributions and the Tree of Life, and reads
to learn something they did not know: a scholar of Western esotericism, a practitioner of twenty years, a historian
of the occult. Write for them. An article they would skim in ten seconds is a failed article, whatever its score.

## What a series is

- **6–12 parts** around one question that matters, with a **thesis**: a claim the series argues, not a topic it
  surveys. «The Sefer Yetzirah tarot» is a topic; «The letter attributions of the Thoth deck are a reading of a
  3rd–6th century text, and the disputes about them are disputes about that text» is a thesis.
- Every part answers **one precise question**, has a title that says something, and stands on its own while
  building on the previous part (link it).
- Every part rests on **sources you can name**: primary texts (with edition or translation), scholars, museum or
  library pages. Never invent a source, a quotation, a date or a manuscript.

## Where good series come from

Look for one of these, always tied back to the tarot (the Thoth deck first, then its history):

- **History, with its disputes**: the Visconti-Sforza and Milanese decks; the game of tarocchi and its rules;
  the Marseille pattern; Court de Gébelin (1781) and the Egyptian myth; Etteilla; Éliphas Lévi's letter attributions
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
  Destinies*, Umberto Eco); Neoplatonism and Ficino; the history of Western esotericism as an academic field
  (Antoine Faivre, Wouter Hanegraaff, the Aries and Correspondences journals).
- **Structure and number**: why 22 = 3 + 7 + 12, 78 as a triangular number, the combinatorics of a spread, the deck
  as a finite system of symbols, information and meaning.
- **Close readings**: Crowley's *The Book of Thoth* chapter by chapter; one Atu through all its sources; one
  disputed attribution traced from its first appearance.

These are directions, not a list to copy: the series you plan must be yours, found by research, not on this page.

## What is never a series

`series plan` and `ideas add` refuse them by themselves, but do not even propose them:
<sign> season articles; moon phases, eclipses, Mercury retrograde; seasonal spreads and rituals (equinox, Samhain,
new year); beginner's guides, «how to read tarot», cheat sheets; love readings, soulmates, twin flames; horoscopes,
manifesting, self-care, «witchy» lifestyle; yes/no and daily-card pieces. Also never: a card meaning repeated in a
different costume, a spread invented to fit a season, a list of «10 ways to…».

## How to research (and not research twice)

1. **Read the record first**: `tarots_blog.py ideas list` and `tarots_blog.py series status`. They hold the topics
   already proposed, rejected and used, the finished series, and the notes of earlier research. Do not search again
   what is there; do not propose what was rejected.
2. **Search the web** for the direction you chose. Prefer pages you can open and cite: university and museum pages,
   the Warburg Institute, archive.org scans of primary texts, Sefaria for Hebrew sources, the Hermetic Library for
   Crowley and the Golden Dawn, JSTOR and academia.edu abstracts, Wikipedia only as a map to the real sources.
   Useful searches: `<subject> scholarship history`, `<subject> primary source edition`, `<subject> dispute
   attribution`, `"Book of Thoth" <atu> letter`, `Sefer Yetzirah <letter> commentary`.
3. **Record what you found** after each useful search:
   `tarots_blog.py ideas research "<what you searched>" --why "<what you learned in one or two lines>" --source <url>`.
4. **Record each candidate series** with `ideas add "<series title>" --why "<the thesis and why an expert would
   read it>" --source <url>`. Reject the weak ones with `ideas reject "<title>" --why "<reason>"`.
5. Choose the strongest: the one with a real thesis, real sources, and parts an expert does not already know.
6. Check every part title against the blog: `tarots_blog.py topic-check "<part title>"`.

## How to record the series

Write a JSON file (anywhere outside the skill folder, e.g. the work root) and run `tarots_blog.py series plan <file>`:

```json
{
  "title": "The Letters Before the Cards: The Sefer Yetzirah and the Tarot",
  "thesis": "The letter attributions of the Thoth deck are a reading of a 3rd-6th century text, and the disputes about them are disputes about that text.",
  "why": "Experts know the attributions; few know their source, its versions and the choices the Golden Dawn made.",
  "section": "kabbalah",
  "sources": ["Sefer Yetzirah, tr. Aryeh Kaplan (1990)", "Peter Hayman, Sefer Yesira: Edition, Translation and Text-Critical Commentary (2004)"],
  "parts": [
    {"title": "Three Mothers and the Breath Between Them",
     "question": "Why do Aleph, Mem and Shin carry the elements, and what does that make of the Fool, the Hanged Man and the Aeon?",
     "sources": ["Sefer Yetzirah ch. 3", "Crowley, The Book of Thoth, 1944"],
     "keyword": "sefer yetzirah tarot"}
  ]
}
```

`section` is a slug from `tarots_blog.py sections` (type «articoli»). `series plan` checks: title, thesis, why,
section and at least two sources; 6–12 parts, each with a title, a question and sources; no popular genre, no
keyword-string title, no part already on the blog (TAKEN), no series that repeats a finished one, and only one open
series at a time. It records the series in `~/.tarots-blog/editorial.json` with its tag (`series-<id>`).

## How to write one part

1. `tarots_blog.py series next`: the brief of the next part (question, sources, previous part to link) and the
   exact `new` command, e.g. `tarots_blog.py new "three-mothers-and-the-breath-between-them" --series <id> --part 1`.
   `new --series` fills the title, the section, the series tag and the `series` block of article.json.
2. Read the sources of the brief (open them), then write:
   - **1,500–3,000 words**, in English, for the expert reader;
   - the **first paragraph states the question and the thesis** of this part (and contains the focus keyword in a
     natural sentence);
   - the **evidence**: what the primary sources say, quoted briefly and attributed (edition, chapter, page or link);
     what the scholars say, by name;
   - **the counter-reading**: the strongest objection, a different tradition, an attribution that disagrees;
   - **what it changes for a reader of the Thoth deck**: concrete, card by card where it applies;
   - the **link to the previous part** in a sentence (`[[post:<slug>]]`, the brief prints it) — `post` refuses part 2
     onwards without it; at the start or the end, one line saying «Part n of N of the series «…»»;
   - internal links to the cards and spreads you discuss (`[[card:…]]`), at least two external sources you opened.
3. The **title** is the part's title (or a better one): a phrase with a point. The focus keyword goes in the SEO
   title, the description, the slug and the first paragraph — not necessarily in the title.
4. Then as usual: `check`, the cover with `tarots_images.py generate --article <slug>`, `post`. `post` marks the part
   as written in the record; the last part closes the series.

## The evening job

One run = one part:

```
tarots_blog.py guide
tarots_blog.py series status          # open series? → series next → write that part
                                      # none open? → research, ideas, series plan → write part 1
tarots_blog.py run-report --hours 12  # the SAVED lines go in the report as they are
```
