"use client";

/* Notifications → Campagne: i messaggi scritti a mano per un gruppo di utenti, dal più recente. Ogni scheda dice
 * stato, tipo, quando parte (o è partita) e come è andata; il nome apre l'editor. */

import Link from "next/link";
import { quandoCompleto } from "@/lib/formato";
import { NOMI_STATO, NOMI_TIPO, elencoCampagne, type Campagna } from "@/lib/notifiche";
import { useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./notifiche.module.css";

function Quando({ c }: { c: Campagna }) {
  if (c.stato === "programmata" && c.programmata_il) return <>Parte {quandoCompleto(c.programmata_il)}</>;
  if (c.stato === "in_invio" && c.iniziata_il) return <>In invio dal {quandoCompleto(c.iniziata_il)}</>;
  if ((c.stato === "inviata" || c.stato === "annullata") && c.finita_il) return <>{NOMI_STATO[c.stato]} {quandoCompleto(c.finita_il)}</>;
  return <>Modificata {quandoCompleto(c.modificata_il)}</>;
}

export default function Campagne() {
  const { dati, errore } = useDati(elencoCampagne);

  return (
    <>
      <div className={stili.azioni}>
        <Link href="/notifiche/campagne/nuova" className={`${comuni.primaria} ${stili.bottoneLink}`}>Nuova campagna</Link>
      </div>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {!dati && !errore && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && dati.campagne.length === 0 && (
        <p className={comuni.vuoto}>
          Nessuna campagna ancora. Una campagna è un messaggio per un gruppo di utenti scelto con dei filtri (lingua,
          paese, attività…): la scrivi, la traduci, la provi su di te e la programmi.
        </p>
      )}
      {dati && dati.campagne.length > 0 && (
        <ul className={stili.elenco}>
          {dati.campagne.map((c) => {
            const base = c.testi[c.lingua_base];
            return (
              <li key={c.id} className={stili.scheda}>
                <div className={stili.schedaTesta}>
                  <Link className={stili.schedaNome} href={`/notifiche/campagne/${c.id}`}>{c.nome}</Link>
                  <span className={comuni.etichetta}>{NOMI_TIPO[c.tipo]}</span>
                  <span className={`${comuni.stato} ${c.stato === "inviata" ? comuni.positivo : c.stato === "annullata" ? comuni.spento : comuni.neutro}`}>
                    {NOMI_STATO[c.stato]}
                  </span>
                </div>
                {base && <p className={stili.schedaTesto}><strong>{base.titolo}</strong> — {base.corpo}</p>}
                <p className={stili.schedaTesto}><Quando c={c} /></p>
                {(c.stato === "inviata" || c.stato === "in_invio") && (
                  <dl className={stili.numeri}>
                    <div><dt>Raggiunti</dt><dd>{c.contatori.destinatari}</dd></div>
                    <div><dt>Consegnati</dt><dd>{c.contatori.inviati}</dd></div>
                    <div><dt>Aperti</dt><dd>{c.contatori.aperti}</dd></div>
                    <div><dt>Errori</dt><dd>{c.contatori.errori}</dd></div>
                    <div><dt>Saltati (tetto)</dt><dd>{c.contatori.saltati}</dd></div>
                  </dl>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
