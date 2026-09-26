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

## Letture speciali: compatibilità e coppia

Due letture **separate dalla standard** con lo stesso motore (`apri → interview →
fan → pick → reveal → synthesis`): una stesa è una voce di `spreads.json` e ogni
passo rilegge la stesa da `Reading.spread_id`. Costano **un credito o una lettura
giornaliera** come le altre e stanno nello stesso storico.

**Il percorso.** Tipo di lettura → dati delle persone (i dati di chi consulta che
mancano nella scheda — genere e data di nascita, che restano nel profilo — e
quelli dell'altra persona: nome, cognome facoltativo, genere, data di nascita,
casella «ricorda») → stile di stesa (tradizionale, moderna, di tendenza) →
intervista di 2–6 domande → mescolata, taglio, scelta → rivelazione → responso.
Il quesito è facoltativo: se resta vuoto il frontend usa «Compatibilità con
{nome}» o «Relazione di coppia con {nome}», nella lingua dell'interfaccia.

**Le nove stese** (`categoria`, `stile` e, per ogni posizione, `soggetto` in
`spreads.json`):

| compatibilità | coppia |
|---|---|
| `compat-tre` (tradizionale) | `coppia-croce` (tradizionale) |
| `compat-sette` (tradizionale) | `coppia-stazione` «Stazione per due» (tradizionale italiana) |
| `compat-nove` (moderna, 3×3, «triangolo della verità») | `coppia-sette` (moderna) |
| `compat-anime` (di tendenza, «soulmate») | `coppia-specchio` (moderna) · `coppia-bivio` (di tendenza) |

`GET /spreads?categoria=` filtra per tipo: la soglia e la lettura standard
chiedono `standard`, così le speciali non vi compaiono. La larghezza delle carte
(`larghezza`, `larghezza_stretto`) e la forma del tavolo (`forma`) stanno nei dati
della stesa, non più nel codice del tavolo. I nomi delle posizioni sono neutri
(«l'altra persona»): Re, Regina, Cavaliere e Fante sono energie, non il genere di
nessuno.

**Genere.** Donna · Uomo · Non binario · Altro (testo libero) · Preferisco non
dirlo, più una casella facoltativa e separata «persona trans» (è un aggettivo, non
un genere). **Non esiste un campo sull'orientamento**: non serve alla lettura ed è
un dato sensibile. Il genere serve solo a pronomi e concordanze; ai prompt si
vieta di dare per scontati il tipo di relazione o l'orientamento e di usare
stereotipi di genere.

**La compatibilità zodiacale è calcolata, non generata** (`tarot/zodiaco.py`): il
segno solare dalla data (confini tropici, con l'avviso di cuspide a ±1 giorno: ora
e luogo non si conoscono, quindi niente ascendente né luna), l'aspetto per distanza
fra i segni, la relazione fra gli elementi (le dignità di Crowley) e un'armonia
**solo qualitativa** — alta, buona, mista, impegnativa —, mai un punteggio. In più
la «carta della coppia», somma teosofica delle due carte dell'anima. Il modello la
riceve già fatta (`tarot/persone.py`) e la usa come sfondo.

**Cosa entra nei prompt** (`tarot/persone.py`, `interpretazione.py`, `cag.py`): per
ogni carta il codice dice **di chi parla la posizione** (`Questa posizione
riguarda: …`, dal `soggetto`), poi il blocco «Le persone» e, nel responso, la
compatibilità zodiacale. Il formato del responso ha una sezione dedicata per
categoria; il prefisso in cache è uno per categoria e quello della lettura standard
è rimasto **identico byte per byte** (lo prova un test con l'impronta). Il
guardrail `relazioni` (niente verdetti, niente certezze sull'altra persona, niente
stereotipi) vale solo per le due categorie.

**Privacy: l'altra persona è un terzo.**

- Il **cognome** sta solo in `Reading.persone` e in `User.partner_ricordato`: la
  struttura dei dati per i prompt (`Persona`) non ha il campo, quindi non può
  arrivare al modello. Il nome e il genere libero si riducono a lettere, cifre,
  spazio, trattino, apostrofo e punto prima di entrare in un prompt.
- `Reading.persone` è una **copia** al momento dell'apertura: lo storico non
  cambia se poi l'utente corregge la scheda, e si cancella con la lettura.
- «Ricorda» salva **un solo** partner nel profilo, nella stessa transazione della
  lettura (con il 402 non salva niente); si cancella da `Profilo → Partner
  ricordato` o con `DELETE /me/partner`. Nell'audit finisce il fatto, mai i dati.
- **Le letture speciali si condividono senza l'altra persona**: nel link, nella
  pagina pubblica e nell'immagine il nome (e il cognome) diventano «qualcuno di
  speciale» nella lingua della lettura, e al suo posto c'è il simbolo del suo
  genere; date, intervista e compatibilità zodiacale non escono mai. Vedi
  «Condivisione» qui sotto.

**Non ancora fatto** (rimandato di proposito): il rilevamento automatico di
violenza o controllo coercitivo con un testo fisso di aiuto (i numeri vanno
verificati uno per lingua prima di pubblicarli: per ora solo la regola del
guardrail e le istruzioni ai prompt), un'età minima, più partner ricordati, ora e
luogo di nascita, la traduzione nelle altre 12 lingue dei nuovi testi.

**Migrazione.** `20260926_1100_letture_speciali`: tre colonne su `users`
(`gender`, `gender_custom`, `is_trans`, più `partner_ricordato`) e una su
`readings` (`persone`). È additiva; `tests/test_migrazione.py` la prova su un
database a parte (upgrade, uguaglianza con i modelli, downgrade). Backend e
frontend vanno rilasciati insieme.

## Pagine pubbliche (senza account)

Carte, stese e la pagina del mazzo si vedono senza registrarsi, e **escono dal server già scritte**:
chi le cerca (un motore di ricerca, l'anteprima di un social) non aspetta il JavaScript.

| percorso | cosa mostra |
|---|---|
| `/carte`, `/carte/{id}` | le 78 carte, attribuzioni e significati |
| `/stese`, `/stese/{id}` | le 14 stese (5 classiche, 4 di compatibilità, 5 di coppia): schema con le posizioni numerate, significato e domanda guida di ciascuna, regole, coppie da leggere insieme, origine |
| `/mazzo` | anteprima del prodotto «mazzo con la grafica originale» (in preparazione: niente prezzo né acquisto) |
| `/sitemap.xml`, `/robots.txt` | mappa del sito e regole per i crawler (le pagine personali e `/s/` sono escluse) |

Come è fatto:

- **`Providers` gira anche sul server** (`app/providers.tsx`): `react-oidc-context` non crea il gestore dell'accesso
  sul server e dice «sessione in caricamento», come nel primo rendering del browser, quindi i due alberi
  coincidono. Prima restituiva `null` fino all'idratazione: il corpo di ogni pagina era vuoto per i crawler.
- **I dati arrivano dal server di Next** (`lib/server-api.ts`, `API_INTERNAL_URL`), con `no-store` e una
  memoria di 30 secondi: la cache dei dati di Next li cuocerebbe nella build, quando l'API non c'è, in un elenco
  vuoto. Le pagine sono dinamiche (`ƒ` nell'elenco della build). `generateMetadata` scrive titolo, descrizione,
  canonical e Open Graph di ogni pagina.
- **Navigazione**: quattro voci sempre in vista (Consulta, Le mie letture, Le carte, Le stese) e «Altro» con
  le altre (Carta del giorno, Il mazzo, Crediti): la barra in basso del telefono non regge più di cinque voci.
  Il collegamento grafico al mazzo (`BannerMazzo`) è in fondo alle pagine pubbliche e in home.
- **Il mazzo**: la scena in testa è composta in CSS con le carte vere. Se esiste `public/mazzo/foto-mazzo.webp`
  (una fotografia vera o generata) la copre. Una prova di generazione con LitMedia non è andata a buon fine: la
  richiesta HTTPS della skill fallisce per la catena di certificati del server (`requests` non la verifica; curl
  sì) e il 2026-09-24 i suoi task per «Nano Banana» venivano chiusi dal server senza motivo. Non si aggira la
  verifica dei certificati.

## Verifica in due passaggi (facoltativa)

Gli amministratori hanno l'OTP obbligatorio (`deploy/keycloak/README.md`). Gli utenti possono attivarlo dal
profilo, sezione «Sicurezza dell'account», con un'app di autenticazione (Google/Microsoft Authenticator,
FreeOTP): il pulsante lancia l'azione *Configure OTP* di Keycloak e torna al sito. A ogni ingresso, a chi
non l'ha attivata compare **un promemoria** (una volta per sessione) con «Attiva ora», «Più tardi» e la
casella **«Non mostrare più»**, che salva `users.promemoria_2fa = false` e si riaccende dal profilo. Il
sito non conserva né vede niente della 2FA: lo stato lo legge dall'API dell'account di Keycloak.

## Condivisione

Ogni lettura conclusa si condivide con un **link** (`/s/{token}`) e un'**immagine**,
da Instagram, Facebook, TikTok, X, email o come solo link. Il pannello
(`frontend/app/leggi/pannello-condivisione.tsx`) mostra l'anteprima del post e
dell'anteprima del link, lascia scrivere un testo personalizzato (sull'immagine e nel
post) e ha i pulsanti coi marchi. Il sito che compare nei link e sulle immagini è
`NEXT_PUBLIC_SITE_URL` (predefinito `https://tarots.chat`).

**L'immagine** si compone nel browser (`app/leggi/immagine-condivisione.ts`), l'unico
posto che scrive in tutte le lingue: a sinistra la stessa stesa della lettura con le
carte uscite nelle loro posizioni, ritagliata e ingrandita sulle carte; a destra il
marchio, il testo personalizzato, il quesito, una sintesi del responso e l'indirizzo
del sito. È **una sola immagine 4:3**, per il post e per l'anteprima del link. Il
browser la disegna a 800×600 e la manda in PNG (l'unico formato che ogni canvas sa
produrre, Safari compreso, che non sa fare WebP); il server (`prepara_immagine`, con
**Pillow**) ne legge l'intestazione e controlla formato (PNG, WebP o JPEG) e misure
(800×600 o 400×300) *prima* di decodificarla, poi la riscrive da zero come **WebP
400×300 molto compresso** (qualità 55, circa 8 KB), quindi senza metadati né dati
accodati. `PUT /me/readings/{id}/share-image` risponde con quel WebP: è ciò che il
pannello mostra in anteprima e allega ai fogli di condivisione. Il disegno parte da ciò
che il server mostra a chiunque (`GET /shared/{token}`), quindi non può dire più della
pagina pubblica.

**Come si condivide** (nessun sito può pubblicare al posto dell'utente):

| canale | cosa succede |
|---|---|
| Facebook, X, email | si apre la finestra di condivisione del canale col link (l'anteprima la leggono da `og:image`) |
| Instagram, TikTok | sul telefono il foglio di condivisione con l'immagine (Web Share API, livello 2); sul computer si scarica l'immagine, si copia il testo e si propone di aprire il sito |
| solo link | copia negli appunti |

**Le anteprime** stanno nell'`<head>` scritto dal server (`app/s/[token]/page.tsx`,
`generateMetadata`), perché i social non eseguono JavaScript. Le letture condivise
sono `noindex`. Il server di Next legge l'API da `API_INTERNAL_URL` (nel cluster,
`http://tarots-api:8100`); l'immagine è servita da `GET /shared/{token}/image.webp`.

**Il premio.** Ogni 5 condivisioni *verificate* una lettura in omaggio, senza tetto;
chi si iscrive dal link di un altro fa guadagnare **5 letture** a chi l'ha condiviso,
anche con l'iscrizione gratuita. Il pannello lo annuncia accanto ai pulsanti e la
scheda utente ha il contatore.

**Come si verifica una condivisione.** Le piattaforme non dicono se un utente ha
pubblicato, quindi si verifica l'**effetto**: dopo che il proprietario ha usato un
pulsante (`POST /me/readings/{id}/share-click`), entro 7 giorni, il link deve essere
aperto da un visitatore vero (`POST /shared/{token}/visit`, inviato dalla pagina dopo
4 secondi a schermo) che

- non è il proprietario (né lo stesso browser, né la stessa rete del clic);
- non è un crawler (`User-Agent` di bot e anteprime non contano);
- conta una volta sola per lettura.

Non prova che il post esista (chi apre il link potrebbe averlo avuto in privato), ma
che il link è uscito dal dispositivo e ha raggiunto qualcuno. Il browser ha un
identificativo casuale (`localStorage`); il server conserva solo **impronte con sale**
(`TAROT_CONDIVISIONE_SALE`, obbligatorio in produzione) di identificativo e indirizzo,
mai i valori. L'indirizzo è `X-Real-IP` (scritto da NPM) o l'ultimo di
`X-Forwarded-For`.

**Iscrizioni dal link.** La pagina pubblica ricorda il link aperto; al primo accesso
dopo l'iscrizione (`AttribuzioneCondivisione`) il frontend lo dice al server
(`POST /me/share-signup`), che accredita solo se l'account è **nuovo** (meno di 48
ore), ha l'**email verificata**, è diverso dal proprietario e da chi ha condiviso per
browser e rete, e non ha già fatto guadagnare a nessuno. Ogni accredito passa dal
registro dei crediti (motivo «omaggio») e dall'audit (`share.reward`, `share.signup`).

**Tabelle** (migrazione `20260926_1500_condivisione`): `share_events`, `share_visits`,
`share_images` (un WebP per lettura), `share_signups`; colonne `users.share_rewards`,
`readings.share_text`, `share_clicked_at`, `share_verified_at`. Ritirare il link
cancella le immagini.

**Limiti noti.** Senza tetto ai premi resta l'esposizione a iscrizioni fasulle
(mitigata da email verificata, account nuovo e impronte, non eliminata); l'immagine
è composta dal client e il server non può verificare che corrisponda alla lettura
(controlla solo che sia un'immagine delle misure giuste, la ricomprime, e solo il
proprietario la carica). A 400×300 i testi sono piccoli: il titolo e il sito si leggono,
la sintesi è quasi solo una texture.

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
  senza nome, con un'immagine composta nel browser e i pulsanti per Instagram,
  Facebook, TikTok, X, email; ogni 5 condivisioni verificate una lettura in omaggio
  (vedi «Condivisione»).
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
- le letture speciali: il calcolo zodiacale, le nove stese (struttura, nomi
  ungheresi, geometria del tavolo su telefono e desktop), le persone e la
  sanificazione dei nomi, il cognome che non arriva mai ai prompt, il profilo
  incompleto (422), «ricorda» e la sua cancellazione, lo storico, il blocco della
  condivisione, la migrazione Alembic e il prefisso della lettura standard
  invariato;
- il consumo di crediti e quote, il 402;
- l'isolamento fra utenti e la cancellazione;
- i pacchetti pagati, gli inviti, la carta del giorno, la console.
