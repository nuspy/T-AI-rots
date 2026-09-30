"use client";

/* Una carta: dorso, faccia e il giro fra i due.
 *
 * **Le carte hanno proporzioni 9:16**, come le immagini: 360×640 px bastano.
 * **La faccia è un'immagine** in `public/cards/{id}.webp` e **il dorso** è
 * `public/cards/dorso.webp`. Se un file manca resta il nome della carta in
 * testo, o il dorso disegnato: mai una carta vuota sul tavolo.
 *
 * **Il rovescio è la faccia girata di 180°**, come sul tavolo vero: la
 * rotazione sta sulla faccia, non sulla carta, così il giro 3D resta lo
 * stesso per tutte.
 */

import { useState } from "react";
import { motion } from "framer-motion";
import type { Carta as TipoCarta } from "@/lib/api";
import { nomeCarta } from "@/lib/i18n";
import { useLingua, useLinguaNomi } from "@/lib/lingua";
import { percorsoCarta, useMazzoAttivo } from "@/lib/mazzo-attivo";
import stili from "./carta.module.css";

/* `webp` è il formato delle immagini definitive; `NEXT_PUBLIC_CARD_EXT` resta
 * per chi serve altro con lo stesso nome. */
import { ESTENSIONE } from "@/lib/geometria-tavolo";
export { ESTENSIONE };

/* Il ventaglio monta 78 dorsi: se `dorso.webp` non c'è, dopo il primo errore
 * gli altri partono già dal disegno invece di rifare 78 richieste.
 * v7: la bandiera è globale, non per mazzo — un dorso mancante su UN mazzo disabiliterebbe il
 * caricamento anche per gli altri finché non si ricarica la pagina. Non è un problema oggi (il
 * mazzo predefinito ha sempre il suo dorso): da rivedere se la Fase J rende comune cambiare mazzo
 * a runtime senza un giro di pagina. */
let dorsoAssente = false;

function DorsoDisegnato() {
  /* L'esagramma unicursale e la rosa a cinque petali: i due emblemi della
   * tradizione thelemica, in oro su notte. Il disegno è 360×640, cioè 9:16. */
  const cx = 180;
  const cy = 320;
  const punti = [0, 1, 2, 3, 4, 5].map((i) => {
    const a = (Math.PI / 3) * i - Math.PI / 2;
    return [cx + Math.cos(a) * 94, cy + Math.sin(a) * 94];
  });
  const [p0, p1, p2, p3, p4, p5] = punti;
  const unicursale = `M${p0} L${p2} L${p5} L${p1} L${p4} L${p3} L${p0}`.replaceAll(",", " ");
  return (
    <svg viewBox="0 0 360 640" className={stili.svg} aria-hidden="true">
      <defs>
        <radialGradient id="dorso-g" cx="0.5" cy="0.5" r="0.7">
          <stop offset="0" stopColor="#2c1f5c" />
          <stop offset="1" stopColor="#0a0717" />
        </radialGradient>
        <pattern id="dorso-p" width="28" height="28" patternUnits="userSpaceOnUse">
          <circle cx="14" cy="14" r="1.3" fill="#d8b45a" fillOpacity="0.35" />
        </pattern>
      </defs>
      <rect width="360" height="640" rx="20" fill="url(#dorso-g)" />
      <rect width="360" height="640" rx="20" fill="url(#dorso-p)" />
      <rect x="14" y="14" width="332" height="612" rx="14" fill="none" stroke="#d8b45a" strokeWidth="2.4" />
      <rect x="26" y="26" width="308" height="588" rx="9" fill="none" stroke="#d8b45a" strokeOpacity="0.35" />
      <circle cx={cx} cy={cy} r="125" fill="none" stroke="#d8b45a" strokeOpacity="0.55" />
      <circle cx={cx} cy={cy} r="115" fill="none" stroke="#d8b45a" strokeOpacity="0.25" />
      <path d={unicursale} fill="none" stroke="#f1d68e" strokeWidth="2.8" strokeLinejoin="round" />
      {[0, 1, 2, 3, 4].map((i) => (
        <ellipse key={i} cx={cx} cy={cy - 14} rx="8.5" ry="16" fill="#e0707a" fillOpacity="0.85"
          transform={`rotate(${i * 72} ${cx} ${cy})`} />
      ))}
      <circle cx={cx} cy={cy} r="6" fill="#f1d68e" />
      <text x={cx} y="582" textAnchor="middle" className={stili.firma}>TAROTS</text>
      <text x={cx} y="78" textAnchor="middle" className={stili.firma}>✦ ✦ ✦</text>
    </svg>
  );
}

export function Dorso() {
  const [assente, setAssente] = useState(dorsoAssente);
  const mazzo = useMazzoAttivo();
  if (assente) return <DorsoDisegnato />;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={percorsoCarta(mazzo, `dorso.${ESTENSIONE}`)}
      alt=""
      className={stili.immagine}
      onError={() => {
        dorsoAssente = true;
        setAssente(true);
      }}
      draggable={false}
    />
  );
}

export function Faccia({ carta }: { carta: TipoCarta }) {
  const [mancante, setMancante] = useState(false);
  const mazzo = useMazzoAttivo();
  const nome = nomeCarta(carta, useLinguaNomi());
  if (mancante) return <div className={stili.testo}>{nome}</div>;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={percorsoCarta(mazzo, `${carta.id}.${ESTENSIONE}`)}
      alt={nome}
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
  /* Un numero è in px; una stringa (es. `clamp(64px, 20vw, 150px)`) passa così com'è —
   * serve per le carte a larghezza responsiva (v7, hero della home). */
  larghezza?: number | string;
  brilla?: boolean;
  onClick?: () => void;
  etichetta?: string;
}) {
  const girata = rivelata && !!carta;
  const { t } = useLingua();
  const lingua = useLinguaNomi();
  const w = typeof larghezza === "number" ? `${larghezza}px` : larghezza;
  return (
    <div
      className={`${stili.carta} ${brilla ? stili.brilla : ""} ${onClick ? stili.cliccabile : ""}`}
      style={{ "--w": w } as React.CSSProperties}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={etichetta ?? (girata && carta ? nomeCarta(carta, lingua) : t.carta_coperta)}
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
