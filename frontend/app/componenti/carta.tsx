"use client";

/* Una carta: dorso, faccia e il giro fra i due.
 *
 * **La faccia è un segnaposto disegnato**, finché non arrivano le immagini
 * definitive: numero, nome, lettera ebraica, elemento e astrologia, sui
 * colori della carta. Con `NEXT_PUBLIC_CARD_IMAGES=true` si prova prima
 * `public/cards/{id}.webp`, e se manca si torna al disegno — un'immagine
 * mancante non deve mai lasciare una carta vuota sul tavolo.
 *
 * **Il rovescio è la faccia girata di 180°**, come sul tavolo vero: la
 * rotazione sta sulla faccia, non sulla carta, così il giro 3D resta lo
 * stesso per tutte.
 */

import { useState } from "react";
import { motion } from "framer-motion";
import type { Carta as TipoCarta } from "@/lib/api";
import stili from "./carta.module.css";

const IMMAGINI = process.env.NEXT_PUBLIC_CARD_IMAGES === "true";

const SIMBOLI_ASTRALI: Record<string, string> = {
  Ariete: "♈", Toro: "♉", Gemelli: "♊", Cancro: "♋", Leone: "♌", Vergine: "♍",
  Bilancia: "♎", Scorpione: "♏", Sagittario: "♐", Capricorno: "♑", Acquario: "♒", Pesci: "♓",
  Sole: "☉", Luna: "☽", Mercurio: "☿", Venere: "♀", Marte: "♂", Giove: "♃", Saturno: "♄",
};

const COLORE_ELEMENTO: Record<string, string> = {
  fuoco: "#e8744a", acqua: "#4a9ee8", aria: "#e8d84a", terra: "#5fae6b", spirito: "#c7b5ff",
};

const NOMI_RANGO: Record<string, string> = {
  asso: "A", due: "II", tre: "III", quattro: "IV", cinque: "V", sei: "VI", sette: "VII",
  otto: "VIII", nove: "IX", dieci: "X", cavaliere: "♞", regina: "♛", principe: "♚", principessa: "♕",
};

/** Il primo simbolo astrologico che compare nel testo dell'attribuzione. */
function simboloAstrale(testo: string): string | null {
  for (const [nome, simbolo] of Object.entries(SIMBOLI_ASTRALI)) {
    if (testo.includes(nome)) return simbolo + "︎";
  }
  return null;
}

/** Il triangolo alchemico dell'elemento, disegnato e non preso da un font. */
function Elemento({ elemento, x, y, r }: { elemento: string; x: number; y: number; r: number }) {
  const colore = COLORE_ELEMENTO[elemento] ?? "#c7b5ff";
  if (elemento === "spirito") {
    return (
      <g stroke={colore} strokeWidth={3} fill="none">
        <circle cx={x} cy={y} r={r * 0.8} />
        <circle cx={x} cy={y} r={r * 0.25} fill={colore} />
      </g>
    );
  }
  const su = elemento === "fuoco" || elemento === "aria";
  const h = r * 1.7;
  const punti = su
    ? `${x},${y - h / 2} ${x + r},${y + h / 2} ${x - r},${y + h / 2}`
    : `${x},${y + h / 2} ${x + r},${y - h / 2} ${x - r},${y - h / 2}`;
  const barra = elemento === "aria" || elemento === "terra";
  const yBarra = su ? y + h * 0.1 : y - h * 0.1;
  return (
    <g stroke={colore} strokeWidth={3} fill="none" strokeLinejoin="round">
      <polygon points={punti} />
      {barra && <line x1={x - r * 0.75} x2={x + r * 0.75} y1={yBarra} y2={yBarra} />}
    </g>
  );
}

/** Il simbolo del seme, al centro delle minori. */
function Seme({ seme, x, y }: { seme: string; x: number; y: number }) {
  const oro = "#f1d68e";
  switch (seme) {
    case "bastoni":
      return (
        <g stroke={oro} strokeWidth={5} strokeLinecap="round" fill="none">
          <line x1={x - 40} y1={y + 55} x2={x + 40} y2={y - 55} />
          <line x1={x + 40} y1={y + 55} x2={x - 40} y2={y - 55} />
          <circle cx={x} cy={y} r={10} fill={oro} />
        </g>
      );
    case "coppe":
      return (
        <g stroke={oro} strokeWidth={4} fill="none">
          <path d={`M${x - 45},${y - 40} Q${x},${y + 45} ${x + 45},${y - 40} Z`} />
          <line x1={x} y1={y + 3} x2={x} y2={y + 45} />
          <line x1={x - 25} y1={y + 48} x2={x + 25} y2={y + 48} />
        </g>
      );
    case "spade":
      return (
        <g stroke={oro} strokeWidth={4} fill="none" strokeLinecap="round">
          <path d={`M${x},${y - 70} L${x + 9},${y + 20} L${x - 9},${y + 20} Z`} />
          <line x1={x - 32} y1={y + 22} x2={x + 32} y2={y + 22} />
          <line x1={x} y1={y + 22} x2={x} y2={y + 58} />
          <circle cx={x} cy={y + 64} r={6} />
        </g>
      );
    default:
      return (
        <g stroke={oro} strokeWidth={4} fill="none">
          <circle cx={x} cy={y} r={52} />
          <circle cx={x} cy={y} r={34} />
          {Array.from({ length: 8 }, (_, i) => {
            const a = (i * Math.PI) / 4;
            return (
              <line key={i} x1={x + Math.cos(a) * 34} y1={y + Math.sin(a) * 34}
                x2={x + Math.cos(a) * 52} y2={y + Math.sin(a) * 52} />
            );
          })}
        </g>
      );
  }
}

export function FacciaDisegnata({ carta }: { carta: TipoCarta }) {
  const [c1, c2] = carta.colori?.length ? carta.colori : ["#2a1f4d", "#d8b45a"];
  const gid = `g-${carta.id}`;
  const maggiore = carta.arcano === "maggiore";
  const astro = simboloAstrale(carta.astrologia ?? "");
  const testata = maggiore ? carta.numero_romano : NOMI_RANGO[carta.rango ?? ""] ?? "";
  const nome = maggiore ? carta.nome_it : carta.nome_it.split(" — ")[0];
  const sottotitolo = maggiore ? carta.nome_thoth : (carta.titolo_thoth ?? carta.nome_thoth);

  return (
    <svg viewBox="0 0 300 500" className={stili.svg} role="img" aria-label={carta.nome_it}>
      <defs>
        <linearGradient id={gid} x1="0" y1="0" x2="0.4" y2="1">
          <stop offset="0" stopColor={c1} />
          <stop offset="1" stopColor="#0b0818" />
        </linearGradient>
        <radialGradient id={`${gid}-l`} cx="0.5" cy="0.45" r="0.55">
          <stop offset="0" stopColor={c2} stopOpacity="0.55" />
          <stop offset="1" stopColor={c2} stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect x="0" y="0" width="300" height="500" rx="18" fill={`url(#${gid})`} />
      <rect x="0" y="0" width="300" height="500" rx="18" fill={`url(#${gid}-l)`} />
      <rect x="12" y="12" width="276" height="476" rx="12" fill="none" stroke="#d8b45a" strokeOpacity="0.8" strokeWidth="2" />
      <rect x="20" y="20" width="260" height="460" rx="8" fill="none" stroke="#d8b45a" strokeOpacity="0.3" strokeWidth="1" />

      <text x="150" y="62" textAnchor="middle" className={stili.numero}>{testata}</text>

      {maggiore && carta.lettera_ebraica ? (
        <text x="150" y="262" textAnchor="middle" className={stili.lettera}>{carta.lettera_ebraica.glifo}</text>
      ) : (
        <Seme seme={carta.seme ?? "dischi"} x={150} y={225} />
      )}

      <Elemento elemento={carta.elemento} x={astro ? 118 : 150} y={330} r={16} />
      {astro && <text x="182" y="342" textAnchor="middle" className={stili.astro}>{astro}</text>}

      <line x1="60" y1="378" x2="240" y2="378" stroke="#d8b45a" strokeOpacity="0.5" />
      <text x="150" y="415" textAnchor="middle" className={stili.nome}>{nome}</text>
      <text x="150" y="446" textAnchor="middle" className={stili.sottotitolo}>{sottotitolo}</text>
    </svg>
  );
}

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
  const [senzaImmagine, setSenzaImmagine] = useState(!IMMAGINI);
  if (senzaImmagine) return <FacciaDisegnata carta={carta} />;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={`/cards/${carta.id}.webp`}
      alt={carta.nome_it}
      className={stili.immagine}
      onError={() => setSenzaImmagine(true)}
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
