"use client";

/* Il tavolo: le posizioni della stesa, le carte posate, il pallino.
 *
 * Le coordinate vengono dalla stesa (0–1 sul tavolo), e la larghezza delle
 * carte dal numero di posizioni: dieci carte della Croce Celtica devono
 * stare dove ne stanno tre. Ogni carta posata porta lo stesso `layoutId`
 * della carta del ventaglio da cui viene, e framer-motion la fa volare.
 */

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import type { Carta as TipoCarta, Dignita, Stesa } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { Carta } from "../componenti/carta";
import stili from "./leggi.module.css";

export interface Posata {
  posizione: number;
  slot: number | null;
  calcolata: boolean;
  rivelata: boolean;
  carta?: TipoCarta;
  rovescio?: boolean;
  interpretazione?: string | null;
  dignita?: Dignita | null;
  doppia?: boolean;
}

const FATTORE: Record<string, number> = {
  "tre-carte": 0.16,
  "croce-semplice": 0.098,
  "ferro-di-cavallo": 0.1,
  "croce-celtica": 0.074,
  "ruota-astrologica": 0.075,
};

function useLarghezza<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [w, setW] = useState(0);
  useEffect(() => {
    if (!ref.current) return;
    const o = new ResizeObserver(([e]) => setW(e.contentRect.width));
    o.observe(ref.current);
    return () => o.disconnect();
  }, []);
  return [ref, w] as const;
}

function Pallino({ posata, nomePosizione }: { posata: Posata; nomePosizione: string }) {
  const { t } = useLingua();
  const [aperto, setAperto] = useState(false);
  if (!posata.rivelata || !posata.carta) return null;
  return (
    <div
      className={stili.pallinoAncora}
      onMouseEnter={() => setAperto(true)}
      onMouseLeave={() => setAperto(false)}
      onFocus={() => setAperto(true)}
      onBlur={() => setAperto(false)}
    >
      <button
        className={posata.interpretazione ? stili.pallino : stili.pallinoAttesa}
        aria-label={`${nomePosizione}: ${posata.carta.nome_it}`}
        aria-expanded={aperto}
        onClick={() => setAperto((a) => !a)}
      />
      <AnimatePresence>
        {aperto && (
          <motion.div
            className={`pannello ${stili.fumetto}`}
            initial={{ opacity: 0, y: 6, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.98 }}
            transition={{ duration: 0.18 }}
            role="tooltip"
          >
            <span className={stili.fumettoPosizione}>{nomePosizione}</span>
            <strong className={stili.fumettoCarta}>
              {posata.carta.nome_it} · {posata.rovescio ? t.rovesciata : t.dritta}
            </strong>
            <span className={stili.fumettoMeta}>
              {posata.carta.astrologia}
              {posata.dignita && posata.dignita.giudizio !== "neutra" && ` · ${t.dignita}: ${posata.dignita.giudizio}`}
              {posata.doppia && ` · ${t.doppia_valenza}`}
            </span>
            {posata.interpretazione && <p className="oracolo">{posata.interpretazione}</p>}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function Tavolo({
  stesa,
  posate,
  prossima,
  onRivela,
  rivelazioneInCorso,
  evidenzia,
}: {
  stesa: Stesa;
  posate: Posata[];
  /* La posizione che aspetta: una carta dal ventaglio, o la rivelazione. */
  prossima: number | null;
  onRivela?: (posizione: number) => void;
  rivelazioneInCorso: boolean;
  evidenzia: "scelta" | "rivelazione" | null;
}) {
  const { lingua } = useLingua();
  const [ref, w] = useLarghezza<HTMLDivElement>();
  const quadrata = stesa.id === "ruota-astrologica";
  /* Sul telefono il tavolo diventa quadrato (vedi il CSS): c'è più altezza,
   * e le carte possono crescere di un terzo senza toccarsi. */
  const stretto = w > 0 && w < 600;
  const larghezzaCarta = Math.max(30, w * (FATTORE[stesa.id] ?? 0.1) * (stretto && !quadrata ? 1.3 : 1));
  const perPosizione = new Map(posate.map((p) => [p.posizione, p]));

  return (
    <div ref={ref} className={quadrata ? stili.tavoloQuadrato : stili.tavolo}>
      <div className={stili.tappeto} aria-hidden="true" />
      {stesa.posizioni.map((pos) => {
        const posata = perPosizione.get(pos.n);
        const nome = lingua === "en" ? pos.nome_en : pos.nome;
        const attesa = prossima === pos.n;
        return (
          <div
            key={pos.n}
            className={stili.posizione}
            style={{
              left: `${pos.x * 100}%`,
              top: `${pos.y * 100}%`,
              width: larghezzaCarta,
              zIndex: pos.rotazione ? 3 : 2,
              transform: `translate(-50%, -50%) rotate(${pos.rotazione}deg)`,
            }}
          >
            {!posata && (
              <div
                className={`${stili.segnaposto} ${attesa && evidenzia === "scelta" ? stili.segnapostoAttivo : ""}`}
                title={`${pos.n}. ${nome}`}
              >
                <span>{pos.n}</span>
              </div>
            )}
            {posata && (
              <motion.div
                layoutId={posata.slot !== null ? `slot-${posata.slot}` : `calcolata-${pos.n}`}
                initial={posata.calcolata ? { opacity: 0, scale: 0.4, rotate: -20 } : false}
                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 120, damping: 18 }}
              >
                <Carta
                  carta={posata.carta}
                  rivelata={posata.rivelata}
                  rovescio={posata.rovescio}
                  larghezza={larghezzaCarta}
                  brilla={attesa && evidenzia === "rivelazione" && !rivelazioneInCorso}
                  onClick={
                    attesa && evidenzia === "rivelazione" && !rivelazioneInCorso && onRivela
                      ? () => onRivela(pos.n)
                      : undefined
                  }
                  etichetta={posata.rivelata ? undefined : `${pos.n}. ${nome}`}
                />
              </motion.div>
            )}
            {posata && !pos.rotazione && <Pallino posata={posata} nomePosizione={`${pos.n}. ${nome}`} />}
            {posata?.rivelata && pos.rotazione !== 0 && (
              <div className={stili.pallinoTraverso}>
                <Pallino posata={posata} nomePosizione={`${pos.n}. ${nome}`} />
              </div>
            )}
            <span className={stili.etichettaPosizione} style={{ transform: pos.rotazione ? `rotate(${-pos.rotazione}deg)` : undefined }}>
              {pos.rotazione ? "" : nome}
            </span>
          </div>
        );
      })}
    </div>
  );
}
