"use client";

/* La dimensione del testo scelta da chi legge (A− / A+ in alto a destra di ogni pagina): dipende dal gusto e dal
 * dispositivo. Cambia la dimensione di base di `<html>`, e con lei tutto ciò che è in rem (quasi tutto il CSS): i
 * testi, e gli spazi che vanno con loro. La testata, misurata in px, resta com'è.
 *
 * Il ricordo sta in localStorage (`CHIAVE_TESTO`: la percentuale). Uno script minimo nel layout la applica prima che
 * la pagina si disegni: niente salti al caricamento. Senza localStorage si torna al 100%. */

import { useEffect, useState } from "react";
import { f } from "@/v2/i18n";
import { useLingua } from "./lingua";
import { BASE_TESTO as BASE, CHIAVE_TESTO, PASSI_TESTO } from "./testo-script";

const valida = (v: unknown): number | null =>
  typeof v === "number" && (PASSI_TESTO as readonly number[]).includes(v) ? v : null;

function leggi(): number {
  try {
    return valida(Number(window.localStorage.getItem(CHIAVE_TESTO))) ?? BASE;
  } catch {
    return BASE;
  }
}

function applica(v: number) {
  document.documentElement.style.fontSize = v === BASE ? "" : `${v}%`;
  try {
    if (v === BASE) window.localStorage.removeItem(CHIAVE_TESTO);
    else window.localStorage.setItem(CHIAVE_TESTO, String(v));
  } catch {
    /* senza localStorage la scelta vale solo per questa pagina */
  }
}

/** A− e A+: due pulsanti da 44 px in alto a destra, sopra il primo contenuto della pagina. */
export function DimensioneTesto() {
  const { t } = useLingua();
  const k = t.comune;
  const [valore, setValore] = useState(BASE);
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { setValore(leggi()); }, []);
  const i = PASSI_TESTO.indexOf(valore as (typeof PASSI_TESTO)[number]);
  const vai = (passo: number) => {
    const nuovo = PASSI_TESTO[Math.min(PASSI_TESTO.length - 1, Math.max(0, i + passo))];
    setValore(nuovo);
    applica(nuovo);
  };
  return (
    <div className="dimensione-testo" role="group" aria-label={k.testo_gruppo}>
      <button type="button" onClick={() => vai(-1)} disabled={i <= 0} aria-label={k.testo_meno} title={k.testo_meno}>
        A<span aria-hidden="true">−</span>
      </button>
      <span className="sr-only" aria-live="polite">{f(k.testo_misura, { n: valore })}</span>
      <button type="button" onClick={() => vai(1)} disabled={i >= PASSI_TESTO.length - 1} aria-label={k.testo_piu} title={k.testo_piu}>
        A<span aria-hidden="true">+</span>
      </button>
    </div>
  );
}
