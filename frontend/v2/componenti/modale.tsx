"use client";

/* Il dialogo della v2: sfondo prugna velato, carta chiara, bordo d'ottone. Esc chiude, il fuoco entra nel
 * dialogo all'apertura e torna dov'era alla chiusura; lo scorrimento della pagina si ferma finché è aperto. */

import { useEffect, useId, useRef } from "react";
import { useLingua } from "@/v2/lib/lingua";

export function Modale({
  aperta, titolo, onChiudi, children, larga = false, scura = false,
}: {
  aperta: boolean;
  titolo: string;
  onChiudi: () => void;
  children: React.ReactNode;
  /** Per contenuti ampi (le carte di un mazzo): quasi tutta la larghezza dello schermo. */
  larga?: boolean;
  /** Il fondo prugna del rito (v8.5): le fasi del rito, sul telefono, si aprono in un dialogo. */
  scura?: boolean;
}) {
  const { t } = useLingua();
  const id = useId();
  const riquadro = useRef<HTMLDivElement>(null);
  /* In un ref: chi apre il dialogo passa spesso una funzione nuova a ogni rendering, e l'effetto non deve
   * ripartire (riportando il fuoco al primo pulsante) a ogni lettera scritta in un campo. */
  const chiudiRef = useRef(onChiudi);
  useEffect(() => { chiudiRef.current = onChiudi; }, [onChiudi]);

  useEffect(() => {
    if (!aperta) return;
    const prima = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const primo = riquadro.current?.querySelector<HTMLElement>("[autofocus], button, a, input, textarea, select");
    (primo ?? riquadro.current)?.focus();
    const tasto = (e: KeyboardEvent) => {
      if (e.key === "Escape") chiudiRef.current();
      if (e.key !== "Tab" || !riquadro.current) return;
      const focabili = [...riquadro.current.querySelectorAll<HTMLElement>(
        "button:not([disabled]), a[href], input:not([disabled]), textarea:not([disabled]), select:not([disabled])",
      )];
      if (!focabili.length) return;
      const [a, z] = [focabili[0], focabili[focabili.length - 1]];
      if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
      else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    };
    document.addEventListener("keydown", tasto);
    return () => {
      document.removeEventListener("keydown", tasto);
      document.body.style.overflow = overflow;
      prima?.focus?.();
    };
  }, [aperta]);

  if (!aperta) return null;
  return (
    <div className="dialog-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onChiudi(); }}>
      <div className={`dialog${larga ? " dialog-wide" : ""}${scura ? " dialog-scuro" : ""}`} role="dialog" aria-modal="true" aria-labelledby={id} ref={riquadro} tabIndex={-1}>
        <button type="button" className="dialog-close" aria-label={t.comune.chiudi} onClick={onChiudi}>✕</button>
        <h2 id={id}>{titolo}</h2>
        {children}
      </div>
    </div>
  );
}
