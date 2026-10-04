"use client";

/* Notifications → Consegne e aperture: quante notifiche sono partite, quante sono arrivate a un dispositivo, quante
 * sono state toccate, per tipo e per giorno. «Consegnata» vuol dire accettata da FCM o dal servizio push del
 * browser: se poi il telefono è spento la riceve alla riaccensione (entro un giorno). */

import { useState } from "react";
import { giorno } from "@/lib/formato";
import { statistiche, type RigaStatistica } from "@/lib/notifiche";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../notifiche.module.css";

const PERIODI = [7, 30, 90];

function percentuale(v: number | null): string {
  return v === null ? "—" : `${Math.round(v * 100)}%`;
}

function Tessera({ nome, valore }: { nome: string; valore: string | number }) {
  return (
    <div className={stili.tessera}>
      <div className={stili.tesseraValore}>{valore}</div>
      <div className={stili.tesseraNome}>{nome}</div>
    </div>
  );
}

function Numeri({ r }: { r: RigaStatistica }) {
  return (
    <dl className={stili.numeri}>
      <div><dt>Invii</dt><dd>{r.invii}</dd></div>
      <div><dt>Consegnati</dt><dd>{r.consegnati}</dd></div>
      <div><dt>Aperti</dt><dd>{r.aperti} ({percentuale(r.tasso_apertura)})</dd></div>
      <div><dt>Errori</dt><dd>{r.errori}</dd></div>
      <div><dt>Dispositivi spariti</dt><dd>{r.token_invalidi}</dd></div>
    </dl>
  );
}

export default function Consegne() {
  const [giorni, setGiorni] = useState(30);
  const { dati, errore } = useDati((t) => statistiche(t, giorni), [giorni]);
  const massimo = Math.max(1, ...(dati?.per_giorno.map((g) => g.invii) ?? [1]));

  return (
    <>
      <div className={stili.azioni} role="group" aria-label="Periodo">
        {PERIODI.map((p) => (
          <button key={p} type="button" className={p === giorni ? comuni.primaria : comuni.secondaria} aria-pressed={p === giorni}
            onClick={() => setGiorni(p)}>
            Ultimi {p} giorni
          </button>
        ))}
      </div>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {!dati && !errore && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && (
        <>
          <div className={stili.tessere}>
            <Tessera nome="Invii" valore={dati.totali.invii} />
            <Tessera nome="Consegnati" valore={dati.totali.consegnati} />
            <Tessera nome="Aperti" valore={dati.totali.aperti} />
            <Tessera nome="Tasso di apertura" valore={percentuale(dati.totali.tasso_apertura)} />
            <Tessera nome="Dispositivi disattivati" valore={dati.dispositivi_disattivati} />
          </div>

          <section className={comuni.riquadro} aria-labelledby="titolo-tipi">
            <h2 id="titolo-tipi" className={comuni.riquadroTitolo}>Per tipo</h2>
            {dati.per_tipo.length === 0 ? <p className={comuni.vuoto}>Nessun invio nel periodo.</p> : (
              <ul className={stili.elenco}>
                {dati.per_tipo.map((r) => (
                  <li key={r.tipo} className={stili.scheda}>
                    <strong>{r.nome}</strong>
                    <Numeri r={r} />
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className={comuni.riquadro} aria-labelledby="titolo-giorni">
            <h2 id="titolo-giorni" className={comuni.riquadroTitolo}>Per giorno</h2>
            <p className={stili.legenda}>
              <span><span className={stili.puntoConsegnati} aria-hidden="true" />consegnati</span>
              <span><span className={stili.puntoAperti} aria-hidden="true" />aperti</span>
              <span>La barra intera: gli invii del giorno (ora italiana).</span>
            </p>
            {dati.per_giorno.length === 0 ? <p className={comuni.vuoto}>Nessun invio nel periodo.</p> : (
              <ul className={stili.barre}>
                {dati.per_giorno.map((g) => (
                  <li key={g.giorno} className={stili.barra}>
                    <span className={comuni.mono}>{giorno(g.giorno)}</span>
                    <span className={stili.barraTraccia} style={{ width: `${(g.invii / massimo) * 100}%` }} aria-hidden="true">
                      <span className={stili.barraAperti} style={{ width: `${(g.aperti / Math.max(1, g.invii)) * 100}%` }} />
                      <span className={stili.barraConsegnati} style={{ width: `${((g.consegnati - g.aperti) / Math.max(1, g.invii)) * 100}%` }} />
                    </span>
                    <span className={comuni.mono}>{g.invii} · {g.consegnati} · {g.aperti}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </>
  );
}
