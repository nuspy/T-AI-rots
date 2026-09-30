"use client";

/* Il tavolo della v2: le posizioni della stesa, le carte posate, il punto che apre l'interpretazione di ciascuna.
 * La geometria è quella del sito (`app/(sito)/leggi/tavolo.tsx`: coordinate 0–1 dalla stesa, larghezza delle
 * carte dalla stesa, tavolo quadrato quando è più alto che largo); cambiano l'abito e i testi. Ogni carta posata
 * porta lo stesso `layoutId` della carta del ventaglio da cui viene: framer-motion la fa volare al suo posto. */

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import type { Carta, Dignita, Soggetto, Stesa } from "@/lib/api";
import { nomeCarta, nomePosizione } from "@/lib/i18n/nomi";
import { CartaV2 } from "@/v2/componenti/carta";
import { useLingua, useLinguaNomi } from "@/v2/lib/lingua";
import stili from "./lettura.module.css";

export interface Posata {
  posizione: number;
  slot: number | null;
  calcolata: boolean;
  rivelata: boolean;
  carta?: Carta;
  rovescio?: boolean;
  interpretazione?: string | null;
  dignita?: Dignita | null;
  doppia?: boolean;
}

export const larghezzaBase = (stesa: Stesa): number => stesa.larghezza ?? 0.1;
const SCALA_CARTE = 1.2;

/* Chi parla una posizione, nelle letture di due persone: colori leggibili sul panno prugna, mai da soli (c'è la
 * legenda, e il nome della posizione lo dice già). */
export const COLORE_SOGGETTO: Record<Soggetto, string> = {
  tu: "#d6b66d",
  partner: "#9fd8d2",
  coppia: "#f0c8a8",
  "strada-a": "#e8a0b4",
  "strada-b": "#b7c9f2",
};

function useMisura<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [misura, setMisura] = useState({ w: 0, h: 0 });
  useEffect(() => {
    if (!ref.current) return;
    const o = new ResizeObserver(([e]) => setMisura({ w: e.contentRect.width, h: e.contentRect.height }));
    o.observe(ref.current);
    return () => o.disconnect();
  }, []);
  return [ref, misura] as const;
}

function Legenda({ stesa, nomePartner }: { stesa: Stesa; nomePartner?: string | null }) {
  const { t } = useLingua();
  const s = t.lettura.soggetti;
  const usati = new Set(stesa.posizioni.map((p) => p.soggetto).filter(Boolean) as Soggetto[]);
  const voci: { chiave: Soggetto; testo: string }[] = [
    { chiave: "tu", testo: s.tu },
    { chiave: "partner", testo: nomePartner || s.partner },
    { chiave: "coppia", testo: s.coppia },
    { chiave: "strada-a", testo: s.strada_a },
    { chiave: "strada-b", testo: s.strada_b },
  ];
  return (
    <ul className={stili.legenda} aria-label={t.lettura.legenda}>
      {voci.filter((v) => usati.has(v.chiave)).map((v) => (
        <li key={v.chiave} style={{ "--soggetto": COLORE_SOGGETTO[v.chiave] } as React.CSSProperties}>
          <span className={stili.legendaPunto} aria-hidden="true" />{v.testo}
        </li>
      ))}
    </ul>
  );
}

function Punto({ posata, titolo, scoperta }: { posata: Posata; titolo: string; scoperta: boolean }) {
  const { t } = useLingua();
  const lingua = useLinguaNomi();
  const [aperto, setAperto] = useState(false);
  if (!scoperta || !posata.carta) return null;
  const l = t.lettura;
  return (
    <div
      className={stili.pallinoAncora}
      onMouseEnter={() => setAperto(true)}
      onMouseLeave={() => setAperto(false)}
      onFocus={() => setAperto(true)}
      onBlur={() => setAperto(false)}
    >
      <button
        type="button"
        className={posata.interpretazione ? stili.pallino : stili.pallinoAttesa}
        aria-label={`${titolo}: ${nomeCarta(posata.carta, lingua)}`}
        aria-expanded={aperto}
        onClick={() => setAperto((a) => !a)}
      />
      <AnimatePresence>
        {aperto && (
          <motion.div
            className={stili.fumetto}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.18 }}
            role="tooltip"
          >
            <span className={stili.fumettoPosizione}>{titolo}</span>
            <strong className={stili.fumettoCarta}>
              {nomeCarta(posata.carta, lingua)} · {posata.rovescio ? l.rovesciata : l.dritta}
            </strong>
            <span className={stili.fumettoMeta}>
              {posata.carta.astrologia}
              {posata.dignita && posata.dignita.giudizio !== "neutra" && ` · ${l.dignita}: ${posata.dignita.giudizio}`}
              {posata.doppia && ` · ${l.doppia}`}
            </span>
            {posata.interpretazione && <p dir="auto">{posata.interpretazione}</p>}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function Tavolo({
  stesa, posate, prossima, onRivela, rivelazioneInCorso, evidenzia, nomePartner, manuale, onSelezionaPosizione,
  testoAggiungi, testoModifica,
}: {
  stesa: Stesa;
  posate: Posata[];
  prossima: number | null;
  onRivela?: (posizione: number) => void;
  rivelazioneInCorso: boolean;
  evidenzia: "scelta" | "rivelazione" | null;
  nomePartner?: string | null;
  /** Le proprie carte (mazzo fisico): le facce si vedono da subito. */
  manuale?: boolean;
  /** Solo quando si posano le proprie carte: tocca una posizione per dire quale carta c'è. */
  onSelezionaPosizione?: (posizione: number) => void;
  testoAggiungi?: string;
  testoModifica?: string;
}) {
  const lingua = useLinguaNomi();
  const [ref, { w, h }] = useMisura<HTMLDivElement>();
  const quadrata = stesa.forma === "quadrata";
  const stretto = w > 0 && h / w > 0.9;
  const base = larghezzaBase(stesa);
  const larghezzaCarta = Math.max(30, w * (stretto && !quadrata ? (stesa.larghezza_stretto ?? base * 1.15) : base) * SCALA_CARTE);
  const perPosizione = new Map(posate.map((p) => [p.posizione, p]));

  return (
    <>
      <div ref={ref} className={quadrata ? stili.tavoloQuadrato : stili.tavolo}>
        <div className={stili.tappeto} aria-hidden="true" />
        {stesa.posizioni.map((pos) => {
          const posata = perPosizione.get(pos.n);
          const nome = nomePosizione(pos, lingua);
          const attesa = prossima === pos.n;
          const scoperta = !!posata && (posata.rivelata || !!manuale);
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
                ...(pos.soggetto ? ({ "--soggetto": COLORE_SOGGETTO[pos.soggetto] } as React.CSSProperties) : {}),
              }}
            >
              {!posata && (
                <div
                  className={`${stili.segnaposto} ${pos.soggetto ? stili.segnapostoSoggetto : ""} ${attesa && evidenzia === "scelta" ? stili.segnapostoAttivo : ""} ${onSelezionaPosizione ? stili.segnapostoManuale : ""}`}
                  title={`${pos.n}. ${nome}`}
                  {...(onSelezionaPosizione
                    ? {
                        role: "button", tabIndex: 0, "aria-label": `${pos.n}. ${nome} — ${testoAggiungi ?? ""}`,
                        onClick: () => onSelezionaPosizione(pos.n),
                        onKeyDown: (e: React.KeyboardEvent) => {
                          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelezionaPosizione(pos.n); }
                        },
                      }
                    : {})}
                >
                  <span>{pos.n}</span>
                  {onSelezionaPosizione && <small>{testoAggiungi}</small>}
                </div>
              )}
              {posata && (
                <motion.div
                  className={pos.soggetto ? stili.cartaSoggetto : undefined}
                  style={{ position: "relative" }}
                  layoutId={posata.slot !== null ? `slot-${posata.slot}` : `calcolata-${pos.n}`}
                  initial={posata.calcolata ? { opacity: 0, scale: 0.4, rotate: -20 } : false}
                  animate={{ opacity: 1, scale: 1, rotate: 0 }}
                  transition={{ type: "spring", stiffness: 120, damping: 18 }}
                >
                  <CartaV2
                    carta={posata.carta}
                    rivelata={scoperta}
                    rovescio={posata.rovescio}
                    larghezza={larghezzaCarta}
                    brilla={attesa && evidenzia === "rivelazione" && !rivelazioneInCorso}
                    onClick={attesa && evidenzia === "rivelazione" && !rivelazioneInCorso && onRivela ? () => onRivela(pos.n) : undefined}
                    etichetta={scoperta ? undefined : `${pos.n}. ${nome}`}
                  />
                  {onSelezionaPosizione && (
                    <button type="button" className={stili.modificaManuale} onClick={() => onSelezionaPosizione(pos.n)}>
                      {testoModifica}
                    </button>
                  )}
                </motion.div>
              )}
              {posata && !pos.rotazione && <Punto posata={posata} titolo={`${pos.n}. ${nome}`} scoperta={scoperta} />}
              {scoperta && pos.rotazione !== 0 && (
                <div className={stili.pallinoTraverso} style={{ transform: `rotate(${-pos.rotazione}deg)` }}>
                  <Punto posata={posata!} titolo={`${pos.n}. ${nome}`} scoperta={scoperta} />
                </div>
              )}
              <span className={stili.etichettaPosizione} style={{ transform: pos.rotazione ? `rotate(${-pos.rotazione}deg)` : undefined }}>
                {pos.rotazione ? "" : nome}
              </span>
            </div>
          );
        })}
      </div>
      {stesa.categoria !== "standard" && <Legenda stesa={stesa} nomePartner={nomePartner} />}
    </>
  );
}
