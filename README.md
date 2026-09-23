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

  Una domanda scartata viene rigenerata; se il modello insiste, si usa una
  domanda di riserva.
- **CAG.** Il prefisso stabile contiene la dottrina, le stese, il mazzo intero
  e le regole dei guardrail. È identico a ogni lettura e resta in cache presso
  il fornitore (`cache_control` di Anthropic, o la KV-cache di un motore
  locale). Dopo il confine di cache arrivano:
  - la domanda e il quadro dell'intervista;
  - il profilo (carta dell'anima e dell'anno);
  - le carte con posizione e orientamento, e le letture immediate;
  - le dignità, le prevalenze e la sintesi di Wirth.
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

Per ora le facce sono segnaposto col solo valore della carta in testo, generati
da uno script a partire dal mazzo del backend:

```bash
cd frontend && npm run carte    # scrive public/cards/{id}.svg per le 78 carte
```

**I prompt per le immagini definitive** sono in
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

Salva ogni immagine in `frontend/public/cards/` con il nome indicato in
`file` e imposta `NEXT_PUBLIC_CARD_EXT=webp`.

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
- Interfaccia in **italiano e inglese**.

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
- il guardrail;
- una lettura completa per ogni stesa, con il modello finto;
- il consumo di crediti e quote, il 402;
- l'isolamento fra utenti e la cancellazione;
- i pacchetti pagati, gli inviti, la carta del giorno, la console.
