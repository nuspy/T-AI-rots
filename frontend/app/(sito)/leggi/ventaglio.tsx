"use client";

/* Il mazzo e il ventaglio: mescolata, taglio, scelta.
 *
 * - `Mescolamento`: i mazzetti si dividono e si ricompongono finché chi
 *   consulta non clicca il mazzo per fermarli.
 * - `Taglio`: il mazzo è disteso in fila; il clic sceglie il punto in cui
 *   dividerlo, e le due metà si scambiano di posto come a mano.
 * - `Ventaglio`: tutte le carte, coperte, disposte ad arco — in più archi
 *   impilati se sono tante, perché un solo arco di 78 carte le stringe a
 *   ~34 px l'una: troppo poco per scegliere col dito o col mouse.
 *
 * Le carte sono già assegnate agli slot sul server prima che il ventaglio si
 * apra: qui si conoscono solo gli indici. Al passaggio del mouse la carta si
 * solleva.
 */

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { useLingua } from "@/lib/lingua";
import { Dorso } from "../componenti/carta";
import stili from "./leggi.module.css";

//: Oltre questo numero di carte in un arco solo, le carte si accavallano troppo per essere scelte con
//: precisione: si divide in più archi, ciascuno non più grande di questo.
const CARTE_PER_ARCO = 26;

export function Ventaglio({
  quante,
  scelte,
  attivo,
  onScegli,
}: {
  quante: number;
  scelte: Set<number>;
  attivo: boolean;
  onScegli: (slot: number) => void;
}) {
  const gruppi = Math.max(1, Math.ceil(quante / CARTE_PER_ARCO));
  if (gruppi <= 1) {
    return <ArcoVentaglio inizio={0} quante={quante} scelte={scelte} attivo={attivo} onScegli={onScegli} />;
  }
  return (
    <div className={stili.ventaglioGruppi} aria-label="Ventaglio delle carte, diviso in più archi">
      {Array.from({ length: gruppi }, (_, g) => {
        const inizio = g * CARTE_PER_ARCO;
        const fine = Math.min(quante, inizio + CARTE_PER_ARCO);
        return (
          <ArcoVentaglio
            key={g} inizio={inizio} quante={fine - inizio} scelte={scelte} attivo={attivo} onScegli={onScegli}
          />
        );
      })}
    </div>
  );
}

/** Un arco solo, al più `CARTE_PER_ARCO` carte: la geometria che segue è pensata per quella misura, non per 78 —
 *  è per questo che dividere in più archi basta a ingrandire le carte, senza toccare il calcolo. `inizio` sposta
 *  gli indici locali (0..quante-1) sugli slot assoluti che il resto del flusso conosce (`scelte`, `onScegli`). */
function ArcoVentaglio({
  inizio,
  quante,
  scelte,
  attivo,
  onScegli,
}: {
  inizio: number;
  quante: number;
  scelte: Set<number>;
  attivo: boolean;
  onScegli: (slot: number) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(900);
  /* La carta sotto il puntatore sale sopra le vicine: in un arco fitto se ne
   * vede solo una striscia, e sollevarla senza portarla davanti la
   * lascerebbe coperta a metà. Indice locale: lo stato non deve cambiare
   * forma quando cambiano gli slot assoluti del gruppo. */
  const [sopra, setSopra] = useState<number | null>(null);
  useEffect(() => {
    if (!ref.current) return;
    const o = new ResizeObserver(([e]) => setW(e.contentRect.width));
    o.observe(ref.current);
    return () => o.disconnect();
  }, []);

  /* La geometria dell'arco. L'apertura cresce col numero di carte; il raggio
   * si ricava dalla corda, così l'arco occupa sempre la larghezza utile.
   * Con al più `CARTE_PER_ARCO` carte si resta sempre nel ramo più largo. */
  const apertura = quante > 30 ? 118 : 84; // gradi
  const corda = w * 0.92;
  const raggio = corda / 2 / Math.sin(((apertura / 2) * Math.PI) / 180);
  const larghezzaCarta = Math.min(quante > 30 ? 64 : 92, Math.max(30, (corda / quante) * (quante > 30 ? 3.2 : 1.9)));
  const altezzaCarta = larghezzaCarta * (16 / 9);
  const freccia = raggio * (1 - Math.cos(((apertura / 2) * Math.PI) / 180));
  const altezza = freccia + altezzaCarta + 40;

  return (
    <div ref={ref} className={stili.ventaglio} style={{ height: altezza }} aria-label="Ventaglio delle carte">
      {Array.from({ length: quante }, (_, i) => {
        const slot = inizio + i;
        if (scelte.has(slot)) return null;
        const angolo = -apertura / 2 + (apertura * i) / Math.max(1, quante - 1);
        return (
          <div
            key={slot}
            className={stili.ventaglioBraccio}
            style={{
              width: larghezzaCarta,
              height: altezzaCarta,
              marginLeft: -larghezzaCarta / 2,
              transformOrigin: `50% ${raggio}px`,
              transform: `rotate(${angolo}deg)`,
              zIndex: sopra === i ? quante + 1 : i,
            }}
            onMouseEnter={() => setSopra(i)}
            onMouseLeave={() => setSopra((s) => (s === i ? null : s))}
          >
            <motion.button
              layoutId={`slot-${slot}`}
              className={stili.ventaglioCarta}
              disabled={!attivo}
              onClick={() => onScegli(slot)}
              aria-label={`Carta ${slot + 1}`}
              initial={{ opacity: 0, y: 60 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: Math.min(1.2, i * 0.012), type: "spring", stiffness: 140, damping: 18 }}
              whileHover={attivo ? { y: -22, scale: 1.06 } : undefined}
              whileFocus={attivo ? { y: -22, scale: 1.06 } : undefined}
            >
              <Dorso />
            </motion.button>
          </div>
        );
      })}
    </div>
  );
}

/** La mescolata: il mazzo si divide e si ricompone finché non si clicca per
 *  fermarlo. Senza `onFerma` è solo l'animazione. */
export function Mescolamento({ onFerma }: { onFerma?: () => void }) {
  const { t } = useLingua();
  const mazzo = (
    <div className={stili.mescolamento} aria-hidden={onFerma ? undefined : "true"}>
      {Array.from({ length: 9 }, (_, i) => (
        <motion.div
          key={i}
          className={stili.mazzettoCarta}
          animate={{
            x: [0, (i % 2 ? 1 : -1) * (50 + i * 6), 0, (i % 2 ? -1 : 1) * 30, 0],
            y: [0, -i * 2, i * 1.5, -i, 0],
            rotate: [0, (i % 2 ? 8 : -8), 0, (i % 2 ? -4 : 4), 0],
          }}
          transition={{ duration: 1.6, repeat: Infinity, delay: i * 0.05, ease: "easeInOut" }}
          style={{ zIndex: i }}
        >
          <Dorso />
        </motion.div>
      ))}
    </div>
  );
  if (!onFerma) return mazzo;
  return (
    <button type="button" className={stili.mazzoCliccabile} onClick={onFerma} aria-label={t.ferma_mescolata}>
      {mazzo}
    </button>
  );
}

/* Quante carte si mostrano nel taglio: il mazzo disteso, non i 22 o 78 slot
 * veri. Conta il punto del clic, che si trasmette come frazione del mazzo. */
const CARTE_DEL_TAGLIO = 22;

/** Il taglio: si clicca il punto in cui dividere il mazzo. `onTaglia` riceve
 *  la frazione (0–1) dopo che le due metà si sono scambiate di posto. */
export function Taglio({ onTaglia }: { onTaglia: (frazione: number) => void }) {
  const { t } = useLingua();
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(720);
  /* Il punto scelto: da 1 a N−1, il confine fra la carta i−1 e la carta i. */
  const [punto, setPunto] = useState<number | null>(null);
  const [tagliato, setTagliato] = useState<number | null>(null);
  useEffect(() => {
    if (!ref.current) return;
    const o = new ResizeObserver(([e]) => setW(e.contentRect.width));
    o.observe(ref.current);
    return () => o.disconnect();
  }, []);

  const n = CARTE_DEL_TAGLIO;
  const larghezzaCarta = Math.min(96, w / 6);
  const passo = (w - larghezzaCarta) / (n - 1);
  const altezzaCarta = larghezzaCarta * (16 / 9);

  const puntoDa = (clientX: number) => {
    const r = ref.current?.getBoundingClientRect();
    if (!r) return null;
    const x = clientX - r.left - larghezzaCarta / 2 + passo / 2;
    return Math.min(n - 1, Math.max(1, Math.round(x / passo)));
  };

  const taglia = (p: number) => {
    if (tagliato !== null) return;
    setPunto(p);
    setTagliato(p);
    /* Il tempo dell'animazione: poi il server fissa il mazzo tagliato. */
    setTimeout(() => onTaglia(p / n), 1100);
  };

  const tasto = (e: React.KeyboardEvent) => {
    if (tagliato !== null) return;
    if (e.key === "ArrowLeft") setPunto((p) => Math.max(1, (p ?? n / 2) - 1));
    else if (e.key === "ArrowRight") setPunto((p) => Math.min(n - 1, (p ?? n / 2) + 1));
    else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      taglia(punto ?? Math.round(n / 2));
    }
  };

  return (
    <div className={stili.taglio}>
      <div
        ref={ref}
        className={stili.tagliaMazzo}
        style={{ height: altezzaCarta + 24 }}
        role="button"
        tabIndex={0}
        aria-label={`${t.taglia_mazzo}. ${t.taglia_istruzione}`}
        onPointerMove={(e) => tagliato === null && setPunto(puntoDa(e.clientX))}
        onPointerLeave={() => tagliato === null && setPunto(null)}
        onClick={(e) => {
          const p = puntoDa(e.clientX);
          if (p !== null) taglia(p);
        }}
        onKeyDown={tasto}
      >
        {Array.from({ length: n }, (_, i) => {
          const dopo = punto !== null && i >= punto;
          return (
            <motion.div
              key={i}
              className={stili.cartaDelTaglio}
              style={{ width: larghezzaCarta, height: altezzaCarta, left: i * passo, zIndex: i }}
              animate={
                tagliato !== null
                  ? {
                      /* Le carte dopo il punto passano davanti, le altre dietro. */
                      x: i >= tagliato ? -tagliato * passo : (n - tagliato) * passo,
                      y: [0, i >= tagliato ? -28 : 28, 0],
                    }
                  : { x: 0, y: dopo ? -10 : 0 }
              }
              transition={{ duration: tagliato !== null ? 1 : 0.18, ease: "easeInOut" }}
            >
              <Dorso />
            </motion.div>
          );
        })}
        {punto !== null && tagliato === null && (
          <div className={stili.lineaTaglio} style={{ left: punto * passo }} aria-hidden="true">
            <span>✦</span>
          </div>
        )}
      </div>
    </div>
  );
}
