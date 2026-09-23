"use client";

/* Una carta: dorso, faccia e il giro fra i due.
 *
 * **La faccia è un'immagine** in `public/cards/{id}.{estensione}`. Finché
 * non arrivano quelle definitive sono segnaposto col solo valore della carta,
 * generati da `scripts/genera-carte.mjs`. Se un file manca resta il nome
 * della carta in testo: mai una carta vuota sul tavolo.
 *
 * **Il rovescio è la faccia girata di 180°**, come sul tavolo vero: la
 * rotazione sta sulla faccia, non sulla carta, così il giro 3D resta lo
 * stesso per tutte.
 */

import { useState } from "react";
import { motion } from "framer-motion";
import type { Carta as TipoCarta } from "@/lib/api";
import stili from "./carta.module.css";

/* `svg` per i segnaposto generati da `npm run carte`; `webp` (o altro) quando
 * arrivano le immagini definitive con lo stesso nome. */
const ESTENSIONE = process.env.NEXT_PUBLIC_CARD_EXT ?? "svg";

export function Dorso() {
  /* L'esagramma unicursale e la rosa a cinque petali: i due emblemi della
   * tradizione thelemica, in oro su notte. */
  const punti = [0, 1, 2, 3, 4, 5].map((i) => {
    const a = (Math.PI / 3) * i - Math.PI / 2;
    return [150 + Math.cos(a) * 78, 250 + Math.sin(a) * 78];
  });
  const [p0, p1, p2, p3, p4, p5] = punti;
  const unicursale = `M${p0} L${p2} L${p5} L${p1} L${p4} L${p3} L${p0}`.replaceAll(",", " ");
  return (
    <svg viewBox="0 0 300 500" className={stili.svg} aria-hidden="true">
      <defs>
        <radialGradient id="dorso-g" cx="0.5" cy="0.5" r="0.7">
          <stop offset="0" stopColor="#2c1f5c" />
          <stop offset="1" stopColor="#0a0717" />
        </radialGradient>
        <pattern id="dorso-p" width="24" height="24" patternUnits="userSpaceOnUse">
          <circle cx="12" cy="12" r="1.1" fill="#d8b45a" fillOpacity="0.35" />
        </pattern>
      </defs>
      <rect width="300" height="500" rx="18" fill="url(#dorso-g)" />
      <rect width="300" height="500" rx="18" fill="url(#dorso-p)" />
      <rect x="12" y="12" width="276" height="476" rx="12" fill="none" stroke="#d8b45a" strokeWidth="2" />
      <rect x="22" y="22" width="256" height="456" rx="8" fill="none" stroke="#d8b45a" strokeOpacity="0.35" />
      <circle cx="150" cy="250" r="104" fill="none" stroke="#d8b45a" strokeOpacity="0.55" />
      <circle cx="150" cy="250" r="96" fill="none" stroke="#d8b45a" strokeOpacity="0.25" />
      <path d={unicursale} fill="none" stroke="#f1d68e" strokeWidth="2.4" strokeLinejoin="round" />
      {[0, 1, 2, 3, 4].map((i) => (
        <ellipse key={i} cx="150" cy="238" rx="7" ry="13" fill="#e0707a" fillOpacity="0.85"
          transform={`rotate(${i * 72} 150 250)`} />
      ))}
      <circle cx="150" cy="250" r="5" fill="#f1d68e" />
      <text x="150" y="455" textAnchor="middle" className={stili.firma}>T·AI·ROTS</text>
      <text x="150" y="62" textAnchor="middle" className={stili.firma}>✦ ✦ ✦</text>
    </svg>
  );
}

export function Faccia({ carta }: { carta: TipoCarta }) {
  const [mancante, setMancante] = useState(false);
  if (mancante) return <div className={stili.testo}>{carta.nome_it}</div>;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={`/cards/${carta.id}.${ESTENSIONE}`}
      alt={carta.nome_it}
      className={stili.immagine}
      onError={() => setMancante(true)}
      draggable={false}
    />
  );
}

export function Carta({
  carta,
  rivelata,
  rovescio = false,
  larghezza = 120,
  brilla = false,
  onClick,
  etichetta,
}: {
  carta?: TipoCarta | null;
  rivelata: boolean;
  rovescio?: boolean;
  larghezza?: number;
  brilla?: boolean;
  onClick?: () => void;
  etichetta?: string;
}) {
  const girata = rivelata && !!carta;
  return (
    <div
      className={`${stili.carta} ${brilla ? stili.brilla : ""} ${onClick ? stili.cliccabile : ""}`}
      style={{ "--w": `${larghezza}px` } as React.CSSProperties}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={etichetta ?? (girata ? carta?.nome_it : "Carta coperta")}
      onKeyDown={onClick ? (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onClick(); } } : undefined}
    >
      <motion.div
        className={stili.interno}
        initial={false}
        animate={{ rotateY: girata ? 180 : 0 }}
        transition={{ duration: 0.9, ease: [0.2, 0.7, 0.2, 1] }}
      >
        <div className={stili.lato}>
          <Dorso />
        </div>
        <div className={`${stili.lato} ${stili.fronte}`}>
          <div className={stili.orientamento} style={{ transform: rovescio ? "rotate(180deg)" : undefined }}>
            {carta && <Faccia carta={carta} />}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
