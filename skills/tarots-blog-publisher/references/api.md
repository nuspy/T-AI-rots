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
| `GET /sections` | write | Sections you can publish in (`slug`, `nome`, `percorso`) |
| `GET /tags` | write | Tags already used, with counts |
| `GET /catalog` | write | Cards and spreads with the `[[card:…]]` / `[[spread:…]]` shortcut |
| `POST /seo-check` | write | SEO report for an article body, nothing saved |
| `POST /media` | write | Upload an image (raw `image/png|jpeg|webp` body, or JSON `{"immagine_base64": "…"}`) → `{id, url, larghezza, altezza, byte}` |
| `POST /posts` | write | Create an article (`dry_run: true` → report only) |
| `GET /posts` | write | Articles created by this key (`stato`, `pagina`, `per_pagina`) |
| `GET /posts/{id}` | write | One of this key's articles, with its SEO report |
| `PATCH /posts/{id}` | write (publish for published ones) | Change fields of this key's article |
| `DELETE /posts/{id}` | write | Delete a **draft** created by this key |

## Article fields (`POST /posts`, `PATCH /posts/{id}` sends only what changes)

| Field | Type | Notes |
|---|---|---|
| `titolo` | string ≤ 200 | required. The page H1 |
| `sottotitolo` | string ≤ 300 | one-line subtitle |
| `testo` | Markdown ≤ 200 000 | no HTML. Start sections at `##`. Shortcuts `[[card:slug]]`, `[[spread:slug]]`, `[[post:slug]]`, `[[video:youtube:ID]]` (own line, YouTube only). Inline images: ordinary `![alt](url)`, the url from `POST /media` |
| `lang` | `^[a-z]{2}(-[A-Za-z]{2})?$` | default `en`; `it` for Italian |
| `sezione` | slug or id | a section of type "articoli" from `GET /sections` |
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
(draft|published|archived), publish_at, featured`, and FAQ items as `{question, answer}`.

## Response of `POST /posts`, `GET /posts/{id}`, `PATCH /posts/{id}`

```json
{
  "articolo": {"id": "…", "slug": "…", "stato": "bozza", "lang": "en", "seo_parola_chiave": "…", "...": "…"},
  "url": "https://tarots.chat/blog/…",
  "seo": {"punteggio": 88, "giudizio": "ottimo", "controlli": [{"id": "…", "esito": "ok|avviso|errore", "peso": 2, "messaggio": "…", "messaggio_it": "…"}], "suggerimenti": ["…"], "statistiche": {"parole": 1180}},
  "avvisi": ["Saved as a draft: this key has no `blog:publish` permission. …"]
}
```

## Rules the server enforces (no parameter bypasses them)

- `blog:write` alone creates drafts: `stato: "pubblicato"`, `pubblicato_il` and `in_evidenza` are ignored with an
  entry in `avvisi`. Changing an already published article needs `blog:publish`.
- A key changes and deletes only what it created; the same `404` is returned for "missing" and "not yours". Only
  drafts can be deleted.
- Images are never fetched from a URL (that would be a request from our server to an address chosen from outside):
  upload the file or send base64.
- Limits per key: requests per minute and articles per day (`GET /guide`). `429` means stop and wait.
- A `422` explains what is wrong (unknown section → the list of valid ones; a too-long FAQ; a bad canonical URL).
