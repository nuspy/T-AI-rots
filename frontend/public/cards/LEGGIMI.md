# Immagini delle carte

Metti qui le immagini definitive delle 78 carte, una per file, con il nome
uguale all'identificativo della carta in `backend/tarot_core/knowledge/deck.json`:

- Arcani maggiori: `maj-00.webp` … `maj-21.webp`
- Minori: `bastoni-01.webp` … `bastoni-10.webp`, `bastoni-cavaliere.webp`,
  `bastoni-regina.webp`, `bastoni-principe.webp`, `bastoni-principessa.webp`
  (lo stesso per `coppe`, `spade`, `dischi`)

Proporzioni consigliate 3:5 (per esempio 600×1000 px). Poi imposta
`NEXT_PUBLIC_CARD_IMAGES=true` e ricompila il frontend. Una carta senza
immagine continua a mostrare il segnaposto disegnato.
