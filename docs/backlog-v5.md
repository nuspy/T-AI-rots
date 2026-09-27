# Backlog v5 — richieste rimandate

Funzionalità richieste dall'utente ma esplicitamente rimandate a un rilascio futuro (v5), non ancora
iniziate. Registrate qui perché non vadano perse tra una sessione e l'altra.

---

## 1. Blog: formattazione ricca + media inline via API/skill

Il post del blog oggi è testo semplice. Serve:
- Formattazione ricca (grassetto, corsivo, titoli, liste, citazioni) nel corpo del post.
- Immagini e video **inline** nel corpo (non solo la cover), inseribili tramite l'API di
  pubblicazione (non solo a mano in console).
- La skill `tarots-blog-publisher` va aggiornata di conseguenza: linee guida su come e quando
  scegliere/posizionare le immagini nel corpo con LitMedia (non solo la cover), mantenendo
  l'ottimizzazione SEO già prevista.

## 2. Gestione multi-mazzo

Oggi l'app usa un solo mazzo (Thoth). Serve:
- Scelta del mazzo nella pipeline di lettura (l'utente sceglie con quale mazzo leggere).
- **Vendita di mazzi digitali** (nuovo prodotto acquistabile — sblocco della grafica/mazzo per le
  letture in app —, non solo abbonamento/pacchetti crediti); distinta dalla versione fisica
  stampabile del punto 2bis, che è un prodotto a parte.
- Attributi per-mazzo, incluso un periodo di **attivazione automatica** (es. un mazzo a tema
  stagionale che si attiva/disattiva da solo in certe date).
- Import massivo di nuovi mazzi che segua lo standard di nomenclatura carte già in uso nel
  progetto (stesso schema di file/id delle carte del Thoth).

### 2bis. "Stampa i tuoi Tarocchi" — mazzo fisico stampabile (PDF)

Nella pagina di vendita dei mazzi, un bottone/link aggiuntivo **"Stampa i tuoi Tarocchi"** (i18n) che
propone, per il mazzo scelto, un **PDF stampabile**: le carte del mazzo già impaginate (più carte per
pagina, per minimizzare il numero di pagine necessarie alla stampa), in una **dimensione standard** da
mazzo di carte da gioco. Prezzo di questo prodotto (distinto dallo sblocco digitale del mazzo)
**impostabile da console admin**.

### 2ter. Un'offerta per mazzo, con sconto a scaglioni per acquisti multipli

Dato che in v5 esistono più grafiche di mazzo (oltre al Thoth), la pagina vendita mostra un'**offerta
distinta per ciascun mazzo disponibile**, ognuna con il proprio prezzo e un bottone **"Aggiungi
all'acquisto"** (carrello/selezione multipla, non acquisto singolo immediato). Più bottoni "Completa
l'ordine" sparsi lungo la pagina (non solo in fondo).

**Sconto per quantità di mazzi diversi nello stesso ordine** (non è un browser di "compra N copie
dello stesso", è "compra N mazzi *diversi* insieme"): ogni mazzo aggiuntivo oltre al primo porta uno
sconto supplementare del 10% sul totale (2 mazzi → 10%, 3 mazzi → 20%, 4 → 30%…), fino a un **tetto
massimo del 50%**.

**Sconti singoli per mazzo, configurabili da admin** (indipendenti dallo sconto-quantità sopra):
- Per ciascun mazzo (fisico o virtuale/digitale) l'admin può impostare da console uno sconto con
  **data di scadenza**.
- Mentre attivo: prezzo pieno mostrato barrato + prezzo scontato accanto, e una piccola grafica
  sovrapposta all'immagine di copertina del mazzo con la scritta **"Offerta"** (i18n).
- **Rimozione automatica** alla scadenza (nessun intervento manuale: un job/controllo a tempo, o un
  controllo a lettura che confronta la data corrente con la scadenza, da decidere in fase di
  progettazione — coerente con come sono già gestite le altre offerte a tempo del progetto).

### 2quater. Carrello, indirizzi di spedizione, registro acquisti

Necessario dal momento in cui si vendono più mazzi insieme (con lo sconto a scaglioni sopra): non basta
più un acquisto istantaneo per singolo prodotto, serve un vero **carrello** (più mazzi/PDF nello stesso
ordine, quantità, il "Completa l'ordine" agisce sul carrello intero, non su un singolo bottone
"Aggiungi").

**Gestione indirizzi di spedizione**: necessaria perché non tutti i prodotti-mazzo sono digitali/PDF —
esiste già un riferimento nel sito attuale a un mazzo fisico vero e proprio, professionalmente stampato
(`MAZZO.description` in `frontend/lib/seo-testi.ts`: "78 carte illustrate, un dorso dorato e un
cofanetto da collezione", oggi segnato "in preparazione"). Per quel prodotto serve: raccolta e
validazione dell'indirizzo al checkout, possibilità di salvare più indirizzi sul profilo, scelta
dell'indirizzo di spedizione al momento dell'ordine. Il PDF stampabile in proprio (2bis) e lo sblocco
digitale (punto 2) restano senza spedizione.

**Registro acquisti (log ordini)**: storico ordini con cosa è stato comprato, prezzo pagato, sconti
applicati (quantità + eventuale offerta a tempo), per prodotto digitale il collegamento di
download/sblocco, per prodotto fisico lo stato di spedizione. Visibile sia in console admin (tutti gli
ordini) sia nel profilo dell'utente (i propri ordini) — probabilmente un `Ordine`/`RigaOrdine` nuovo,
distinto dal `credit_ledger` già esistente per i crediti, dato che qui si tratta di beni (mazzi), non
crediti di lettura.

**File/aree presumibilmente coinvolte quando si affronterà** (da verificare, non ancora esplorato):
la tabella `Deck`/`Mazzo` prevista al punto 2, un nuovo modello `OffertaMazzo` (prezzo pieno, prezzo
scontato, scadenza), generazione PDF impaginato (nuova dipendenza da valutare, es. libreria di
composizione PDF lato backend), la pagina vendita mazzi lato frontend (carrello multi-selezione,
calcolo sconto a scaglioni lato client o server, badge "Offerta" i18n), nuovi modelli `Ordine`/
`RigaOrdine`/`IndirizzoSpedizione`.

**Precisazioni sul PDF stampabile (2026-09-27)**: fronte e retro allineati per la stampa fronte/retro
(ogni carta fronte deve cadere esattamente sopra il proprio dorso quando il foglio si stampa sui due
lati — non solo "tutti i fronti poi tutti i dorsi", ma un'impaginazione pensata per l'allineamento
fisico pagina per pagina). Comportamento legato al prezzo del mazzo:
- **Prezzo 0** (gratuito): download diretto/automatico (nessun acquisto, nessun carrello), ma il PDF
  in questo caso è una **versione speciale con marchio**: un piccolo logo "tarots.chat" nel margine di
  ogni carta, sia sui dorsi sia sui fronti.
- **Prezzo > 0**: PDF senza marchio (o con marchio ridotto/assente, da decidere), dietro acquisto come
  gli altri prodotti del negozio.
Questa distinzione (marchio condizionale sul prezzo) va nel modello `OffertaMazzo`/`Deck` insieme al
resto (prezzo, sconto, scadenza).

## 3. "Interpreta i miei tarocchi" — lettura da carte fisiche già estratte

Nuova sezione dell'app per chi ha già tirato le carte fisicamente (mazzo reale in mano) e vuole
solo l'interpretazione, non l'estrazione digitale.

**Flusso:**
1. L'utente entra nella nuova sezione; l'app chiede **quale schema** è stato usato (stesso elenco
   stese di sempre: Croce Celtica, ecc.).
2. Si visualizza lo **schema vuoto** (le posizioni della stesa scelta, senza carte).
3. L'utente tocca una posizione → si apre un **dialog** che chiede il tipo di carta: Arcano
   Maggiore, Bastoni, Coppe, Spade, Dischi (i semi effettivi del mazzo Thoth).
   - **Senza bottone di conferma**: appena scelto il tipo, sotto appare subito l'elenco delle
     carte di quella categoria (i 22 arcani maggiori, oppure le carte del seme scelto — asso,
     2..10, cavaliere/regina/principe/principessa secondo la nomenclatura Thoth).
   - Bottoni **Indietro** (torna alla scelta del tipo) e **OK** (conferma la carta scelta per
     quella posizione).
4. Le opzioni (seme/arcano maggiore, poi valore/nome carta) sono **in testo**, ciascuna con
   un'icona coerente con lo stile del sito, dentro elenchi puntati (bullet), non griglie di
   immagini — per restare leggero e navigabile anche su mobile.
5. **Stato visivo delle posizioni**: sulle posizioni **già impostate** appare il bottone
   "**Modifica**"; su quelle **non ancora impostate** appare "**Aggiungi**".
6. A differenza della lettura normale, le carte impostate **sono già scoperte/rivelate**
   nell'immagine dello schema (mai il dorso), perché l'utente le ha già viste dal vivo.
7. Quando **tutte** le posizioni della stesa hanno una carta assegnata, appare il bottone finale
   **OK**.
8. Alla pressione: si passa alla **richiesta della domanda**, esattamente come nella lettura
   normale (stessa barra laterale, stesse domande di approfondimento generate dall'app).
9. Da lì in poi la lettura **procede come una lettura normale** (intervista di approfondimento,
   interpretazione carta per carta, sintesi, giudizio) — l'unica differenza è che le carte non
   vengono estratte digitalmente ma inserite manualmente all'inizio.

**Promozione in home (2026-09-27)**: una volta costruita, questa funzione va pubblicizzata in home
page come tratto distintivo — l'utente l'ha definita esplicitamente "una unique feature che abbiamo
solo noi". Non va promossa prima che esista davvero.

**Note tecniche da valutare quando si affronterà l'implementazione** (non ancora esplorate nel
codice):
- Riuso del componente `ventaglio`/geometria-stesa esistente per disegnare lo schema vuoto e poi
  popolato, invece di crearne uno nuovo da zero.
- Nuovo componente "selettore posizione → dialog seme/arcano → dialog carta", con la lista carte
  già disponibile lato frontend (stesso catalogo usato da `/carte`).
- Il resto della pipeline di lettura (intervista, interpretazione, sintesi, giudizio) dovrebbe
  poter partire da un set di carte "già note" invece che da un'estrazione casuale: verificare dove
  oggi la pipeline genera l'estrazione (`readings.py` e dintorni) per capire il punto di innesto
  giusto senza duplicare logica.

## 4. Testi lunghi (carte/stese) tradotti in tutte le lingue dell'interfaccia, non solo it/en

Oggi (`backend/tarot_core/tarot/conoscenza.py`, `LINGUE_CONTENUTO = ("it", "en")`) i testi lunghi —
descrizione e origine di una stesa, significato/domanda di ogni posizione, le schede complete delle
carte (essoterico, psicologico, iniziatico, ombra, dritto/rovescio, ambiti, nota Crowley) — esistono
**solo** in italiano e inglese (`knowledge/en/`). L'interfaccia supporta una quindicina di lingue
(`lib/i18n`), ma in quelle lingue i contenuti lunghi ripiegano sull'inglese: solo i **nomi** (carte,
stese, posizioni) sono tradotti per lingua, in `knowledge/nomi.json`.

Da fare: tradurre i testi lunghi (stesso schema di `knowledge/en/`, una cartella `knowledge/<lingua>/`
per lingua) per le lingue che si vogliono coprire, con la stessa validazione rigorosa già in vigore per
l'inglese (una carta o una stesa senza la sua scheda in una lingua dichiarata è un errore di rilascio).

**Non confondere con**: il bug corretto in questa sessione (le mattonelle stese in home non passavano
`lang` all'API e mostravano sempre l'italiano anche sulla versione inglese del sito) — quello era un
difetto di collegamento, già risolto; qui si tratta di scrivere/generare contenuto nuovo per lingue che
oggi non hanno affatto una traduzione dei testi lunghi.

## 5. Traduzione automatica degli articoli del blog

Gli articoli del blog oggi si scrivono in inglese (canonico) più, quando serve, una versione italiana
separata scritta a mano — nessuna traduzione automatica delle altre lingue.

Cercata in questa sessione un'estensione di terze parti gratuita e illimitata per tradurre le pagine
del blog: nessuna opzione affidabile trovata per questo stack (GTranslate gratuito esclude i siti che
generano ricavi come questo; TranslatePress gratuito è solo per WordPress; l'unica alternativa "open
source gratuita" trovata è di un fornitore non verificato, da non usare senza controlli più seri).

Probabile strada alternativa da valutare: **generare** la traduzione con l'LLM già usato dal progetto
per le letture (stesso motore, nuovo compito "traduci articolo"), invece di un widget di terze parti —
mantenendo la qualità SEO (slug, meta tag, `hreflang`) per ogni lingua generata, come già avviene per
it/en scritti a mano. Meccanismo esatto (a richiesta, al salvataggio, in batch) non ancora deciso.
