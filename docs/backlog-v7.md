# Backlog v7 — TAROTS chat

Registrato verbatim dalle istruzioni dell'operatore (2026-09-29), come da convenzione già usata per
`backlog-v6.md`. Non ancora pianificato in fasi: vedi il piano quando disponibile.

## 1. Reasoning per-compito, configurabile da GUI admin

Poter abilitare/disabilitare il ragionamento ("reasoning") separatamente per ogni tipo di
inferenza: domande dell'intervista, interpretazione delle carte, risposta finale (sintesi), e
tutte le altre. Configurabile dalla console admin. **Default: reasoning disattivato.**

**Contesto tecnico (sessione 2026-09-29, non dall'operatore)**: risolto in sessione un bug per cui
il "pensiero" del modello (`<think>...</think>`) finiva nel testo mostrato all'utente, e un secondo
bug per cui il tetto di `max_tokens` (6144, fisso nel codice) era inferiore al `reasoning_budget`
(16384) dichiarato nei parametri del fornitore attivo — causa primaria della lentezza e dei
fallimenti sulla risposta finale segnalati dall'operatore. Un confronto diretto sul modello di
produzione (Nemotron 3.5 Lightning via Nebius) su interpretazione di carta + sintesi finale,
stesso input, tre varianti (reasoning_budget 16384 / 4096 / disattivato) ha mostrato: **disattivato
è risultato il più veloce (0,8s vs 29,5s sulla carta) e non ha peggiorato la qualità** (sintesi più
lunga e dettagliata delle tre); **4096 ha troncato la sintesi finale a metà frase** — la scelta
peggiore delle tre per quel compito. Questo motiva il default "disattivato" richiesto qui, con la
possibilità di riattivarlo per compito se un'evidenza futura mostra un vantaggio di qualità.

## 2. Registro linguistico meno esoterico, per utente (scheda profilo)

Un controllo sulla scheda utente per evitare, nelle risposte, espressioni troppo esoteriche e usare
invece un registro di lingua quotidiana. Effetto per singolo utente (non globale).

## 3. Riorganizzazione del menu

- Le voci "The Cards" e "Spreads" vanno spostate in un sottomenu "...more".
- "Card of the Day" e "Blog" diventano voci del menu principale.

## 4. Posizione del banner "Ask something"

Il banner "Ask something" (invito "fammi una domanda", v6 Fase F) va ancorato alla parte
**inferiore** dello schermo, non a quella superiore.

## 5. Regole GDPR

- Possibilità e accettazione esplicita di condividere dati e informazioni con i partner (tutti i
  partner).
- Custode del trattamento dati: Andrea Taini.
- Il salvataggio dell'accettazione include: data, IP, ora, e altre informazioni utili a ricostruire
  la paternità della decisione (audit/provenienza).
- Messaggio di accettazione cookie con due opzioni: "It's fine" oppure "Please no".

## 6. Come aggiungere un mazzo e venderlo — chiarito in sessione, non richiede sviluppo per la parte base

Domanda dell'operatore, risposta trovata nel codice esistente (2026-09-29): il mazzo si crea con la
skill `crea-mazzo-tarocchi`, l'artwork va in `frontend/public/cards/<slug>/` (richiede build+deploy
frontend), il mazzo si registra in console (`POST /admin/decks`) con tre prezzi indipendenti già
esistenti nello schema: `prezzo_digitale`, `prezzo_stampa`, `prezzo_fisico` (+ `richiede_spedizione`
per il fisico). **Da verificare**: solo `prezzo_digitale` risulta pienamente cablato nella logica
sconti/offerte (`billing/mazzi.py`); `prezzo_stampa`/`prezzo_fisico` sono nello schema ma il flusso
di checkout (`billing/ordini.py`) andrebbe verificato prima di contarci per una vendita reale.

## 7. Upload di un mazzo da GUI admin

Poter caricare la cartella con i file di un mazzo nuovo direttamente dalla GUI admin, con
salvataggio automatico nella posizione corretta (oggi: `frontend/public/cards/<slug>/`, con relativo
build+deploy del frontend — da capire se l'upload da GUI possa evitare quel passaggio o debba
comunque innescarlo).

## 8. Pubblicazione automatica nello shop — verificato in sessione, GIÀ funzionante

Verificato (2026-09-29): `GET /decks` (pubblico) interroga `deck_repositories.attivi_ora()`, che
seleziona dinamicamente ogni mazzo con `attivo=true` entro la finestra di attivazione. Un mazzo
creato in console con `attivo: true` (il default) compare nello shop immediatamente, senza un passo
di pubblicazione separato. Nessuno sviluppo necessario per questo punto.

## 9. Selezione del mazzo nelle letture + mazzo di default per utente

- In ogni lettura: un menu a tendina per scegliere il mazzo, con miniatura (thumbnail) dell'immagine
  e nome del mazzo.
- Sulla scheda personale (profilo): selezione del mazzo di default per l'utente.

## 10. Vota il prossimo mazzo

Sezione "Vota prossimo mazzo": sistema di votazione per utenti registrati, con statistiche in
percentuale mostrate dopo la votazione. Se esiste una tornata di votazione precedente, la pagina di
voto mostra anche i vincitori precedenti con la percentuale di votanti ottenuta per quel mazzo.
Possibilità di rifare la votazione modificando il proprio voto (il nuovo voto sostituisce il
precedente, non si somma).

GUI Admin per: inserire (upload delle carte e attribuzione automatica del valore/nome carta per
convenzione del nome file) e modificare nuovi mazzi candidati, la loro descrizione e alcune carte di
prova (numero variabile) per i mazzi da mettere al voto; vedere le statistiche; CRUD completo;
accettare uno o più vincitori (possibilità di accettarne più di uno: checkbox per candidato +
bottone "Accetta selezionati").

Bottone grafico (bullet) in home page che porta alla pagina di voto.

**Estensione "tornate elettorali" (dettata durante l'implementazione, 2026-09-29)**: quando si crea
una votazione, si selezionano le proposte di nuovi mazzi già inserite (riserva) e si dichiara la
data di fine della votazione; la tornata si chiude in automatico a quella data (nessun pulsante da
premere) e il risultato viene esposto in home page con link alle statistiche di voto e le miniature
(ingrandibili in un dialogo) di ogni mazzo che era in corsa, non solo del vincitore.

**Estensione "genera anche i non vincitori" (stessa sessione)**: possibilità di generare da GUI il
`Deck` reale anche per un candidato che non ha vinto la votazione, non solo per gli accettati
(nessuna automazione ulteriore sulla generazione dell'artwork — resta la pipeline
`crea-mazzo-tarocchi`, supervisionata con i suoi due cancelli umani: l'operatore ha scelto
esplicitamente di non automatizzare oltre la creazione del `Deck`).

**Estensione "suggerisci tema mazzo" (stessa sessione)**: gli utenti iscritti possono proporre
liberamente un tema per un futuro mazzo, in testo libero; l'admin rivede i suggerimenti in console e
decide se trasformarli in una proposta vera nella riserva.

## 11. Voce "Home" nel menu

Aggiungere una voce "Home" al menu di navigazione principale.

## 12-13. Centratura e zoom della home, specialmente su mobile

I contenuti della home non sono centrati nell'allineamento orizzontale — problema evidente
specialmente su mobile, dove il livello di zoom di default è troppo elevato e causa pan orizzontale
(scorrimento a destra/sinistra). Serve correggere zoom e centratura per la visualizzazione completa
degli elementi.

**Diagnosi trovata in sessione (2026-09-29, non dall'operatore)**: causa individuata nell'hero della
home (`frontend/app/soglia.tsx`) — carte posizionate in assoluto fino al 78% di un contenitore senza
`overflow: hidden`, a larghezza fissa non responsive (150px), che sfondano il viewport su schermi
stretti.

## 14. Pubblicazione del sito alternativo v2

Esiste una directory `frontend/public/v2/` creata da un altro strumento (Codex) con una versione
alternativa del sito ottimizzata per il marketing. Applicare anche a questa le modifiche UI dettate
per v7, e pubblicarla — dovrebbe essere già raggiungibile da `tarots.chat/v2`.

**Verificato in sessione**: `v2/` è un sito statico autonomo (HTML/CSS/JS scritto a mano, non legato
al frontend Next.js principale) — non tracciato da git oggi. Basta includerlo nel prossimo
build+deploy del frontend perché diventi raggiungibile (nessuna configurazione aggiuntiva
necessaria per i file già presenti); le URL pulite senza `/index.html` richiederebbero un piccolo
`rewrite` in più, opzionale. Il sito v2 risulta già corretto rispetto al bug dei punti 12-13 (non
serve intervento lì), a differenza del sito principale.

## Istruzione di chiusura (dall'operatore)

"Quando hai finito committa tutto, crea su pc locale le immagini docker e pubblicale." — il commit
e il deploy (build immagini + pubblicazione) vanno fatti solo a lavoro completo e verificato, non
punto per punto, sullo stesso principio già seguito per v6 (Fase H solo a fine ciclo).
