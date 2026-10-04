# Proposte sui prompt, da decidere con l'operatore

*4 ottobre 2026. Nessuna di queste modifiche è nel codice: i testi mandati al modello (istruzioni, dottrina, cosa
entra nell'intervista, nelle interpretazioni e nella sintesi) sono **identici a prima**. Fa eccezione il punto 6, il
prompt nuovo dello stato sintetico della memoria: gira già dopo ogni lettura, ma il suo risultato **non entra** nei
prompt delle letture finché l'interruttore della console («Usa la memoria breve nelle letture e nell'oracolo») resta
spento. Le misure di riferimento sono in `docs/costi-inferenze.md`.*

Per ogni proposta: com'è oggi e come sarebbe, che cosa perderebbe il modello e perché pensiamo che non serva, quanti
token si risparmiano, il rischio per la qualità. I token sono quelli misurati sul modello della produzione (Nemotron
3.5 Lightning) senza ragionamento.

---

## 1. Intervista: non ripetere due volte le domande già fatte

| Oggi | Proposta |
|---|---|
| Il messaggio porta **l'elenco delle domande già fatte** («Domande già fatte (NON ripeterle e non riformularle; esplora un aspetto diverso): – …») **e poi il colloquio intero**, che contiene di nuovo le stesse domande, una per riga («Oracolo: …»). | Solo il colloquio intero, con la stessa avvertenza spostata sopra di esso: «Colloquio finora (le domande dell'oracolo sono già fatte: NON ripeterle e non riformularle; esplora un aspetto diverso):». |

- **Che cosa perde il modello:** niente. Le domande restano scritte, una volta sola, nel colloquio; l'avvertenza resta.
  Il controllo deterministico delle ripetizioni (`ripete_una_domanda`) non cambia.
- **Token:** ~25 token per domanda già fatta, a ogni chiamata. Con 6 domande: ~100–150 token alla sesta chiamata,
  **~400 per lettura** (il 5–8% dell'ingresso dell'intervista).
- **Rischio:** basso. Da rileggere qualche colloquio: il modello potrebbe ripetere più spesso una domanda (oggi il
  controllo deterministico ne ha scartate 6 dall'1/10, quasi tutte per ripetizione).

## 2. Intervista: un riassunto progressivo al posto del colloquio intero

| Oggi | Proposta |
|---|---|
| A ogni domanda: istruzioni (828 token), quesito, stesa, profilo, memorie, elenco delle domande **e colloquio intero**, che cresce a ogni turno (alla sesta domanda il messaggio è ~1 700 token, la parte nuova è una riga). | Il modello restituisce, insieme alla domanda, un campo `quadro` (2–4 frasi: ciò che si sa finora). Al turno dopo riceve il `quadro` del turno prima, **le ultime due risposte per intero** e l'elenco breve delle domande già fatte (per non ripeterle). |

Esempio del messaggio proposto:

```
Quesito: Devo accettare la nuova offerta di lavoro in un'altra città?
Stesa scelta: Tre carte …
Domande già poste: 4 (minimo 2, massimo 6)
Domande già fatte (NON ripeterle): – Da quanto … – Che cosa ti attira … – Entro quando … – Hai già chiesto …
Quadro finora: L'offerta è di Milano, arrivata tre mesi fa; vive a Bologna col compagno, che ha appena aperto uno
studio. Teme di perdere amicizie e la vicinanza ai genitori. Deve rispondere entro fine mese.
Ultime risposte:
Oracolo: Hai già provato a chiedere il lavoro da remoto?
Chi consulta: Sì, mi hanno detto che forse dopo sei mesi si può.
```

- **Che cosa perde il modello:** le parole esatte delle risposte più vecchie (restano nel `quadro`, riassunte). È la
  ragione del rischio: un dettaglio che il riassunto ha lasciato fuori non torna più nelle domande successive.
- **Token:** −30/−50% dell'ingresso dell'intervista: **~1 500–2 500 token per lettura completa**, ~40% di quella
  abbandonata dopo 2 domande è già piccola (lì il colloquio è corto e il guadagno quasi nullo). In uscita: +40–60
  token per domanda (il campo `quadro`).
- **Rischio:** medio. Domande meno agganciate alle risposte vecchie; il riassunto finale (`riassunto`, che serve a
  interpretazioni e sintesi) andrebbe scritto dal `quadro` dell'ultimo turno e potrebbe perdere sfumature. Da provare
  su 10–20 letture e rileggere.

## 3. Interpretazioni carta per carta: il quadro dell'intervista, senza il colloquio intero

| Oggi | Proposta |
|---|---|
| Ogni carta riceve «Contesto emerso dall'intervista: <riassunto>» **e** «Colloquio (domande dell'oracolo e risposte di chi consulta): <colloquio intero>». | Solo il riassunto; il colloquio intero no. In alternativa più prudente: il riassunto e **l'ultima risposta** di chi consulta. |

- **Che cosa perde il modello:** le frasi esatte di chi consulta. Il prompt dell'interpretazione chiede di riprendere
  «ciò che è stato detto nel colloquio, senza citarlo alla lettera»: il riassunto lo contiene già, e la sintesi
  continua a ricevere il colloquio intero (lì la fedeltà alle parole conta di più).
- **Token:** ~300–450 token per carta: **~1 000 per una tre carte, ~4 000 per una croce celtica** (~20% dell'ingresso
  delle interpretazioni).
- **Rischio:** medio-basso. Interpretazioni un po' meno concrete. Nota: oggi il colloquio sta prima della parte che
  cambia da carta a carta, quindi un fornitore con la cache del prefisso lo sconta già dalla seconda carta in poi;
  con un fornitore così il guadagno in dollari è minore del guadagno in token.

## 4. L'ordine dei messaggi pensato per la cache del fornitore

Già oggi le parti fisse stanno in testa: il prefisso della sintesi (regole, guardie, dottrina: ~6 500 token) è il
primo messaggio di sistema, identico a ogni lettura della stessa categoria; le istruzioni di intervista,
interpretazione e giudizio sono messaggi di sistema senza dati della lettura. Due ritocchi possibili:

| Dove | Oggi | Proposta | Effetto |
|---|---|---|---|
| Intervista | «Domande già poste: 4 (minimo 2, massimo 6)» sta **prima** dell'elenco e del colloquio: cambia a ogni turno e rompe il prefisso comune fra un turno e l'altro. | Spostarlo in fondo, dopo il colloquio, insieme agli avvisi «Hai fatto N domande…». | Fra un turno e il successivo resta identico tutto il messaggio fino all'ultima risposta: con un fornitore con cache (DeepInfra, Darkbloom) quella parte costa il 50% in meno. Nessun token risparmiato, nessuna informazione persa. Rischio: nullo. |
| Interpretazioni | Quesito, contesto e colloquio in testa, poi la carta. | Invariato (è già l'ordine giusto). | — |
| Sintesi | Prefisso fisso, poi la parte variabile. | Invariato. | — |

Con Nebius la cache non è nel listino: oggi questo punto non fa risparmiare nulla, diventa utile solo cambiando
fornitore.

## 5. Sintesi: «sintetici ma non magri»

| Oggi | Proposta |
|---|---|
| «Formato (Markdown, 350-650 parole): esattamente queste quattro sezioni…». Senza ragionamento il modello scrive in media **~1 000 parole** (1 000–1 750 token), ben oltre la forchetta, e la croce celtica si troncava al tetto. | Aggiungere sotto il formato: «Sii sintetico ma non magro: ogni frase dice qualcosa di questa lettura, nessuna sezione ripete un'altra, niente formule generiche. Resta dentro la forchetta di parole.» |

- **Che cosa perde il modello:** niente di informativo; perde le ripetizioni fra le sezioni (nelle letture di prova
  «Il quadro» e «La tendenza» ridicono spesso le stesse cose).
- **Token:** se i responsi tornano a ~650 parole, **−400/−600 token d'uscita per sintesi** (−30/−40% dell'uscita della
  sintesi, la voce d'uscita più grande di una lettura senza ragionamento).
- **Rischio:** basso-medio: un responso più corto può sembrare meno ricco. Il tetto dei token è già stato alzato
  (2 600, +400 per le letture speciali, +600 per le stese con più di cinque posizioni): da solo evita i tagli a metà,
  questa frase servirebbe solo a spendere meno.

## 6. Il prompt nuovo: l'aggiornamento dello stato sintetico della memoria

**Gira già** dopo ogni lettura completata di una persona registrata, con il ragionamento sempre spento (`per(...,
senza_ragionamento=True)`), al posto dell'estrazione delle memorie di prima (che ragionava: 4–6 mila token d'uscita a
lettura, buttati perché l'embedding non funzionava). Il suo risultato aggiorna lo stato che la persona vede nel
profilo; **non entra nei prompt delle letture** finché l'interruttore resta spento.

Il testo, ridotto al minimo (`tarot/stato_memoria.py`, `PROMPT_STATO_MEMORIA`):

```
# Compito: memoria_stato

Aggiorni la memoria breve che TAROTS chat tiene su chi consulta. Ricevi lo stato attuale (voci con un id) e il
quadro di una lettura appena conclusa.
- stabile: un fatto che non cambia da solo (con chi vive, un lutto, una condizione permanente).
- volatile: una situazione in corso che può cambiare (una scelta da fare, una crisi, un progetto).
Aggiungi solo fatti nuovi, detti da chi consulta, utili a una prossima lettura: una frase in terza persona ciascuno.
Conferma gli id ancora veri; rimuovi quelli che la lettura smentisce o dice superati. Non riscrivere il quesito: lo
registra il sistema.
Campi: amore, lavoro, salute, famiglia, denaro, spirituale, altro.

Rispondi SOLO con JSON:
{"aggiungi": [{"categoria": "stabile|volatile", "campo": "<campo>", "testo": "<frase>"}], "conferma": ["<id>"], "rimuovi": ["<id>"], "campo_quesito": "<campo del quesito>"}
```

Il messaggio variabile porta solo: la data, lo stato attuale (senza i temi, che scrive il codice) e il quadro della
lettura — il quesito e il riassunto dell'intervista, **mai la trascrizione né il responso**:

```
Data di oggi: 2026-10-04

Stato attuale:
- [a1b2c3] stabile · famiglia: Vive a Bologna con il compagno. (visto il 2026-09-20)

Nuova lettura
Quesito: Devo accettare la nuova offerta di lavoro in un'altra città?
Quadro emerso dal colloquio: <il riassunto dell'intervista>

Scrivi i testi delle voci nuove nella lingua di chi consulta. <istruzione della lingua>
```

Cosa decide il codice, senza il modello: il tema (il quesito, con la data e il campo che il modello indica), i
doppioni (una voce uguale conferma quella che c'è), gli id sconosciuti (ignorati), la salute senza consenso (scartata,
e tolta se c'era), l'oblio (le situazioni del momento spariscono dopo 60 giorni senza conferme, i temi dopo 120, al più
12 stabili, 6 temi, 8 situazioni).

Misure (sezione «Dopo gli interventi» di `docs/costi-inferenze.md`): ~490–600 token in ingresso e ~130–230 in uscita
per lettura, contro ~2 300 in ingresso e ~5 300 in uscita dell'estrazione di prima col ragionamento acceso.

Cosa si è visto nelle prove (sei letture): voci utili ma rumorose — alcune in prima persona («Non vedo mia sorella da
tre mesi…»), un campo sbagliato (una scadenza messa in «denaro»), una confusione fra le persone, una voce «stabile»
discutibile. Possibili ritocchi, da decidere: un esempio di voce buona e una cattiva nel prompt (+~60 token); scartare
nel codice le voci in prima persona (deterministico, gratis).

**Da decidere:** (a) se il testo va bene così; (b) quando accendere l'interruttore — da quel momento l'oracolo,
l'intervista e la sintesi ricevono le voci dello stato al posto delle memorie di prima, nella stessa forma («[STABILE —
famiglia] …», al più 5 voci e ~200 token) e con lo stesso testo delle istruzioni.

---

## Riepilogo

| # | Proposta | Token risparmiati | Rischio | Decisione (4/10) |
|---|---|---|---|---|
| 1 | Intervista senza l'elenco doppio delle domande | ~400 in ingresso per lettura | basso | **fatta** |
| 2 | Intervista con riassunto progressivo | ~1 500–2 500 in ingresso per lettura completa | medio | no: il `quadro` costa uscita (4× l'ingresso) e la cache sconta già il colloquio |
| 3 | Interpretazioni senza il colloquio intero | ~1 000 (tre carte) – ~4 000 (croce celtica) in ingresso | medio-basso | superata: con la chiamata unica il colloquio entra una volta sola |
| 4 | Contatore dell'intervista in fondo, per la cache | 0 token; −50% sulla parte cacheabile con un fornitore con cache | nullo | **fatta** |
| 5 | Sintesi concisa ma completa | ~400–600 in uscita per sintesi | basso-medio | **fatta**, con la formula «conciso ma completo, esaustivo e chiaro» |
| 6 | Prompt dello stato sintetico | già attivo; nei prompt delle letture solo con l'interruttore | da rileggere le voci | in attesa |
