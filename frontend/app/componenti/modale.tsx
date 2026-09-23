"use client";

/* Le finestre modali: il disclaimer prima della lettura e l'invito ad
 * acquistare crediti. */

import { useEffect } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { useLingua } from "@/lib/lingua";
import stili from "./modale.module.css";

export function Modale({
  aperta,
  titolo,
  onChiudi,
  children,
}: {
  aperta: boolean;
  titolo: string;
  onChiudi?: () => void;
  children: React.ReactNode;
}) {
  useEffect(() => {
    if (!aperta || !onChiudi) return;
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") onChiudi(); };
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [aperta, onChiudi]);

  return (
    <AnimatePresence>
      {aperta && (
        <motion.div className={stili.sfondo} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onClick={onChiudi}>
          <motion.div
            className={`pannello ${stili.finestra}`}
            role="dialog"
            aria-modal="true"
            aria-label={titolo}
            initial={{ y: 30, scale: 0.96, opacity: 0 }}
            animate={{ y: 0, scale: 1, opacity: 1 }}
            exit={{ y: 20, opacity: 0 }}
            transition={{ type: "spring", stiffness: 220, damping: 24 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className={stili.sigillo} aria-hidden="true">✦</div>
            <h2 className={stili.titolo}>{titolo}</h2>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function Disclaimer({
  aperta,
  testo,
  onAccetta,
  onChiudi,
}: {
  aperta: boolean;
  testo: string;
  onAccetta: () => void;
  onChiudi: () => void;
}) {
  const { t } = useLingua();
  return (
    <Modale aperta={aperta} titolo={t.disclaimer_titolo} onChiudi={onChiudi}>
      <p className={`oracolo ${stili.testo}`}>{testo}</p>
      <div className={stili.azioni}>
        <button className="bottone" onClick={onAccetta} autoFocus>{t.accetto}</button>
      </div>
    </Modale>
  );
}

export function Acquisto({
  aperta,
  onChiudi,
  ritorno,
}: {
  aperta: boolean;
  onChiudi: () => void;
  ritorno?: string;
}) {
  const { t } = useLingua();
  const destinazione = ritorno ? `/piano?ritorno=${encodeURIComponent(ritorno)}` : "/piano";
  return (
    <Modale aperta={aperta} titolo={t.crediti_finiti} onChiudi={onChiudi}>
      <p className={stili.testo}>{t.crediti_finiti_testo}</p>
      <div className={stili.azioni}>
        <Link href={destinazione} className="bottone">{t.compra}</Link>
        <button className="bottone-secondario" onClick={onChiudi}>{t.chiudi}</button>
      </div>
    </Modale>
  );
}
