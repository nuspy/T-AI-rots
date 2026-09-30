# The image endpoints (REST v1, permission `blog:media`)

All requests carry `Authorization: Bearer tk_live_…` (or `X-API-Key`). Base: `TAROTS_API_URL` + `/v1/blog`.
A `blog:media` key works on **every** article, published or not, but changes **only pictures**: the text changes
only on the lines that hold a picture, and the previous version is kept by the server.

| Method and path | What it does |
|---|---|
| `GET /media-posts?stato=&lang=&pagina=&per_pagina=` | Every article: `id`, `slug`, `titolo`, `lang`, `stato`, `sezione`, `parola_chiave`, `tags`, `url`, `estratto`, `copertina` (`id`, `url`, `mini`, `alt` or null), `immagini_nel_testo` (`indice`, `alt`, `url`). Paged: `totale`, `pagina`, `per_pagina` (≤ 100). |
| `GET /media-posts/{id}` | The same for one article, plus the whole `testo` (Markdown). |
| `POST /media` | Upload a picture: raw body with `Content-Type: image/png|jpeg|webp`, or JSON `{"immagine_base64": "…"}`. Answers `id`, `url`, `mini` (the list thumbnail, made by the server), `larghezza`, `altezza`. 8 MB at most. |
| `PUT /posts/{id}/cover` | `{"immagine_id": "…" or "immagine_base64": "…", "alt": "…"}` → the cover and its alt text change; nothing else. |
| `PUT /posts/{id}/inline` | `{"sostituisci": [{"indice": 0 or "url_attuale": "…", "immagine_id"/"immagine_base64", "alt"?}], "aggiungi": [{"dopo_paragrafo": 0, "immagine_id"/"immagine_base64", "alt"}], "rimuovi": [2]}`. Indices refer to the text **before** the change. Paragraphs are blocks separated by a blank line, from 0. Answers the article with the new `testo` and `immagini_nel_testo`. |

Errors: `401` wrong or revoked key · `403` the key lacks `blog:media` · `404` no such article or picture ·
`422` a picture number or paragraph that does not exist (nothing is changed) · `429` too many requests.

Pictures in the text are ordinary Markdown on a line of their own: `![alt text](/blog/media/<id>.webp)`.
Each picture has a thumbnail at `/blog/media/<id>-mini.webp` (480 px wide) used by the blog lists.
