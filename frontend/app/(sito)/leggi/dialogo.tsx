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
  const pannello = useRef<HTMLDivElement>(null);
  const contenitore = useRef<HTMLDivElement>(null);
  const ultima = battute[battute.length - 1];

  const inFondo = () => {
    const c = contenitore.current;
    if (c) c.scrollTo({ top: c.scrollHeight, behavior: "smooth" });
  };

  /* Si scorre solo quando arriva una battuta NUOVA (non a ogni lettera che si aggiunge mentre
   * l'oracolo scrive): una risposta dell'oracolo si porta in vista dal suo inizio, così si legge
   * dall'alto invece di essere spinti in fondo; la propria risposta, in fondo.
   *
   * Si scorre SOLO il contenitore del dialogo, non la pagina: un `scrollIntoView` annidato
   * (contenitore + finestra) faceva saltare la pagina in modo imprevedibile, perché il campo di
   * risposta sparisce e ricompare mentre l'oracolo pensa, e l'ultima battuta finiva sotto la barra
   * di navigazione mobile. Alla pagina si chiede solo di tenere il pannello intero in vista. */
  useEffect(() => {
    if (!ultima) return;
    pannello.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    if (ultima.autore === "utente") {
      inFondo();
      return;
    }
    const c = contenitore.current;
    const elemento = c?.querySelector<HTMLElement>(`[data-battuta="${CSS.escape(ultima.id)}"]`);
    if (!c || !elemento) return;
    // `.battute` è `position: relative`: `offsetTop` è già relativo al contenitore.
    const obiettivo = Math.max(0, elemento.offsetTop - 12);
    c.scrollTo({ top: obiettivo, behavior: "smooth" });

    /* L'oracolo scrive a macchina (o in streaming): il testo cresce DOPO lo scorrimento, e
     * `scrollTo` si ferma al massimo di quel momento — con una risposta lunga se ne vedrebbe solo
     * la prima riga in fondo al riquadro. Man mano che cresce si continua ad avvicinarne l'inizio
     * alla cima; ci si ferma quando è arrivato, o appena chi legge scorre da sé. */
    const osservatore = new ResizeObserver(() => {
      if (c.scrollTop >= obiettivo - 1) { smetti(); return; }
      c.scrollTop = Math.min(obiettivo, c.scrollHeight - c.clientHeight);
    });
    const smetti = () => {
      osservatore.disconnect();
      c.removeEventListener("wheel", smetti);
      c.removeEventListener("touchstart", smetti);
    };
    osservatore.observe(elemento);
    c.addEventListener("wheel", smetti, { passive: true });
    c.addEventListener("touchstart", smetti, { passive: true });
    return smetti;
  }, [ultima?.id, ultima?.autore]); // eslint-disable-line react-hooks/exhaustive-deps

  // I puntini "l'oracolo sta pensando" si mostrano in fondo, dopo la propria risposta.
  useEffect(() => {
    if (attesa) inFondo();
  }, [attesa]);

  const invia = () => {
    const pulito = testo.trim();
    if (!pulito) return;
    setTesto("");
    onRispondi(pulito);
  };

  return (
    <div className={`pannello ${stili.dialogo}`} ref={pannello}>
      <div className={stili.battute} aria-live="polite" ref={contenitore}>
        <AnimatePresence initial={false}>
          {battute.map((b) => (
            <motion.div
              key={b.id}
              data-battuta={b.id}
              className={b.autore === "utente" ? stili.battutaUtente : b.autore === "sistema" ? stili.battutaSistema : stili.battutaOracolo}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35 }}
            >
              <span className={stili.autore}>
                {b.titolo ?? (b.autore === "utente" ? t.tu : b.autore === "oracolo" ? t.oracolo : "✦")}
              </span>
              <p className={b.autore === "utente" ? undefined : "oracolo"} dir="auto">
                {b.macchina ? <Macchina testo={b.testo} /> : b.testo}
                {b.inCorso && <span className={stili.cursore}>▍</span>}
              </p>
            </motion.div>
          ))}
        </AnimatePresence>
        {attesa && (
          <div className={stili.attesaOracolo} aria-label={t.oracolo_pensa}>
            <span /><span /><span />
          </div>
        )}
      </div>
      {inputAttivo && (
        <form className={stili.risposta} onSubmit={(e) => { e.preventDefault(); invia(); }}>
          <textarea
            value={testo}
            onChange={(e) => setTesto(e.target.value)}
            placeholder={segnaposto ?? t.risposta_segnaposto}
            dir="auto"
            rows={2}
            maxLength={2000}
            disabled={attesa}
            aria-label={t.risposta_segnaposto}
          />
          <button className="bottone" type="submit" disabled={attesa || !testo.trim()}>{t.rispondi}</button>
        </form>
      )}
    </div>
  );
}
