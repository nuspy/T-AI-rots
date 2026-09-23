"use client";

/* Il dialogo con l'oracolo: domande dell'intervista, risposte, e poi le
 * interpretazioni delle carte man mano che si girano. */

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useLingua } from "@/lib/lingua";
import stili from "./leggi.module.css";

export interface Battuta {
  id: string;
  autore: "oracolo" | "utente" | "sistema";
  testo: string;
  titolo?: string;
  /* Le battute nuove dell'oracolo si scrivono a macchina; quelle ricaricate
   * dallo storico no. */
  macchina?: boolean;
  inCorso?: boolean;
}

/** Scrive il testo una lettera per volta, come una penna. */
function Macchina({ testo }: { testo: string }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    if (n >= testo.length) return;
    const passo = setTimeout(() => setN((k) => Math.min(testo.length, k + 2)), 18);
    return () => clearTimeout(passo);
  }, [n, testo]);
  return <>{testo.slice(0, n)}{n < testo.length && <span className={stili.cursore}>▍</span>}</>;
}

export function Dialogo({
  battute,
  attesa,
  inputAttivo,
  onRispondi,
  segnaposto,
}: {
  battute: Battuta[];
  attesa: boolean;
  inputAttivo: boolean;
  onRispondi: (testo: string) => void;
  segnaposto?: string;
}) {
  const { t } = useLingua();
  const [testo, setTesto] = useState("");
  const fondo = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fondo.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [battute, attesa]);

  const invia = () => {
    const pulito = testo.trim();
    if (!pulito) return;
    setTesto("");
    onRispondi(pulito);
  };

  return (
    <div className={`pannello ${stili.dialogo}`}>
      <div className={stili.battute} aria-live="polite">
        <AnimatePresence initial={false}>
          {battute.map((b) => (
            <motion.div
              key={b.id}
              className={b.autore === "utente" ? stili.battutaUtente : b.autore === "sistema" ? stili.battutaSistema : stili.battutaOracolo}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}
            >
              <span className={stili.autore}>
                {b.titolo ?? (b.autore === "utente" ? t.tu : b.autore === "oracolo" ? t.oracolo : "✦")}
              </span>
              <p className={b.autore === "utente" ? undefined : "oracolo"}>
                {b.macchina ? <Macchina testo={b.testo} /> : b.testo}
                {b.inCorso && <span className={stili.cursore}>▍</span>}
              </p>
            </motion.div>
          ))}
        </AnimatePresence>
        {attesa && (
          <div className={stili.attesaOracolo} aria-label="L'oracolo sta pensando">
            <span /><span /><span />
          </div>
        )}
        <div ref={fondo} />
      </div>
      {inputAttivo && (
        <form className={stili.risposta} onSubmit={(e) => { e.preventDefault(); invia(); }}>
          <textarea
            value={testo}
            onChange={(e) => setTesto(e.target.value)}
            placeholder={segnaposto ?? t.risposta_segnaposto}
            rows={2}
            maxLength={2000}
            disabled={attesa}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); invia(); }
            }}
            aria-label={t.risposta_segnaposto}
          />
          <button className="bottone" type="submit" disabled={attesa || !testo.trim()}>{t.rispondi}</button>
        </form>
      )}
    </div>
  );
}
