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

### 3. Immagine di prova con GPT Image (cancello 2)

**Predefinito: `browser-image-gen`** (skill condivisa, GPT Image via litmedia.ai — gratis per questo
modello al momento della scrittura, 2026-09-29; verificare comunque `Credits Required` nell'output,
il sito può cambiarlo senza preavviso). Richiede il login una tantum di quella skill già fatto una
volta per l'account. Per il fronte e poi per il dorso:
```
python -m tarot_core.tools.crea_mazzo genera --set <NomeSet> <id-o-dorso>
```
Legge il `prompt` già scritto in `descrizioni.json` (nessuna necessità di incollarlo a mano), genera
a 9:16/2K/Alta qualità di default, e scrive il file grezzo in
`Grafica/Cards/<NomeSet>/_staging/<id-o-dorso>.png` — **non lo salva ancora nel mazzo finale**:
guarda l'immagine (leggi il file) e mostrala all'operatore prima di continuare.

**Niente prompt negativo**: `descrizioni.json` contiene solo `prompt` (positivo). litmedia.ai (dietro
`browser-image-gen`) espone un unico campo di testo, senza un secondo campo "negative prompt" —
concatenare un blocco "Avoid: ..." dentro lo stesso prompt non è un vero negative prompt e, bug
osservato (2026-09-29), può far scattare il filtro di contenuti sensibili del sito e far fallire la
generazione in silenzio (`{"code":1005,"msg":"Create failed, contains sensitive prompt"}`) anche per
parole elencate solo per dire di evitarle (es. "nudity" dentro un "Avoid: nudity, ..."). Le esclusioni
(niente foto reali, niente testo/watermark indesiderato, niente anatomia deforme, ecc.) vanno invece
scritte nel prompt positivo come istruzioni dirette allo stile e alla scena.

**Alternativa manuale, se il sito è cambiato o il browser automatizzato non funziona**: usa
**Claude in Chrome** (nessuno script, lavoro interattivo) — apri ChatGPT, genera con **GPT Image**
incollando il `prompt` da `descrizioni.json`, imposta **formato 9:16, risoluzione 2K, qualità Alta**
nell'interfaccia (mai nel testo del prompt), scarica il risultato.

- **Approvate** → passo 4.
- **Da correggere** → chiedi cosa cambiare, torna al passo 2 con `--cambia` se il problema è nella
  scena, oppure rilancia `genera` (o rigenera nella stessa conversazione ChatGPT, via manuale) se è
  solo una questione di resa. Ripeti finché fronte e dorso non sono approvati.

**Limite onesto**: 77 fronti + 1 dorso restano 78 generazioni singole (una alla volta, ~60-90s
ciascuna con `browser-image-gen`) — più veloce e senza supervisione continua rispetto alla via
manuale, ma pur sempre non istantaneo né in batch. Fai il punto con l'operatore ogni 10-15 carte,
non macinarle tutte senza mostrare almeno qualche risultato lungo la strada.

### 4. Descrivere e generare tutte le altre carte
```
python -m tarot_core.tools.crea_mazzo tutte --set <NomeSet>
```
Scrive la scena per le carte restanti (bozza incrementale in `descrizioni.json`: non tocca mai il
campione già approvato né le carte già fatte; un'interruzione a metà si riprende rilanciando lo
stesso comando). Poi, per ciascuna, ripeti la generazione del passo 3 (`crea_mazzo genera --set
<NomeSet> <id>`, o la via manuale) — senza il cancello di approvazione singolo (quello è stato il
campione), ma controllando comunque il file generato prima di lanciare `salva` (passo 5).

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
  `genera`, `salva`). `-h` su ciascun sottocomando per i dettagli. `genera` chiama la skill globale
  `browser-image-gen` (percorso di default `~/.claude/skills/browser-image-gen`, sovrascrivibile con
  `BROWSER_IMAGE_GEN_DIR`) — richiede il suo login una tantum già fatto, vedi il suo `SKILL.md`.
- `backend/tarot_core/tools/stampa_bozza_mazzo.py`: il PDF di prova.
- `tools/resize_cards.py` (radice del repo, non dentro il backend): la conversione WebP per il web.
- `backend/tarot_core/tarot/stampa_mazzo.py`: la griglia di stampa condivisa con la produzione.
- `references/pipeline.md`: la stessa procedura, con più dettaglio su cosa cercare in ogni cancello
  di approvazione.
