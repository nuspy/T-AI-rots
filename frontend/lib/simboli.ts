/* I simboli con cui una lettura condivisa rappresenta l'altra persona, al posto
 * del suo nome: quelli astrologici e alchemici dei tarocchi, non i pittogrammi dei
 * servizi igienici. Venere, Marte e Mercurio per donna, uomo e non binario; una
 * stella a quattro punte per chi ha scelto «altro» o non ha risposto.
 *
 * Sono tracciati su un quadrato di 64 unità e si disegnano a **solo contorno**: lo
 * stesso percorso serve al DOM (`<svg>`) e al canvas (`new Path2D(...)`), così la
 * pagina pubblica e l'immagine da condividere mostrano lo stesso segno. */

import type { Simbolo } from "./api";

export const LATO_SIMBOLO = 64;

/* Un cerchio come percorso SVG: due archi. */
const cerchio = (cx: number, cy: number, r: number) =>
  `M ${cx + r} ${cy} A ${r} ${r} 0 1 0 ${cx - r} ${cy} A ${r} ${r} 0 1 0 ${cx + r} ${cy}`;

export const PERCORSI_SIMBOLI: Record<Simbolo, string> = {
  /* ♀ — un cerchio sopra una croce. */
  venere: `${cerchio(32, 22, 14)} M 32 36 L 32 58 M 22 48 L 42 48`,
  /* ♂ — un cerchio con la freccia verso l'alto a destra. */
  marte: `${cerchio(26, 38, 14)} M 36 28 L 54 10 M 40 10 L 54 10 L 54 24`,
  /* ☿ — un cerchio, la mezzaluna sopra e la croce sotto. */
  mercurio: `${cerchio(32, 34, 11)} M 23 14 A 9 9 0 0 0 41 14 M 32 45 L 32 62 M 24 54 L 40 54`,
  /* ✦ — una stella a quattro punte con i lati incavati. */
  stella: "M 32 4 L 38 26 L 60 32 L 38 38 L 32 60 L 26 38 L 4 32 L 26 26 Z",
};

export const simboloDi = (nome: string | null | undefined): Simbolo =>
  nome === "venere" || nome === "marte" || nome === "mercurio" ? nome : "stella";
