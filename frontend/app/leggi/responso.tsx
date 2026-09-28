"use client";

/* Il responso finale, le sue fasi, e ciò che se ne può fare dopo: condividerlo
 * (il pannello compone l'immagine e dà il link) o cominciare una nuova lettura. */

import { useCallback, useState } from "react";
import Link from "@/app/componenti/link";
import { AnimatePresence, motion } from "framer-motion";
import { useLingua } from "@/lib/lingua";
import { Markdown } from "../componenti/markdown";
import { PannelloCondivisione } from "./pannello-condivisione";
import stili from "./leggi.module.css";

export function FaseResponso({ fase }: { fase: string }) {
  const { t } = useLingua();
  const testi: Record<string, string> = {
    unione: t.fase_unione,
    guardia: t.fase_guardia,
    revisione: t.fase_revisione,
  };
  return (
    <div className={stili.fase}>
      <motion.div
        className={stili.sigilloRotante}
        animate={{ rotate: 360 }}
        transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
        aria-hidden="true"
      >
        <svg viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="46" fill="none" stroke="#d8b45a" strokeOpacity="0.5" />
          <circle cx="50" cy="50" r="38" fill="none" stroke="#b9a4ff" strokeOpacity="0.35" strokeDasharray="2 4" />
          <path d="M50 12 L83 69 L17 69 Z M50 88 L17 31 L83 31 Z" fill="none" stroke="#f1d68e" strokeWidth="1.4" />
        </svg>
      </motion.div>
      <AnimatePresence mode="wait">
        <motion.p key={fase} className="oracolo" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}>
          {testi[fase] ?? t.fase_unione}
        </motion.p>
      </AnimatePresence>
    </div>
  );
}

export function Responso({
  id,
  testo,
  finito,
  disclaimer,
  commitment,
  saldo,
  onNuova,
  anonimo = false,
  onRegistrati,
}: {
  id: string;
  testo: string;
  finito: boolean;
  disclaimer: string;
  commitment: string | null;
  saldo: number | null;
  onNuova: () => void;
  /* v6, Fase F: vero per un visitatore anonimo — `testo` è l'anteprima, non il responso vero, e
   * condividere o vedere il mazzo non hanno senso finché la lettura non è sua. */
  anonimo?: boolean;
  onRegistrati?: () => void;
}) {
  const { t } = useLingua();
  const [condividendo, setCondividendo] = useState(false);
  const chiudi = useCallback(() => setCondividendo(false), []);
  const nessunaAzione = useCallback(() => undefined, []);

  return (
    <motion.section
      className={`pannello ${stili.responso}`}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      aria-live="polite"
    >
      <h2 className={stili.responsoTitolo}>✦ {anonimo ? t.anteprima_titolo : t.il_responso} ✦</h2>
      <Markdown testo={testo} className={`oracolo ${stili.responsoTesto}`} />
      {finito && anonimo && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <div className={stili.azioniCentro}>
            <button className="bottone" onClick={onRegistrati}>{t.anteprima_registrati}</button>
          </div>
        </motion.div>
      )}
      {finito && !anonimo && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <p className={stili.disclaimerFinale}>{disclaimer}</p>
          {commitment && (
            <details className={stili.verifica}>
              <summary>{t.verifica_mazzo}</summary>
              <p>{t.verifica_testo}</p>
              <code>{commitment}</code>
            </details>
          )}
          <div className={stili.azioniCentro}>
            <button className="bottone" onClick={() => setCondividendo(true)}>{t.condividi}</button>
            <button className="bottone-secondario" onClick={onNuova}>{t.nuova_lettura}</button>
          </div>
          {saldo === 0 && (
            <p className={stili.avviso}>
              {t.crediti_finiti}. <Link href="/piano">{t.compra}</Link>
            </p>
          )}
          <PannelloCondivisione id={id} aperta={condividendo} onChiudi={chiudi} onLink={nessunaAzione} />
        </motion.div>
      )}
    </motion.section>
  );
}
