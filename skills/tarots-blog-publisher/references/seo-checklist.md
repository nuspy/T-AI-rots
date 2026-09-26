# SEO checks: what the server measures and how to pass

`check` and `post` return a score from 0 to 100 (weighted sum of the checks below; `ok` = full weight, `WARN` =
half, `FIX` = none) and a verdict: `ottimo` (≥ 85 and no error), `buono` (≥ 65), `da_migliorare`.

**What the score is not.** It does not know search volume, competition or ranking. It says whether the article follows
well-established good practice. A 100 does not promise page one; a 40 says where to start. Never chase the number
with tricks (repeated keywords, padding, hidden text): the density check exists to catch exactly that.

| Check id | Weight | Passes when | If it fails |
|---|---|---|---|
| `titolo_seo` | 2 | SEO title (or the title) is 30–60 characters | Shorten a long title; add the benefit or the year to a thin one |
| `descrizione_seo` | 2 | SEO description is 120–160 characters | Write it: keyword once, a promise, a reason to click |
| `parola_chiave` | 3 | `focus_keyword` is set | Choose the one phrase the article should be found for |
| `chiave_nel_titolo` | 3 | keyword appears in the SEO title | Put it near the start, in natural words |
| `chiave_nella_descrizione` | 2 | keyword appears in the SEO description | Once, naturally |
| `chiave_nello_slug` | 1 | the slug contains the keyword's slug | Set `slug` explicitly to the keyword, hyphenated |
| `chiave_nell_inizio` | 2 | keyword is in the first 100 words | Answer the question straight away in the opening |
| `chiave_in_un_h2` | 1 | keyword (or the whole phrase) is in one `##` heading | Name a section after it |
| `chiave_nell_alt` | 1 | keyword is in the cover alt text | Only if the image really shows it; otherwise accept the warning |
| `densita` | 1 | the phrase appears, but under 3 % of the words | Remove forced repetitions; use synonyms |
| `lunghezza` | 3 | ≥ 800 words (WARN below, FIX below 300) | Cover the topic in depth: examples, cases, misconceptions, a practical exercise |
| `titoli_h2` | 1 | at least 2 `##` headings | Structure the text in sections |
| `h1_nel_testo` | 1 | the body has no `# H1` | Use `##`; the page title is already the H1 |
| `frasi` | 1 | average sentence ≤ 24 words | Split long sentences |
| `collegamenti_interni` | 2 | ≥ 2 links to cards, spreads or posts (`[[card:…]]`, `[[spread:…]]`, `[[post:…]]`) | Link the cards and spreads the article talks about |
| `collegamenti_esterni` | 1 | ≥ 1 external link | Cite a reputable source you opened (a museum, an academic or established reference) |
| `immagine` | 1 | there is a cover and its alt text is at least 8 characters | Add a cover and `cover_alt` |
| `etichette` | 1 | 2–6 tags | Reuse existing tags (`tags`) |
| `faq` | 1 | at least 2 FAQ items (3–5 is the target) | Real questions readers ask, 1–3 sentence direct answers |
| `slug` | 1 | ≤ 75 characters and ≤ 9 words (not judged before the article has one) | Shorten it, drop filler words |

## What the site adds on its own

The article page renders the title as H1, the cover with `width`/`height`, a visible FAQ section, breadcrumbs, and
structured data (`BlogPosting`, `BreadcrumbList`, `FAQPage`) with your keywords, word count and reading time; it
sets the canonical URL, Open Graph and Twitter cards, `hreflang` between languages, and lists the page in the
sitemap and RSS feed (unless `noindex`). You do not need to do any of that in the text.

## Quality beyond the score

- **Search intent first.** Someone searching "the tower tarot meaning" wants the meaning, keywords, upright and
  ill-dignified reading, love/work angles, and how it differs from Rider-Waite; give that before the history.
- **Experience and precision** (E-E-A-T): name the correspondences correctly (Hebrew letter, path, element or planet),
  say who said what, separate tradition from modern interpretation.
- **Freshness**: for timely topics put the year and the dates in the text, and verify them.
- **One page per intent.** Don't publish a second article for the same keyword; update the first (`update`).
