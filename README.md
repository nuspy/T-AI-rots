# T·AI·rots

Letture dei **Tarocchi di Thoth** (Aleister Crowley) guidate da un'intelligenza
artificiale. Il flusso di una lettura:

1. **Domanda.** L'utente scrive cosa vuole chiedere.
2. **Intervista.** L'oracolo fa poche domande di contesto. Non chiede mai la
   risposta al quesito, né una previsione.
3. **Stesa.** L'utente sceglie le carte da un ventaglio. Le carte sono già
   assegnate agli slot prima della scelta.
4. **Rivelazione.** Le carte si girano una a una, ciascuna con la sua
   interpretazione immediata.
5. **Responso.** La sintesi finale unisce tutto con la tecnica **CAG**, passa
   dal **guardrail** e solo allora viene mostrata.

Frontend e backend sono separati. Il sistema è multiutente e ha una console di
amministrazione. Lo stack e le parti comuni (auth, crediti, piani, pagamenti,
fornitori LLM, guardrail, console) vengono da
[Personalities](https://github.com/nuspy/personalities) e sono state riciclate
il più possibile.

> Ogni lettura si apre e si chiude con questa avvertenza: è una lettura AI,
> coerente e rigorosa sul piano esoterico. Non è una certezza: indica il più
> probabile dei futuri. Non esiste alcuna base scientifica che dimostri la
> validità delle previsioni dei tarocchi.

## Struttura

| cartella | cosa | da Personalities |
|---|---|---|
| `backend/` | API FastAPI, SQLAlchemy async, PostgreSQL, Alembic | `settings`, `auth/` (Keycloak), `billing/` (crediti, piani, quote, pagamenti), `llm/` (fornitori e registro dei compiti), `guards/policy`, `domain/` (base, sessioni, utenti, audit), `observability/`, test |
| `frontend/` | sito Next.js 16, React 19, CSS Modules, three.js e framer-motion | provider OIDC, hook `useCarica`/`useAzione`, client API con SSE, pagina del piano |
| `admin/` | console Next.js | `guscio`, grafici SVG, statistiche, registro, modelli |
| `deploy/` | Dockerfile, realm Keycloak | Dockerfile, realm e generatore del realm di produzione |

## Avvio in sviluppo

**Con un solo comando**, senza Keycloak e col modello finto:

```bash
python tools/run_local.py    # API su :8100, sito su :3000; Ctrl+C li ferma entrambi
```

Prepara da solo `backend/.venv` (serve Python 3.11 o più recente) e
`frontend/node_modules`, applica migrazioni e seed e lancia i due servizi con i
log affiancati. Serve un PostgreSQL raggiungibile: quello di
`docker compose up -d postgres` (:5433, lo avvia da solo se Docker è attivo) o
uno locale sulla 5432 con l'utente `tarot`; altrimenti `--db <url>`. Con
`--llm-reale` usa il modello di `backend/.env`; `--help` elenca il resto.

Oppure a mano:

```bash
# 1. database, Keycloak (realm "tarots" con utenti di prova), API
docker compose up -d
docker compose run --rm api python -m tarot_core.tools.seed   # piani, pacchetti, 1000 crediti di prova

# 2. sito e console
cd frontend && cp .env.example .env.local && npm install && npm run dev    # http://localhost:3000
cd admin    && cp .env.example .env.local && npm install && npm run dev    # http://localhost:3001
```

Utenti di prova:

| utente | password | ruolo | crediti |
|---|---|---|---|
| `test@tarots.local` | `test` | user | 1000 |
| `admin@tarots.local` | `admin` | user, admin | 1000 |

**Senza Docker né Keycloak.** Servono solo PostgreSQL e Python 3.11:

```bash
cd backend && python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
export TAROT_DATABASE_URL=postgresql+psycopg://tarot:tarot@localhost:5432/tarot
export TAROT_AUTH_DISABLED=true TAROT_LLM_FINTO=true   # utente di sviluppo (admin), modello finto
.venv/bin/alembic upgrade head && .venv/bin/python -m tarot_core.tools.seed
.venv/bin/python -m tarot_core.api --port 8100
# e nel frontend / admin: NEXT_PUBLIC_AUTH_DISABLED=true npm run dev
```

**I modelli** si configurano in `backend/.env` (vedi `.env.example`):

- `TAROT_LLM_PROVIDER` può essere `anthropic` oppure un server OpenAI-compatibile (OpenAI, LM Studio, vLLM, llama.cpp).
- In alternativa, `TAROT_MODELLI` dichiara un elenco di modelli. La console
  (**Modelli**) assegna poi un modello a ciascun compito: `intervista`,
  `validazione`, `interpretazione`, `sintesi`, `giudizio`. È il registro dei
  fornitori di Personalities, dove si innesta llmswitch.

## Deploy

`deploy/k8s/tarots.yaml` porta tutto su k3s (sito, API, Keycloak e un gateway
nginx) sotto un solo dominio, con il PostgreSQL già presente nel cluster. La
procedura, le immagini e i segreti sono in `deploy/k8s/LEGGIMI.md`; il realm di
produzione di Keycloak (`deploy/keycloak/realm-tarots.prod.json`) si rigenera
come spiegato in `deploy/keycloak/README.md`.

## Il dominio esoterico

- **Il mazzo** è in `backend/tarot_core/knowledge/deck.json`: 78 carte del Thoth con le attribuzioni reali.
  - Maggiori: lettera ebraica, sentiero sull'Albero della Vita. Vale «Tzaddi non è la Stella»: l'Imperatore prende Tzaddi e la Stella prende He.
  - Minori: sefira e decano (per esempio Marte in Ariete per il Due di Bastoni, «Dominio»).
  - Figure di corte: gli archi zodiacali e i quadranti delle Principesse.
  - Ogni carta ha significati su più livelli (essoterico, psicologico, iniziatico, ombra), testi per dritta e rovescia, e ambiti di lettura (amore, lavoro, spirito).
- **La dottrina** è in `knowledge/doctrine.md`: la struttura del mazzo, le **dignità elementali** di Crowley, l'uso dei rovesci come complemento moderno, numeri, corti, tempi, principi di sintesi ed etica della lettura.
- **Le cinque stese** sono in `knowledge/spreads.json`:

| stesa | carte | mazzo | note |
|---|---|---|---|
| Tre carte | 3 | 22 maggiori | passato, presente, futuro |
| Croce semplice (Wirth) | 4 + 1 | 22 maggiori | la 5ª carta è la **somma teosofica** delle altre, con la «doppia valenza» se è già uscita |
| Ferro di cavallo | 7 | 78 | dal passato all'esito, con ostacolo e consiglio |
| Croce Celtica (Waite) | 10 | 78 | la croce e il bastone, con le coppie da leggere insieme |
| Ruota astrologica | 12 + 1 | 78 | le dodici case e il significatore al centro |

- **Rovesci e dignità.** Crowley non usava i rovesci. Qui ci sono entrambi: il
  rovescio come espressione bloccata o interiorizzata della carta, e le
  dignità elementali calcolate lungo le linee di ogni stesa
  (`tarot/dignita.py`).
- **Il mazzo fissato.** Quando si apre il ventaglio, il server mescola le
  carte con il generatore casuale del sistema e fissa carta e orientamento di
  ogni slot. Pubblica poi l'hash SHA-256 dello stato del mazzo con un sale.
  Il frontend riceve solo gli indici degli slot. A lettura conclusa si
  rivelano mazzo e sale, e chiunque può verificare che nessuna carta sia
  cambiata dopo la scelta.

## Il flusso sul server

| passo | endpoint |
|---|---|
| apertura, pagamento, disclaimer | `POST /readings` (402 se mancano crediti) |
| intervista | `POST /readings/{id}/interview` |
| mescolamento e ventaglio | `POST /readings/{id}/fan` |
| scelta di una carta | `POST /readings/{id}/pick` |
| rivelazione e lettura immediata (SSE) | `POST /readings/{id}/reveal/{pos}` |
| responso CAG col guardrail (SSE) | `POST /readings/{id}/synthesis` |
| storico, diario, condivisione, cancellazione | `/me/readings…` |

- **Intervista.** La regola «mai chiedere la risposta al quesito» è difesa in
  tre modi:
  1. il prompt la dichiara;
  2. un controllo deterministico scarta le domande che ricalcano il quesito o
     chiedono una previsione;
  3. un modello di validazione separato giudica ogni domanda candidata.

  Una domanda scartata viene rigenerata; se il modello non risponde o insiste
  con domande vietate, l'intervista fallisce con un errore chiaro (503) e la
  lettura resta salvata: **non ci sono domande di riserva fisse**. Le domande
  sono da 2 a 6 (`TAROT_INTERVISTA_MIN_DOMANDE`, `TAROT_INTERVISTA_MAX_DOMANDE`)
  e quante ne servano lo decide il modello in base al quesito.
- **Senza modello non c'è lettura.** Domande, letture per posizione e responso
  li scrive un modello. Senza un modello configurato `POST /readings` risponde
  503 e non addebita nulla; il modello finto (`TAROT_LLM_FINTO`) è solo per
  sviluppo e test. La lettura di ogni carta e il responso ricevono il colloquio
  integrale (domande e risposte), l'orientamento (dritta o rovesciata) e il
  significato della posizione nella stesa.
- **Mescolata e taglio.** Chi consulta ferma la mescolata cliccando il mazzo e
  poi lo taglia cliccando nel punto voluto: `POST /readings/{id}/fan` riceve la
  frazione `taglio` e il server la applica **prima** del commitment.
- **CAG.** Il prefisso stabile contiene il ruolo, le regole dei guardrail e la
  dottrina di lettura: nient'altro. È identico a ogni lettura e resta in cache
  presso il fornitore (`cache_control` di Anthropic, o la KV-cache di un motore
  locale). **Non contiene le stese né il mazzo**: una lettura ne usa una e dieci
  carte, e il resto sarebbe rumore che costa token. Dopo il confine di cache
  arrivano solo i dati della lettura:
  - la domanda, il colloquio e il quadro dell'intervista;
  - il profilo (carta dell'anima e dell'anno);
  - la stesa scelta, con le sue regole e le sue coppie di posizioni;
  - le carte estratte, ciascuna con la scheda del suo orientamento;
  - l'ordine del racconto (vedi sotto);
  - le dignità, le prevalenze e la sintesi di Wirth.

### Cosa si passa al modello: lo sceglie il codice

Per ogni carta il messaggio porta **solo i valori di quella posa esatta**, scelti
in modo deterministico (`tarot/schede.py`, `tarot/interpretazione.py`,
`tarot/cag.py`):

- il significato di *quella* posizione nella stesa, non delle altre;
- la scheda della carta per *l'orientamento uscito*: dritta (significato dritto e
  tre livelli) **oppure** rovesciata (significato rovesciato, ombra, energia di
  base), mai entrambi;
- la dignità rispetto alle vicine già girate, e le regole di coppia che toccano
  quella posizione **solo se l'altra carta è già visibile**.

Il modello non cerca né sceglie niente: meno token, e nessuna occasione di
leggere «rovesciata» una carta dritta o di dare a una posizione il significato
di un'altra. Nella **Croce Celtica la carta 2** (posata di traverso: ciò che si
oppone o si aggiunge) **si legge sempre dritta** (`senza_rovescio` in
`spreads.json`): la regola è del codice, non dello slot.

### Il responso è una storia

Ogni stesa dichiara in `spreads.json` il suo `racconto`: l'ordine in cui le
posizioni si raccontano (nella croce semplice 3-1-2-4-5, nella Croce Celtica
fondamento, passato, presente, sfida…). Il messaggio del responso contiene
l'«Ordine del racconto»: una riga per tappa con posizione, carta, orientamento e
il suo valore in una frase. Il prompt chiede di legare le tappe con nessi
espliciti, così da avere un filo — per esempio *stasi → rovina → fine di un
periodo → successo* diventa «hai un momento di stasi che porta a una rovina; ma
quella fine apre un nuovo inizio in cui puoi avere successo» — e non un elenco di
significati. Il colloquio si intreccia nel discorso.

### La lingua è quella del quesito

L'interfaccia e la lettura hanno lingue diverse. La **lingua della lettura** è
quella in cui è scritto il quesito: la ricava il server **una volta**, all'apertura
(`tarot/lingue.py`, deterministico: script Unicode più parole e lettere
caratteristiche, senza chiamare un modello), la salva in `Reading.lang` e la
restituisce nella risposta di `POST /readings`. Da lì la leggono l'intervista, le
interpretazioni, il responso e i testi fissi (disclaimer, aiuto in caso di crisi).
Ogni nuovo quesito è una nuova lettura e rinnova la lingua. Senza indizi vale la
lingua dell'interfaccia. Domande, interpretazioni e responso escono quindi nella
lingua del quesito anche se il sito è in un'altra.

Sono supportate 15 lingue (it, hu, en, de, ru, uk, fr, es, pt, ro, pl, zh, hi,
ko, ar). I testi fissi del server e i nomi di carte, stese e posizioni
(`knowledge/nomi.json`) sono **tradotti davvero solo in italiano, inglese e
ungherese**; nelle altre lingue ricadono sull'inglese (i nomi di Thoth), mentre
le risposte del modello sono comunque nella lingua del quesito. Il filtro di
crisi riconosce le formule di tutte e quindici.
- **Guardrail.** Le regole sono in `backend/data/guards/*.md`, nel formato di
  Personalities: la sezione istruzioni va nel prompt, la sezione verifica è la
  rubrica del giudice. Coprono crisi e autolesionismo, salute, diritto e
  denaro, fatalismo, autonomia e dipendenza.
  - Una domanda o una risposta con segnali di crisi ferma la lettura, mostra i
    numeri di aiuto e restituisce il credito.
  - Il responso passa dal giudice. L'esito può essere: ok, riscrivi (una
    volta, con i vincoli), oppure blocca (messaggio sicuro).

## Crediti e abbonamenti

Una lettura usa **la quota giornaliera dell'abbonamento**, se ce n'è ancora,
altrimenti **un credito**. Se non c'è né l'una né l'altro, il server risponde
402 e l'interfaccia propone l'acquisto, sia prima di iniziare sia a fine
lettura. Il catalogo si crea con il seed:

- **Piani:** Gratuito (solo la carta del giorno), Mensile Base (3 letture al giorno), Mensile Oro (10 al giorno).
- **Pacchetti:** 5, 15 o 50 letture, senza scadenza.

In questa versione i pagamenti sono **simulati**: il `PagamentiSimulati` di
Personalities ha un checkout ospitato dall'API ed eventi firmati HMAC. Un
fornitore vero, come Stripe, si aggiunge implementando `ProviderPagamenti`.

## Le immagini delle carte

Le carte sono immagini **WebP 9:16** (per esempio 360×640 px) in
`frontend/public/cards/`: `{id}.webp` per le 78 facce e `dorso.webp` per il
dorso. Se il dorso manca il frontend ne disegna uno di ripiego.

Gli originali (1440×2560) stanno in `Cards/`; per il sito si rimpiccioliscono al
25% in WebP con perdita:

```bash
python tools/resize_cards.py    # Cards/*.webp -> Cards/web/*.webp, poi copiali in frontend/public/cards/
```

**I prompt per le immagini** sono in
`frontend/public/cards/prompts.json`: una voce per carta con `file`
(`{id}.webp`), `name`, `top_text`, `bottom_text`, `font` (Cinzel), `width`,
`height`, `prompt` e `negative_prompt`, tutto in inglese. Ogni prompt è
autonomo: ripete per intero lo stile comune, l'identità esoterica della carta,
la scena con i simboli spiegati e il testo da scrivere col suo font. Le scene
sono in `backend/tarot_core/knowledge/immagini/scene_*.py`; il file si rigenera
con:

```bash
cd backend && python -m tarot_core.tools.prompt_immagini
```

Salva ogni immagine con il nome indicato in `file`. Il prompt del dorso è in
`frontend/public/cards/prompt-dorso.json`.

## Funzioni per la viralità, già incluse

- **Condivisione.** Un link pubblico anonimo alla lettura, senza intervista e
  senza nome, più un'**immagine 1080×1350** generata nel browser per le storie
  di Instagram e TikTok (Web Share API).
- **Carta del giorno** gratuita, con la **serie** dei giorni consecutivi.
- **Inviti.** Chi invita e chi si iscrive con il codice ricevono 3 letture a
  testa.
- **Diario.** «Si è avverato?» per ogni lettura. I risultati aggregati sono
  nella console.
- **Carta dell'anima e dell'anno** dalla data di nascita, usate anche come
  contesto delle letture.
- **Pagine pubbliche** delle 78 carte, porte d'ingresso dalla ricerca.
- **Verifica crittografica** del mazzo: un argomento di fiducia raro fra le app
  di tarocchi.
- Interfaccia in **quindici lingue** (traduzioni reali: italiano, inglese,
  ungherese; le altre ricadono sull'inglese), con la lingua del quesito che
  decide quella della lettura.

## Test

```bash
cd backend && TAROT_TEST_DATABASE_URL=postgresql+psycopg://tarot:tarot@localhost:5433/tarot_test \
    .venv/bin/python -m pytest
cd frontend && npm run lint && npm run build
cd admin && npm run lint && npm run build
```

Coprono:

- le attribuzioni del mazzo e le cinque stese;
- la somma di Wirth e le dignità;
- il mazzo fissato e verificabile;
- il validatore dell'intervista («il tuo ragazzo ti ama?» viene scartata);
- il guardrail, e il segnale di crisi nelle quindici lingue;
- il rilevamento della lingua del quesito e i testi fissi;
- i valori passati al modello (solo la posizione e l'orientamento di quella
  posa), la catena del racconto nell'ordine della stesa, la carta 2 della Croce
  Celtica sempre dritta;
- una lettura completa per ogni stesa, con il modello finto, e la lingua che si
  rinnova a ogni quesito;
- il consumo di crediti e quote, il 402;
- l'isolamento fra utenti e la cancellazione;
- i pacchetti pagati, gli inviti, la carta del giorno, la console.
