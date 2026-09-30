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
import type { Carta as TipoCarta, Dignita, Soggetto, Stesa } from "@/lib/api";
import { nomeCarta, nomePosizione } from "@/lib/i18n";
import { useLingua, useLinguaNomi } from "@/lib/lingua";
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

export { COLORE_SOGGETTO, SCALA_CARTE, larghezzaBase } from "@/lib/geometria-tavolo";
import { COLORE_SOGGETTO, SCALA_CARTE, larghezzaBase } from "@/lib/geometria-tavolo";

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

/* Sotto il tavolo delle letture speciali: chi è chi. Solo i soggetti che la
 * stesa usa; visibile anche sul telefono, dove le etichette delle posizioni
 * sono nascoste. */
function Legenda({ stesa, nomePartner }: { stesa: Stesa; nomePartner?: string | null }) {
  const { t } = useLingua();
  const usati = new Set((stesa.posizioni.map((p) => p.soggetto).filter(Boolean)) as Soggetto[]);
  const voci: { chiave: Soggetto; testo: string }[] = [
    { chiave: "tu", testo: t.soggetto_tu },
    { chiave: "partner", testo: nomePartner || t.soggetto_partner },
    { chiave: "coppia", testo: t.soggetto_coppia },
    { chiave: "strada-a", testo: `${t.soggetto_strada} · A` },
    { chiave: "strada-b", testo: `${t.soggetto_strada} · B` },
  ];
  return (
    <ul className={stili.legenda} aria-label={t.legenda}>
      {voci.filter((v) => usati.has(v.chiave)).map((v) => (
        <li key={v.chiave} style={{ "--soggetto": COLORE_SOGGETTO[v.chiave] } as React.CSSProperties}>
          <span className={stili.legendaPunto} aria-hidden="true" />
          {v.testo}
        </li>
      ))}
    </ul>
  );
}

function Pallino({ posata, titolo, scoperta }: { posata: Posata; titolo: string; scoperta: boolean }) {
  const { t } = useLingua();
  const lingua = useLinguaNomi();
  const [aperto, setAperto] = useState(false);
  if (!scoperta || !posata.carta) return null;
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
        aria-label={`${titolo}: ${nomeCarta(posata.carta, lingua)}`}
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
            <span className={stili.fumettoPosizione}>{titolo}</span>
            <strong className={stili.fumettoCarta}>
              {nomeCarta(posata.carta, lingua)} · {posata.rovescio ? t.rovesciata : t.dritta}
            </strong>
            <span className={stili.fumettoMeta}>
              {posata.carta.astrologia}
              {posata.dignita && posata.dignita.giudizio !== "neutra" && ` · ${t.dignita}: ${posata.dignita.giudizio}`}
              {posata.doppia && ` · ${t.doppia_valenza}`}
            </span>
            {posata.interpretazione && <p className="oracolo" dir="auto">{posata.interpretazione}</p>}
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
  nomePartner,
  manuale,
  onSelezionaPosizione,
}: {
  stesa: Stesa;
  posate: Posata[];
  /* La posizione che aspetta: una carta dal ventaglio, o la rivelazione. */
  prossima: number | null;
  onRivela?: (posizione: number) => void;
  rivelazioneInCorso: boolean;
  evidenzia: "scelta" | "rivelazione" | null;
  /* Il nome dell'altra persona, per la legenda delle letture speciali. */
  nomePartner?: string | null;
  /* "Interpreta i miei tarocchi" (v5): il mazzo è fisico, le carte si vedono già scoperte da subito
   * — `posata.rivelata` resta il ritmo con cui arriva l'interpretazione, invariato, e non decide più
   * da solo la faccia mostrata. */
  manuale?: boolean;
  /* Tocca una posizione vuota (solo in modalità manuale): apre il dialogo seme/carta. */
  onSelezionaPosizione?: (posizione: number) => void;
}) {
  const { t } = useLingua();
  const lingua = useLinguaNomi();
  const [ref, { w, h }] = useMisura<HTMLDivElement>();
  const quadrata = stesa.forma === "quadrata";
  /* Sul telefono il tavolo diventa quadrato (vedi il CSS): c'è più altezza, e le
   * carte possono crescere ancora un po' senza toccarsi. Lo si riconosce dalle
   * PROPORZIONI misurate e non dalla larghezza: fra 641 e ~700 px il tavolo è
   * ancora 16:12, e ingrandire lì le carte le farebbe sovrapporre. */
  const stretto = w > 0 && h / w > 0.9;
  const base = larghezzaBase(stesa);
  const larghezzaCarta = Math.max(
    30,
    w * (stretto && !quadrata ? (stesa.larghezza_stretto ?? base * 1.15) : base) * SCALA_CARTE,
  );
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
                      role: "button", tabIndex: 0,
                      onClick: () => onSelezionaPosizione(pos.n),
                      onKeyDown: (e: React.KeyboardEvent) => {
                        if (e.key === "Enter" || e.key === " ") onSelezionaPosizione(pos.n);
                      },
                    }
                  : {})}
              >
                <span>{pos.n}</span>
                {onSelezionaPosizione && <small>{t.interpreta_aggiungi}</small>}
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
                <Carta
                  carta={posata.carta}
                  rivelata={scoperta}
                  rovescio={posata.rovescio}
                  larghezza={larghezzaCarta}
                  brilla={attesa && evidenzia === "rivelazione" && !rivelazioneInCorso}
                  onClick={
                    attesa && evidenzia === "rivelazione" && !rivelazioneInCorso && onRivela
                      ? () => onRivela(pos.n)
                      : undefined
                  }
                  etichetta={scoperta ? undefined : `${pos.n}. ${nome}`}
                />
                {onSelezionaPosizione && (
                  <button
                    type="button"
                    className={stili.modificaCartaManuale}
                    onClick={() => onSelezionaPosizione(pos.n)}
                  >
                    {t.interpreta_modifica}
                  </button>
                )}
              </motion.div>
            )}
            {posata && !pos.rotazione && <Pallino posata={posata} titolo={`${pos.n}. ${nome}`} scoperta={scoperta} />}
            {scoperta && pos.rotazione !== 0 && (
              /* Il tavolo di una carta orizzontale è ruotato: il pallino e il suo
               * fumetto si contro-ruotano, così il testo resta verticale come
               * quello delle altre carte. L'origine è il punto d'ancoraggio. */
              <div className={stili.pallinoTraverso} style={{ transform: `rotate(${-pos.rotazione}deg)` }}>
                <Pallino posata={posata!} titolo={`${pos.n}. ${nome}`} scoperta={scoperta} />
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
