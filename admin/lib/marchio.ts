/* Il nome e il segno del prodotto, in un posto solo.
 *
 * Il prodotto si chiamava con il suo nome tecnico, T·AI·rots; oggi è **TAROTS chat**: TAROTS, la parola
 * incisa, e *chat*, la voce che risponde. I due pezzi hanno tipografie diverse (Cinzel maiuscolo, Cormorant
 * corsivo) e in un testo semplice — titoli di pagina, metadati, email — si scrivono di seguito: «TAROTS chat».
 *
 * Il segno è una carta dei tarocchi con la coda di un fumetto di conversazione; dentro, la stella a sette punte
 * di Babalon, la stessa che nel Thoth sta sopra la carta della Stella. La geometria sta qui perché la usano
 * il componente (`componenti/marchio.tsx`), l'immagine di condivisione disegnata sul canvas e, con gli stessi
 * numeri, lo script che scrive favicon e immagine di anteprima (`tools/genera_marchio.py`). */

export const PAROLA = "TAROTS";
export const VOCE = "chat";
export const NOME_MARCHIO = `${PAROLA} ${VOCE}`;

/** Dove sta il segno: una tela di 68 × 105 unità. */
export const TELA = { larghezza: 68, altezza: 105 } as const;

/** Il contorno della carta con la coda del fumetto in basso a destra. */
export const CONTORNO_CARTA =
  "M13 4H55A7 7 0 0 1 62 11V85A7 7 0 0 1 55 92H46V101L36 92H13A7 7 0 0 1 6 85V11A7 7 0 0 1 13 4Z";

/** La cornice interna: quella che ogni carta ha sul dorso. */
export const CORNICE = { x: 11.5, y: 9.5, larghezza: 45, altezza: 77, raggio: 3.5 } as const;

export const CENTRO_STELLA = { x: 34, y: 48 } as const;
export const RAGGIO_STELLA = 20;

const arrotonda = (n: number) => Math.round(n * 100) / 100;

/** Le sette punte, a partire da quella in alto, in senso orario. */
export const PUNTE_STELLA: ReadonlyArray<readonly [number, number]> = Array.from({ length: 7 }, (_, k) => {
  const angolo = -Math.PI / 2 + (k * 2 * Math.PI) / 7;
  return [
    arrotonda(CENTRO_STELLA.x + RAGGIO_STELLA * Math.cos(angolo)),
    arrotonda(CENTRO_STELLA.y + RAGGIO_STELLA * Math.sin(angolo)),
  ] as const;
});

/** Il percorso della stella {7/2}: si salta una punta su due, e si chiude dopo sette tratti. */
export const PERCORSO_STELLA =
  [0, 2, 4, 6, 1, 3, 5]
    .map((k, i) => `${i === 0 ? "M" : "L"}${PUNTE_STELLA[k][0]} ${PUNTE_STELLA[k][1]}`)
    .join("") + "Z";

/** Due piccoli rombi, uno sopra e uno sotto la stella, come sul dorso di una carta. */
export const ROMBI = [
  "M34 13.2l1.7 2.3-1.7 2.3-1.7-2.3z",
  "M34 78.2l1.7 2.3-1.7 2.3-1.7-2.3z",
] as const;

/** Colori del segno (gli stessi variabili del tema, scritti in chiaro per i contesti senza CSS). */
export const COLORI = {
  oroChiaro: "#f6e4a8",
  oro: "#d8b45a",
  oroScuro: "#8f6c24",
  notteAlta: "#241a48",
  notte: "#0b0818",
  viola: "#b9a4ff",
} as const;
