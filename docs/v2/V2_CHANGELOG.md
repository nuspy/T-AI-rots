# V2 — registro del porting in Next

## Architettura

- Il sito (v1) è in `frontend/app/(sito)`, la v2 in `frontend/app/(v2)/v2`: due layout radice nella stessa app
  (si passa dall'uno all'altro ricaricando la pagina). Il 404 degli indirizzi sconosciuti fuori da `/v2` è
  `app/global-not-found.tsx` (`experimental.globalNotFound`).
- Il codice della v2 sta in `frontend/v2/`: `i18n/` (dizionari), `lib/` (lingua, hook, percorsi, dati pubblici,
  metadati), `componenti/` (testata, piede, dock, carte, dialoghi, banner, Markdown del blog), `lettura/` (la lettura
  e la lettura delle proprie carte), `pagine/` (le viste).
- Stile: `app/(v2)/v2/v2.css` (il design system del prototipo, esteso: moduli, dialoghi, dock, liste), più moduli CSS
  per lettura, carte e blog. Caratteri Libre Baskerville e DM Sans (next/font).
- Il prototipo statico (`public/v2`) è stato spostato in `docs/v2/prototipo-statico/` come riferimento.

## Lingue

- Dizionario separato da quello del sito: `frontend/v2/i18n/<lingua>/<sezione>.ts`. Tradotte davvero: inglese
  (base), italiano, ungherese. Le altre dodici lingue sono copie dell'inglese generate da
  `node v2/i18n/copia-inglese.mjs` (una riga «COPIA DELL'INGLESE» in cima; toglierla quando si traduce).
- Il tipo è quello dell'inglese: una chiave che manca in una lingua è un errore di compilazione.
- Inglese e italiano sono nel pacchetto; le altre lingue si caricano quando servono.
- La lingua: `/it/v2` → italiano; poi la scelta salvata (la stessa chiave del sito), la lingua del browser, quella
  del server. I contenuti editoriali (blog, testi di carte e stese) esistono in italiano e inglese.

## API riusate (nessuna modifica di contratto)

Letture (anonima e con account, intervista, ventaglio con taglio, scelta, rivelazione e sintesi in streaming,
carte manuali), carte, stese, mazzi, voto, negozio e ordini (PDF), piani, pagamento, codici, saldo e movimenti,
profilo, indirizzi, memoria, chat proattiva, condivisione (immagine, clic, visite, attribuzione), consensi,
statistiche, impostazioni pubbliche, blog (articoli, sezioni, etichette, collegamenti).

## Riusato dal sito senza copia

`lib/api.ts`, `lib/sessione.tsx`, `lib/condivisione.ts`, `lib/inviti.ts`, `lib/analytics.ts`, `lib/sicurezza.ts`,
`lib/mazzo-attivo.tsx`, `lib/i18n/lingue.ts` e `nomi.ts` (metadati delle lingue e nomi di carte/stese dai dati),
e i componenti senza testi né collegamenti: attribuzione delle condivisioni, riscatto degli inviti, Markdown del
responso, composizione dell'immagine di condivisione e del bigliettino d'invito, loghi dei social.

Due ritocchi compatibili al codice condiviso: `impostaMessaggiErrore()` in `lib/api.ts` (i due messaggi d'errore
dell'API dal dizionario v2) e `ritorno2fa` in `SessioneKeycloak` (la v2 torna al proprio profilo). Il sito si
comporta come prima.

## Analytics

Stesso osservatore (`lanterna`), eventi della specifica v2 dove il prodotto li produce davvero:
`question_started`, `question_submitted`, `reading_started`, `shuffle_started`, `shuffle_interrupted`,
`deck_cut`, `card_drawn`, `card_revealed`, `reading_completed`, `physical_reading_started`, `signup_started`,
`memory_viewed`, `memory_updated`, `followup_started`, `share_started`, `share_completed`, `paywall_viewed`,
`package_selected`, `subscription_started`, `purchase_completed`, `deck_viewed`, `deck_pdf_viewed`, `qr_entry`,
più `lettura_fase` come nel sito. Nuovi imbuti in console: `lettura_v2` e `acquisto_v2`; l'imbuto della lettura
del sito ora conta solo gli eventi di `/leggi`.

## Limiti noti

- Le pagine della v2 leggono i dati nel browser (sono un'anteprima non indicizzata): niente dati strutturati né
  hreflang. Per sostituire il sito servirà riportare il rendering dal server delle pagine pubbliche.
- Una lettura anonima non si riprende dopo un ricaricamento (come nel sito).
- I mazzi futuri elencati come «planned» vengono dalla specifica, non dall'API.
