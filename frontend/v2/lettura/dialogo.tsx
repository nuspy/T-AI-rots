"use client";

/* La conversazione con il lettore: le domande dell'intervista, le risposte, poi le interpretazioni delle carte man
 * mano che si girano. Si scorre solo dentro il riquadro, mai la pagina (come nel sito): una risposta nuova del
 * lettore si porta in vista dal suo inizio, la propria in fondo. */

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useLingua } from "@/v2/lib/lingua";
import stili from "./lettura.module.css";

export interface Battuta {
  id: string;
  autore: "oracolo" | "utente" | "sistema";
  testo: string;
  titolo?: string;
  /** Le battute nuove del lettore si scrivono a macchina; quelle riprese dallo storico no. */
  macchina?: boolean;
  inCorso?: boolean;
}

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
  battute, attesa, inputAttivo, onRispondi, scelte = [], libero = false, fluido = false,
}: {
  /** v9.5, la lettura in chat: niente riquadro con lo scorrimento interno, la conversazione scorre con la pagina. */
  fluido?: boolean;
  battute: Battuta[];
  attesa: boolean;
  /** Il campo c'è solo quando si risponde a una domanda o si scrive il testo libero (v9.5): durante la scelta no. */
  inputAttivo: boolean;
  onRispondi: (testo: string) => void;
  /** v9.5: i pulsanti in fondo alla chat («Passa alla lettura», «Voglio dire qualcosa di libero», «Voglio
   *  rispondere a un'altra domanda»), già filtrati da chi chiama. */
  scelte?: { etichetta: string; azione: () => void; primaria?: boolean }[];
  /** v9.5: il campo è per il testo libero, non per una risposta. */
  libero?: boolean;
}) {
  const { t } = useLingua();
  const l = t.lettura;
  const [testo, setTesto] = useState("");
  const contenitore = useRef<HTMLDivElement>(null);
  const campo = useRef<HTMLTextAreaElement>(null);
  const ultima = battute[battute.length - 1];

  const inFondo = () => {
    const c = contenitore.current;
    if (c) c.scrollTo({ top: c.scrollHeight, behavior: "smooth" });
  };

  useEffect(() => {
    if (!ultima) return;
    if (ultima.autore === "utente") { inFondo(); return; }
    const c = contenitore.current;
    const el = c?.querySelector<HTMLElement>(`[data-battuta="${CSS.escape(ultima.id)}"]`);
    if (!c || !el) return;
    const obiettivo = Math.max(0, el.offsetTop - 12);
    c.scrollTo({ top: obiettivo, behavior: "smooth" });
    /* Il testo cresce dopo lo scorrimento (macchina, streaming): si continua ad avvicinarne l'inizio alla cima,
     * finché non ci arriva o finché chi legge non scorre da sé. */
    const osservatore = new ResizeObserver(() => {
      if (c.scrollTop >= obiettivo - 1) { smetti(); return; }
      c.scrollTop = Math.min(obiettivo, c.scrollHeight - c.clientHeight);
    });
    const smetti = () => {
      osservatore.disconnect();
      c.removeEventListener("wheel", smetti);
      c.removeEventListener("touchstart", smetti);
    };
    osservatore.observe(el);
    c.addEventListener("wheel", smetti, { passive: true });
    c.addEventListener("touchstart", smetti, { passive: true });
    return smetti;
  }, [ultima?.id, ultima?.autore]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { if (attesa) inFondo(); }, [attesa]);

  const invia = () => {
    const pulito = testo.trim();
    if (!pulito) return;
    setTesto("");
    onRispondi(pulito);
  };

  return (
    <div className={stili.dialogo}>
      <div className={`${stili.battute} ${fluido ? stili.battuteFluide : ""}`} aria-live="polite" ref={contenitore}>
        <AnimatePresence initial={false}>
          {battute.map((b) => (
            <motion.div
              key={b.id}
              data-battuta={b.id}
              className={`${stili.battuta} ${b.autore === "utente" ? stili.battutaUtente : b.autore === "sistema" ? stili.battutaSistema : stili.battutaOracolo}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <span className={stili.autore}>
                {b.titolo ?? (b.autore === "utente" ? l.tu : b.autore === "oracolo" ? l.lettore : l.sistema)}
              </span>
              <p dir="auto">
                {b.macchina ? <Macchina testo={b.testo} /> : b.testo}
                {b.inCorso && <span className={stili.cursore}>▍</span>}
              </p>
            </motion.div>
          ))}
        </AnimatePresence>
        {attesa && <div className={stili.attesa} aria-label={l.pensa} role="status"><span /><span /><span /></div>}
        {/* v9.5: le scelte stanno dentro la chat, in fondo alla conversazione, ben visibili. */}
        {!attesa && scelte.length > 0 && (
          <div className={stili.sceltaChat} role="group" aria-label={l.scelta_titolo}>
            {scelte.map((s) => (
              <button key={s.etichetta} type="button" className={s.primaria ? "button button-brass" : "button button-quiet"}
                onClick={s.azione}>
                {s.etichetta}
              </button>
            ))}
          </div>
        )}
      </div>
      {inputAttivo && (
        <form className={stili.risposta} onSubmit={(e) => { e.preventDefault(); invia(); }}>
          <textarea
            ref={campo}
            value={testo}
            onChange={(e) => setTesto(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); invia(); } }}
            placeholder={libero ? l.libero_segnaposto : l.risposta_segnaposto}
            aria-label={libero ? l.libero_segnaposto : l.risposta_segnaposto}
            dir="auto" rows={2} maxLength={2000} disabled={attesa}
            autoFocus={libero}
          />
          {/* Sotto il campo solo l'invio: le scelte stanno nella chat (v9.5). */}
          <div className={stili.rispostaAzioni}>
            <button className="button" type="submit" disabled={attesa || !testo.trim()}>
              {libero ? l.libero_invia : l.rispondi}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
