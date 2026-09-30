# Backlog v8

## 0. Blog: niente filtro per lingua (2026-09-30)

Gli articoli del blog sono e restano **solo in inglese**: non vanno filtrati per la lingua scelta
nel selettore dell'interfaccia, vanno mostrati comunque. **Implementato** (2026-09-30): rimosso il
parametro `lang` dalle query di elenco articoli (`/blog`, `/blog/sezione/[slug]`, `/blog/tag/[slug]`,
`/blog/feed.xml`); la pagina del singolo articolo già reindirizzava alla sua lingua vera (invariata).
Conseguenza SEO decisa dopo ricerca (vedi nota sotto): niente `hreflang` fra `/blog` e `/it/blog` (non
sono una traduzione, è la stessa lista), canonical delle liste in italiano → versione inglese, per
non far indicizzare due indirizzi con contenuto identico. Le sezioni di tipo «carte»/«stese» restano
davvero tradotte (il catalogo lo è) e mantengono l'hreflang; le sezioni «articoli» e le etichette
(nessuna lingua propria) seguono lo stesso trattamento del blog.

**Ricerca SEO fatta prima di questa modifica (2026-09-30)**, sintesi delle raccomandazioni applicate
o ancora aperte:
- `priority`/`changefreq` nella sitemap non contano più per Google: `app/sitemap.ts` (dinamica, non
  statica) resta la scelta giusta, già in uso.
- Un contenuto esistente in una sola lingua **non richiede `hreflang`**: nessun rischio di duplicate
  content nel non dichiararlo (diverso da avere due lingue e dimenticare il collegamento reciproco).
- `rel=next/prev` è deprecato/ignorato da Google: la paginazione del blog (canonical
  auto-referenziale per pagina, già implementato) resta il pattern corretto.
- JSON-LD va scritto in Server Component (già così in questo progetto).
- **Aperto, da decidere con l'operatore, non ancora implementato**: distinguere nel `robots.ts` i
  crawler AI di **addestramento** (`GPTBot`, `Google-Extended`, `ClaudeBot` — bloccabili senza perdere
  visibilità) da quelli di **ricerca/citazione** (`OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`
  — da lasciare passare per comparire nelle risposte AI). È una scelta di prodotto, non solo tecnica.
- `llms.txt` (già presente in `app/llms.txt`) ha oggi ritorno minimo: i crawler AI principali non lo
  seguono ancora, leggono l'HTML direttamente — non serve altro investimento lì per ora.
- Attenzione per la pipeline di generazione articoli del blog: Google penalizza volume di contenuto
  sottile/templated, non l'uso di AI in sé — qualità/originalità contano più del numero di articoli.

## 1. Blog: paginazione lato admin (dal backlog dettato il 2026-09-29)

La lista degli articoli in admin non deve caricare tutti gli articoli insieme, ma pagine con un
navigatore fra le pagine. **Verificato (2026-09-30): già implementato** — `admin/app/blog/page.tsx`
pagina davvero lato server (`GET /admin/blog/posts` con `pagina`/`per_pagina`, default 25, non 10 ma
lo stesso principio), con navigatore "Precedente/Successiva" e conteggio pagine/totale. Nessun lavoro
necessario; il backlog era stato scritto senza sapere che era già stato fatto in una sessione
precedente.

## 2. Pubblicazione automatica sui motori di ricerca (dal backlog dettato il 2026-09-29)

Sistema di pubblicazione sui motori di ricerca degli articoli pubblicati, quando vengono autorizzati
(o inseriti direttamente con autorizzazione alla pubblicazione), con una pagina GUI in admin per
verifiche e gestione. **Decisione esplicita dell'operatore**: va costruito come **progetto separato e
riutilizzabile** (una libreria, non codice incorporato in T-AI-rots), da importare qui e integrare —
così da poterlo riusare in altri progetti.

**Ricerca fatta (2026-09-30)**, prima di decidere cosa costruire:
- **Google Indexing API** (`urlNotifications`): resta ufficialmente limitata a `JobPosting` e
  `BroadcastEvent` — un blog generico non rientra nell'uso supportato. **Da non costruire**: userlo
  per articoli normali è un uso non supportato, rischioso da offrire come funzione di prodotto.
- **Sitemap ping classico** (`google.com/ping?sitemap=`): **morto**, l'endpoint risponde 404 da
  agosto 2026 (Google lo ha deprecato nel 2023). L'alternativa reale è la **Search Console API,
  risorsa `sitemaps.submit`** — richiede credenziali OAuth/service account da configurare una tantum.
- **IndexNow** (Bing, Yandex, e altri — non Google): protocollo semplice (un POST JSON con host,
  chiave, elenco URL, chiave verificata via file statico). Nessuna libreria Python matura da cui
  dipendere in modo affidabile (la più stellata ha 8 stelle, la più moderna/adatta a FastAPI non è
  ancora rilasciata) — **conviene scrivere un client minimale in casa** (poche righe: payload, POST,
  retry) piuttosto che dipendere da un pacchetto fragile o immaturo. Questo client scritto in casa È
  la "libreria separata riutilizzabile" richiesta.
- **WebSub** (ex PubSubHubbub): ancora vivo e mantenuto nel 2026, non è indicizzazione diretta ma
  propagazione push del feed RSS/Atom — aggiunta a basso sforzo dato che il feed (`/blog/feed.xml`)
  esiste già; complementare, non alternativo agli altri due.

**Proposta di architettura (da confermare con l'operatore prima di scrivere codice)**:
1. Nuovo progetto Python separato (nome e posizione da decidere insieme — non creato in autonomia:
   comporta una scelta di repository/naming che spetta all'operatore), con tre funzioni indipendenti:
   client IndexNow (Bing/Yandex), client Search Console API (`sitemaps.submit`, Google), ping WebSub
   sul feed RSS. Nessuna delle tre richiede le altre: si possono attivare separatamente.
2. In T-AI-rots: un piccolo hook nel flusso di pubblicazione articolo (`admin_blog.py`, quando uno
   stato passa a "pubblicato") che chiama la libreria; una pagina admin che mostra l'esito delle
   ultime notifiche (successo/errore per motore) e permette un invio manuale di riprova.
3. Le credenziali (chiave IndexNow, service account Search Console) vanno in un Secret k8s, non nel
   codice né in un endpoint modificabile da console (stesso principio già seguito per le chiavi LLM,
   vedi `deploy/k8s/LEGGIMI.md`).

**Fatto (2026-09-30)**: il progetto separato esiste — `E:\Projects\seo-notify` (repository git locale
proprio, non ancora un remote GitHub: quella scelta resta dell'operatore), pacchetto Python
`seo_notify` con i tre canali (`ClientIndexNow`, `notifica_hub`, `sottometti_sitemap`), zero
dipendenze per IndexNow/WebSub, extra opzionale `[search-console]` per quello. 9/9 test verdi
(mockati, nessuna chiamata di rete reale nei test). README con esempi d'uso.

**Collegato in T-AI-rots (2026-09-30)**, su indicazione dell'operatore: gli articoli escono a gruppi
(3 alla volta), quindi **niente notifica a ogni pubblicazione ma un giro al giorno a mezzanotte**, in
automatico. Implementazione:
- CronJob k8s `tarots-notifica-motori` (`0 0 * * *`, `Europe/Rome`) → `python -m
  tarot_core.tools.notifica_motori`; logica in `tarot/notifiche_motori.py`. La finestra parte
  dall'esecuzione precedente (un giro saltato non perde articoli); senza novità non parte nulla.
- Registro degli invii nella tabella `notifiche_motori`; console admin → **SEO**: stato dei canali,
  storico, «Invia ora».
- IndexNow attivo (chiave pubblica in `frontend/public/<chiave>.txt`); WebSub attivo (hub dichiarato
  nel feed RSS); **Search Console in attesa del service account** dell'operatore (procedura in
  `deploy/k8s/LEGGIMI.md`, "Notifica ai motori di ricerca").
- `seo-notify` entra nell'immagine dal contesto di build (accanto a `backend/`), resta un progetto
  separato. Ancora da decidere: pubblicarlo come repository proprio (GitHub/GitBucket).

## 3. Oracolo: widget ancorato in fondo pagina (dal backlog dettato il 2026-09-29)

Il componente Oracolo non va più aperto/chiuso al click come oggi: va **ancorato al fondo pagina**, a
sostituzione del componente "Ask me something, I'll give you a free reading" (che lascia la stessa
scritta). Resta visibile anche agli utenti non loggati, con una serie di messaggi generici già
esistenti in i18n (ne esistono già decine). Se un utente non loggato risponde o scrive, l'app deve
continuare con l'AI come per un utente loggato. Per gli utenti loggati, usare le memorie per creare
opportunità di dialogo. **Non ancora implementato**: da riconciliare con la Fase D di v7 (banner
"Ask something" ancorato in basso, già fatta) — probabilmente questo punto la assorbe/sostituisce
piuttosto che coesistere con essa; da chiarire con l'operatore prima di scrivere codice.

---

# Backlog v8 — Analytics e statistiche

Registrato verbatim dalle istruzioni dell'operatore (2026-09-29), dettate durante l'implementazione
di v7.

**Stato (2026-09-30)**: progettato insieme all'operatore (piano «lanterna»: raccoglitore nostro,
visite dei registrati legate all'account per legittimo interesse con informativa, libreria
`lanterna` in `E:\Projects\lanterna`, paese e città da DB-IP, Colab con notebook scaricato,
raccolta in produzione prima del resto). Fasi:

- **F0 fondamenta — fatto.** Libreria (schema congelato v1, impronta giornaliera, canali, UA, geo),
  tabelle `an_*` via `domain/analytics_models.py` e migrazione `2556daf22909`, `ip_client` unico
  (`lanterna.rete`) nei router admin, consenso e condivisioni al posto di `request.client.host`,
  Dockerfile (lanterna + DB-IP con `GEO_MESE`), LEGGIMI.
- **F1 raccolta traffico + privacy — fatto.** `POST /e` e `/e/dimentica` (`api/routers/analytics.py`),
  osservatore JS `lanterna-osservatore` montato in `providers.tsx` (entrambi i rami), livello esteso
  acceso da «It's fine», sezione «Statistiche di utilizzo» nell'informativa (it/en/hu),
  `docs/privacy/lia-analytics.md`.
- **F2 eventi di business e attribuzione — fatto.** Eventi lato server (`analytics/eventi.py`):
  registrazione, lettura aperta/completata/crisi/cancellata/feedback/condivisa, checkout avviato,
  acquisto (webhook e coupon gratuito), coupon, invito, voto, carta del giorno. `lettura_fase` dal
  client, `data-an` su piano, carrello e CTA d'iscrizione. Opposizione dal profilo
  (`GET/PUT /me/statistiche`). **Da rilasciare** (primo rilascio).
- **F3-F4 interrogazioni e console — fatto.** Catalogo dichiarato (`analytics/catalogo.py`: visite,
  eventi, utenti, letture, acquisti, ordini, riepilogo; niente SQL libero, soglia k per le dimensioni
  personali, timeout 10 s), imbuti (lettura, iscrizione, acquisto, negozio) e coorti (letture, ritorni,
  spesa), riepilogo notturno e pulizia (`tools/analytics_notte.py`, CronJob 3:30). Console
  `admin/app/analytics/`: Traffico, Utenti, Imbuti, Ricavi (con coorti), Esploratore con drill-down,
  stato nell'indirizzo.
- **F5 export — fatto.** Vista corrente in CSV/XLSX, collezioni (traffico, utenti, ricavi, letture,
  rapporto) in Excel con un foglio per tabella.
- **F6 interpretazione AI — fatto.** Compito `analisi_dati` (modello scelto in Modelli), fatti numerati
  calcolati lato server (variazioni e significatività, quote e contributi, anomalie, imbuti, coorti),
  risposta verificata numero per numero, storico con giudizio e «azione adottata» che rientra
  nell'analisi successiva, contesto del business in Impostazioni. Pannello in ogni pagina.
- **F7 rapporto settimanale — fatto.** Lunedì 0:30 (CronJob), destinatari in console, AI facoltativa
  (solo voci verificate), anteprima, invio manuale, registro. SMTP Stalwart di Keycloak.
- **F8 Colab — fatto.** Token con scadenza e ambiti (solo impronta nel DB), export JSON con soglia k,
  import firmato HMAC, notebook precompilato da scaricare, pagina Studi.
- **Da fare prima del secondo rilascio**: prova a vista della console a 360 px e 1280 px (rimandata
  per memoria del PC impegnata), deploy di API/sito/console col manifest completo (CronJob notturno e
  settimanale), destinatari del rapporto. I risultati importati da Colab non entrano ancora come fatti
  nell'interpretazione AI.

## 4. Statistiche di ingresso (traffico)

Provenienza del traffico, utenti già registrati vs nuovi, utenti che ritornano sulla pagina, tempi
medi fra le visite, luogo di connessione (geolocalizzazione), tempo di permanenza sul sito, pagine
visitate per utente, pagine più visitate in totale nel tempo (assoluto, ultima settimana, ultimo
mese, ultimi X mesi, dinamica di visita alle pagine nel tempo), funzioni più utilizzate, utenti che
entrano e poi si registrano (dopo quante visite, in percentuale). Altre informazioni tipiche di
questo tipo di analisi (da determinare in fase di progettazione).

## 5. Statistiche utenti

Fasce di età, sesso, cosa comprano, provenienza (se disponibile, da IP o altro), incroci fra età /
sesso / provenienza / campagna (referral o ID campagna) e media per campagna. Funzioni più usate,
pagine più visitate. Altri dati tipici di questo genere di statistiche.

## 6. Grafici interattivi e incrocio dinamico dei dati

Statistiche di entrate e utenti con grafici adeguati e interattivi; possibilità di incrociare i dati
dinamicamente per studi ad hoc (non solo viste precostituite).

## 7. Export ed invio automatico

- Export dei dati visualizzati (qualunque vista/grafico corrente).
- Export di collezioni di dati standard — da determinare quali sono utili esportare
  automaticamente in fase di progettazione.
- Cron job che invia questi dati a una lista di email in automatico ogni domenica notte.

## 8. Ricerca di mercato

Ricerca online su quali funzioni e quale raccolta dati offrono i pacchetti commerciali per analisi
degli ingressi (web analytics) e analisi clienti (CRM/customer analytics) — da fare come parte della
progettazione, prima di scegliere cosa costruire.

## 9. Google Colab per BI e interpretazione automatica

Idea dell'operatore (2026-09-29): esportare dati verso Google Colab (https://colab.research.google.com)
e predisporre notebook/algoritmi di analisi per business intelligence e interpretazione automatica.
Due modalità coesistenti: apertura diretta del link Colab, e importazione dei risultati delle analisi
fra le statistiche della GUI admin.

Obiettivi indicati per i notebook: ottimizzare le campagne, rafforzare le aree del sito di maggiore
interesse per il pubblico, analizzare gli utenti (inclusi quelli che si iscrivono e quelli già
iscritti), ottimizzare la conversione da uso gratuito ad acquisto di pacchetti/abbonamenti,
individuare mercati in crescita/dominanti — in generale, tutto ciò che è utile per la crescita.

**Valutazione (2026-09-29, non dall'operatore)**: Colab è adatto all'analisi esplorativa ad-hoc
(coorti, funnel di conversione, segmentazione, trend), ma richiede l'apertura manuale di un umano —
non copre da solo il cron job automatico del punto 4 (invio email ogni domenica notte), che resta
un'automazione separata nella propria infrastruttura. L'importazione dei risultati in GUI admin è il
pezzo più delicato: serve un endpoint admin che accetti un export (con autenticazione/firma) dal
notebook, non solo l'apertura del link. Da trattare come un canale complementare all'automazione del
punto 4, non un sostituto.

## 10. Interpretazione automatica dei risultati BI da un'AI (dettato il 2026-09-30)

I risultati delle analisi (punti 4-6) devono poter essere interpretati **anche in automatico da
un'AI**, non solo guardati come numeri/grafici:
- Scelta del modello per l'analisi BI configurabile da GUI admin (stesso principio già usato per gli
  altri compiti LLM del progetto — console "Modelli", non hardcoded).
- L'analisi si fa **su richiesta**, premendo un bottone, non in automatico/periodicamente — per ogni
  singola vista/ricerca corrente (non un report generico): l'AI deve **mettere in relazione tutti i
  punti della sezione e della ricerca specifica** aperta in quel momento, non limitarsi a descrivere
  un singolo numero isolato.
- Deve essere **molto approfondita**: l'operatore ha chiesto esplicitamente di studiare **come
  ottimizzare l'utilità degli outcome** (non solo generare testo plausibile, ma un'analisi che serva
  davvero a decidere qualcosa) — questo è un punto di progettazione, non solo di prompt-engineering:
  da affrontare insieme, dato che l'intera BI è ancora da progettare (vedi Nota sotto).
- **Non ancora implementato, non ancora progettato**: dipende dall'intera architettura BI (punti 4-9),
  che non esiste ancora nel codice.

## Nota

**Decisione esplicita dell'operatore (2026-09-29)**: questo sistema di analytics/BI va costruito come
**progetto separato e riutilizzabile** (una libreria da importare in T-AI-rots e integrare, non codice
incorporato), così da poter servire anche altri progetti. La struttura va pensata con **observer
generici per le pagine**; da capire, in fase di progettazione condivisa con l'operatore, come
integrare anche le funzioni business che sono pagine ma non solo pagine (es. la lettura dei tarocchi:
acquisti, funzioni). L'operatore ha detto esplicitamente di volerne discutere insieme dopo l'analisi
("ragioniamo insieme dopo tua analisi") — non decidere l'architettura da soli.

Non ancora esplorato nel codice: da verificare se esiste già una qualche raccolta dati (log
richieste, tabella `audit_log`, ecc.) riusabile come base, o se va costruita da zero una pipeline di
tracciamento eventi. Data la portata (paragonabile a v6/v7), andrà pianificato a fasi separatamente,
con probabile bisogno di decisioni preliminari dell'operatore su: quali dati si è disposti a
raccogliere (privacy/GDPR, vedi v7 punto 5), se usare uno strumento esistente (self-hosted tipo
Plausible/Umami/PostHog) invece di costruire tracciamento e dashboard da zero, e il formato/mittente
delle email automatiche del punto 7.
