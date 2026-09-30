# V2 route map

Static V2 uses exact HTML entry points because it is constrained to `frontend/public/v2`. Every counterpart below stays within V2.

| V1 reference route / component | V2 counterpart | Reason for the change |
| --- | --- | --- |
| `/` · `app/page.tsx`, `soglia.tsx` | `/v2/index.html` | Reorders the home around question, conversation, ritual and continuity; removes repeated signup bars. |
| `/leggi` · `app/leggi/*` | `/v2/read/index.html` | Makes non-registered conversation and a user-driven shuffle/reveal visibly primary. |
| `/interpreta` · `app/interpreta/*` | `/v2/physical-reading/index.html` | Promotes existing manual-card intent as a clear secondary route. |
| `/mazzo` · `app/mazzo/*` | `/v2/decks/thoth/index.html`, `/v2/shop/index.html` | Separates deck discovery from commercial/PDF presentation. |
| `/carte`, `/carte/[id]` | `/v2/cards/index.html`, `/v2/cards/the-lovers/index.html` | Establishes a card-to-article-to-reading V2 content path. |
| `/stese`, `/stese/[id]` | `/v2/spreads/index.html` | Makes spread selection feed the ritual rather than a disconnected page. |
| `/carta-del-giorno` | `/v2/daily-card/index.html` | Keeps the free daily prompt as a lightweight reading entry. |
| `/blog`, `/blog/[slug]`, tags and sections | `/v2/blog/index.html`, `/v2/blog/the-lovers-and-choice/index.html`, `/v2/explore/index.html` | Frames content as a graph that leads to a card, question and reading. |
| `/letture`, `/letture/[id]`, `/profilo` | `/v2/my-story/index.html`, `/v2/profile/index.html` | Makes prior readings and user-managed memory a visible continuity experience. |
| `/piano` | `/v2/pricing/index.html` | Positions packages/subscriptions after demonstrated reading value. |
| `/s/[token]` and share panels | `/v2/shared/index.html` | Ensures V2 sharing starts a V2 acquisition path; real attribution remains server-owned. |

## Navigation map

The V2 header contains only V2 destinations:

- Read → `/v2/read/index.html`
- Decks → `/v2/decks/index.html`
- Explore → `/v2/explore/index.html`
- My story → `/v2/my-story/index.html`
- Shop → `/v2/shop/index.html`
- Start reading → `/v2/read/index.html`

## Deep-link design

The V2 UI already preserves deck, card, source, topic and spread query context in V2 URLs, for example:

- `/v2/read/index.html?deck=thoth`
- `/v2/read/index.html?deck=thoth&card=the-lovers`
- `/v2/physical-reading/index.html?deck=thoth&source=qr`

The requested clean V2 forms (`/v2/read?deck=thoth`, etc.) require a server route/rewrite and cannot be added without modifying a file outside the allowed V2 directory.
