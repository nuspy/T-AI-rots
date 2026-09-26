import { useId } from "react";
import { COLORI, CENTRO_STELLA, CONTORNO_CARTA, PERCORSO_STELLA, TELA } from "@/lib/marchio";

/* Il segno di TAROTS chat, per la console: la carta col fumetto e la stella a sette punte.
 * Versione semplice (tratto pieno, niente cornice): qui sta a 26 px, e i filetti si impasterebbero.
 * La geometria è quella del sito (`lib/marchio.ts`, copiato qui perché la console è un'app a parte). */
export function Emblema({ altezza = 26 }: { altezza?: number }) {
  const id = useId().replace(/:/g, "");
  const oro = `oro${id}`;
  const notte = `notte${id}`;
  return (
    <svg
      viewBox={`0 0 ${TELA.larghezza} ${TELA.altezza}`}
      width={Math.round((altezza * TELA.larghezza) / TELA.altezza)}
      height={altezza}
      aria-hidden="true"
      focusable="false"
      style={{ display: "block", flex: "none" }}
    >
      <defs>
        <linearGradient id={oro} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor={COLORI.oroChiaro} />
          <stop offset="0.5" stopColor={COLORI.oro} />
          <stop offset="1" stopColor={COLORI.oroScuro} />
        </linearGradient>
        <linearGradient id={notte} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={COLORI.notteAlta} />
          <stop offset="1" stopColor={COLORI.notte} />
        </linearGradient>
      </defs>
      <path d={CONTORNO_CARTA} fill={`url(#${notte})`} stroke={`url(#${oro})`} strokeWidth="3.2" strokeLinejoin="round" />
      <path d={PERCORSO_STELLA} fill="none" stroke={`url(#${oro})`} strokeWidth="2.6" strokeLinejoin="round" />
      <circle cx={CENTRO_STELLA.x} cy={CENTRO_STELLA.y} r="2.6" fill={`url(#${oro})`} />
    </svg>
  );
}
