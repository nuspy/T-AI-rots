# Immagini delle carte

Le carte sono WebP con **proporzioni 9:16** (360×640 px bastano):

- Arcani maggiori: `maj-00.webp` … `maj-21.webp`
- Minori: `bastoni-01.webp` … `bastoni-10.webp`, `bastoni-cavaliere.webp`,
  `bastoni-regina.webp`, `bastoni-principe.webp`, `bastoni-principessa.webp`
  (lo stesso per `coppe`, `spade`, `dischi`)
- Il dorso: `dorso.webp`. Se manca, il frontend disegna un dorso di ripiego.

Gli originali (1440×2560) stanno in `Cards/` nella radice del repository;
`python tools/resize_cards.py` li rimpicciolisce al 25% in `Cards/web/`, e da lì
si copiano qui.

`npm run carte` (`scripts/genera-carte.mjs`) scrive invece dei segnaposto `.svg`
col solo valore della carta: servono solo con `NEXT_PUBLIC_CARD_EXT=svg`.

## Generare le immagini

`prompts.json` contiene, per ciascuna delle 78 carte, il prompt completo e
autonomo per un generatore di immagini (stile, simboli spiegati, testo e font
Cinzel) e il nome del file da produrre (`file`). Si rigenera con
`python -m tarot_core.tools.prompt_immagini` dal backend.

`prompt-dorso.json` ha lo stesso formato e contiene il prompt del dorso.
