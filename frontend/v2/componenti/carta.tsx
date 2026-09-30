"use client";

/* Le carte della v2.
 *
 * - `ImmagineCarta`: l'immagine di una carta (o del dorso), 9:16, con le misure dichiarate — niente salti di
 *   impaginazione mentre arriva.
 * - `CartaV2`: dorso, faccia e il giro fra i due, per il tavolo della lettura. Il rovescio è la faccia girata di
 *   180°, come sul tavolo vero. Se l'immagine manca resta il nome della carta: mai una carta vuota.
 *
 * Il mazzo attivo (`lib/mazzo-attivo`) sceglie la cartella delle immagini: il Thoth sta in `/cards/`, gli altri
 * mazzi in `/cards/<slug>/`. */

import { useState } from "react";
import { motion } from "framer-motion";
import type { Carta } from "@/lib/api";
import { nomeCarta } from "@/lib/i18n/nomi";
import { percorsoCarta, useMazzoAttivo } from "@/lib/mazzo-attivo";
import { useLingua, useLinguaNomi } from "@/v2/lib/lingua";
import stili from "./carta.module.css";

const ESTENSIONE = process.env.NEXT_PUBLIC_CARD_EXT ?? "webp";

export function ImmagineCarta({
  id, alt, classe, priorita = false, mazzo,
}: {
  id: string;
  alt: string;
  classe?: string;
  priorita?: boolean;
  /** Un mazzo diverso da quello attivo (per esempio nelle pagine dei mazzi). */
  mazzo?: string | null;
}) {
  const attivo = useMazzoAttivo();
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      className={classe}
      src={percorsoCarta(mazzo === undefined ? attivo : mazzo, `${id}.${ESTENSIONE}`)}
      width={360}
      height={640}
      alt={alt}
      loading={priorita ? "eager" : "lazy"}
      fetchPriority={priorita ? "high" : undefined}
      decoding="async"
      draggable={false}
    />
  );
}

export function Dorso() {
  return <ImmagineCarta id="dorso" alt="" classe={stili.immagine} />;
}

function Faccia({ carta }: { carta: Carta }) {
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

export function CartaV2({
  carta, rivelata, rovescio = false, larghezza = 120, brilla = false, onClick, etichetta,
}: {
  carta?: Carta | null;
  rivelata: boolean;
  rovescio?: boolean;
  larghezza?: number | string;
  brilla?: boolean;
  onClick?: () => void;
  etichetta?: string;
}) {
  const { t } = useLingua();
  const lingua = useLinguaNomi();
  const girata = rivelata && !!carta;
  const w = typeof larghezza === "number" ? `${larghezza}px` : larghezza;
  return (
    <div
      className={`${stili.carta} ${brilla ? stili.brilla : ""} ${onClick ? stili.cliccabile : ""}`}
      style={{ "--w": w } as React.CSSProperties}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={etichetta ?? (girata && carta ? nomeCarta(carta, lingua) : t.lettura.carta_coperta)}
      onKeyDown={onClick ? (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onClick(); } } : undefined}
    >
      <motion.div
        className={stili.interno}
        initial={false}
        animate={{ rotateY: girata ? 180 : 0 }}
        transition={{ duration: 0.9, ease: [0.2, 0.7, 0.2, 1] }}
      >
        <div className={stili.lato}><Dorso /></div>
        <div className={`${stili.lato} ${stili.fronte}`}>
          <div className={stili.orientamento} style={{ transform: rovescio ? "rotate(180deg)" : undefined }}>
            {carta && <Faccia carta={carta} />}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
