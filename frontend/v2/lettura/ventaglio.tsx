"use client";

/* Il mazzo della v2: la mescolata che si interrompe, il taglio, il ventaglio. La geometria è quella del sito
 * (`app/(sito)/leggi/ventaglio.tsx`): archi di al più 26 carte, il taglio come frazione del mazzo, gli slot già
 * assegnati dal server prima che il ventaglio si apra. Cambiano l'abito e i testi. */

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { f } from "@/v2/i18n";
import { Dorso } from "@/v2/componenti/carta";
import { useLingua } from "@/v2/lib/lingua";
import { useMenoMovimento } from "@/v2/lib/usa";
import stili from "./lettura.module.css";

const CARTE_PER_ARCO = 26;

export function Ventaglio({
  quante, scelte, attivo, onScegli,
}: {
  quante: number;
  scelte: Set<number>;
  attivo: boolean;
  onScegli: (slot: number) => void;
}) {
  const { t } = useLingua();
  const gruppi = Math.max(1, Math.ceil(quante / CARTE_PER_ARCO));
  return (
    <div className={stili.ventaglioGruppi} role="group" aria-label={t.lettura.ventaglio_aria}>
      {Array.from({ length: gruppi }, (_, g) => {
        const inizio = g * CARTE_PER_ARCO;
        const fine = Math.min(quante, inizio + CARTE_PER_ARCO);
        return <Arco key={g} inizio={inizio} quante={fine - inizio} scelte={scelte} attivo={attivo} onScegli={onScegli} />;
      })}
    </div>
  );
}

function Arco({
  inizio, quante, scelte, attivo, onScegli,
}: {
  inizio: number;
  quante: number;
  scelte: Set<number>;
  attivo: boolean;
  onScegli: (slot: number) => void;
}) {
  const { t } = useLingua();
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(640);
  const [sopra, setSopra] = useState<number | null>(null);
  useEffect(() => {
    if (!ref.current) return;
    const o = new ResizeObserver(([e]) => setW(e.contentRect.width));
    o.observe(ref.current);
    return () => o.disconnect();
  }, []);

  const apertura = quante > 30 ? 118 : 84;
  const corda = w * 0.92;
  const raggio = corda / 2 / Math.sin(((apertura / 2) * Math.PI) / 180);
  const larghezzaCarta = Math.min(quante > 30 ? 64 : 88, Math.max(30, (corda / quante) * (quante > 30 ? 3.2 : 1.9)));
  const altezzaCarta = larghezzaCarta * (16 / 9);
  const freccia = raggio * (1 - Math.cos(((apertura / 2) * Math.PI) / 180));

  return (
    <div ref={ref} className={stili.ventaglio} style={{ height: freccia + altezzaCarta + 40 }}>
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
              type="button"
              layoutId={`slot-${slot}`}
              className={stili.ventaglioCarta}
              disabled={!attivo}
              onClick={() => onScegli(slot)}
              onFocus={() => setSopra(i)}
              aria-label={f(t.lettura.carta_n, { n: slot + 1 })}
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

/** La mescolata: il mazzo si divide e si ricompone finché non lo si tocca. */
/* La mescolata parte da sola a intervista finita (9/10) e dura finché chi consulta non la ferma. Con «meno movimento»
 * le carte non volano: il mazzo resta raccolto e respira appena (solo opacità, lenta), e l'istruzione sopra dice di
 * fermarlo come sempre. */
export function Mescolamento({ onFerma }: { onFerma: () => void }) {
  const { t } = useLingua();
  const meno = useMenoMovimento();
  return (
    <button type="button" className={stili.mazzoCliccabile} onClick={onFerma} aria-label={t.lettura.ferma}
      data-an="rito" data-an-passo="shuffle_interrupted">
      <div className={stili.mescolamento}>
        {Array.from({ length: 9 }, (_, i) => (
          <motion.div
            key={i}
            className={stili.mazzettoCarta}
            animate={meno ? {
              x: (i % 3 - 1) * 3, y: -i * 1.2, rotate: (i % 2 ? 1 : -1) * (i % 4),
              opacity: i === 8 ? [1, .82, 1] : 1,
            } : {
              x: [0, (i % 2 ? 1 : -1) * (46 + i * 5), 0, (i % 2 ? -1 : 1) * 28, 0],
              y: [0, -i * 2, i * 1.5, -i, 0],
              rotate: [0, i % 2 ? 8 : -8, 0, i % 2 ? -4 : 4, 0],
            }}
            transition={meno
              ? { duration: 3.2, repeat: Infinity, ease: "easeInOut" }
              : { duration: 1.6, repeat: Infinity, delay: i * 0.05, ease: "easeInOut" }}
            style={{ zIndex: i }}
          >
            <Dorso />
          </motion.div>
        ))}
      </div>
    </button>
  );
}

const CARTE_DEL_TAGLIO = 22;

/** Il taglio: si sceglie il punto in cui dividere il mazzo; `onTaglia` riceve la frazione (0–1) dopo che le due
 *  metà si sono scambiate di posto. Da tastiera: frecce e Invio. */
export function Taglio({ onTaglia }: { onTaglia: (frazione: number) => void }) {
  const { t } = useLingua();
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(640);
  const [punto, setPunto] = useState<number | null>(null);
  const [tagliato, setTagliato] = useState<number | null>(null);
  useEffect(() => {
    if (!ref.current) return;
    const o = new ResizeObserver(([e]) => setW(e.contentRect.width));
    o.observe(ref.current);
    return () => o.disconnect();
  }, []);

  const n = CARTE_DEL_TAGLIO;
  const larghezzaCarta = Math.min(88, w / 6);
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
        aria-label={t.lettura.taglio_aria}
        onPointerMove={(e) => tagliato === null && setPunto(puntoDa(e.clientX))}
        onPointerLeave={() => tagliato === null && setPunto(null)}
        onClick={(e) => {
          const p = puntoDa(e.clientX);
          if (p !== null) taglia(p);
        }}
        onKeyDown={tasto}
      >
        {Array.from({ length: n }, (_, i) => (
          <motion.div
            key={i}
            className={stili.cartaDelTaglio}
            style={{ width: larghezzaCarta, height: altezzaCarta, left: i * passo, zIndex: i }}
            animate={
              tagliato !== null
                ? { x: i >= tagliato ? -tagliato * passo : (n - tagliato) * passo, y: [0, i >= tagliato ? -28 : 28, 0] }
                : { x: 0, y: punto !== null && i >= punto ? -10 : 0 }
            }
            transition={{ duration: tagliato !== null ? 1 : 0.18, ease: "easeInOut" }}
          >
            <Dorso />
          </motion.div>
        ))}
        {punto !== null && tagliato === null && (
          <div className={stili.lineaTaglio} style={{ left: punto * passo }} aria-hidden="true"><span>✦</span></div>
        )}
      </div>
    </div>
  );
}
