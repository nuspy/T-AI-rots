"use client";

/* Adesso (v8): chi c'è sul sito in questo momento — sessioni attive negli ultimi 5 minuti, cosa stanno
 * guardando, da dove arrivano — e le pagine viste minuto per minuto nell'ultima mezz'ora.
 * Si aggiorna da sola ogni 15 secondi, solo mentre la scheda è visibile. */

import { useEffect } from "react";
import { tempoReale } from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Barre, Colonne, Tessera } from "../../grafici";
import grafici from "../../grafici.module.css";
import stili from "../../statistiche.module.css";

const ora = new Intl.DateTimeFormat("it-IT", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Rome" });

export default function Adesso() {
  const dati = useDati(tempoReale);
  const { ricarica } = dati;

  useEffect(() => {
    const giro = setInterval(() => {
      if (document.visibilityState === "visible") ricarica();
    }, 15_000);
    return () => clearInterval(giro);
  }, [ricarica]);

  const d = dati.dati;
  const barre = (voci: { valore: string; sessioni: number }[]) =>
    voci.map((v) => ({ chiave: v.valore, etichetta: v.valore, valore: v.sessioni }));

  // La mezz'ora completa: i minuti senza pagine valgono zero.
  const punti = [];
  if (d) {
    const per = new Map(d.pagine_per_minuto.map((p) => [p.minuto.slice(0, 16), p.pagine]));
    const adesso = new Date();
    adesso.setSeconds(0, 0);
    for (let i = 29; i >= 0; i--) {
      const m = new Date(adesso.getTime() - i * 60_000);
      const chiave = m.toISOString().slice(0, 16);
      punti.push({ chiave, etichetta: ora.format(m), valore: per.get(chiave) ?? 0 });
    }
  }

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Adesso</h1>
          <p className={comuni.sottotitolo}>
            Visite attive negli ultimi {d?.minuti ?? 5} minuti. Si aggiorna ogni 15 secondi mentre la pagina è aperta.
          </p>
        </div>
      </div>
      {dati.errore && <p className={comuni.errore} role="alert">{dati.errore}</p>}
      {!d && dati.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {d && (
        <>
          <div className={grafici.tessere} aria-live="polite">
            <Tessera etichetta="Visite attive" valore={d.sessioni_attive} />
          </div>
          <Colonne titolo="Pagine viste per minuto" descrizione="Ultima mezz'ora, ora italiana." unita="pagine" punti={punti} />
          {d.sessioni_attive === 0 ? (
            <div className={comuni.vuoto}>Nessuna visita attiva in questo momento.</div>
          ) : (
            <div className={stili.coppie}>
              <Barre titolo="Pagine aperte" descrizione="L'ultima pagina di ogni visita attiva." unita="visite" barre={barre(d.pagine)} />
              <Barre titolo="Canali" unita="visite" barre={barre(d.canali)} />
              <Barre titolo="Paesi" unita="visite" barre={barre(d.paesi)} />
              <Barre titolo="Dispositivi" unita="visite" barre={barre(d.dispositivi)} />
            </div>
          )}
        </>
      )}
    </>
  );
}
