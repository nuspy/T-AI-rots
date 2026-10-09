"use client";

/* L'interpretazione finale: le sue fasi mentre arriva, il testo, e ciò che se ne fa dopo. Chi non ha un account
 * vede una prima risposta e l'invito a tenere la lettura intera (la registrazione arriva dopo il valore, non
 * prima: specifica v2, §5-6). Chi è dentro condivide, verifica il mazzo, torna alla sua storia. */

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Markdown } from "@/lib/markdown";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { PulsanteStampa } from "@/v2/componenti/stampa";
import { PannelloCondivisione } from "./condivisione";
import stili from "./lettura.module.css";

export function FaseResponso({ fase }: { fase: string }) {
  const { t } = useLingua();
  const testi = t.lettura.fasi;
  return (
    <div className={stili.fase} role="status">
      <motion.svg className={stili.sigillo} viewBox="0 0 100 100" aria-hidden="true"
        animate={{ rotate: 360 }} transition={{ duration: 14, repeat: Infinity, ease: "linear" }}>
        <circle cx="50" cy="50" r="46" fill="none" stroke="#b28336" strokeOpacity=".6" />
        <circle cx="50" cy="50" r="38" fill="none" stroke="#19706f" strokeOpacity=".5" strokeDasharray="2 4" />
        <path d="M50 12 L83 69 L17 69 Z M50 88 L17 31 L83 31 Z" fill="none" stroke="#3c1846" strokeWidth="1.3" />
      </motion.svg>
      <AnimatePresence mode="wait">
        <motion.p key={fase} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}>
          {testi[fase] ?? testi.unione}
        </motion.p>
      </AnimatePresence>
    </div>
  );
}

export function Responso({
  id, testo, finito, inCorso = false, nota = null, disclaimer, commitment, saldo, anonimo, omaggi, onNuova, onRegistrati,
}: {
  id: string;
  testo: string;
  finito: boolean;
  /** Il testo sta ancora arrivando (9/10, in diretta): il cursore in fondo, e la chat lo segue. */
  inCorso?: boolean;
  /** Una nota discreta sotto il testo mentre lo si controlla (`guardia`, `revisione`): il testo resta in vista. */
  nota?: string | null;
  disclaimer: string;
  commitment: string | null;
  saldo: number | null;
  /** Visitatore senza account: `testo` è l'anteprima, non l'interpretazione intera. */
  anonimo: boolean;
  omaggi: number;
  onNuova: () => void;
  onRegistrati: () => void;
}) {
  const { t } = useLingua();
  const l = t.lettura;
  const [condividendo, setCondividendo] = useState(false);

  return (
    <motion.section className={stili.responso} initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }} aria-live="polite" aria-busy={inCorso} aria-labelledby="titolo-responso">
      <p className="eyebrow">✦</p>
      <h2 id="titolo-responso">{anonimo ? l.anteprima_titolo : l.il_responso}</h2>
      <div data-in-scrittura={inCorso ? "testo" : undefined}>
        <Markdown testo={testo} className={stili.testo} />
        {inCorso && <span className={`${stili.cursore} ${stili.cursoreResponso}`} aria-hidden="true">▍</span>}
      </div>
      {nota && (
        <p className={stili.notaControllo} role="status">
          <span className={stili.lettoreLeggePunti} aria-hidden="true"><i /><i /><i /></span>
          {nota}
        </p>
      )}

      {finito && anonimo && (
        <div className={stili.anteprima}>
          <p>{l.anteprima_testo}</p>
          <p>{f(l.anteprima_extra, { n: omaggi })}</p>
          <button type="button" className="button button-brass" onClick={onRegistrati}
            data-an="cta_iscrizione" data-an-dove="anteprima">
            {l.anteprima_cta}
          </button>
        </div>
      )}

      {finito && !anonimo && (
        <>
          <p className={stili.avvertenza}>{disclaimer}</p>
          {commitment && (
            <details className={stili.verifica}>
              <summary>{l.verifica}</summary>
              <p>{l.verifica_testo}</p>
              <code>{commitment}</code>
            </details>
          )}
          <div className="button-row" style={{ marginTop: ".5rem" }}>
            <button type="button" className="button" onClick={() => setCondividendo(true)} data-an="share_started">{l.condividi}</button>
            <LinkV2 className="button button-quiet" href={R.lettura(id)}>{l.vai_storia}</LinkV2>
            <PulsanteStampa etichetta={l.stampa_pdf} />
            <button type="button" className="button button-quiet" onClick={onNuova}>{l.nuova}</button>
          </div>
          {saldo === 0 && (
            <p className="notice">
              {l.crediti_finiti}. <LinkV2 className="inline" href={R.prezzi}>{l.vedi_prezzi}</LinkV2>
            </p>
          )}
          <PannelloCondivisione id={id} aperta={condividendo} onChiudi={() => setCondividendo(false)} />
        </>
      )}
    </motion.section>
  );
}
