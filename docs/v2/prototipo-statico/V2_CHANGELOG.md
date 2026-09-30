# TAROTS.chat V2 change log

## Scope and isolation

V2 is a self-contained static parallel implementation located only in `frontend/public/v2`.
It imports no V1 component, CSS, route or application code. It reads the existing card artwork from the shared public asset path `/cards/`; these are assets, not V1 page destinations, and no source artwork was altered.

## Design direction

- Palette: parchment `#f4efe5`, ink/plum `#20162b` / `#3c1846`, brass `#b28336`, verdigris `#19706f`, mist `#d8e7df`.
- Type: Libre Baskerville for the editorial, contemplative voice; DM Sans for concise navigation and controls.
- Layout: question and one ritual-table card are the first viewport; cards remain the central visual object while the rest of the layout is restrained and readable.
- Motion: one slow ritual orbit and interaction-led card transitions only. `prefers-reduced-motion` removes animations.

## Files created

- `index.html`, `styles.css`, `app.js`
- Static V2 route entry points under `read`, `decks`, `cards`, `physical-reading`, `explore`, `blog`, `my-story`, `pricing`, `shop`, `daily-card`, `spreads`, `shared`, and `profile`.
- `V2_ROUTE_MAP.md` and this file.

## Pages and routes

All internal user-facing destinations use an explicit V2 HTML route, for example `/v2/read/index.html`, never `/leggi`.

- Homepage: question-first acquisition, basic response, ritual preview, topics, memory, active/future decks, physical Tarot, packages, content graph, FAQ.
- Reading: conversation, interruptible local ritual preview, card selection/reveal and full-reading conversion.
- Physical reading: user-selected card positions plus question entry.
- Decks and cards: Thoth as the only available deck; future decks are labelled planned, not selectable.
- Journal/content, memory/story, packages, deck/PDF, daily card, spreads, shared/referral and account entry all have self-contained V2 destinations.

## APIs and existing functionality mapped for production integration

The static layer deliberately does not call protected services or duplicate server logic. Its production implementation should retain the existing contracts:

- Reading ritual: `/readings/anonime`, `/readings`, `/readings/{id}/interview`, `/readings/{id}/fan`, `/readings/{id}/pick`, reveal and synthesis streams.
- Manual/physical cards: existing `/readings` payload with `manual_cards`.
- Cards, spreads and decks: `/cards`, `/spreads`, `/decks`.
- Memory/profile: `/me/memories`, `/me/profile`.
- Sharing/referral: existing reading-share, share-click, shared-visit and signup-attribution endpoints.
- Plans, checkout, orders and PDF: `/plans`, `/me/checkout`, `/orders`, `/decks/{slug}/pdf`.
- Daily card and public limits: `/daily-card/today`, `/impostazioni-pubbliche`.

## Link audit

Internal page links are generated from the `routes` map in `app.js`; each value begins with `/v2/`.

Classifications found in V2 source:

- V2 internal: `/v2/.../index.html` route constants and their query-string variants.
- Shared assets: `/cards/*.webp`, `/og/tarots-chat.png`.
- External: Google Fonts only.
- APIs/backend: documented above; intentionally not invoked by this static prototype.
- Accidental V1 internal page links: none.

## Limitations

- Next serves `public` files at their exact static path. Because V1 routing/configuration must not change, the deployable static URLs are `/v2/index.html`, `/v2/read/index.html`, and so on; clean URLs such as `/v2/read?deck=thoth` require a V2 route/rewrite layer outside the permitted directory.
- Per-route title, description, canonical and OpenGraph URL are included in each static entry page. Rich structured data, live API data, authentication, actual checkout, streaming reading, referral attribution and persistent memory must be wired in a subsequent V2 application-route implementation, while preserving the listed existing API contracts.
- The interactive ritual and basic response are intentionally local UI demonstrations, not simulated claims of a completed AI reading.

## Validation performed

- JavaScript syntax check: `node --check frontend/public/v2/app.js`.
- Link scan for V1-page-style absolute hrefs and V2 route review.
- Build check: `npm run build` from `frontend`.
- Git path audit confirms no file was modified outside `frontend/public/v2` by this change.
