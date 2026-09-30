# V2 — mappa delle rotte

La v2 vive dentro l'app Next (`frontend/app/(v2)/v2`, layout radice proprio), sotto `/v2`; in italiano sotto
`/it/v2` (il proxy riscrive e imposta la lingua). È un'anteprima **non indicizzata** (`noindex` nel layout, `/v2` e
`/it/v2` esclusi in `robots.txt`). Il prototipo statico da cui nasce è in `docs/v2/prototipo-statico/`.

Nessun collegamento della v2 porta al sito quando la v2 ha la pagina corrispondente: gli indirizzi stanno in
`frontend/v2/lib/percorsi.ts` (`R`), e i collegamenti scritti negli articoli del blog verso il sito si traducono con
`inV2()`.

| Sito (v1) | V2 | Perché cambia |
| --- | --- | --- |
| `/` · `soglia.tsx` | `/v2` | La domanda prima di tutto; il rito visibile, con la dichiarazione «ogni carta è una carta vera»; memoria, differenza, mazzi, carte fisiche, metodo, gratuito → lettura completa, condivisione, diario, domande. Niente barre d'iscrizione ripetute. |
| `/leggi` · `leggi/*` | `/v2/read` | Conversazione a sinistra, console del rito a destra. La lettura anonima vera è il percorso principale; l'iscrizione arriva dopo la prima risposta. Parametri: `?question ?topic ?type ?spread ?card ?deck ?source ?id`. |
| `/interpreta` | `/v2/physical-reading` | Le proprie carte come percorso secondario ben visibile; bozza conservata durante l'accesso. |
| `/letture`, `/letture/[id]`, memoria in `/profilo` | `/v2/my-story`, `/v2/my-story/[id]` | Le letture e la memoria insieme: «Your reader remembers your story», visibile e gestibile. |
| `/s/[token]` | `/v2/shared/[token]` | La condivisione come porta d'ingresso: invito alla propria lettura gratuita, attribuzione e visite verificate come nel sito. Il link condiviso dalla v2 porta qui. |
| `/carta-del-giorno`, `/card-of-the-day` | `/v2/daily-card` | Piccolo incontro senza account; porta a una domanda più ampia. |
| `/carte`, `/carte/[id]` | `/v2/cards`, `/v2/cards/[id]` | La carta prima, poi la domanda («Read this card in a ritual»). |
| `/stese`, `/stese/[id]` | `/v2/spreads`, `/v2/spreads/[id]` | La forma che aiuta la domanda; porta alla lettura con quella stesa. |
| `/mazzo` (vetrina + negozio) | `/v2/decks`, `/v2/decks/[slug]`, `/v2/shop` | Casa di più mazzi separata dal negozio; il negozio è un'estensione fisica, secondaria. |
| `/vota-mazzo` | `/v2/vote` | Il voto come parte dell'architettura multi-mazzo. |
| `/piano`, `/pricing` | `/v2/pricing` | Continuità dopo il valore: gratuito, pacchetti, abbonamenti; codici, saldo, movimenti; ritorno alla lettura dopo il pagamento. |
| `/blog`, `/blog/[slug]`, `/blog/sezione/[slug]`, `/blog/tag/[slug]` | `/v2/blog`, `/v2/blog/[slug]`, `/v2/blog/section/[slug]`, `/v2/blog/tag/[slug]` | Il diario come grafo di contenuti che riporta a una domanda. |
| — | `/v2/explore` | L'ingresso del grafo: diario, carte, stese, mazzi, carta del giorno, carte proprie. |
| `/profilo` | `/v2/profile` | Parità completa (carte personali, genere, persona ricordata, immagine, 2FA, registro, mazzo, inviti, condivisioni, ordini con PDF, indirizzi, statistiche); la memoria è in My story. |
| `/privacy` | `/v2/privacy` | Stesse scelte legali; in più che cosa ricorda il lettore e come si usa l'AI. |
| 404 | `/v2/[...resto]` → 404 della v2 | Gli indirizzi sconosciuti sotto `/v2` restano nella v2. |

Elementi globali: il **dock del lettore** (ingresso conversazionale su ogni pagina che non ne ha già uno: anonimo →
lettura gratuita; con account → chat proattiva vera), il banner dei cookie, il promemoria della 2FA, l'osservatore
degli analytics, l'attribuzione delle condivisioni e il riscatto degli inviti (`?invito=` sulla home della v2).
