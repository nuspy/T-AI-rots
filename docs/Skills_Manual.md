# Manuale degli skill — TAROTS chat

Gli skill di Claude Code che appartengono a questo progetto vivono in `skills/` (versionati con il
codice) e sono anche installati globalmente come **junction** in `~/.claude/skills/`, così sono
disponibili in qualunque sessione Claude Code, non solo quando la cartella di lavoro è questo repo.
Una junction non è una copia: modificare i file dentro `skills/<nome>/` nel repo aggiorna
immediatamente anche la versione globale (e viceversa) — è la stessa cartella vista da due percorsi.

```
C:\Users\atain\.claude\skills\tarots-blog-publisher  →  E:\Projects\T-AI-rots\skills\tarots-blog-publisher
C:\Users\atain\.claude\skills\crea-mazzo-tarocchi     →  E:\Projects\T-AI-rots\skills\crea-mazzo-tarocchi
```

Per ricreare le junction (es. su un'altra macchina, o se cancellate per sbaglio):

```powershell
New-Item -ItemType Junction -Path "$HOME\.claude\skills\tarots-blog-publisher" -Target "E:\Projects\T-AI-rots\skills\tarots-blog-publisher"
New-Item -ItemType Junction -Path "$HOME\.claude\skills\crea-mazzo-tarocchi"   -Target "E:\Projects\T-AI-rots\skills\crea-mazzo-tarocchi"
```

Su Windows **non usare `ln -s` da Git Bash senza privilegi**: senza il permesso di creare symlink,
MSYS copia silenziosamente la cartella invece di collegarla, e la copia smette di aggiornarsi da sola.
Una `New-Item -ItemType Junction` da PowerShell non richiede quel privilegio ed è il modo con cui sono
collegati anche gli altri skill esterni al repo (`book-forge`, `wiki-import`).

## Indice

| Skill | A cosa serve | Invocazione |
|---|---|---|
| [`tarots-blog-publisher`](#tarots-blog-publisher) | Scrivere e pubblicare un articolo del blog di tarots.chat, con SEO e cover | descrivi la richiesta ("pubblica un articolo su...") o `/tarots-blog-publisher` |
| [`crea-mazzo-tarocchi`](#crea-mazzo-tarocchi) | Creare la grafica di un mazzo di tarocchi nuovo (78 carte + dorso), fino al PDF stampabile | descrivi la richiesta ("crea un mazzo con questo stile...") o `/crea-mazzo-tarocchi` |

---

## `tarots-blog-publisher`

**Cosa fa**: ricerca un argomento esoterico/tarocchi attuale (o quello indicato dall'operatore), scrive
un articolo in inglese ottimizzato SEO, genera la cover con LitMedia e pubblica tutto sul blog di
TAROTS chat tramite la REST API del sito, compilando ogni campo SEO (parola chiave, meta title/
description, slug, tag, FAQ, alt text).

**Quando si attiva**: quando si chiede di scrivere, pubblicare, programmare un articolo per TAROTS
chat/tarots.chat, o di tenere il blog alimentato con contenuti tempestivi su tarocchi, Thoth, Golden
Dawn, astrologia o cartomanzia.

### Setup (una volta per chiave, non a ogni esecuzione)

1. Un editor crea una chiave in console: **Blog → Keys**. Permessi: `blog:write` (solo bozze) oppure
   `blog:write` + `blog:publish` (può anche pubblicare).
2. Impostare per l'esecuzione corrente:
   ```
   TAROTS_API_URL=https://tarots.chat/api
   TAROTS_API_KEY=tk_live_…
   ```
   Al primo uso vengono salvate in `~/.tarots-blog/credentials.json` (fuori da qualunque repo): le
   esecuzioni successive non hanno più bisogno delle due variabili.
3. Verifica: `python scripts/tarots_blog.py guide` (percorso relativo alla cartella dello skill)
   stampa cosa può fare la chiave e le soglie SEO.

Se compare una `TAROTS_API_KEY` diversa da quella già salvata, nessun comando la sostituisce da solo:
bisogna scegliere esplicitamente fra `key show`, `key save` o togliere la variabile d'ambiente.

### Comandi (`scripts/tarots_blog.py`)

| Comando | Parametri | Cosa fa |
|---|---|---|
| `guide` | — | Stampa cosa accetta il blog e le soglie SEO. |
| `sections` | — | Elenca le sezioni in cui un articolo può andare. |
| `tags` | — | Elenca i tag già in uso (da riusare, non duplicare). |
| `catalog` | `--grep TESTO` | Elenca carte e stese con le loro scorciatoie di link (`[[card:...]]`, `[[spread:...]]`); `--grep` filtra per slug/nome. |
| `mine` | `--status {bozza,pubblicato,archiviato}` `--page N` `--per-page N` | Articoli già creati con questa chiave (per non ripetere argomento/parola chiave). |
| `check` | `article` (file JSON) `--min-score N` (default 85) | Punteggio SEO 0-100 e lista `FIX`/`WARN`, senza salvare nulla. |
| `upload` | `image` (PNG/JPEG/WebP, max 8 MB) | Carica un'immagine (cover o inline) e restituisce id/URL riutilizzabile nel corpo Markdown. |
| `post` | `article` `--cover FILE` `--min-score N` `--save-anyway` `--dry-run` | Ricontrolla il punteggio, carica la cover, crea l'articolo, stampa l'URL. Rifiuta di salvare sotto la soglia a meno di `--save-anyway`. |
| `update` | `id` `patch` (file JSON con solo i campi da cambiare) | Modifica un articolo creato da questa stessa chiave. |
| `delete-draft` | `id` | Cancella una bozza creata da questa stessa chiave. |
| `key` | `show` \| `save` \| `clear` | Gestisce la chiave salvata localmente (mai stampata per intero, solo il prefisso). |

Flag globale: `--json` su qualunque comando stampa il JSON grezzo invece del riassunto leggibile.

### Flusso di lavoro

1. **Cosa esiste già**: `sections`, `tags`, `mine`, `catalog --grep <termine>` — non ripetere un
   argomento/parola chiave già usati, riusare i tag esistenti.
2. **Scegliere l'argomento**: quello indicato dall'operatore, oppure qualcosa di tempestivo
   (equinozio, plenilunio, un trend di ricerca) da `references/keywords.md`. Ogni data/fatto
   astronomico va verificato con una fonte aperta davvero, altrimenti si scarta.
3. **Struttura per l'intento di ricerca**: prime 100 parole che rispondono subito con la parola
   chiave; 3-6 sezioni `##`; 2-5 link interni, almeno una fonte esterna affidabile, 3-5 FAQ.
4. **Scrivere l'articolo**: inglese, 800+ parole (minimo assoluto 300), Markdown senza `# H1` (il
   titolo della pagina è già l'H1). Link interni con `[[card:slug]]`/`[[spread:slug]]`/
   `[[post:slug]]`; immagini inline con `upload` + `![alt](url)`; video con
   `[[video:youtube:ID]]`. Tono riflessivo, mai previsioni categoriche su salute/soldi/amore.
5. **Campi SEO**: `title`, `seo_title` (30-60 caratteri), `seo_description` (120-160), `focus_keyword`,
   `secondary_keywords`, `slug`, `tags`, `section`, `faq`, `cover_alt`, `language`. Dettaglio di ogni
   regola in `references/seo-checklist.md`. L'articolo va in un file JSON (vedi
   `assets/example-article.json`), il corpo Markdown in un file a parte referenziato con
   `"body_file"`.
6. **Cover**: 16:9, niente testo nell'immagine, generata con LitMedia seguendo
   `references/image-generation.md` (stima costo e consenso dell'operatore prima di generare).
7. **Controllo**: `check article.json`, correggere finché il punteggio è ≥ 85 senza `FIX` (o dopo 4
   round).
8. **Pubblicazione**: `post article.json --cover cover.png`. `"status": "draft"` di default;
   `"published"` solo se l'operatore lo chiede esplicitamente. Su errore di rete, controllare `mine`
   prima di rilanciare (l'articolo potrebbe esistere già).
9. **Report finale**: titolo, parola chiave, punteggio, stato, URL, eventuali `note:` per un editor.

### Regole rigide

- La chiave non finisce mai in un file di progetto, in un articolo o in un messaggio: solo variabile
  d'ambiente o cache locale fuori dal repo; in output appare solo il prefisso a 12 caratteri.
- Niente TLS disabilitato, niente redirect seguiti con la chiave.
- Solo contenuto originale e verificato: niente fatti o citazioni inventate.
- Un articolo per esecuzione salvo richiesta esplicita; `429` vuol dire fermarsi, non ritentare.
- Mai modificare/cancellare un articolo non creato da questa stessa chiave (l'API lo rifiuta comunque).

### File dello skill

- `scripts/tarots_blog.py` — il CLI (`-h` su ogni comando).
- `references/api.md` — endpoint REST, campi, errori.
- `references/keywords.md` — cluster di parole chiave, concorrenza, calendario editoriale.
- `references/seo-checklist.md` — ogni controllo del punteggio SEO.
- `references/image-generation.md` — comandi LitMedia e ricette di prompt per la cover.
- `assets/example-article.json` + `assets/example-article.md` — la forma di un articolo (non un
  modello da copiare: un articolo vero è 800+ parole e originale).

---

## `crea-mazzo-tarocchi`

**Cosa fa**: produce la grafica di un mazzo di tarocchi **nuovo** per TAROTS chat — 78 carte + il
dorso condiviso — con la stessa identità esoterica Thoth (lettera ebraica, sefira, elemento, parole
chiave, presa da `backend/tarot_core/knowledge/deck.json`) ma una resa visiva completamente diversa,
scelta dall'operatore. Copre l'intera pipeline: dal brief di stile, alla scena scritta da un LLM, alla
generazione dell'immagine con GPT Image guidata dal vivo nel browser (Claude in Chrome), fino
all'organizzazione dei file, alla versione Web e al PDF stampabile fronte/retro.

**Quando si attiva**: quando si chiede di progettare, creare o generare la grafica di un mazzo di
tarocchi nuovo o a tema ("un mazzo Halloween", "un mazzo Lovers"...), o di rifare/estendere la
grafica di un mazzo esistente.

**Non tocca mai** il mazzo Thoth predefinito (`Grafica/Cards/Toth/`): ogni mazzo nuovo vive nella
propria cartella `Grafica/Cards/<NomeSet>/`.

### Due cancelli umani, sempre

Nessun passo automatico salta l'approvazione dell'operatore:
1. **Cancello 1 — la scena** (testo): una carta di prova + il dorso, prima di scrivere le altre 77.
2. **Cancello 2 — l'immagine**: la prima immagine generata (fronte e dorso), prima di generare tutte
   le altre.

### Passo 1 — Raccogliere stile e ambientazione (nessun comando)

Un testo libero con tecnica pittorica, palette, luce, ambientazione, e — se già deciso — font/colore
del testo e disegno del bordo. **Mai dimensioni in pixel o rapporto d'aspetto**: si impostano
nell'interfaccia di generazione (passo 3), non nel prompt. Va salvato in un file (es. `stile.md`).

### Passo 2 — Campione (cancello 1)

```
python -m tarot_core.tools.crea_mazzo campione --set <NomeSet> --stile-file stile.md [opzioni]
```

| Parametro | Obbligatorio | Descrizione |
|---|---|---|
| `--set NOME` | sì | Nome del mazzo = nome della sua cartella in `Grafica/Cards/`. |
| `--stile-file PERCORSO` | sì | File di testo con lo stile/ambientazione (passo 1). |
| `--carta ID` | no (default `maj-06`) | Id della carta maggiore di prova (es. `maj-00`…`maj-21`). |
| `--cambia "TESTO"` | no | Cosa correggere rispetto al tentativo precedente: rigenera la scena tenendo lo stesso stile. |
| `--solo {fronte,dorso,entrambi}` | no (default `entrambi`) | Limita la generazione a una sola delle due parti. |

Chiede all'LLM assegnato a `Compito.CREAZIONE_MAZZO` (console → modelli) una scena nuova per la carta
scelta e una per il dorso, stampa i due prompt completi e scrive
`Grafica/Cards/<NomeSet>/descrizioni.json` + `stile.md` (copia) + `manifest.json`. Si ripete con
`--cambia` finché l'operatore non approva.

### Passo 3 — Immagine di prova (cancello 2, nessun comando: Claude in Chrome)

Apri ChatGPT, genera con **GPT Image** incollando il `prompt` (ed eventualmente il
`negative_prompt`) da `descrizioni.json`; imposta **9:16 / 2K / qualità Alta** nell'interfaccia, mai
nel testo; scarica e mostra il risultato. Si ripete finché fronte e dorso non sono approvati (vedi
`references/pipeline.md` nello skill per cosa controllare a occhio).

### Passo 4 — Tutte le altre carte

```
python -m tarot_core.tools.crea_mazzo tutte --set <NomeSet> [--solo-carte ID,ID,...]
```

| Parametro | Descrizione |
|---|---|
| `--set NOME` | Obbligatorio, come sopra. |
| `--solo-carte ID,ID,...` | Rigenera proprio queste carte anche se già presenti in `descrizioni.json`. Senza questo parametro, salta automaticamente quelle già fatte (incluso il campione approvato) e prosegue solo con le mancanti — **non riparte mai da zero**, anche se rilanciato più volte in sessioni diverse. |

Poi si ripete la generazione dell'immagine del passo 3 per ciascuna, senza il cancello di
approvazione singolo (quello è il campione), ma controllando ogni immagine prima di scaricarla.

### Passo 5 — Salvare l'immagine scaricata

```
python -m tarot_core.tools.crea_mazzo salva --set <NomeSet> <ID|dorso> <percorso-file-scaricato>
```

Converte il file scaricato (tipicamente PNG) in WebP quasi senza perdita a piena risoluzione,
salvandolo come `Grafica/Cards/<NomeSet>/{id}.webp` o `dorso.webp` (stesso standard di
`Grafica/Cards/Toth/`), e aggiorna `manifest.json`.

### Passo 6 — Versione Web (360×640)

```
python tools/resize_cards.py --src "Grafica/Cards/<NomeSet>" --dst "Grafica/Cards/<NomeSet>/Web" [--scala 25] [--quality 60] [--only NOME NOME ...]
```

Script generico (non specifico a questo skill, riusato invariato): `--scala` è la percentuale di ogni
lato (25% di 1440×2560 dà 360×640), `--quality` la qualità WebP 0-100, `--only` limita ai file
indicati (senza estensione). Nota: WebP non ha un campo DPI standard e il mazzo Thoth attuale è RGB a
24 bit (non RGBA a 32) — si mantiene quella convenzione salvo esigenze diverse indicate a valle.

### Passo 7 — PDF stampabile

```
python -m tarot_core.tools.stampa_bozza_mazzo --set <NomeSet> [--anno ANNO]
```

| Parametro | Descrizione |
|---|---|
| `--set NOME` | Obbligatorio. |
| `--anno N` | Anno nel marchio di copyright (default: l'anno corrente). |

Legge `Grafica/Cards/<NomeSet>/Web/`, impagina su A4 (griglia 70×120 mm, pagine alternate
fronte/dorso con le colonne del dorso specchiate per l'allineamento nella stampa fronte/retro — la
stessa logica di `backend/tarot_core/tarot/stampa_mazzo.py`, il modulo di produzione di "Stampa i
tuoi Tarocchi"), e scrive `Grafica/Cards/<NomeSet>/<NomeSet>-stampa.pdf` col marchio
"© {anno} Copyright https://tarots.chat" **sempre presente** su ogni fronte e dorso (a differenza del
PDF di produzione, che lo mostra solo sul download gratuito). Una carta senza immagine ancora pronta
riceve un segnaposto grigio invece di far fallire l'intera stampa.

### Regole rigide

- Mai passare al passo successivo senza che l'operatore abbia visto e approvato quello attuale.
- L'identità esoterica (lettera ebraica, sefira, percorso, elemento, astrologia, parole chiave) non
  si tocca mai: solo la scena dipinta cambia. Una richiesta che spinge a cambiarla richiede una
  pausa e una domanda esplicita, non un'esecuzione silenziosa.
- Il mazzo Thoth (`Grafica/Cards/Toth/`) non si modifica mai da questo skill.
- 77 fronti + 1 dorso generati uno alla volta via interfaccia web sono lenti (verosimilmente più
  sessioni): fare il punto con l'operatore ogni 10-15 carte, non macinarle tutte senza supervisione.

### File dello skill e strumenti coinvolti

- `backend/tarot_core/tools/crea_mazzo.py` — `campione`, `tutte`, `salva` (`-h` per i dettagli).
- `backend/tarot_core/tools/stampa_bozza_mazzo.py` — il PDF di prova.
- `tools/resize_cards.py` (radice del repo) — la conversione WebP, condivisa con il mazzo Thoth.
- `backend/tarot_core/tarot/stampa_mazzo.py` — la griglia di stampa, condivisa con la produzione
  ("Stampa i tuoi Tarocchi", Fase B4).
- `backend/tarot_core/llm/compiti.py` — `Compito.CREAZIONE_MAZZO`: qui si assegna quale modello LLM
  scrive le scene (console → modelli).
- `references/pipeline.md` (nello skill) — dettaglio di cosa controllare a ogni cancello di
  approvazione e come riprendere una corsa interrotta leggendo `manifest.json`.

---

## Aggiungere un nuovo skill del progetto a questo manuale

1. Crearlo in `skills/<nome>/` con `SKILL.md` (frontmatter `name`/`description`) come gli altri due.
2. Collegarlo globalmente: `New-Item -ItemType Junction -Path "$HOME\.claude\skills\<nome>" -Target "E:\Projects\T-AI-rots\skills\<nome>"`.
3. Aggiungere una voce nell'indice e una sezione qui, con la stessa struttura: cosa fa, quando si
   attiva, comandi/parametri in tabella, flusso di lavoro, regole rigide, file dello skill.
