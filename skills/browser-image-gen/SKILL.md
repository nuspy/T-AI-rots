---
name: browser-image-gen
description: Browser automation fallback (Playwright on the litmedia.ai website) used by the crea-mazzo-tarocchi skill to draw tarot deck cards with GPT Image. Use it only when crea-mazzo-tarocchi invokes it, or when the operator asks by name for the free browser method. Never for the TAROTS chat blog (covers or pictures in articles), which are made only by tarots-blog-images with litmedia-skill, and never as a substitute for litmedia-skill when it fails or costs credits.
---

# Generazione immagini via browser (litmedia.ai, gratis/economico)

Ripiego di automazione del browser: guida un browser reale (Playwright/Chromium, headless)
sull'interfaccia **web** di litmedia.ai, che offre alcuni modelli **gratuiti** (0 crediti a certe
risoluzioni). Più lenta (un'immagine alla volta, ~60-90s) e fragile (dipende dal layout del sito).

**Chi la usa**: la skill `crea-mazzo-tarocchi` (le 78 illustrazioni di un mazzo nuovo con GPT Image,
tramite `crea_mazzo genera`), oppure l'operatore quando chiede per nome il metodo gratuito via browser.

**Chi non la usa mai**: il blog di TAROTS chat. Copertine e immagini degli articoli si fanno solo con
la skill `tarots-blog-images` (`tarots_images.py generate`, che chiama `litmedia-skill`): niente carte,
prompt controllati, nessun riuso. Se `litmedia-skill` non risponde o mancano i crediti, per il blog
non si ripiega su questa skill: l'articolo resta senza immagine e lo si dice nel rapporto.

**Non sostituisce `litmedia-skill`**: sono due strumenti distinti con la stessa "materia prima"
(litmedia.ai) ma percorsi diversi.

## Setup (una tantum, per account)

La sessione web (cookie di login) va salvata una volta sola, con un vero login umano — non c'è un
meccanismo di credenziali automatico qui (a differenza di `litmedia-skill`, che usa OAuth device
grant per la sua API key separata):

```
python scripts/login_una_tantum.py
```

Apre una finestra Chromium **visibile** (non headless) su litmedia.ai e resta aperta 180 secondi:
l'operatore fa login lì dentro nel tempo a disposizione. Allo scadere, la sessione (cookie +
storage) viene salvata in `sessione_litmedia.json`, accanto a questo file — **mai committarlo in un
repository**, contiene una sessione di login reale.

Verifica che la sessione salvata sia valida (senza aprire finestre, headless):
```
python scripts/verifica_sessione.py
```
Stampa un indizio di login riuscito (crediti visibili, nessun invito a fare login) e salva uno
screenshot di controllo.

La sessione scade prima o poi (durata esatta non nota, non documentata da litmedia.ai): quando
`genera_immagine.py` inizia a fallire nel trovare il modello o a restare bloccato senza mai vedere
un'immagine nuova, la causa più probabile è la sessione scaduta — rilanciare `login_una_tantum.py`.

## Uso

```
python scripts/genera_immagine.py --model nano-banana --prompt "<prompt in inglese>" \
    --aspect 16:9 --resolution 1K --output percorso/immagine.png
```

- `--model`: uno tra `gpt-image`, `nano-banana`, `seedream`, `wan`, `flux`, `stable-diffusion`
  (nomi come appaiono nel selettore del sito). **Il costo dipende dalla COMBINAZIONE di modello +
  aspect + risoluzione + qualità, non solo dal modello**: confermato nei test (2026-09-29) che
  `nano-banana` a 1:1/1K e a 3:2/1K costa 0 crediti, ma `gpt-image` a 9:16/2K/Alta qualità ne costa
  **30** — la stessa famiglia può quindi essere gratis o a pagamento a seconda delle altre
  impostazioni. Non fidarsi di un test fatto con impostazioni diverse: **leggere sempre
  `Credits Required` nell'output di QUESTA esecuzione**, con QUESTI parametri, prima di assumere
  gratuità.
- `--aspect`: `1:1`, `4:3`, `3:4`, `3:2`, `2:3`, `16:9`, `9:16`.
- `--resolution`: `1K`, `2K`, `4K`.
- `--output`: percorso del file da scrivere. Il formato reale (PNG/JPEG/WebP) è quello che il sito
  restituisce, non necessariamente quello suggerito dall'estensione del percorso — lo script
  verifica la firma binaria del file e la stampa nell'output finale.
- `--timeout`: secondi massimi di attesa del risultato (default 180; una generazione reale ha
  impiegato circa 70-90s nei test).

Un'esecuzione tipica stampa, su stderr, il costo in crediti mostrato prima di generare e l'URL
dell'immagine trovata, e su stdout la riga finale `Immagine salvata in: <path> (<formato>, <byte>)`.
Un agente chiamante dovrebbe trattare l'assenza di quella riga finale (l'errore va su stderr con
prefisso `errore:`) come fallimento esplicito, mai assumere successo dal solo exit code.

## Come funziona (per manutenzione futura)

1. Apre `https://www.litmedia.ai/app/litvideo/text-to-image/` riusando la sessione salvata.
2. **Chiude subito il banner promozionale in alto** (click a coordinate fisse, in alto a destra).
   Il suo testo ("GPT Image 2.5 Flare Included", ecc.) condivide parole con i nomi dei modelli
   veri: lasciato aperto, un `get_by_text` sul nome del modello può cliccare quello invece del vero
   elemento del menu (bug osservato: apriva la pagina dei prezzi invece di selezionare il modello).
3. **Clicca sul tab "Record"** (cronologia personale), mai lasciato su "Inspiration" (galleria
   pubblica di esempi altrui, a volte vecchia di mesi) — bug osservato: con "Inspiration" attivo,
   il rilevamento del risultato prendeva l'immagine di un esempio pubblico scelta a caso, senza
   errore, semplicemente il file sbagliato.
4. **Seleziona il modello in due click, sempre, mai saltati anche se sembra gia' quello giusto**
   (scelta esplicita dell'operatore: se il default del sito cambia in futuro, un salto silenzioso
   genererebbe con un modello diverso senza che nessuno se ne accorga):
   - Primo click: la FAMIGLIA nella lista di primo livello (GPT Image / Nano Banana / Seedream /
     Wan / Flux / Stable Diffusion) — qui il nome e' ancora univoco, un match parziale va bene.
   - Secondo click: la VARIANTE esatta, con testo **esatto** (`exact=True`). Necessario perche'
     alcune famiglie (osservato per Nano Banana) aprono un riquadro con piu' varianti a pagamento
     ("Nano Banana 2", "Nano Banana Pro") oltre a quella base gratuita — un match parziale su
     "Nano Banana" prenderebbe "Nano Banana 2" per errore, perche' lo contiene come sottostringa.
     Se la famiglia non ha varianti (es. Flux), il secondo click su testo esatto trova comunque
     lo stesso elemento e non fa danno.
5. Scrive il prompt nel primo `<textarea>` della pagina (unico presente in questo tab). Poi prova
   aspect ratio e risoluzione per testo esatto — questi *possono* fallire silenziosamente su
   varianti dell'interfaccia; lo script continua comunque, non blocca la generazione.
6. Clicca "Create", poi **intercetta la risposta di rete** (non il DOM) che porta l'URL
   dell'immagine risultante — un `page.on("response", ...)` filtrato per dominio `litvid.org`,
   estensione immagine, e dimensione minima plausibile (150 KB) per scartare avatar/icone
   dell'interfaccia che condividono dominio ed estensione. **Storia dei bug, in ordine, ciascuno
   causa del successivo cambio di approccio**: ancoraggio DOM per posizione/dimensione (prendeva
   quasi sempre il risultato sbagliato: miniature della colonna laterale o della galleria
   "Inspiration"), ancoraggio sul testo "Processing" (il locator diventa invalido appena il testo
   sparisce a fine generazione), ancoraggio sulla data/ora (gia' presente in pagina da un test
   precedente, quindi `.first` post-click non garantisce la voce nuova).
   **Bug costoso, risolto per ultimo (2026-09-29), lo stesso giorno della soglia dimensionale**:
   anche con l'intercettazione di rete, "la prima risposta MAI VISTA da questo script" non basta —
   diversi tentativi FALLITI precedenti (bug gia' risolti ma che avevano gia' fatto danno) avevano
   lasciato veri risultati generati correttamente ma MAI scaricati (quindi "mai visti" per l'elenco
   persistente); una richiesta successiva, scollegata, poteva riprendere in modo incidentale uno di
   questi URL orfani PRIMA che arrivasse la vera risposta nuova (che richiede secondi reali di
   elaborazione AI, ~30-90s, mentre un refresh incidentale di rete puo' arrivare quasi subito dopo
   il click). **Fix**: non prendere la prima risposta nuova, ma continuare a raccoglierle e
   aspettare che la scritta "Processing" sparisca dalla pagina (polling ogni 10s, mai un'attesa
   fissa) prima di prendere l'ULTIMA arrivata fino a quel momento — verificato con un test
   Nano Banana gratuito (contenuto E rapporto d'aspetto entrambi corretti dopo il fix).
7. Un margine di 2s dopo la scomparsa di "Processing" per lasciare atterrare l'ultima risposta di
   rete in transito, poi si ferma l'ascolto e si passa all'URL scelto.
8. Scarica il file via HTTP diretto (non uno screenshot dell'elemento) e verifica la firma binaria
   (PNG/JPEG/WebP/GIF) prima di dichiarare successo — un file sotto i 5000 byte o senza firma
   valida è quasi certamente un placeholder o un'icona presa per errore, non il risultato.

## Limiti onesti

- **Fragile per natura**: è un'automazione su un'interfaccia web non pensata per essere
  scriptata, non un'API. Un cambio di layout del sito può rompere silenziosamente la selezione
  del modello o il rilevamento del risultato. Se `genera_immagine.py` inizia a fallire dopo aver
  funzionato per settimane, il sospetto principale è "il sito è cambiato", non un bug del codice.
- **Un'immagine alla volta**, niente generazione in batch/parallela — usare `litmedia-skill`
  (l'API a pagamento) se serve produrre molte immagini velocemente.
- **La gratuità dei modelli non è garantita nel tempo**: controllare sempre `Credits Required`
  nell'output prima di assumere che una generazione non abbia avuto un costo.
- Non generare contenuti che violino i termini di litmedia.ai; le stesse regole etiche di
  `litmedia-skill` (niente foto false di persone reali, niente riproduzioni delle carte Thoth
  protette da copyright) valgono anche qui.

## File
- `scripts/login_una_tantum.py`: login interattivo una tantum, salva la sessione.
- `scripts/verifica_sessione.py`: controllo headless che la sessione salvata sia ancora valida.
- `scripts/genera_immagine.py`: generazione + download, il comando che un altro skill invoca.
- `sessione_litmedia.json`: sessione salvata (creato al primo login, **non versionare**).
- `venv/`: ambiente virtuale isolato con `browser-use` e `playwright` (creato durante il setup,
  non condiviso con l'ambiente Python globale del sistema).
