"use client";

/* Il ventaglio: tutte le carte, coperte, disposte ad arco.
 *
 * Le carte sono già assegnate agli slot sul server prima che il ventaglio si
 * apra: qui si conoscono solo gli indici. Ogni slot si vede — anche con 78
 * carte — perché l'arco si calcola dalla larghezza disponibile e le carte si
 * sovrappongono quanto basta. Al passaggio del mouse la carta si solleva.
 */

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Dorso } from "../componenti/carta";
import stili from "./leggi.module.css";

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
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(900);
  /* La carta sotto il puntatore sale sopra le vicine: in un ventaglio di 78
   * carte se ne vede solo una striscia, e sollevarla senza portarla davanti
   * la lascerebbe coperta a metà. */
  const [sopra, setSopra] = useState<number | null>(null);
  useEffect(() => {
    if (!ref.current) return;
    const o = new ResizeObserver(([e]) => setW(e.contentRect.width));
    o.observe(ref.current);
    return () => o.disconnect();
  }, []);

  /* La geometria dell'arco. L'apertura cresce col numero di carte; il raggio
   * si ricava dalla corda, così l'arco occupa sempre la larghezza utile. */
  const apertura = quante > 30 ? 118 : 84; // gradi
  const corda = w * 0.92;
  const raggio = corda / 2 / Math.sin(((apertura / 2) * Math.PI) / 180);
  const larghezzaCarta = Math.min(quante > 30 ? 64 : 92, Math.max(30, (corda / quante) * (quante > 30 ? 3.2 : 1.9)));
  const altezzaCarta = larghezzaCarta * (5 / 3);
  const freccia = raggio * (1 - Math.cos(((apertura / 2) * Math.PI) / 180));
  const altezza = freccia + altezzaCarta + 40;

  return (
    <div ref={ref} className={stili.ventaglio} style={{ height: altezza }} aria-label="Ventaglio delle carte">
      {Array.from({ length: quante }, (_, i) => {
        if (scelte.has(i)) return null;
        const angolo = -apertura / 2 + (apertura * i) / Math.max(1, quante - 1);
        return (
          <div
            key={i}
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
              layoutId={`slot-${i}`}
              className={stili.ventaglioCarta}
              disabled={!attivo}
              onClick={() => onScegli(i)}
              aria-label={`Carta ${i + 1}`}
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

/** Il mescolamento: il mazzo si divide e si ricompone, prima del ventaglio. */
export function Mescolamento() {
  return (
    <div className={stili.mescolamento} aria-hidden="true">
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
}
