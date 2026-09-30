"use client";

/* La dichiarazione del rito: mescolare, tagliare e scegliere non sono un'animazione. Sul tavolo c'è un mazzo vero
 * di carte virtuali, e ogni gesto conta. Tutto ciò che dice è vero nel backend (`tarot/shuffle.py`): ordine da un
 * generatore casuale crittografico, taglio applicato al mazzo nel punto toccato, mazzo sigillato (SHA-256 con sale)
 * prima della scelta, sale rivelato a lettura conclusa per la verifica. Interrompere la mescolata decide quando
 * finisce, non l'ordine: il testo non dice di più.
 *
 * Due forme: intera (la home, nella sezione del rito) e breve (la console della lettura). */

import { useLingua } from "@/v2/lib/lingua";

export function Dichiarazione({ breve = false }: { breve?: boolean }) {
  const { t } = useLingua();
  const h = t.home;
  if (breve) {
    return (
      <aside className="declaration-short" aria-label={h.vero_eyebrow}>
        <strong>{h.vero_titolo}</strong>
        <span>{t.lettura.vero_breve}</span>
      </aside>
    );
  }
  return (
    <aside className="declaration" aria-labelledby="dichiarazione-titolo">
      <div className="declaration-head">
        <p className="eyebrow">{h.vero_eyebrow}</p>
        <h3 id="dichiarazione-titolo">{h.vero_titolo}</h3>
        <p>{h.vero_testo}</p>
      </div>
      <ul className="declaration-facts">
        {h.vero_fatti.map((f) => <li key={f.titolo}><b>{f.titolo}</b><span>{f.testo}</span></li>)}
      </ul>
      <p className="declaration-close">{h.vero_chiusa}</p>
    </aside>
  );
}
