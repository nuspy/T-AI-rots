# Guida dettagliata ai due cancelli

## Cancello 1 — la scena (testo)

Cosa guardare nel prompt che `crea_mazzo campione`/`tutte` stampa, prima di mostrarlo all'operatore:
- **La scena descrive un'illustrazione, non una didascalia**: niente frasi tipo "the card shows a
  title reading...". Il nome della carta lo aggiunge già il blocco `TEXT ON THE CARD` a parte.
- **I riferimenti esoterici sono presenti come simboli dipinti**, non come etichette (es. il glifo di
  Mercurio disegnato su un oggetto della scena, non scritto a fianco).
- **Nessuna dimensione in pixel o rapporto d'aspetto**: se compare, è un bug di `crea_mazzo`
  (`SceneNonRiuscita` avrebbe dovuto fermarlo) — segnalalo, non limitarti a toglierlo a mano.
- **Coerenza con lo stile**: la scena deve leggersi dentro l'ambientazione data, non limitarsi a
  citarla in una riga e poi ignorarla.

Quando l'operatore chiede una correzione, capisci se riguarda:
- **la scena** (soggetto, composizione, simboli) → `--cambia "..."` rigenera la scena con l'LLM;
- **lo stile generale** (tecnica, palette, bordo) → il file di stile va corretto e il campione
  rilanciato da capo (non solo `--cambia`, che corregge la scena tenendo fisso lo stile).

## Cancello 2 — l'immagine (GPT Image, nel browser)

Passi concreti con Claude in Chrome (carica i tool `tabs_context_mcp`, `navigate`, `computer`,
`read_page`, `tabs_create_mcp` prima di iniziare, se deferred):

1. Apri una tab su ChatGPT (o l'interfaccia di GPT Image che l'operatore usa).
2. Incolla il `prompt` di `descrizioni.json` per la carta corrente (o il dorso) — solo quello: niente
   prompt negativo separato (vedi nota sotto, `descrizioni.json` non ne contiene uno).
3. Imposta **9:16**, **2K**, **qualità Alta** nei controlli dell'interfaccia — mai riscrivendoli nel
   prompt.
4. Genera, aspetta il risultato, scaricalo.
5. Mostra l'immagine scaricata all'operatore in conversazione prima di procedere.

**Perché niente prompt negativo**: `descrizioni.json` contiene solo `prompt` (positivo), non un
campo separato per le esclusioni. GPT Image via litmedia.ai (`browser-image-gen`) espone un unico
campo di testo: concatenare un blocco tipo "Avoid: nudity, gore, horror, ..." nello stesso prompt non
funziona come vero negative prompt e, bug osservato (2026-09-29), può far scattare il filtro di
contenuti sensibili del sito e far fallire la generazione senza nessun segnale visibile in pagina
(`{"code":1005,"msg":"Create failed, contains sensitive prompt"}` nella risposta di rete) — anche per
parole elencate solo per dire di evitarle. Le esclusioni vanno espresse come istruzioni positive
dentro lo stile/la scena (es. "bordo dorato pulito, nessun elemento moderno" invece di "no modern
objects" in un blocco a parte).

Cosa controllare prima di chiedere l'approvazione:
- **Il testo sulla carta è esatto e leggibile** (nome in alto/basso, ortografia corretta) — GPT Image
  rende bene il testo ma non è garantito, controlla lettera per lettera sulle prime carte.
- **Il bordo/cornice è coerente** con le altre carte già approvate (stesso spessore, stesso stile) —
  fondamentale dalla seconda carta in poi, altrimenti il mazzo non sembra un mazzo.
- **Niente elementi vietati**: watermark, firme, testo spurio, anatomia deformata — non c'è un
  prompt negativo a scoraggiarli (vedi nota sotto), quindi il `prompt` positivo deve già dire cosa
  rendere bene (bordo pulito, testo corretto, anatomia coerente); un difetto va corretto rigenerando
  o correggendo la scena, non aggiungendo un'esclusione a parte.

Se la carta non va bene, chiedi all'operatore cosa cambiare e valuta se serve:
- rigenerare con lo stesso prompt (variazione casuale) — spesso basta;
- una scena diversa (torna al cancello 1 con `--cambia`);
- una correzione allo stile generale (rara dopo il campione, ma possibile se una caratteristica dello
  stile si rivela impossibile da rendere bene).

## Tenere lo stato onesto su una corsa lunga

`Grafica/Cards/<NomeSet>/manifest.json` traccia, per carta e per il dorso, `descritta` (la scena è
scritta e approvata) e `scaricata` (l'immagine è salvata su disco). Prima di riprendere una sessione
interrotta:
1. Leggi `manifest.json` per sapere cosa manca — non ricostruirlo a occhio dalla cartella.
2. `descrizioni.json` contiene già tutte le scene fatte finora: `crea_mazzo tutte` (senza
   `--solo-carte`) genera solo quelle mancanti, non tocca le altre.
3. Le immagini mancanti (descritte ma non ancora scaricate) sono quelle in `manifest.json` con
   `descritta: true` e `scaricata: false` — riprendi il cancello 2 da lì.

## Prima del passo 6/7 (Web e PDF)

Controlla che `Grafica/Cards/<NomeSet>/` abbia tutte le 78 carte + `dorso.webp` prima di lanciare
`resize_cards.py`: una carta mancante genera comunque un `Web/` parziale (nessun errore), e il PDF di
prova disegna un segnaposto grigio al posto suo — utile per una prova di impaginazione, ma da
correggere prima della versione finale.
