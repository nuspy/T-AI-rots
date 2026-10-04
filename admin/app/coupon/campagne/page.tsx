"use client";

/* Il resoconto per campagna (v9, Fase 2d): per ogni etichetta di campagna — e i coupon senza — riscatti, incasso lordo,
 * sconto concesso, nuovi utenti, prove avviate e convertite. Le cifre vengono dagli usi dei coupon e dai pagamenti
 * (`billing/resoconto_coupon.py`). Sul telefono una scheda per campagna; il resoconto coupon per coupon sta nella
 * scheda «Coupon». */

import { soldi } from "@/lib/formato";
import { campagne } from "@/lib/offerte";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../coupon.module.css";
import { CifreResoconto } from "../pezzi";

export default function PaginaCampagne() {
  const dati = useDati(campagne);
  const t = dati.dati?.totale;

  return (
    <>
      <p className={comuni.riquadroNota}>
        <strong>Incasso lordo</strong>: quanto è stato pagato con il coupon, rinnovi scontati compresi.{" "}
        <strong>Sconto concesso</strong>: quanto il coupon ha tolto in più rispetto agli sconti che ci sarebbero stati
        comunque (rinnovo automatico, prova). <strong>Nuovi utenti</strong>: chi l&apos;ha usato con un account nato dopo il
        coupon. <strong>Prove → pagate</strong>: prove gratuite partite col codice e diventate un abbonamento pagato.
      </p>
      {dati.errore && <p className={comuni.errore}>{dati.errore}</p>}
      {!dati.dati && dati.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {t && (
        <section className={`${comuni.riquadro} ${stili.totale}`} aria-labelledby="totale-campagne">
          <h2 id="totale-campagne" className={comuni.riquadroTitolo}>Tutti i coupon</h2>
          <p className={comuni.riquadroNota}>
            {t.riscatti ?? 0} riscatti · incasso lordo {soldi(t.incasso_lordo ?? 0)} · sconto concesso {soldi(t.sconto_concesso ?? 0)}
          </p>
        </section>
      )}
      {dati.dati && dati.dati.campagne.length === 0 && (
        <div className={comuni.vuoto}>Nessun coupon ancora: il resoconto comincia con il primo.</div>
      )}
      {dati.dati && dati.dati.campagne.length > 0 && (
        <ul className={`${stili.elenco} ${dati.inCorso ? comuni.inRicarica : ""}`} aria-label="Campagne">
          {dati.dati.campagne.map((c) => (
            <li key={c.campagna ?? "senza"} className={stili.voce}>
              <div className={stili.testata}>
                <h2 className={stili.titoloScheda}>{c.campagna ?? "Senza campagna"}</h2>
                <span className={comuni.mono}>{c.coupon} coupon{c.lotti ? ` · ${c.lotti} lotti` : ""}</span>
              </div>
              <CifreResoconto r={c} />
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
