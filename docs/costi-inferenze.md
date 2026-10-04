# Quanto costano le inferenze di TAROTS chat

*Misure del 4 ottobre 2026. Nessun comportamento delle pipeline è stato cambiato: si è solo misurato e aggiunto un
registro dei consumi. Le decisioni restano all'operatore.*

## In breve

- **Oggi il grosso della spesa non sono le letture: è l'oracolo (la chat proattiva).** Ogni apertura dell'oracolo
  gira col ragionamento acceso e budget 16 384, perché il compito `chat_proattiva` non è assegnato e ricade sul
  fornitore predefinito (Nebius, con `enable_thinking: true`). Con le 294 aperture registrate dal 28/9 al 3/10, è
  circa **metà dei token in uscita** del pannello Nebius.
- **I cinque compiti delle letture in produzione non ragionano.** Le assegnazioni hanno `ragiona_override = false`:
  il codice in produzione (v8.3) manda quindi `enable_thinking: false` e toglie il `reasoning_budget`. Il ragionamento
  acceso con budget 16 384 vale solo per i compiti **non assegnati**: oracolo, estrazione delle memorie, embedding (e
  gli strumenti della console: traduzioni del blog, analisi dei dati).
- **L'estrazione delle memorie costa più di tutto il resto della lettura in uscita** (ragiona: 4–6 mila token per un
  JSON di poche righe) **e oggi non serve a niente**: l'embedding verso Nebius fallisce (il modello di chat non fa
  embedding), la tabella delle memorie in produzione è vuota e il recupero all'apertura va in errore.
- **In cifre assolute la spesa è piccola.** Le due settimane del pannello (540 mila token in ingresso, 620 mila in
  uscita) valgono circa **0,18 $** al listino pubblico di Nebius. Una lettura completata costa oggi circa
  **mezzo centesimo** (compreso il peso di quelle abbandonate); con il ragionamento acceso ovunque costerebbe circa
  il triplo.
- **Il confronto col pannello torna:** con la distribuzione reale delle letture e delle aperture dell'oracolo, i token
  misurati spiegano quasi tutto l'ingresso e circa tre quarti dell'uscita; il resto sta nella variabilità del
  ragionamento dell'oracolo e in chiamate che non sono letture (prove, traduzioni del blog, analisi dei dati).

## Come si è misurato

- **Modello**: lo stesso della produzione, `nvidia-nemotron-3.5-lightning-30b-a3b`, su LM Studio in locale (gratuito),
  una chiamata alla volta. LM Studio riporta i token di ragionamento (`completion_tokens_details.reasoning_tokens`).
- **Pipeline vere**: lo script `backend/tarot_core/tools/misura_costi.py` fa girare l'app intera in-process su un
  database suo (`tarot_ui_costi`, portato a head), con il fornitore e le assegnazioni scritti nelle tabelle come li
  scrive la console. Ogni chiamata passa dal nuovo registro dei consumi.
- **Tre configurazioni del ragionamento**:
  - *come oggi in produzione*: i cinque compiti assegnati senza ragionamento, oracolo e memoria col ragionamento;
  - *acceso ovunque*: come il fornitore è dichiarato (`reasoning_budget: 16384`);
  - *spento ovunque*.
- **Due ripetizioni** per ogni scenario: le tabelle riportano la media. Il modello decide da sé quante domande fare
  (da 2 a 6) e se il giudice chiede una riscrittura: due letture uguali possono costare in modo diverso anche del
  50%.
- **Limiti di LM Studio**: ignora `chat_template_kwargs.enable_thinking` e `reasoning_budget` (verificato): il
  ragionamento si spegne solo con `reasoning_effort: "none"`, che lo script aggiunge dove la produzione manda
  `enable_thinking: false`. **Un budget piccolo (es. 1024) non si può imporre su LM Studio**: si può solo tagliare
  `max_tokens`, che tronca la risposta invece di far ragionare meno. Su Nebius il `reasoning_budget` dovrebbe valere
  (è il motivo per cui è nei parametri), ma non è stato provato: servirebbe una chiamata vera a pagamento.
- **Ingresso cacheabile**: è la parte del prompt che resta identica fra una chiamata e l'altra dello stesso tipo — in
  questa piattaforma i messaggi di sistema in testa, che non contengono mai dati della lettura. Solo quella può
  essere trovata in cache dal fornitore. Le percentuali di cache hit dei listini (70% Darkbloom, 90% DeepInfra) si
  applicano solo a questa parte.
- **Prezzi** in dollari per milione di token: Nebius 0,06 in / 0,24 out (listino pubblico di Token Factory per
  Nemotron 3.5 Lightning; lo sconto per la cache non è noto, quindi nessuno); Darkbloom 0,039 / cached 0,019 / 0,18;
  DeepInfra 0,06 / cached 0,03 / 0,16.

## 1. La mappa delle pipeline

Ogni chiamata a un modello passa da `api/deps.provider_per(compito)`. I compiti sono in `llm/compiti.py`. In
produzione i compiti `intervista`, `validazione`, `interpretazione`, `sintesi`, `giudizio` sono assegnati a
`nebius-nemotron-lightning` **con il ragionamento spento** (`ragiona_override = false`); tutti gli altri ricadono sul
fornitore predefinito, che per il registro è il primo fornitore attivo in ordine di nome — oggi lo stesso
`nebius-nemotron-lightning`, ma **con i suoi parametri pieni** (`reasoning_budget: 16384`, `enable_thinking: true`,
`max_tokens` alzato a 18 432).

Tutte le chiamate sono in streaming verso il fornitore, con `stream_options.include_usage`; «testo» vuol dire che
l'app legge il testo man mano, «JSON» che aspetta la risposta intera.

### Una lettura completa, chiamata per chiamata

| # | Passo | Compito (fase) | Quante volte | Forma | Cosa c'è nel prompt (token misurati) | Prefisso stabile |
|---|---|---|---|---|---|---|
| 0 | Apertura | `embedding` | 1, solo se la persona ha già memorie | vettore | il quesito | — |
| 1 | Domanda di contesto | `intervista` | una per domanda (2–6), più una per ogni domanda scartata | JSON | istruzioni fisse 828 (+385 coppia, +280 lavoro); quesito, stesa e posizioni, profilo, memorie (fino a 5, ~120), **elenco delle domande già fatte e trascrizione intera** che cresce a ogni turno: 1 200–1 800 in totale | sì: le istruzioni (~60% dell'ingresso) |
| 2 | Controllo della domanda | `validazione` | una per domanda candidata che supera i controlli deterministici | JSON | istruzioni fisse 230 (+125 coppia); quesito e domanda: ~330 | sì (~80%) |
| 3 | Chiusura | `intervista` (`intervista.riassunto`) | solo se il modello chiude senza riassunto o con «basta così» | JSON | istruzioni dell'intervista + trascrizione: ~1 300 | sì |
| 4 | Ogni carta girata | `interpretazione` | una per posizione (3 nella tre carte, 10 nella croce celtica) | testo, a schermo mentre arriva | istruzioni fisse 661 (+336 coppia); quesito, **riassunto dell'intervista e trascrizione intera** (di nuovo a ogni carta), stesa, posizione, dignità, carte già girate, **scheda della carta nel solo orientamento uscito** (~380 dritta, ~310 rovesciata): ~1 800 | sì (~40%) |
| 5 | Responso | `sintesi` (`sintesi`) | 1 | testo, mostrato solo dopo il giudice | **prefisso fisso 6 460** (regole 1 000, guardie 450, dottrina 5 000; 7 300 per le letture di coppia); poi quesito, riassunto, trascrizione, memorie (fino a 3), schede di tutte le carte, interpretazioni già date, ordine del racconto, prevalenze: 9 000–14 000 in totale | sì: il prefisso, 50–70% |
| 6 | Guardia | `giudizio` | 1, e un'altra dopo ogni riscrittura | JSON | istruzioni 230 + rubriche 580 (760 coppia); quesito e responso intero: ~2 500 | sì (~30%) |
| 7 | Revisione | `sintesi` (`sintesi.revisione`) | solo se il giudice dice «riscrivi» (poi di nuovo il giudice) | testo | come il responso, più le correzioni: ~12 000 | sì |
| 8 | Anteprima | `sintesi` (`teaser`) | 1, solo per chi non è registrato | testo | istruzioni 200 + responso intero: ~1 700 | poco (~10%) |
| 9 | Memoria | `memoria_estrazione` | 1, in background, solo per i registrati | JSON | istruzioni 365; quesito, trascrizione, responso intero: ~2 300 | poco (~15%) |
| 10 | Memoria | `embedding` | 1, solo se l'estrazione ha trovato qualcosa | vettore | le memorie estratte | — |

Fuori dal modello, senza costo: il filtro delle parole di crisi (prima delle carte e su ogni risposta), i controlli
deterministici sulle domande (ricalca il quesito, previsioni, più domande, ripetizioni), il filtro delle formule
proibite sull'uscita.

### Una lettura abbandonata all'intervista

Si paga l'apertura e ogni domanda mostrata: per chi se ne va dopo 2 domande sono **2 chiamate d'intervista e 2 di
validazione** (più quelle delle domande scartate), circa 2 700 token in ingresso e 170 in uscita senza ragionamento.
In produzione 15 letture su 26 si sono fermate qui (in media 2 domande ciascuna).

### L'oracolo (chat proattiva)

| Passo | Quando parte | Prompt | Forma |
|---|---|---|---|
| Apertura | al caricamento della pagina se l'ultima proposta ha più di 12 ore, e dopo i minuti di silenzio decisi in console; al più 2 per visita (impostazione attuale); il server non rigenera se c'è già un'apertura di meno di 12 ore nella stessa lingua | istruzioni 322; memorie più recenti (fino a 5, ~120); spunto a caso; le ultime 6 aperture da non ripetere: 400–700 | JSON |
| Risposta | a ogni messaggio della persona | istruzioni, memorie, conversazione recente, messaggio: 450–600 | JSON |

**Per chi non è registrato l'oracolo non chiama nessun modello** (verificato in `frontend/v2/componenti/dock.tsx` e
nel backend, dove la chat richiede l'accesso): la barra mostra temi già scritti nei dizionari, uno a caso, e porta
alla lettura gratuita.

Nota dai dati di produzione: le 294 aperture dal 28/9 al 3/10 vengono da **3 account** in tutto; il 29 e il 30
settembre se ne sono accumulate 230 (aperture impilate prima della v8.5), dall'1 al 3 ottobre 53.

## 2. I token misurati

| Scenario | Ragionamento | Chiamate | Ingresso | di cui cacheabile | Uscita | di cui ragionamento | Nebius | Darkbloom | DeepInfra |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Tre carte completa (registrata, con memoria) | come oggi | 20 | 31 625 | 17 005 | 8 510 | 5 437 | $0,0039 | $0,0025 | $0,0028 |
| Tre carte completa (registrata, con memoria) | acceso ovunque | 11 | 21 682 | 12 370 | 32 879 | 30 530 | $0,0092 | $0,0066 | $0,0062 |
| Tre carte completa (registrata, con memoria) | spento ovunque | 18 | 28 328 | 16 017 | 2 530 | 0 | $0,0023 | $0,0013 | $0,0017 |
| Croce celtica completa (con memoria) | come oggi | 32 | 63 368 | 27 698 | 10 314 | 4 910 | $0,0063 | $0,0039 | $0,0047 |
| Croce celtica completa (con memoria) | acceso ovunque | 21 | 41 260 | 18 468 | 67 252 | 63 483 | $0,0186 | $0,0135 | $0,0127 |
| Croce celtica completa (con memoria) | spento ovunque | 29 | 58 867 | 26 116 | 5 840 | 0 | $0,0049 | $0,0030 | $0,0038 |
| Compatibilità, 3 carte (con memoria) | come oggi | 27 | 59 522 | 36 633 | 10 202 | 5 042 | $0,0060 | $0,0036 | $0,0042 |
| Compatibilità, 3 carte (con memoria) | acceso ovunque | 14 | 31 737 | 19 432 | 51 122 | 48 586 | $0,0142 | $0,0102 | $0,0096 |
| Compatibilità, 3 carte (con memoria) | spento ovunque | 22 | 53 698 | 33 470 | 5 528 | 0 | $0,0045 | $0,0026 | $0,0032 |
| Tre carte anonima (con anteprima) | come oggi | 30 | 45 608 | 25 227 | 4 574 | 0 | $0,0038 | $0,0022 | $0,0028 |
| Tre carte anonima (con anteprima) | acceso ovunque | 13 | 22 196 | 13 231 | 38 828 | 36 806 | $0,0107 | $0,0077 | $0,0072 |
| Tre carte anonima (con anteprima) | spento ovunque | 22 | 31 004 | 18 291 | 2 858 | 0 | $0,0025 | $0,0015 | $0,0018 |
| Abbandonata dopo 2 domande | come oggi | 4 | 2 746 | 2 180 | 164 | 0 | $0,0002 | $0,0001 | $0,0001 |
| Abbandonata dopo 2 domande | acceso ovunque | 4 | 2 750 | 2 183 | 6 554 | 6 369 | $0,0017 | $0,0013 | $0,0012 |
| Abbandonata dopo 2 domande | spento ovunque | 5 | 3 962 | 3 019 | 198 | 0 | $0,0003 | $0,0001 | $0,0002 |
| Oracolo: 2 aperture e 2 risposte | come oggi | 4 | 1 951 | 1 303 | 8 663 | 8 282 | $0,0022 | $0,0016 | $0,0015 |
| Oracolo: 2 aperture e 2 risposte | acceso ovunque | 4 | 1 946 | 1 301 | 6 968 | 6 650 | $0,0018 | $0,0013 | $0,0012 |
| Oracolo: 2 aperture e 2 risposte | spento ovunque | 4 | 1 946 | 1 305 | 256 | 0 | $0,0002 | $0,0001 | $0,0001 |

Token totali e costo in dollari di **uno** scenario (media delle ripetizioni).

Cosa si vede:

- **Col ragionamento acceso l'uscita di una lettura si moltiplica per 10–13 volte** rispetto al ragionamento spento:
  il 90–95% dei token in uscita è ragionamento. Una validazione — un sì o un no — passa da ~45 a ~1 600 token;
  un'interpretazione da ~165 a ~3 500.
- **Senza ragionamento la parte più cara di una lettura è l'ingresso**: la sintesi (10–14 mila token, di cui 6,5 mila
  sempre uguali) e l'intervista, che a ogni domanda rimanda istruzioni, elenco delle domande e trascrizione.
- **Il modello senza ragionamento fa più domande** (4–6, spesso il massimo) e ne vede scartare di più; col
  ragionamento si ferma prima (2–5, in media 3). Senza ragionamento l'intervista costa quindi più ingresso, ma
  ogni chiamata costa ~50 token d'uscita invece di ~3 500.

### Token medi per singola chiamata

| Fase | Ragionamento | Chiamate misurate | Ingresso | di cui cacheabile | Uscita | di cui ragionamento |
|---|---|--:|--:|--:|--:|--:|
| intervista | come oggi | 83 | 1 505 | 905 | 58 | 0 |
| intervista | acceso ovunque | 36 | 1 296 | 937 | 3 488 | 3 419 |
| intervista | spento ovunque | 66 | 1 411 | 914 | 50 | 0 |
| intervista.riassunto | come oggi | 3 | 1 484 | 1 073 | 147 | 0 |
| intervista.riassunto | spento ovunque | 6 | 1 290 | 946 | 154 | 0 |
| validazione | come oggi | 72 | 334 | 264 | 44 | 0 |
| validazione | acceso ovunque | 28 | 327 | 268 | 1 571 | 1 518 |
| validazione | spento ovunque | 53 | 325 | 262 | 43 | 0 |
| interpretazione | come oggi | 38 | 1 908 | 747 | 165 | 0 |
| interpretazione | acceso ovunque | 38 | 1 727 | 755 | 3 507 | 3 382 |
| interpretazione | spento ovunque | 38 | 1 809 | 751 | 166 | 0 |
| sintesi | come oggi | 8 | 10 722 | 6 571 | 1 687 | 0 |
| sintesi | acceso ovunque | 8 | 10 336 | 6 588 | 3 758 | 2 268 |
| sintesi | spento ovunque | 8 | 10 626 | 6 579 | 1 548 | 0 |
| sintesi.revisione | come oggi | 4 | 11 261 | 6 780 | 1 582 | 0 |
| sintesi.revisione | spento ovunque | 3 | 11 727 | 6 937 | 1 618 | 0 |
| giudizio | come oggi | 12 | 2 573 | 810 | 96 | 0 |
| giudizio | acceso ovunque | 8 | 2 396 | 795 | 2 359 | 2 343 |
| giudizio | spento ovunque | 12 | 2 492 | 826 | 200 | 0 |
| teaser | come oggi | 2 | 1 918 | 187 | 95 | 0 |
| teaser | acceso ovunque | 2 | 1 390 | 184 | 1 566 | 1 458 |
| teaser | spento ovunque | 2 | 1 841 | 186 | 116 | 0 |
| memoria_estrazione | come oggi | 6 | 2 377 | 333 | 5 279 | 5 130 |
| memoria_estrazione | acceso ovunque | 6 | 2 198 | 334 | 6 392 | 6 273 |
| memoria_estrazione | spento ovunque | 5 | 2 220 | 334 | 246 | 0 |
| chat_proattiva | come oggi | 8 | 488 | 326 | 2 166 | 2 070 |
| chat_proattiva | acceso ovunque | 8 | 486 | 325 | 1 742 | 1 662 |
| chat_proattiva | spento ovunque | 8 | 486 | 326 | 64 | 0 |

## 3. Costo per lettura e per 1000 letture

Costo di **1000 letture** di ciascun tipo:

| Scenario | Ragionamento | Nebius | Darkbloom | DeepInfra |
|---|---|--:|--:|--:|
| Tre carte completa (registrata, con memoria) | come oggi | $3,94 | $2,53 | $2,80 |
| Tre carte completa (registrata, con memoria) | acceso ovunque | $9,19 | $6,59 | $6,23 |
| Tre carte completa (registrata, con memoria) | spento ovunque | $2,31 | $1,34 | $1,67 |
| Croce celtica completa (con memoria) | come oggi | $6,28 | $3,94 | $4,70 |
| Croce celtica completa (con memoria) | acceso ovunque | $18,62 | $13,46 | $12,74 |
| Croce celtica completa (con memoria) | spento ovunque | $4,93 | $2,98 | $3,76 |
| Compatibilità, 3 carte (con memoria) | come oggi | $6,02 | $3,64 | $4,21 |
| Compatibilità, 3 carte (con memoria) | acceso ovunque | $14,17 | $10,17 | $9,56 |
| Compatibilità, 3 carte (con memoria) | spento ovunque | $4,55 | $2,62 | $3,20 |
| Tre carte anonima (con anteprima) | come oggi | $3,83 | $2,25 | $2,79 |
| Tre carte anonima (con anteprima) | acceso ovunque | $10,65 | $7,67 | $7,19 |
| Tre carte anonima (con anteprima) | spento ovunque | $2,55 | $1,47 | $1,82 |
| Abbandonata dopo 2 domande | come oggi | $0,20 | $0,11 | $0,13 |
| Abbandonata dopo 2 domande | acceso ovunque | $1,74 | $1,26 | $1,15 |
| Abbandonata dopo 2 domande | spento ovunque | $0,29 | $0,15 | $0,19 |

Il **mix reale** mette insieme le letture delle ultime due settimane come sono andate davvero — 26 aperte, 9
completate (6 tre carte, una anonima, 3 croce celtica), 2 ferme alla sintesi, 15 abbandonate all'intervista — e divide
il costo di tutte per le 9 completate: è il costo vero di «una lettura completata», compreso il peso di quelle lasciate
a metà.

| Ragionamento | Nebius | Darkbloom | DeepInfra | Per 1000 completate: Nebius / Darkbloom / DeepInfra |
|---|--:|--:|--:|--:|
| come oggi | $0,0053 | $0,0033 | $0,0039 | $5,35 / $3,32 / $3,88 |
| acceso ovunque | $0,0167 | $0,0120 | $0,0113 | $16,66 / $12,01 / $11,28 |
| spento ovunque | $0,0039 | $0,0023 | $0,0029 | $3,94 / $2,29 / $2,89 |

L'oracolo va contato a parte, perché dipende dalle visite e non dalle letture: un'apertura costa circa
1 040 token d'uscita (0,0003 $ con Nebius) con il ragionamento acceso, come oggi, e un
ventesimo dell'uscita senza. Per esempio, 1000 persone registrate che aprono l'oracolo 2 volte al giorno per 30 giorni
fanno 60 000 aperture: circa 18 $ al mese con Nebius col ragionamento acceso, circa 4 $ senza (lì resta quasi solo
l'ingresso).

## 4. Il confronto col pannello Nebius

Il pannello dice **540 mila token in ingresso e 620 mila in uscita** nelle ultime due settimane. Le assegnazioni a
Nebius sono del 27/9: le due croci celtiche del 25/9 sono quasi certamente passate dal fornitore di prima e qui non si
contano. Fino al 30/9 tutti i compiti ragionavano (il `ragiona_override = false` mandava ancora
`enable_thinking: true`: è il difetto corretto il 30/9 e descritto in `llm/compiti.py`); dall'1/10 i cinque compiti
delle letture non ragionano più. L'oracolo e la memoria hanno sempre ragionato.

| Voce | Quante | Ingresso a testa | Uscita a testa | Ingresso | Uscita |
|---|--:|--:|--:|--:|--:|
| Oracolo: aperture (ragionamento acceso, 28/9–3/10) | 294 | 704 | 1 042 | 206 902 | 306 274 |
| Croce celtica completata, registrata (28/9, tutto acceso) | 1 | 41 260 | 67 252 | 41 260 | 67 252 |
| Tre carte ferma alla sintesi (29/9, tutto acceso) | 1 | 8 484 | 21 576 | 8 484 | 21 576 |
| Abbandonate all'intervista (27/9–30/9, tutto acceso) | 4 | 2 750 | 6 554 | 11 000 | 26 218 |
| Tre carte completate, registrate (1–3/10) | 5 | 31 625 | 8 510 | 158 125 | 42 552 |
| Tre carte completata, anonima (1/10) | 1 | 45 608 | 4 574 | 45 608 | 4 574 |
| Tre carte anonima ferma alla sintesi (1/10) | 1 | 25 732 | 1 875 | 25 732 | 1 875 |
| Abbandonate all'intervista (1–3/10) | 11 | 2 746 | 164 | 30 206 | 1 798 |
| **Totale stimato** | | | | **527 318** | **472 120** |
| **Pannello Nebius** | | | | **540 000** | **620 000** |
| Spiegato | | | | 98% | 76% |

**Cosa manca e perché:**

- l'**ingresso** torna quasi per intero;
- nell'**uscita** mancano circa 150 000 token. La voce più incerta è l'oracolo: lo stesso prompt d'apertura
  ha prodotto qui fra 850 e 1 200 token d'uscita, e le risposte fino a 3 400; con 294 aperture, 500 token in più o in
  meno a testa sono già 150 mila. Le aperture vere hanno anche una cronologia più lunga (fino a 6 aperture precedenti da
  non ripetere) che spinge a ragionare di più;
- le **chiamate che non sono letture** non sono nei dati della produzione e girano tutte col ragionamento acceso:
  traduzioni degli articoli del blog dalla console (`traduzione_articolo`, ingresso lungo), analisi dei dati
  (`analisi_dati`, fino a 5 000 token d'uscita più il ragionamento), traduzioni delle notifiche, e le prove fatte a
  mano sul servizio;
- le 294 righe dell'oracolo sono un **minimo**: dalla v8.5 un'apertura vecchia si sostituisce nella stessa riga, quindi
  le inferenze possono essere più delle righe (dall'1/10: 56 richieste di apertura nei log contro 53 righe);
- l'**embedding** non costa niente: verso Nebius fallisce (nei log «Recupero memorie non riuscito»).

Dal 4/10 il registro dei consumi (sotto) toglie ogni stima: la pagina «Costi» della console mostrerà il conto vero,
chiamata per chiamata, da confrontare giorno per giorno col pannello.

## 5. Le voci più costose, in ordine (configurazione di oggi)

| # | Voce | Perché costa | Peso oggi |
|---|---|---|---|
| 1 | **Oracolo: le aperture** | ragionamento acceso con budget 16 384 su un JSON di 1–3 frasi; ~95% dell'uscita è ragionamento | circa metà dell'uscita del pannello |
| 2 | **Estrazione delle memorie** | ragionamento acceso; 4–6 mila token d'uscita per lettura registrata, più di tutto il resto della lettura; il risultato si butta perché l'embedding fallisce | ~60% dell'uscita di una tre carte registrata |
| 3 | **Sintesi** (e revisione quando il giudice la chiede) | 10–14 mila token in ingresso a chiamata; la revisione raddoppia | ~30–35% dell'ingresso di una lettura completata |
| 4 | **Intervista e validazione** | fino a 6 domande (più le scartate), ognuna con istruzioni, elenco delle domande e trascrizione intera; un controllo LLM per ogni candidata | ~30–40% dell'ingresso di una lettura completata; quasi tutto quello di un'abbandonata |
| 5 | **Interpretazioni** | una chiamata per carta, ognuna con riassunto **e** trascrizione intera dell'intervista | ~30% dell'ingresso di una croce celtica |

Con il ragionamento acceso ovunque l'ordine cambierebbe: interpretazioni, intervista e validazione passerebbero in
testa, perché ragionano a ogni chiamata.

## 6. Analisi dello spreco

### A) Quanto pesa la memoria dell'utente nel prompt

| Dove | Cosa entra | Token | Quante volte |
|---|---|---|---|
| Intervista | fino a 5 memorie, scelte all'apertura per somiglianza col quesito | ~120 | a ogni domanda (6 domande ≈ 700 a lettura) |
| Sintesi | le prime 3, con «prima si sapeva» per le variabili | ~70–120 | 1 (2 con la revisione) |
| Oracolo | le 5 più recenti | ~120 (misurato: apertura da 402 a 518 token) | a ogni apertura e risposta |

È **meno del 2% dell'ingresso di una lettura** e circa un quinto di quello di un'apertura dell'oracolo. **Oggi in
produzione vale zero**: la tabella delle memorie è vuota e il recupero all'apertura fallisce. Togliere la memoria non
farebbe risparmiare quasi niente; il costo della memoria sta tutto nell'**estrazione** (voce 2), non nel suo uso.

### B) Informazioni inutili o ripetute

- **Dritto e rovescio insieme: no.** Ogni scheda porta solo l'orientamento uscito (`tarot/schede.py`): ~380 token da
  dritta, ~310 da rovesciata. È già fatto bene.
- **La scheda di una carta entra due volte**: nella sua interpretazione e di nuovo nella sintesi (che riceve anche
  l'interpretazione già data). Nella croce celtica sono ~3 500 token di schede nella sintesi.
- **La trascrizione dell'intervista si ripete a ogni carta, insieme al riassunto** che la sintetizza: ~300–450 token per
  carta, ~4 000 nella croce celtica, e poi ancora nella sintesi e nell'estrazione della memoria (il giudice invece vede
  solo quesito e responso).
- **L'intervista rimanda tutto a ogni domanda**: istruzioni (828), elenco delle domande già fatte **e** la trascrizione
  che le contiene già. Alla sesta domanda il messaggio è ~1 700 token, di cui la parte nuova è una riga.
- **Istruzioni lunghe**: dottrina 5 000 token in ogni sintesi (il prefisso più grande, ma stabile: è quello che la cache
  sconta meglio); istruzioni dell'intervista 828 e dell'interpretazione 661, ripetute a ogni chiamata.
- **Responso troncato**: senza ragionamento la sintesi si è fermata al tetto di 1 800 token (`finish_reason: length`)
  in 9 chiamate su 25 — tutte quelle della croce celtica — e mai col ragionamento acceso, che ha un tetto di 18 432.
  I responsi troncati sono di ~7 000 caratteri, contro le 350–650 parole chieste. Non è uno spreco ma un rischio di
  qualità: in produzione può arrivare un responso tagliato a metà.

### C) Guardie e controlli

| Controllo | Dove | Cosa fa | Chiamate LLM | Quanto interviene davvero |
|---|---|---|---|---|
| Parole di crisi | `guards/lettura.py` | ferma la lettura e mostra l'aiuto | nessuna | — |
| Controlli deterministici delle domande | `tarot/intervista.py` | ricalca il quesito, previsioni, più domande, ripetizioni | nessuna | dall'1/10: 6 domande scartate |
| **Validatore delle domande** | `tarot/intervista.py::_giudica` | un secondo modello giudica ogni domanda candidata | 1 per domanda | dall'1/10: 5 domande scartate, su 63 poste |
| **Giudice del responso** | `guards/lettura.py::giudica` | ok / riscrivi / blocca contro le rubriche | 1 per lettura (+1 per riscrittura) | in produzione 9 letture su 9 «ok», nessuna riscrittura, nessun blocco |
| **Revisione** | `readings.py::sintesi` | riscrive il responso con le correzioni | 0 o 1 (una sintesi intera in più) | in produzione mai; nelle prove locali 7 letture su 16 senza ragionamento, nessuna su 8 col ragionamento |
| Formule proibite in uscita | `guards/lettura.py` | sostituisce l'interpretazione | nessuna | — |

Peso: senza ragionamento validazione e giudizio sono **~15% dell'ingresso e ~5% dell'uscita** di una tre carte; la
revisione, quando scatta, aggiunge una sintesi e un giudizio interi (circa +35–40% del costo della lettura). Senza
ragionamento il giudice locale ha chiesto di riscrivere quasi una volta su due, in produzione finora mai: il registro
dei consumi dirà quale dei due vale. Col ragionamento acceso validazione e giudizio ragionerebbero 1 500–2 400 token a
chiamata per dare un sì o un no.

### D) Oracolo per chi non è registrato

Verificato: **nessuna inferenza**. La barra mostra un tema scritto nei dizionari, scelto a caso; scrivendo si apre la
lettura gratuita (una per browser). La chat con il modello richiede l'accesso anche nel backend.

### E) Quanto pesa il ragionamento, compito per compito

Token d'uscita medi per chiamata:

| Compito | Uscita senza ragionamento | Uscita con ragionamento | Moltiplicatore | Oggi in produzione |
|---|--:|--:|--:|---|
| intervista | 50 | 3 488 | ×70 | spento |
| validazione | 43 | 1 571 | ×36 | spento |
| interpretazione | 166 | 3 507 | ×21 | spento |
| sintesi | 1 548 | 3 758 | ×2 | spento |
| giudizio | 200 | 2 359 | ×12 | spento |
| teaser | 116 | 1 566 | ×13 | spento |
| memoria_estrazione | 246 | 6 392 | ×26 | **acceso** |
| chat_proattiva | 64 | 1 742 | ×27 | **acceso** |

## 7. Possibili interventi

Stime sul mix reale e sulla configurazione di oggi; i risparmi sono sui token, i costi in dollari restano piccoli.

| # | Intervento | Risparmio stimato | Rischio per la qualità |
|---|---|---|---|
| 1 | **Oracolo senza ragionamento** (assegnare `chat_proattiva` in console con il ragionamento spento, o un budget piccolo su Nebius) | ~95% dell'uscita dell'oracolo: **circa metà dell'uscita totale di oggi** | medio-basso: aperture più piatte o più ripetitive; da rileggere un campione. È una modifica di configurazione, non di codice |
| 2 | **Memoria: spegnere il ragionamento dell'estrazione**, oppure **non estrarre finché l'embedding non funziona** | ~4–6 mila token d'uscita per lettura registrata (oltre metà dell'uscita di una tre carte) | basso per lo spegnimento (è un'estrazione in JSON); nessuno per la sospensione, visto che oggi le memorie non si salvano |
| 3 | **Assegnare un fornitore di embedding vero** (Nebius ne offre) | — (costa pochissimo) | nessuno: oggi la memoria non funziona affatto; senza questo l'intervento 2 è solo un risparmio |
| 4 | **Fornitore con cache del prefisso** (DeepInfra o Darkbloom) | sintesi: il prefisso di 6 500 token diventa ~90% scontato; sul mix reale −25/−40% del costo (vedi tabella 3) | nessuno sul testo; da verificare che il fornitore accetti `response_format` `json_object` (vedi sotto) |
| 5 | **Intervista più leggera**: mandare il riassunto progressivo invece di elenco + trascrizione, o un tetto di 4 domande | −30/−50% dell'ingresso dell'intervista (~10–15% della lettura completata, ~40% di quella abbandonata) | medio: domande meno legate al colloquio, ripetizioni; il tetto riduce il contesto per le stese lunghe |
| 6 | **Interpretazioni senza la trascrizione intera** (solo riassunto, o solo le ultime risposte) | ~300–450 token a carta; ~20% dell'ingresso delle interpretazioni | medio-basso: meno dettagli concreti ripresi nella lettura della carta |
| 7 | **Validatore solo sui casi dubbi** (o sullo stesso giro dell'intervista) | ~1 chiamata per domanda (~330 token in, ~45 out senza ragionamento) | medio: è la seconda difesa della regola «non chiedere la risposta»; dall'1/10 ha fermato 5 domande |
| 8 | **Dottrina per stesa** (solo le parti che servono alla stesa scelta) | fino a −3 000 token per sintesi | medio: la dottrina è ciò che rende la sintesi «di scuola»; con un fornitore con cache il guadagno si riduce molto |
| 9 | **Budget di ragionamento piccolo invece di acceso/spento** (es. 1024 su Nebius) per i compiti dove la qualità senza ragionamento non basta | da −70 a −90% del ragionamento di quel compito | da provare su Nebius: LM Studio non lo permette |

**Altre cose viste, da decidere:**

- **Il responso troncato** a 1 800 token senza ragionamento (vedi B): alzare il tetto costerebbe poco (qualche
  centinaio di token d'uscita), lasciarlo vuol dire responsi tagliati a metà di una sezione.
- **La negoziazione del formato JSON si rifà a ogni chiamata** per i compiti con un'assegnazione che sovrascrive il
  ragionamento: il fornitore si ricostruisce ogni volta e dimentica il formato già negoziato (nei log: «Modalità JSON
  negoziata» 199 volte in 4 giorni). Con Nebius non costa nulla, perché accetta subito `json_object`; con un fornitore
  che lo rifiuta (LM Studio lo rifiuta) **ogni chiamata JSON costa un tentativo fallito in più** (163 nelle due serie di prove, senza token ma con un giro in
  più).
  Prima di cambiare fornitore va verificato.
- **Con il ragionamento spento la qualità va guardata**: in una prova il validatore ha giudicato non valida una
  domanda corretta; il banco del 27/9 aveva prodotto una sintesi senza senso senza ragionamento. Nelle letture di
  queste prove i responsi senza ragionamento erano leggibili ma lunghi (spesso troncati).

## 8. Cosa è stato aggiunto

- **Registro dei consumi** (vale anche in produzione): ogni chiamata a un modello scrive una riga nella nuova tabella
  `llm_consumi` — compito, fase («# Compito: …» del prompt), fornitore, modello, token in ingresso, in cache, in uscita
  e di ragionamento, caratteri (per stimare quando il fornitore non riporta il consumo), tetto chiesto, durata, esito
  (`ok`, `troncata`, `errore`, `interrotta`), id della lettura o riferimento (`chat`, `apertura`), streaming. Punto unico:
  `llm/openai_compatible.py` e `llm/anthropic.py`; il compito e la lettura li porta `ProviderMisurato`
  (`llm/consumi.py`), che `provider_per` mette intorno a ogni fornitore. Scrive in background con una sessione propria:
  un errore di scrittura finisce nel log e non tocca la lettura. Si spegne con `TAROT_CONSUMI_LLM=false`. Nessun testo
  dei prompt o delle risposte viene salvato.
- **Migrazione** `a5c7e9b1d3f6` (dopo `e3a5c7e9b1d4`): tabelle `llm_consumi` e `llm_listini`, con Nebius, Darkbloom e
  DeepInfra già inseriti.
- **Pagina «Costi» della console** (`admin/app/costi/`, API `GET /admin/costi`, `…/costi/listini`): consumi per
  compito, per giorno e per lettura (completata, abbandonata), costo stimato con il listino scelto, quota di
  ragionamento e di cache, e i listini modificabili.
- **Script delle misure** `backend/tarot_core/tools/misura_costi.py`: riproduce queste misure contro LM Studio (o un
  altro server OpenAI-compatibile) e stampa il riepilogo.

**Da fare al rilascio**: la migrazione; nient'altro (il registro parte da solo). I dati della pagina «Costi»
cominciano dal rilascio.

## 9. Dopo gli interventi (4 ottobre 2026, sera)

*Le scelte dell'operatore, nel codice. **I testi dei prompt non sono cambiati**: le proposte per accorciarli sono in
`docs/proposte-prompt.md`, da decidere. Misurato come sopra (LM Studio, Nemotron 3.5 Lightning, ragionamento spento,
una chiamata alla volta, due ripetizioni, database `tarot_ui_costi2`), solo su ciò che cambia.*

### Cosa è cambiato

| # | Intervento | Dove |
|---|---|---|
| 1 | **Il ragionamento in console si legge com'è davvero.** Ogni compito mostra il livello in uso e chi l'ha deciso: «Acceso, livello medio — ereditato dal fornitore X», «Spento — scelto per questo compito», «Spento — lo decide il servizio» (embedding e aggiornamento della memoria). In testa alla pagina un avviso elenca i compiti che ragionano per eredità. | `llm/compiti.py` (`ragionamento_di`, `stato`), `admin/app/modelli/page.tsx` |
| 1 | **Livelli di ragionamento** al posto della casella: «eredita dal fornitore», `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, per compito e (come predefinito) per fornitore. Scegliere un livello per un compito senza assegnazione la crea, sul fornitore che già usa. Il livello diventa parametri **in un punto solo** (`llm/ragionamento.py`, chiamato da `RegistroModelli._configurazione_per`): `reasoning_effort` per Nebius, LM Studio e gli OpenAI-compatibili; `enable_thinking` + `reasoning_budget` proporzionale per NVIDIA NIM; budget del thinking per Claude. Mai i due dialetti insieme. Migrazione: `ragiona=true` → `medium`, `false` → `none` (fornitori e compiti), con downgrade. | `llm/ragionamento.py`, migrazione `b6d8f0a2c4e7` |
| 1 | **`store: false` in ogni richiesta** OpenAI-compatibile, scritto per ultimo; detto anche nell'informativa (sei lingue tradotte, le altre ricopiate dall'inglese). | `llm/openai_compatible.py`, `frontend/v2/i18n/*/privacy.ts` |
| 2 | **Validatore delle domande in tre modi** (console → Impostazioni): «solo nei casi dubbi» (predefinito), «sempre», «mai». I controlli deterministici restano sempre. Caso dubbio (`intervista.sospetta`): formula d'opinione («pensi», «secondo te», «do you think»), futuro o esito («succede», «andrà», «will»), somiglianza col quesito oltre 0,35, nelle letture di coppia il mondo interiore dell'altro o un dato sensibile; per le lingue diverse da italiano e inglese sempre. | `tarot/intervista.py` |
| 3 | **Guardia del responso in tre modi**, stesso predefinito. Prima della guardia LLM un controllo deterministico (`guards/lettura.da_guardare`) cerca: crisi, formule proibite, promesse di certezza, morte/malattia/disgrazie (non la carta della Morte), salute/diritto/denaro nel quesito o consigli operativi nel responso, certezze su un terzo, controllo o letture compulsive, e nelle letture di coppia verdetti, astrologia non fornita, violenza nel colloquio; altre lingue sempre. «Mai»: resta il filtro delle formule proibite. La revisione parte solo se la guardia segnala. | `guards/lettura.py` |
| 4 | **Stato sintetico della memoria** (tabella `memoria_stato`): voci `stabile`, `tema` (il quesito con la data, scritto dal codice), `volatile`. Dopo ogni lettura completata **una chiamata breve sempre senza ragionamento** sul quadro dell'intervista; aggiunte, conferme, rimozioni, doppioni, salute senza consenso e oblio (volatili 60 giorni, temi 120, al più 12/6/8 voci) li fa il codice. **Non entra nei prompt** finché l'interruttore della console resta spento: oracolo, intervista e sintesi leggono le memorie come prima. Il profilo («La mia storia») mostra lo stato, con la data in cui ogni voce si dimentica, modificabile e cancellabile; esportazione, cancellazione dell'account, revoca del consenso art. 9 e unione degli account lo includono. Conversione una tantum: `python -m tarot_core.tools.converti_memorie`. La memoria di prima (estrazione che ragionava + embedding) è spenta: si riaccende con `TAROT_MEMORIA_EMBEDDING=true`. | `tarot/stato_memoria.py`, `domain/memoria_repositories.py`, `api/routers/profile.py` |
| 5 | **Tetto della sintesi**: 2 600 token, +400 per le letture speciali, +600 per le stese con più di cinque posizioni (era 1 800 / 2 200). | `api/routers/readings.py` (`_tetto_sintesi`) |
| 6 | **Il dialetto JSON si negozia una volta per indirizzo e modello** per tutta la vita del processo, anche per i fornitori ricostruiti a ogni chiamata; se il server cambia, si rinegozia una volta. Lo **schema JSON rigoroso** (`strict`) si accende per compito in console, con ripiego automatico su `json_object` e poi sul testo, anche questo ricordato. | `llm/openai_compatible.py`, `llm/schemi_json.py` |
| — | Il catalogo dei fornitori ha **DeepInfra** (`https://api.deepinfra.com/v1/openai`, Stati Uniti) e **Darkbloom** (generico: indirizzo, campo del ragionamento e sede da verificare). | `llm/catalogo_fornitori.py` |

Scartati su indicazione dell'operatore: `max_completion_tokens` (conterebbe anche il ragionamento e troncherebbe le
risposte), `service_tier`, `presence_penalty`/`frequency_penalty`. Il registro dei consumi legge già
`prompt_tokens_details.cached_tokens` e `completion_tokens_details.reasoning_tokens`, anche nell'ultimo evento dello
streaming con `choices` vuoto (provato in `test_riduzione_costi.py`).

### Token per scenario, ragionamento spento: prima e dopo

| Scenario | | Chiamate | Ingresso | Uscita | Nebius | Darkbloom | DeepInfra |
|---|---|--:|--:|--:|--:|--:|--:|
| Tre carte (registrata) | prima | 18 | 28 328 | 2 530 | $0,0023 | $0,0013 | $0,0017 |
| | dopo | 17,5 | 34 032 | 3 146 | $0,0028 | $0,0016 | $0,0020 |
| Croce celtica | prima | 29 | 58 867 | 5 840 | $0,0049 | $0,0030 | $0,0038 |
| | dopo | 22,5 | 48 387 | 5 558 | $0,0042 | $0,0026 | $0,0032 |
| Compatibilità, 3 carte | prima | 22 | 53 698 | 5 528 | $0,0045 | $0,0026 | $0,0032 |
| | dopo | 20 | 42 249 | 3 793 | $0,0034 | $0,0020 | $0,0024 |
| Abbandonata dopo 2 domande | prima | 5 | 3 962 | 198 | $0,0003 | $0,0001 | $0,0002 |
| | dopo | 2 | 2 153 | 90 | $0,0002 | $0,0001 | $0,0001 |
| Oracolo: 2 aperture e 2 risposte | prima | 4 | 1 946 | 256 | $0,0002 | $0,0001 | $0,0001 |
| | dopo | 4 | 1 991 | 296 | $0,0002 | $0,0001 | $0,0001 |

Come leggerla: con due ripetizioni la variabilità del modello (quante domande fa, se il giudice chiede di riscrivere)
pesa quanto gli interventi. La tre carte «dopo» costa di più perché in una delle due letture il controllo
deterministico ha trovato una frase da guardare, il giudice ha chiesto di riscrivere e la revisione ha aggiunto una
sintesi intera (+14 000 token in ingresso su quella lettura); senza la revisione sarebbe a ~29 000 / ~2 500, come prima.
Gli effetti veri si vedono fase per fase:

| Fase | Prima | Dopo |
|---|---|---|
| Validatore delle domande | ~5 chiamate per lettura (una per candidata) | 1,5 (tre carte), 1,5 (croce celtica), 4 (compatibilità: più casi dubbi), 0 (abbandonata) |
| Guardia del responso | sempre, 1–2 per lettura | 0 su 2 compatibilità, 2 su 2 croci celtiche, 2 su 2 tre carte (una con revisione) |
| Memoria dopo la lettura | 2 220 in / 246 out (spenta) — **2 377 in / 5 279 out come in produzione, col ragionamento** | **486–605 in / 134–234 out**, sempre senza ragionamento |
| Negoziazione JSON con LM Studio | un tentativo fallito per ogni chiamata JSON dei compiti assegnati (163 nelle due serie) | **uno per processo** |
| Sintesi della croce celtica | troncata a 1 800 token 9 volte su 25 | 2 235–2 969 token, **finita sempre** («stop») |

### Cosa vuol dire in produzione (stima, Nebius)

Con la configurazione di oggi (cinque compiti assegnati senza ragionamento; dopo la migrazione il fornitore Nebius ha
livello `medium`, i cinque compiti `none`):

| Scenario | Prima | Dopo (stima) | Da dove viene |
|---|--:|--:|---|
| Tre carte registrata | $0,0039 | ~$0,0024 | memoria (−$0,0013), validatore e guardia sui soli casi dubbi |
| Croce celtica | $0,0063 | ~$0,0050 | memoria; +~700 token d'uscita perché la sintesi non si tronca più |
| Compatibilità | $0,0060 | ~$0,0044 | memoria, guardia saltata nei casi sereni |
| Abbandonata | $0,0002 | ~$0,00015 | validatore |
| **Una lettura completata (mix reale)** | **$0,0053** | **~$0,0039 (−27%)** | |

**L'oracolo non cambia da solo**: dopo la migrazione eredita `medium` dal fornitore, e la console ora lo dice
nell'avviso in testa a «Modelli». Scegliendo «Nessuno» per «Chat proattiva» l'uscita di un'apertura passa da ~1 000 a
~65 token (−90% del suo costo): era circa metà dell'uscita del pannello Nebius.

### Qualità (letture lette prima e dopo)

- **Sintesi**: la croce celtica ora finisce (prima si fermava a metà frase: «…l'energia creativa del», «…nel rapporto
  con»). I responsi restano lunghi — 730–1 800 parole contro le 350–650 chieste: è la proposta 5 di
  `docs/proposte-prompt.md`.
- **Domande dell'intervista**: uguali per stile a prima (i prompt non sono cambiati). Molte sono doppie («Da quanto
  tempo… e quali fattori…?») e qualcuna chiede cose superflue («i nomi o le iniziali delle persone più vicine a te»):
  succedeva anche col validatore sempre acceso, che non le scartava. Nessuna domanda passata senza validatore chiedeva
  la risposta al quesito o una previsione.
- **Guardia**: nelle letture lette, quelle saltate erano serene; una tre carte con frasi da guardare è stata riscritta
  dal giudice, come prima.
- **Stato della memoria**: le voci sono utili ma rumorose — alcune in prima persona («Non vedo mia sorella da tre
  mesi…»), qualche campo sbagliato (una scadenza come «denaro»), una confusione («un'offerta lavorativa a Milano per
  Marco»), una voce «stabile» discutibile. Da rivedere il prompt con l'operatore (proposta 6) prima di accendere
  l'interruttore.
- **Oracolo**: invariato (stesso prompt, stesse memorie).

### Cosa resta da decidere

- **Come spegnere il ragionamento su Nebius**: oggi il codice manda `reasoning_effort` (il livello), come documenta
  Token Factory, e **non più** `enable_thinking`/`reasoning_budget`, che i parametri del fornitore in produzione
  dichiarano. Va provato con una chiamata vera che Nemotron 3.5 Lightning su Nebius rispetti `reasoning_effort: none`
  (e i livelli intermedi); se non lo facesse, il tipo `nebius` va spostato nel dialetto `thinking`
  (`llm/ragionamento.TIPI_THINKING`), una riga.
- Il livello dell'oracolo (e degli strumenti della console) in console.
- Lo schema JSON rigoroso: da provare su Nebius compito per compito.
- I prompt: `docs/proposte-prompt.md`; l'interruttore della memoria breve.
- DeepInfra e Darkbloom: indirizzo e modello di Darkbloom, campo del ragionamento di entrambi, sede di Darkbloom per
  l'informativa.

**Da fare al rilascio**: la migrazione `b6d8f0a2c4e7`; facoltativo `python -m tarot_core.tools.converti_memorie`
(in produzione la tabella delle memorie è vuota).

## 10. Interpretazioni con una chiamata sola e livelli predefiniti (4 ottobre 2026, notte)

*Decisione dell'operatore, senza prove preliminari. Nessuna misura nuova a pagamento: una prova sul modello locale.*

| Cosa | Dove |
|---|---|
| **Una chiamata sola per tutte le carte.** La prima richiesta di svelamento di una lettura interpreta tutte le carte ancora da leggere e risponde in JSON (`{"carte": [{"posizione", "interpretazione"}]}`); il codice divide e scrive ogni testo nella sua carta. Le altre posizioni lo trovano pronto (stessi eventi SSE di prima: sito e app vecchi funzionano). Fase del registro dei consumi: `interpretazione_unica`. | `api/rivelazione.py`, `tarot/interpretazione.py` (`PROMPT_INTERPRETAZIONE_UNICA`, `messaggio_unico`, `dividi`) |
| Il prompt sono le regole di `PROMPT_INTERPRETAZIONE` parola per parola (cambia solo la frase «Interpreti UNA carta»), più lavoro / coppia / sicurezza della relazione come prima, più in fondo i blocchi e il formato JSON. Il contesto comune (quesito, quadro, colloquio, persone, stesa) una volta sola; per ogni carta lo stesso blocco della chiamata singola, calcolato come se le carte si girassero una alla volta (dignità, regole di coppia e «carte già rivelate» solo con quelle prima). | `tarot/interpretazione.py`, `rivelazione.dati_carta` |
| **Una generazione per lettura**: un task del processo per lettura; chi arriva mentre lavora lo aspetta (con `battito` ogni 5 s). Un client che chiude la connessione non butta l'interpretazione: il task la scrive comunque. Una replica dell'API in produzione: con più repliche, nel caso raro di due svelamenti simultanei su repliche diverse, la chiamata si farebbe due volte. | `rivelazione.avvia` |
| **Ripieghi**: JSON illeggibile, errore o carte mancanti/vuote → per le sole posizioni senza testo la chiamata singola di prima, in streaming; la chiamata unica non si ritenta. Una carta sola da leggere → direttamente la singola. Testo vuoto → `errore` come prima. | `readings.rivela`, `_interpreta_una` |
| `POST /readings/{id}/reveal-all`: gira tutte le carte coperte e manda i testi in un flusso (`carta` × N, `fase: lettura`, `token`/`fine` con `posizione`). Sito e app lo usano, con ripiego sugli svelamenti singoli se il server non lo conosce (404/405). L'utente vede un solo momento d'attesa («Il tuo lettore sta leggendo le carte…»). | `readings.rivela_tutte`, `frontend/v2/lettura/lettura.tsx`, `mobile/lib/pagine/lettura.dart` |
| Le interpretazioni delle carte ancora coperte non escono da `GET /me/readings/{id}` (anche nelle letture manuali). La sintesi sblocca una lettura con tutte le carte girate rimasta in «rivelazione» (client chiuso prima dell'ultima `fine`). | `readings.carta_json`, `readings.sintesi` |
| **Il tetto col ragionamento**: con un livello diverso da `none` il `max_tokens` è il tetto visibile **più il margine del livello** — `minimal` 2 048, `low` 4 096, `medium` 8 192, `high` 16 384, `xhigh` 24 576, `max` 32 768 (almeno il `reasoning_budget` mandato a NIM). Configurabile senza codice: `TAROT_MARGINI_RAGIONAMENTO='{"xhigh": 32768}'`. Vale per tutte le chiamate, sintesi compresa (2 600–3 600 + margine). Claude: tetto visibile + budget del thinking. Il tetto visibile della chiamata unica è 500 per carta + 200. | `llm/ragionamento.py` (`MARGINE_LIVELLO`, `tetto_con_ragionamento`), `llm/openai_compatible._tetto`, `llm/anthropic.py` |
| **Livelli predefiniti** (migrazione `c7e9a1b3d5f8`, solo dati, con downgrade): interpretazione e sintesi `xhigh`; intervista, validazione, giudizio, oracolo (`chat_proattiva`) e memoria `none`. I fornitori assegnati non cambiano; oracolo e memoria, senza assegnazione in produzione, la ricevono sul fornitore predefinito. Lo stato di prima va nel registro delle azioni (`modello.livelli_predefiniti`), da cui il downgrade lo rimette. | `migrations/versions/20261021_0900_livelli_predefiniti.py` |
| Lo schema JSON rigoroso si può accendere anche per «Interpretazione delle carte» (vale per la chiamata unica). | `llm/schemi_json.py` |
| **Salvaguardia sull'orientamento** (le regole del prompt non cambiano): il JSON chiede per ogni carta anche `orientamento` («dritta»/«rovesciata»), scritto prima del testo, così il modello lo ripete dal blocco. Una carta torna alla chiamata singola se il campo manca o non coincide con l'orientamento vero, o se è dritta e il testo la dice rovesciata (radici per lingua: it «rovesciat», en «reversed», es «invertid»/«al revés», hu «fordított», ru «перевёрнут»/«перевернут», uk «перевернут»; nelle altre lingue il testo non si controlla). Il motivo finisce nel log. Un falso allarme (un testo che nomina «rovesciata» una carta precedente) costa solo una chiamata singola in più. | `interpretazione.dividi`, `RADICI_ROVESCIATA` |
| **L'anteprima ha un compito suo** (`teaser`, «Anteprima del responso (senza account)» in console, con i suoi due menu). Senza assegnazione usa il modello della sintesi, ma col livello predefinito del compito, `none`: non eredita più `xhigh` dalla sintesi. Scegliendo un livello in console vale quello. Nessuna migrazione: il predefinito sta nel codice. | `llm/compiti.py` (`FORNITORE_DI`, `LIVELLO_PREDEFINITO_COMPITO`), `readings.sintesi` |

**Prova sul modello locale** (LM Studio, Nemotron 3.5 Lightning, `reasoning_effort: none`, prompt e divisione veri,
lettura finta): tre carte 3/3 in 3,1 s; croce celtica 10/10 in 6,5 s, JSON sempre valido. In una delle due croci
celtiche la carta 1 (dritta) è stata detta «rovesciata»: con dieci blocchi nello stesso messaggio l'orientamento può
scivolare da una carta all'altra. Da qui la salvaguardia sull'orientamento (sopra), provata solo col modello finto. Da
rileggere su Nebius con `xhigh`, guardando nel log quante carte tornano alla chiamata singola.

**Da sapere**: la chiamata unica con `xhigh` arriva tutta insieme: l'attesa prima dei testi è quella di una
generazione con ragionamento (su Nebius, nelle prove del 27/9, fino a ~8 000 token di pensiero).

**Da fare al rilascio**: la migrazione `c7e9a1b3d5f8` (dopo `b6d8f0a2c4e7`); rilasciare backend, sito e app insieme o
il backend per primo (sito e app nuovi ripiegano sugli svelamenti singoli se il server non conosce `reveal-all`).
