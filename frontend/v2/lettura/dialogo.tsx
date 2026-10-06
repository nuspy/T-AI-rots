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
  battute, attesa, inputAttivo, onRispondi, onBasta, puoiFermarti = false, aggiunta,
}: {
  /** v9.5: «vuoi aggiungere qualcosa?» dopo l'ultima domanda: il campo invia l'aggiunta, accanto «No, basta». */
  aggiunta?: { onSalta: () => void };
  battute: Battuta[];
  attesa: boolean;
  inputAttivo: boolean;
  onRispondi: (testo: string) => void;
  /** «Basta con le domande» (v8.5): chiude l'intervista; attivo solo dopo il minimo di domande. */
  onBasta?: () => void;
  puoiFermarti?: boolean;
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
      <div className={stili.battute} aria-live="polite" ref={contenitore}>
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
        {/* v9.5: dentro la chat, sotto l'ultima domanda dell'oracolo, le due strade ben visibili: rispondere o
         * passare subito alle carte (prima il pulsante stava sotto il campo e si vedeva poco). */}
        {onBasta && puoiFermarti && inputAttivo && !attesa && ultima?.autore === "oracolo" && (
          <div className={stili.sceltaChat} role="group" aria-label={l.basta_domande}>
            <button type="button" className="button button-quiet" onClick={() => campo.current?.focus()}>
              {l.rispondo_domanda}
            </button>
            <button type="button" className="button" onClick={onBasta} data-an="intervista_basta">
              {l.basta_mescola}
            </button>
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
            placeholder={aggiunta ? l.aggiunta_segnaposto : l.risposta_segnaposto}
            aria-label={aggiunta ? l.aggiunta_segnaposto : l.risposta_segnaposto}
            dir="auto" rows={2} maxLength={2000} disabled={attesa}
          />
          {/* Sotto il campo solo l'invio: la scelta di fermarsi sta nella chat (v9.5). */}
          <div className={stili.rispostaAzioni}>
            <button className="button" type="submit" disabled={attesa || !testo.trim()}>
              {aggiunta ? l.aggiunta_invia : l.rispondi}
            </button>
            {aggiunta && (
              <button className="button button-brass" type="button" onClick={aggiunta.onSalta} disabled={attesa}>
                {l.aggiunta_salta}
              </button>
            )}
          </div>
        </form>
      )}
    </div>
  );
}
