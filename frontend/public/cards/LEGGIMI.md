# Immagini delle carte

I file `{id}.svg` sono segnaposto col solo valore della carta, generati da
`npm run carte` (`scripts/genera-carte.mjs`) a partire da
`backend/tarot_core/knowledge/deck.json`. Si rigenerano, non si modificano a mano.

Per le immagini definitive usa lo stesso nome con un'altra estensione:

- Arcani maggiori: `maj-00.webp` … `maj-21.webp`
- Minori: `bastoni-01.webp` … `bastoni-10.webp`, `bastoni-cavaliere.webp`,
  `bastoni-regina.webp`, `bastoni-principe.webp`, `bastoni-principessa.webp`
  (lo stesso per `coppe`, `spade`, `dischi`)

Proporzioni 3:5 (per esempio 600×1000 px). Poi imposta
`NEXT_PUBLIC_CARD_EXT=webp` e ricompila il frontend.

## Generare le immagini

`prompts.json` contiene, per ciascuna delle 78 carte, il prompt completo e
autonomo per un generatore di immagini (stile, simboli spiegati, testo e font
Cinzel) e il nome del file da produrre (`file`). Si rigenera con
`python -m tarot_core.tools.prompt_immagini` dal backend.
