# Keyword map and topic calendar

Target: **international, English-first** (canonical language of the site is English; Italian is a secondary
version linked with `hreflang`). Niche: tarot, the **Thoth Tarot**, Golden Dawn / Hermetic Qabalah, esoteric
practice, cartomancy, with an **AI reading** angle.

> **Method and limits.** Built from live SERP research (September 2026) on the English-language competitors
> listed below. There are **no search-volume numbers** here: no keyword-data API was connected. Priorities
> (P1/P2/P3) are editorial estimates based on intent, competition and fit with what the site really offers.
> Validate with Google Search Console / Bing Webmaster Tools after launch and re-rank. Never quote a volume
> that is not measured.

## Who we compete with (English SERPs)

| Group | Sites seen ranking | What they do well | Gap we can use |
|---|---|---|---|
| Free readings | Trusted Tarot, Free-Tarot-Reading.net, Deckaura, Taro's Tarot, Tarotap, Nostra | instant one/three-card draws, no signup | shallow, mostly Rider-Waite, no doctrine, no follow-up questions |
| Card meanings / learning | Labyrinthos, Biddy Tarot, Tarot.com, Aeclectic Tarot, Learn Tarot | huge card-by-card libraries, spreads lists | almost all Rider-Waite; **Thoth-specific, correspondence-rich pages are scarce** |
| Thoth / Golden Dawn niche | crowley-thoth.com, crowleythoth.net, tarotx.net, tarotsmith.com, Mary K. Greer, esotericmeanings.com | depth, Qabalah/astrology attributions | dated UX, no interactive reading, thin structured data |
| AI tarot | Tarotap, chatarot, CardMuse, Elvi Tarot, Whisper, AI Hub roundups | "AI reader" positioning | most produce isolated card meanings with no narrative across the spread; accuracy claims are distrusted |

**Positioning to own:** *"Thoth Tarot reading online with AI — every card read in its position, grounded in
Golden Dawn correspondences (Hebrew letter, path, Sephirah, element, astrology), after a short interview about
your question."* Compatibility and relationship spreads (couple, soulmates, crossroads) are a second wedge.

## Keyword clusters → target page

One primary keyword per page. Never target the same primary keyword with two pages (cannibalization).
Secondary keywords go in the H2s, the first 100 words, image alt text and the FAQ.

### Home (`/`) — brand + transactional
- P1: `online tarot reading`, `AI tarot reading`, `Thoth tarot reading online`
- P2: `tarot reading with interview`, `Golden Dawn tarot`, `esoteric tarot reading`, `tarot card of the day`
- P3: `Aleister Crowley tarot online`, `Hermetic tarot reading`

### Card library (`/cards`) — informational hub
- P1: `tarot card meanings`, `Thoth tarot card meanings`, `all 78 tarot cards`
- P2: `major arcana meanings`, `minor arcana meanings`, `Thoth tarot cards list`, `tarot cards Hebrew letters`
- Each card page (`/cards/{slug}`) primary: `{card name} tarot card meaning`. Secondary:
  `{card name} Thoth tarot`, `{card name} love`, `{card name} career`, `{card name} reversed` (Thoth has no
  reversals by design — say so, then give the ill-dignified reading, which is what searchers want),
  `{card name} Hebrew letter`, `{card name} astrology`.

### Spreads (`/spreads`) — informational + tool
- P1: `tarot spreads`, `celtic cross tarot spread`, `tarot spreads for love`
- P2: `three card tarot spread`, `tarot horseshoe spread`, `astrological wheel tarot spread`,
  `relationship tarot spread`, `tarot compatibility spread`
- P3: `soulmate tarot spread`, `crossroads tarot spread`, `tarot mirror spread`, `couple tarot spread`
- Each spread page (`/spreads/{slug}`) primary: `{spread name} tarot spread` (+ `positions`, `how to read`,
  `meaning`). These pages carry `HowTo` structured data.

### Card of the day (`/card-of-the-day`) — habit page
- P1: `tarot card of the day`, `daily tarot card`
- P2: `daily tarot reading`, `free daily tarot`

### Shop (`/deck`, `/pricing`) — transactional
- `/deck` P1: `Thoth tarot deck`, `original artwork tarot deck`; P2: `collector tarot deck box set`,
  `buy Thoth tarot deck`. (Product is *in preparation* — keep availability honest; do not invent prices.)
- `/pricing` P1: `online tarot reading price`, `AI tarot reading subscription`; P2: `buy tarot reading credits`,
  `tarot reading packages`. Only claim what the plans really include (the card of the day is free; readings use
  credits or a subscription).

### Blog (`/blog/...`) — informational clusters
| Cluster | Example primary keywords |
|---|---|
| Learn tarot | `how to read tarot cards`, `tarot for beginners`, `how to do a tarot reading`, `how tarot works` |
| Thoth & Golden Dawn | `Thoth tarot vs Rider-Waite`, `Golden Dawn tarot correspondences`, `tarot Tree of Life`, `tarot Hebrew letters meaning`, `Aleister Crowley Book of Thoth explained`, `Lady Frieda Harris Thoth artwork` |
| Practice | `tarot journaling`, `shadow work tarot`, `tarot spreads for shadow work`, `tarot and astrology`, `tarot numerology birth card` |
| Love & relationships | `tarot for love`, `tarot for relationship problems`, `tarot compatibility`, `twin flame tarot` (handle with care: no verdicts, no fidelity claims) |
| AI & trust | `is AI tarot accurate`, `AI tarot vs human reader`, `how AI tarot readings work`, `tarot ethics` |
| Seasonal | see calendar below |

## Topic calendar (from September 2026)

Verify each date before publishing (sources: Farmers' Almanac, Britannica, CHANI, Almanac Supply Co.).

| When | Hook | Angle for us |
|---|---|---|
| 22–23 Sep 2026 | Autumn equinox / Mabon | Balance spread; *The Universe / Art (Temperance) / Adjustment (Justice)* in the Thoth |
| 12 Oct | Aleister Crowley's birthday (b. 1875) | Who was Crowley; how he changed the tarot |
| 23 Oct – 22 Nov 2026 | Scorpio season | *Death* and *Lust* in Thoth; shadow-work spread |
| 24 Oct – 13 Nov 2026 | Mercury retrograde in Scorpio (verify) | Reading with *The Magus*; communication spread |
| 31 Oct – 1 Nov | Samhain / Halloween | Divination history, Samhain spread |
| Nov – Jan | "tarot 2027" year-ahead searches | 12-month wheel spread → `/spreads/astrological-wheel` |
| 21 Dec | Winter solstice | Rebirth: *The Aeon*, *The Sun* |
| Always | Full and new moons | Moon-cycle spreads (`three-card`, `crossroads-spread`) |
| Always | Social trends: pick-a-card, shadow work, tarot journaling, AI tarot | "How to journal your tarot reading", "pick a card vs a real spread" |

## On-page rules (what the code and the publisher enforce)

- `seo_title`: 30–60 characters, primary keyword near the start.
- `seo_description`: 120–160 characters, primary keyword once, a promise + a reason to click.
- Slug: lowercase, hyphenated, ≤ 75 characters, contains the primary keyword, no stop-word padding.
- Body: ≥ 800 words for an article (≥ 600 minimum), primary keyword in the first 100 words and in at least one
  H2, 3–6 H2s, ≥ 2 internal links (`[[card:the-star]]`, `[[spread:celtic-cross]]`, `[[post:slug]]`), ≥ 1
  reputable external source, keyword density 0.5–2.5 % (never stuff).
- 3–5 FAQ items (real questions, direct 1–3 sentence answers) → `FAQPage` markup and AI-overview friendliness.
- Cover image: 16:9, alt text describing the image (with the keyword only if it fits naturally).
- One article per primary keyword. Before writing, list existing posts and pick a keyword not already used.
