import { useId } from "react";
import {
  COLORI, CENTRO_STELLA, CONTORNO_CARTA, CORNICE, NOME_MARCHIO, PAROLA, PERCORSO_STELLA, ROMBI, TELA, VOCE,
} from "@/lib/marchio";
import stili from "./marchio.module.css";

/* Il marchio di TAROTS chat.
 *
 * `Emblema` è il segno: una carta con la coda di un fumetto e, dentro, la stella a sette punte di Babalon.
 * `Marchio` lo affianca al nome: TAROTS inciso in oro, *chat* sussurrato in corsivo viola — le due voci del sito,
 * l'iscrizione e l'oracolo.
 *
 * Tre disposizioni: `riga` (la testata), `blocco` (la soglia: il segno grande a sinistra, TAROTS e *chat* a destra,
 * allineati a sinistra come il resto della pagina) e `verticale` (tutto centrato, per i luoghi che centrano).
 *
 * Due misure. Piccolo (un `semplice`, sotto i ~24 px: favicon, testata compatta) il segno perde cornice e rombi e
 * ingrossa il tratto, perché i filetti a quella scala si impastano. Grande (`animato`, sulla soglia) la carta e la
 * stella si disegnano una volta sola; con `prefers-reduced-motion` compaiono già finite.
 *
 * Nessun JavaScript: si scrive anche dal server. Gli identificativi dei gradienti vengono da `useId`, perché lo
 * stesso segno può comparire due volte nella stessa pagina (testata e soglia). */

export function Emblema({
  altezza = 34, semplice = false, animato = false, titolo,
}: {
  altezza?: number;
  semplice?: boolean;
  animato?: boolean;
  /** Se c'è, il segno è un'immagine con questo nome; altrimenti è decorativo. */
  titolo?: string;
}) {
  const id = useId().replace(/:/g, "");
  const oro = `oro${id}`;
  const notte = `notte${id}`;
  const alone = `alone${id}`;
  const larghezza = Math.round((altezza * TELA.larghezza) / TELA.altezza);
  const spessore = semplice ? 3.2 : 1.9;
  return (
    <svg
      className={`${stili.emblema} ${animato ? stili.animato : ""}`}
      viewBox={`0 0 ${TELA.larghezza} ${TELA.altezza}`}
      width={larghezza}
      height={altezza}
      role={titolo ? "img" : undefined}
      aria-label={titolo}
      aria-hidden={titolo ? undefined : true}
      focusable="false"
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
        <radialGradient id={alone} cx="0.5" cy="0.46" r="0.52">
          <stop offset="0" stopColor={COLORI.viola} stopOpacity="0.42" />
          <stop offset="1" stopColor={COLORI.viola} stopOpacity="0" />
        </radialGradient>
      </defs>
      <path d={CONTORNO_CARTA} fill={`url(#${notte})`} />
      <path d={CONTORNO_CARTA} fill={`url(#${alone})`} />
      <path
        className={stili.contorno}
        d={CONTORNO_CARTA}
        fill="none"
        stroke={`url(#${oro})`}
        strokeWidth={spessore}
        strokeLinejoin="round"
        pathLength={1}
      />
      {!semplice && (
        <>
          <rect
            className={stili.cornice}
            x={CORNICE.x} y={CORNICE.y} width={CORNICE.larghezza} height={CORNICE.altezza} rx={CORNICE.raggio}
            fill="none" stroke={`url(#${oro})`} strokeWidth="0.6" opacity="0.5"
          />
          {ROMBI.map((d) => (
            <path key={d} className={stili.rombo} d={d} fill={`url(#${oro})`} />
          ))}
        </>
      )}
      <g className={stili.stella}>
        <path
          className={stili.tracciato}
          d={PERCORSO_STELLA}
          fill="none"
          stroke={`url(#${oro})`}
          strokeWidth={semplice ? 2.6 : 1.5}
          strokeLinejoin="round"
          pathLength={1}
        />
        <circle className={stili.centro} cx={CENTRO_STELLA.x} cy={CENTRO_STELLA.y} r={semplice ? 2.6 : 2.1} fill={`url(#${oro})`} />
      </g>
    </svg>
  );
}

/** Il nome, senza segno: due voci, una accanto all'altra. */
export function Nome({ className }: { className?: string }) {
  return (
    <span className={`${stili.nome} ${className ?? ""}`}>
      <span className={stili.parola}>{PAROLA}</span>
      <span className={stili.voce}>{VOCE}</span>
    </span>
  );
}

/**
 * Il marchio completo. `riga` è la testata (segno e nome sulla stessa linea); `verticale` è la soglia: il segno
 * grande, poi TAROTS, poi *chat* fra due filetti.
 */
export function Marchio({
  variante = "riga", altezza, animato = false, titolo = NOME_MARCHIO,
}: {
  variante?: "riga" | "blocco" | "verticale";
  altezza?: number;
  animato?: boolean;
  titolo?: string;
}) {
  if (variante === "blocco") {
    return (
      <span className={`${stili.blocco} ${animato ? stili.animato : ""}`} role="img" aria-label={titolo}>
        <Emblema altezza={altezza ?? 150} animato={animato} />
        <span className={stili.bloccoTesto} aria-hidden="true">
          <span className={stili.parolaGrande}>{PAROLA}</span>
          <span className={stili.voceGrande}>{VOCE}</span>
        </span>
      </span>
    );
  }
  if (variante === "verticale") {
    return (
      <span className={`${stili.verticale} ${animato ? stili.animato : ""}`} role="img" aria-label={titolo}>
        <Emblema altezza={altezza ?? 132} animato={animato} />
        <span className={stili.parolaGrande} aria-hidden="true">{PAROLA}</span>
        <span className={stili.voceGrande} aria-hidden="true">{VOCE}</span>
      </span>
    );
  }
  return (
    <span className={stili.riga} role="img" aria-label={titolo}>
      <Emblema altezza={altezza ?? 34} semplice={(altezza ?? 34) < 26} />
      <Nome />
    </span>
  );
}
