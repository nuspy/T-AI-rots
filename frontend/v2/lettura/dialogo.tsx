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

/** Un pulsante sotto il campo dell'intervista: manda il testo scritto e dice cosa viene dopo («Invia, basta con le
 *  domande», «Invia e fammi un'altra domanda», «Invia e voglio dire una cosa»). Con il campo vuoto vale
 *  `etichettaVuoto` («Saltiamo, basta con le domande»…), e la scritta torna com'era appena si scrive; se manca, il
 *  pulsante aspetta che si scriva qualcosa. `primaria`: quello di Ctrl+Invio (non cambia l'aspetto: dal 9/10 i
 *  pulsanti hanno tutti lo stesso peso). */
export interface Invio {
  chiave: string;
  etichetta: string;
  etichettaVuoto?: string;
  primaria?: boolean;
  onInvia: (testo: string) => void;
}

export function Dialogo({
  battute, attesa, inputAttivo, invii = [], libero = false, fluido = false, fuocoLibero = 0,
}: {
  /** Cresce quando il campo passa al testo libero per un gesto («voglio dire…»): il fuoco va nel campo. */
  fuocoLibero?: number;
  /** v9.5, la lettura in chat: niente riquadro con lo scorrimento interno, la conversazione scorre con la pagina. */
  fluido?: boolean;
  battute: Battuta[];
  attesa: boolean;
  /** Il campo c'è per tutta l'intervista, finché non si passa alle carte. */
  inputAttivo: boolean;
  /** I pulsanti sotto il campo, già scelti da chi chiama (sempre visibili, dalla prima domanda). */
  invii?: Invio[];
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

  /* «Voglio dire…» a campo vuoto: il campo diventa per il testo libero e lo si porta sotto le dita. */
  useEffect(() => {
    if (fuocoLibero > 0) campo.current?.focus();
  }, [fuocoLibero]);

  const pulito = testo.trim();
  const usabile = (i: Invio) => !attesa && (!!pulito || i.etichettaVuoto !== undefined);
  const invia = (i: Invio | undefined) => {
    if (!i || !usabile(i)) return;
    setTesto("");
    i.onInvia(pulito);
  };
  /* Ctrl+Invio: il pulsante principale («basta»), se si può usare; altrimenti il primo che si può usare. Solo con un
   * testo scritto: a campo vuoto i pulsanti saltano la domanda, e un salto si chiede col dito, non per sbaglio. */
  const predefinito = () => (pulito ? invii.find((i) => i.primaria && usabile(i)) ?? invii.find(usabile) : undefined);

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
      </div>
      {inputAttivo && (
        <form className={stili.risposta} onSubmit={(e) => { e.preventDefault(); invia(predefinito()); }}>
          <textarea
            ref={campo}
            value={testo}
            onChange={(e) => setTesto(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); invia(predefinito()); } }}
            placeholder={libero ? l.libero_segnaposto : l.risposta_segnaposto}
            aria-label={libero ? l.libero_segnaposto : l.risposta_segnaposto}
            dir="auto" rows={2} maxLength={2000} disabled={attesa}
            autoFocus={libero}
          />
          {/* I tre invii, sempre visibili sotto il campo: ognuno manda il testo e dice cosa viene dopo. Stesso
            * aspetto per tutti (pieni, prugna): sono tre scelte di pari dignità, nessuna sembra una scritta. */}
          <div className={stili.rispostaInvii} role="group" aria-label={l.scelta_titolo}>
            {invii.map((i) => (
              <button key={i.chiave} type="button" disabled={!usabile(i)}
                className="button"
                data-an={`intervista_${i.chiave}`}
                onClick={() => invia(i)}>
                {!pulito && i.etichettaVuoto !== undefined ? i.etichettaVuoto : i.etichetta}
              </button>
            ))}
          </div>
        </form>
      )}
    </div>
  );
}
