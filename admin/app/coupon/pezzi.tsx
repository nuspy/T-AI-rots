"use client";

/* Pezzi comuni alle tre schede dei coupon (v9, Fase 2d): copiare un codice o un link, le cifre del resoconto, le date
 * «a giorno». */

import { useState } from "react";
import { soldi } from "@/lib/formato";
import type { Coupon, Resoconto } from "@/lib/offerte";
import stili from "./coupon.module.css";

/* Una data «a giorno» → l'istante ISO: l'inizio del giorno per «dal», la fine per «fino». */
export const inizioGiorno = (d: string) => (d ? new Date(`${d}T00:00:00`).toISOString() : null);
export const fineGiorno = (d: string) => (d ? new Date(`${d}T23:59:59`).toISOString() : null);

export function validita(c: Pick<Coupon, "valido_dal" | "valido_fino">): string {
  const dal = c.valido_dal ? new Date(c.valido_dal).toLocaleDateString("it-IT") : null;
  const fino = c.valido_fino ? new Date(c.valido_fino).toLocaleDateString("it-IT") : null;
  if (dal && fino) return `${dal} – ${fino}`;
  if (fino) return `fino al ${fino}`;
  if (dal) return `dal ${dal}`;
  return "sempre";
}

/** Copia un testo negli appunti e lo dice (il bottone cambia scritta: mai solo un colore). */
export function Copia({ testo, etichetta, descrizione }: { testo: string; etichetta: string; descrizione: string }) {
  const [copiato, setCopiato] = useState(false);
  const copia = async () => {
    try {
      await navigator.clipboard.writeText(testo);
      setCopiato(true);
      window.setTimeout(() => setCopiato(false), 2500);
    } catch {
      setCopiato(false);
    }
  };
  return (
    <button type="button" className={stili.copia} onClick={copia} aria-label={descrizione} title={testo}>
      <span aria-live="polite">{copiato ? "Copiato ✓" : etichetta}</span>
    </button>
  );
}

/** Le cifre del resoconto, compatte (la scheda di un coupon, la riga di una campagna). */
export function CifreResoconto({ r }: { r: Resoconto }) {
  return (
    <dl className={stili.cifre}>
      <div><dt>Riscatti</dt><dd>{r.riscatti}</dd></div>
      <div><dt>Incasso lordo</dt><dd>{soldi(r.incasso_lordo)}</dd></div>
      <div><dt>Sconto concesso</dt><dd>{soldi(r.sconto_concesso)}</dd></div>
      <div><dt>Nuovi utenti</dt><dd>{r.nuovi_utenti}</dd></div>
      <div><dt>Prove → pagate</dt><dd>{r.prove} → {r.conversioni_da_prova}</dd></div>
      {r.crediti_regalati > 0 && <div><dt>Crediti regalati</dt><dd>{r.crediti_regalati}</dd></div>}
    </dl>
  );
}
