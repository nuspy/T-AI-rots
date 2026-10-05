# REST API reference (v1)

Use `scripts/tarots_blog.py` when you can: it handles authentication, image upload, the SEO gate and errors. This
page is for calling the API directly.

- Base: `TAROTS_API_URL` (for example `https://tarots.chat/api`); all paths below are under `/v1/blog`.
- Authentication: `Authorization: Bearer tk_live_…` (or `X-API-Key: tk_live_…`). Keys are created in the console.
  Send the key only to the API host. Do not follow redirects with it.
- JSON in and out (`Content-Type: application/json`), except `POST /media` with a raw image body.
- Errors: FastAPI style, `{"detail": "…"}` or `{"detail": {"errore": "sezione_non_valida", "sezioni_valide": […]}}`.

## Endpoints

| Method and path | Permission | Purpose |
|---|---|---|
| `GET /guide` | write | What is accepted, SEO thresholds, this key's scopes and daily limit |
| `GET /sections` | write | Sections you can publish in (`slug`, `nome`, `percorso`, and `tipo`: articoli, carte, stese) |
| `GET /tags` | write | Tags already used, with counts |
| `GET /catalog` | write | Cards and spreads with their `id` and the `[[card:…]]` / `[[spread:…]]` shortcut |
| `POST /seo-check` | write | SEO report for an article body, nothing saved |
| `POST /media` | write | Upload an image (raw `image/png|jpeg|webp` body, or JSON `{"immagine_base64": "…"}`) → `{id, url, larghezza, altezza, byte}` |
| `POST /posts` | write | Create an article (`dry_run: true` → report only) |
| `GET /posts` | write | **Every** article, newest first (`stato`, `pagina`, `per_pagina`); `mine=true`: only this key's |
| `GET /titles` | write or media | **Every** article of the blog (any key, the console too), compact: see below |
| `GET /posts/{id}` | write | Any article, with its SEO report |
| `PATCH /posts/{id}` | write (publish for published or archived ones) | Change fields of any article |
| `DELETE /posts/{id}` | write for a draft, publish for a published one | Delete an article (any key's) |

## Article fields (`POST /posts`, `PATCH /posts/{id}` sends only what changes)

| Field | Type | Notes |
|---|---|---|
| `titolo` | string ≤ 200 | required. The page H1 |
| `sottotitolo` | string ≤ 300 | one-line subtitle |
| `testo` | Markdown ≤ 200 000 | no HTML. Start sections at `##`. Shortcuts `[[card:slug]]`, `[[spread:slug]]`, `[[post:slug]]`, `[[video:youtube:ID]]` or `[[video:vimeo:ID]]` (own line). Inline images: ordinary `![alt](url "caption")`, the url from `POST /media`. Rich text: `:text[…]{color=brass\|plum\|verdigris\|muted size=small\|large\|title}`, `:underline[…]` |
| `lang` | `^[a-z]{2}(-[A-Za-z]{2})?$` | default `en`; `it` for Italian |
| `sezione` | slug or id | a section from `GET /sections`: of type "articoli", or "carte" / "stese" (an article about a card goes in that card's section, one about a spread in a section of spreads). Empty with a subject: the server puts it in the subject's section |
| `subject` | `{"tipo": "carta"\|"stesa", "ref": "…"}` \| null | what the article is about (`card`/`spread` accepted too); `ref` is the card's or spread's id or slug from `GET /catalog` (`maj-16`, `coppe-01`, `the-tower`, `croce-celtica`). **Not sent**: the server works it out from the title and the focus keyword; `null`: about no card or spread. Answers carry it as `{"tipo", "ref", "nome", "slug"}` (`GET /titles`: `{"tipo", "ref"}` or null) |
| `tags` | ≤ 10 strings | reuse existing |
| `slug` | ≤ 160 | empty: derived from the title |
| `immagine_id` | uuid | from `POST /media` |
| `immagine_base64` | string | alternative to `immagine_id`; PNG/JPEG/WebP ≤ 8 MB |
| `immagine_alt` | ≤ 200 | alt text of the cover |
| `seo_titolo` | ≤ 200 | 30–60 recommended |
| `seo_descrizione` | ≤ 320 | 120–160 recommended |
| `seo_parola_chiave` | ≤ 120 | the focus keyword |
| `seo_parole_chiave` | ≤ 10 strings | secondary keywords |
| `canonical_url` | https URL | only if the text lives elsewhere |
| `noindex` | bool | keep out of search engines and the sitemap |
| `faq` | ≤ 10 × `{domanda, risposta}` | shown on the page and emitted as FAQPage data |
| `stato` | `bozza` \| `pubblicato` (\| `archiviato` on PATCH) | default `bozza` |
| `pubblicato_il` | ISO 8601 | a future time with `pubblicato` schedules it (needs `blog:publish`) |
| `in_evidenza` | bool | feature at the top of the blog (needs `blog:publish`) |
| `dry_run` | bool | `POST /posts` only: return the report, save nothing |

`tarots_blog.py` also accepts English names in the article file: `title, subtitle, body, body_file, language,
section, cover_image_id, cover_alt, seo_title, seo_description, focus_keyword, secondary_keywords, status
(draft|published|archived), publish_at, featured`, FAQ items as `{question, answer}`, and `subject` as
`{"type": "card"|"spread", "ref": "…"}` (sent as `subject` `{"tipo": "carta"|"stesa", "ref": "…"}`; `{"type": "",
"ref": ""}`: nothing is sent; `null`: sent as null).

## Response of `POST /posts`, `GET /posts/{id}`, `PATCH /posts/{id}`

```json
{
  "articolo": {"id": "…", "slug": "…", "stato": "bozza", "lang": "en", "seo_parola_chiave": "…", "...": "…"},
  "url": "https://tarots.chat/blog/…",
  "seo": {"punteggio": 88, "giudizio": "ottimo", "controlli": [{"id": "…", "esito": "ok|avviso|errore", "peso": 2, "messaggio": "…", "messaggio_it": "…"}], "suggerimenti": ["…"], "statistiche": {"parole": 1180}},
  "avvisi": ["Saved as a draft: this key has no `blog:publish` permission. …"]
}
```

## `GET /titles`: the compact list of every article

To learn what the blog already covers without downloading articles. `tarots_blog.py titles` and `topic-check` use
it (with a local copy); call it directly only if you cannot run the script.

Query parameters (all optional):

| Parameter | Meaning |
|---|---|
| `lang` | only this language (`en`, `it`, …) |
| `stato` | `bozza` \| `pubblicato` \| `archiviato`. Without it: drafts and published |
| `archiviati` | `true`: without `stato`, archived articles too |
| `sezione` | a section slug (an unknown slug simply gives no rows) |
| `q` | case-insensitive search in title, slug and focus keyword (`%` and `_` are literal) |
| `dal` | ISO 8601: only articles **updated** at or after that moment (a naive time is UTC) |
| `pagina`, `per_pagina` | page from 1; size up to **1000**, default 200 |

Order: newest first (`pubblicato_il`, or the creation time for drafts). Response:

```json
{
  "totale": 1834, "pagina": 1, "per_pagina": 200, "adesso": "2026-10-05T09:12:44.120931+00:00",
  "articoli": [
    {"id": "…", "slug": "the-tower-thoth-tarot-meaning", "titolo": "The Tower in the Thoth Tarot",
     "estratto": "subtitle, else SEO description, else the start of the text (~160 chars)",
     "parola_chiave": "tower tarot meaning", "sezione": "cards", "lang": "en", "stato": "pubblicato",
     "pubblicato_il": "2026-09-30T08:00:00+00:00", "aggiornato": "2026-10-01T10:02:11+00:00",
     "mio": false, "tradotto_da_id": null, "subject": {"tipo": "carta", "ref": "maj-16"}}
  ]
}
```

- `mio` is true for the articles created by the key making the request.
- `tradotto_da_id` is the original an article was translated from (`null` for an original).
- Keeping a copy up to date: remember `adesso` and next time ask with `dal` = that moment **minus a few minutes**
  (a slow save can carry a slightly earlier time) and `archiviati=true` (to see articles that got archived). A
  **deleted** article is never in a `dal` answer: reload everything from time to time to drop it.

## Rules the server enforces (no parameter bypasses them)

- `blog:write` alone creates drafts: `stato: "pubblicato"`, `pubblicato_il` and `in_evidenza` are ignored with an
  entry in `avvisi`. Changing an already published article needs `blog:publish`.
- One key reads, changes and deletes any article (5/10/2026: no more «only the articles of this key»): any draft
  with `blog:write`; a published or archived one needs `blog:publish`, to change it and to delete it. When the key
  is not the author, the change is recorded with its before and after. `404` means the article does not exist.
- Images are never fetched from a URL (that would be a request from our server to an address chosen from outside):
  upload the file or send base64.
- Limits per key: requests per minute and articles per day (`GET /guide`). `429` means stop and wait.
- A `422` explains what is wrong (unknown section → the list of valid ones; a too-long FAQ; a bad canonical URL).

## The pictures of the sections and of the spreads (permission `blog:media`)

Made and set only by the `tarots-blog-images` skill (`tarots_images.py sections | spreads | section-cover |
spread-cover`, see its `references/api.md`): `GET /media-sections`, `GET /media-spreads`, `PUT
/media-sections/{slug}`, `PUT /media-spreads/{id}` with `{"immagine_id": "…", "alt": "…"}`.

The contract (server side, v9.4):

| Method and path | Body | Answer |
|---|---|---|
| `GET /media-sections` | | every section, hidden ones too: `[{"id", "slug", "nome", "tipo", "filtro", "descrizione", "percorso", "visibile", "immagine": {"url", "mini", "alt"} \| null}]` |
| `PUT /media-sections/{slug}` | `{"immagine_id": "<uuid from POST /media>", "alt": "…"}` or `{"immagine_base64": "…", "alt": "…"}`; `alt` 3–200 characters, required | `{"slug", "immagine": {"url", "mini", "alt"}}` |
| `GET /media-spreads` | | every spread, in English: `[{"id", "slug", "nome", "descrizione", "origine", "tradizione", "categoria", "n_carte", "immagine": {…} \| null}]` |
| `PUT /media-spreads/{id}` | as for a section; `{id}` is the spread's id (`croce-celtica`) or English slug (`celtic-cross`) | `{"id", "slug", "immagine": {"url", "mini", "alt"}}` |

`null` means the picture is missing. A second `PUT` replaces the picture (the old one stays among the media). Errors:
`403` without `blog:media`, `404` for an unknown section or spread, `422` without an image or with a bad one. Every
change is recorded with its before and after.
