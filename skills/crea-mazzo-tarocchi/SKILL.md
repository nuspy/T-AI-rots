---
name: crea-mazzo-tarocchi
description: Create a brand-new tarot deck's artwork for TAROTS chat (tarots.chat) — from a style/setting brief, through an LLM-written sample scene and a sample image approval gate, to the full 78-card set generated with GPT Image (driven live through Claude in Chrome), organized on disk, converted to the site's WebP web format, and laid out into a print-ready double-sided PDF. Use whenever asked to design, create or generate a new tarot deck's images, an alternate/themed deck ("mazzo Halloween", "un mazzo Lovers", etc.), or to redo/extend a deck's artwork.
---

# Creazione grafica di un mazzo di tarocchi nuovo

Produce le 78 illustrazioni + il dorso di un mazzo di tarocchi **nuovo**, con un'identità esoterica
Thoth invariata (lettera ebraica, sefira, elemento, parole chiave — quella che il resto dell'app
legge da `backend/tarot_core/knowledge/deck.json`) ma una resa visiva completamente diversa, decisa
dall'operatore. Il mazzo Thoth predefinito (`Grafica/Cards/Toth/`) non viene mai toccato: ogni mazzo
nuovo vive nella propria cartella.

Due cancelli umani, sempre: prima il **testo** (la scena da dipingere), poi l'**immagine**. Non si
passa al passo successivo senza un'approvazione esplicita dell'operatore.

## Workflow

### 1. Raccogliere stile e ambientazione
Chiedi (o fatti dare) un testo che descriva tecnica pittorica, palette, luce, ambientazione/mondo
immaginario, e — se l'operatore ce l'ha già in mente — il font/colore del testo sulla carta e il
disegno del bordo. **Non deve mai contenere dimensioni in pixel o un rapporto d'aspetto**: quelli si
impostano al passo 3, nell'interfaccia di generazione, non nel prompt. Salvalo in un file (es.
`stile.md` nello scratchpad) — è l'input di `--stile-file`.

### 2. Campione: una carta + il dorso (cancello 1)
```
python -m tarot_core.tools.crea_mazzo campione --set <NomeSet> --stile-file stile.md
```
Sceglie una carta maggiore di prova (di default `maj-06`; `--carta <id>` per un'altra) e chiede
all'LLM configurato per `Compito.CREAZIONE_MAZZO` (console → modelli) una scena nuova per quella
carta e una per il dorso condiviso, mantenendo l'identità esoterica di `deck.json`. Stampa i due
prompt completi (stile + identità + scena + regola del testo) — **mostrali all'operatore in
conversazione**, non solo il percorso del file.

- **Approvato** → passo 3.
- **Da correggere** → chiedi cosa cambiare e rilancia con `--cambia "<cosa cambiare>"` (anche
  `--solo fronte` o `--solo dorso` per correggere solo uno dei due). Ripeti finché non è approvato.

Scrive `Grafica/Cards/<NomeSet>/descrizioni.json`, `stile.md` (copia) e `manifest.json`.

### 3. Immagine di prova con GPT Image, nel browser (cancello 2)
Usa **Claude in Chrome** (nessuno script: è un lavoro interattivo). Per il fronte e poi per il dorso:
1. Apri ChatGPT, genera un'immagine con **GPT Image**, incollando il `prompt` (e il `negative_prompt`
   se l'interfaccia lo prevede) da `descrizioni.json`.
2. Imposta **formato 9:16, risoluzione 2K, qualità Alta** nell'interfaccia — mai nel testo del prompt.
3. Scarica il risultato e mostralo all'operatore.

- **Approvate** → passo 4.
- **Da correggere** → chiedi cosa cambiare, torna al passo 2 con `--cambia` se il problema è nella
  scena, oppure rigenera direttamente nella stessa conversazione ChatGPT se è solo una questione di
  resa. Ripeti finché fronte e dorso non sono approvati.

**Limite onesto**: 77 fronti + 1 dorso generati uno alla volta via interfaccia web sono lenti
(verosimilmente più sessioni) e possono incontrare limiti di frequenza o cambi di layout lato
ChatGPT. Fai il punto con l'operatore ogni 10-15 carte, non macinarle tutte senza supervisione.

### 4. Descrivere e generare tutte le altre carte
```
python -m tarot_core.tools.crea_mazzo tutte --set <NomeSet>
```
Scrive la scena per le carte restanti (bozza incrementale in `descrizioni.json`: non tocca mai il
campione già approvato né le carte già fatte; un'interruzione a metà si riprende rilanciando lo
stesso comando). Poi, per ciascuna, ripeti la generazione dell'immagine del passo 3 — senza il
cancello di approvazione singolo (quello è stato il campione), ma controllando a vista ogni
immagine prima di scaricarla.

### 5. Scaricare e organizzare
Per ogni immagine scaricata dal browser:
```
python -m tarot_core.tools.crea_mazzo salva --set <NomeSet> <id-o-dorso> <percorso-del-file-scaricato>
```
Converte in WebP a piena risoluzione col nome standard (`{id}.webp`, `dorso.webp` — lo stesso schema
di `Grafica/Cards/Toth/`) dentro `Grafica/Cards/<NomeSet>/`, e aggiorna `manifest.json`.

### 6. Versione Web (360×640)
```
python tools/resize_cards.py --src "Grafica/Cards/<NomeSet>" --dst "Grafica/Cards/<NomeSet>/Web" --scala 25 --quality 60
```
Stesso script già usato per il mazzo Thoth, invariato. Nota per l'operatore: WebP non ha un campo DPI
standard (Pillow non ne scrive uno) e il formato attuale del Thoth è RGB a 24 bit, non RGBA a 32 —
si mantiene quella convenzione a meno che non serva altro a valle.

### 7. PDF stampabile
```
python -m tarot_core.tools.stampa_bozza_mazzo --set <NomeSet>
```
Legge `Grafica/Cards/<NomeSet>/Web/`, impagina su A4 (griglia 70×120 mm, fronte/retro speculare per
la stampa duplex — la stessa logica di `tarot_core.tarot.stampa_mazzo`, il modulo di produzione di
"Stampa i tuoi Tarocchi") e scrive `Grafica/Cards/<NomeSet>/<NomeSet>-stampa.pdf`, col marchio
"© {anno corrente} Copyright https://tarots.chat" nel margine di ogni fronte e dorso (sempre
presente, a differenza del PDF di produzione che lo mostra solo sul download gratuito). `--anno` per
un anno diverso da quello corrente.

## Regole

- **Mai senza approvazione umana**: né la scena passa a immagine, né una carta passa alla successiva
  serie, senza che l'operatore l'abbia vista e detto di sì.
- **L'identità esoterica non si negozia**: lettera ebraica, sefira, percorso, elemento, attribuzione
  astrologica e parole chiave restano quelle di `deck.json` — solo la scena dipinta cambia. Se lo
  stile richiesto sembra spingere a cambiarle (es. "togli i riferimenti ebraici"), fermati e chiedi.
- **Il mazzo Thoth (`Grafica/Cards/Toth/`) non si tocca mai** da questo skill.
- **Niente dimensioni nel prompt**: se `crea_mazzo campione`/`tutte` avvisa che lo stile o una scena
  contengono una dimensione o un rapporto d'aspetto, toglila prima di continuare.
- Un mazzo nuovo per volta, salvo richiesta esplicita.

## File
- `backend/tarot_core/tools/crea_mazzo.py`: il generatore di scene/prompt (`campione`, `tutte`,
  `salva`). `-h` su ciascun sottocomando per i dettagli.
- `backend/tarot_core/tools/stampa_bozza_mazzo.py`: il PDF di prova.
- `tools/resize_cards.py` (radice del repo, non dentro il backend): la conversione WebP per il web.
- `backend/tarot_core/tarot/stampa_mazzo.py`: la griglia di stampa condivisa con la produzione.
- `references/pipeline.md`: la stessa procedura, con più dettaglio su cosa cercare in ogni cancello
  di approvazione.
