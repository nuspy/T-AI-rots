"use client";

import { useCallback, useState } from "react";
import { ErroreApi } from "@/lib/api";
import {
  anteprimaConservazione, eseguiConservazione, leggiConservazione,
  type Anteprima, type ChiaveVoce, type VoceConservazione,
} from "@/lib/conservazione";
import { useDati, useToken } from "@/lib/usa";
import stili from "../comuni.module.css";
import propri from "./conservazione.module.css";

/* «Conservazione dati» (GDPR, Fase 1).
 *
 * L'operatore ha deciso di conservare letture e chat senza scadenza automatica («fino a cancellazione
 * dell'interessato o dell'amministratore», `docs/privacy/conservazione.md`): qui si vede quanto c'è e di che età,
 * e si cancella a mano. Il percorso è sempre lo stesso: si sceglie l'età minima delle righe, si chiede l'anteprima
 * (quante, la più vecchia, la più recente), si conferma ripetendo quel numero. Se nel frattempo i dati sono cambiati
 * il server si ferma e chiede una nuova anteprima. Ogni esecuzione resta nel Registro. */

const SCELTE_GIORNI = [
  { giorni: 0, etichetta: "tutte" },
  { giorni: 30, etichetta: "oltre 30 giorni" },
  { giorni: 182, etichetta: "oltre 6 mesi" },
  { giorni: 365, etichetta: "oltre 1 anno" },
  { giorni: 730, etichetta: "oltre 2 anni" },
  { giorni: 1825, etichetta: "oltre 5 anni" },
];

const data = (iso: string | null) =>
  iso ? new Date(iso).toLocaleDateString("it-IT", { day: "numeric", month: "short", year: "numeric" }) : "—";

export default function Conservazione() {
  const { dati, errore, inCorso, ricarica } = useDati(useCallback((t: string) => leggiConservazione(t), []));

  return (
    <>
      <div className={stili.intestazione}>
        <div>
          <h1 className={stili.titolo}>Conservazione dati</h1>
          <p className={stili.sottotitolo}>
            Letture anonime e chat si conservano senza scadenza automatica: qui si vede quanto c&apos;è e di che
            età, e si cancella a mano, sempre con un&apos;anteprima. Il GDPR (art. 5.1.e) chiede una durata
            motivata: la decisione è scritta nel registro dei trattamenti, da far vedere al consulente.
          </p>
        </div>
      </div>

      {errore && <p className={stili.errore}>{errore}</p>}
      {!dati && inCorso && <p className={stili.caricamento}>Caricamento…</p>}

      {dati && (
        <div className={`${propri.voci} ${inCorso ? stili.inRicarica : ""}`}>
          {dati.voci.map((v) => <Voce key={v.chiave} voce={v} suCambio={ricarica} giorniRipensamento={dati.giorni_ripensamento} />)}
        </div>
      )}
    </>
  );
}

function Voce({ voce, suCambio, giorniRipensamento }: { voce: VoceConservazione; suCambio: () => void; giorniRipensamento: number }) {
  const token = useToken();
  const [giorni, setGiorni] = useState(voce.chiave === "consensi_storici" ? 1825 : 365);
  const [anteprima, setAnteprima] = useState<Anteprima | null>(null);
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);
  const [esito, setEsito] = useState<string | null>(null);

  const chiedi = async () => {
    if (token === null) return;
    setInCorso(true); setErrore(null); setEsito(null);
    try {
      setAnteprima(await anteprimaConservazione(token, voce.chiave as ChiaveVoce, giorni));
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "Anteprima non riuscita");
    } finally {
      setInCorso(false);
    }
  };

  const esegui = async () => {
    if (token === null || !anteprima) return;
    setInCorso(true); setErrore(null);
    try {
      const r = await eseguiConservazione(token, voce.chiave, anteprima.giorni, anteprima.quanti);
      const falliti = r.falliti?.length ? ` · ${r.falliti.length} non riuscite (Keycloak?): riprova più tardi` : "";
      setEsito(`Fatto: ${r.fatti} ${r.fatti === 1 ? "riga" : "righe"}${falliti}.`);
      setAnteprima(null);
      suCambio();
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "Esecuzione non riuscita");
      setAnteprima(null);
    } finally {
      setInCorso(false);
    }
  };

  const massimo = Math.max(1, ...voce.fasce.map((f) => f.quanti));
  return (
    <section className={stili.riquadro} aria-labelledby={`v-${voce.chiave}`}>
      <div className={propri.testa}>
        <h2 id={`v-${voce.chiave}`} className={stili.riquadroTitolo}>{voce.titolo}</h2>
        <span className={propri.totale}>{voce.totale.toLocaleString("it-IT")}</span>
      </div>
      <p className={stili.riquadroNota}>{voce.descrizione}</p>
      {voce.chiave === "account_in_cancellazione" && (
        <p className={stili.riquadroNota}>
          Nei primi {giorniRipensamento} giorni la persona può ancora riaprire l&apos;account: eseguire prima vuol
          dire toglierle questa possibilità.
        </p>
      )}

      <ul className={propri.fasce} aria-label="Per età">
        {voce.fasce.map((f) => (
          <li key={f.etichetta}>
            <span className={propri.etichetta}>{f.etichetta}</span>
            <span className={propri.barra} aria-hidden="true"><span style={{ width: `${(f.quanti / massimo) * 100}%` }} /></span>
            <span className={propri.numero}>{f.quanti.toLocaleString("it-IT")}</span>
          </li>
        ))}
      </ul>

      <div className={propri.comandi}>
        <label className={stili.campo}>
          <span className={stili.campoEtichetta}>Quali righe</span>
          <select className={stili.selezione} value={giorni} disabled={inCorso}
            onChange={(e) => { setGiorni(Number(e.target.value)); setAnteprima(null); }}>
            {SCELTE_GIORNI.map((s) => <option key={s.giorni} value={s.giorni}>{s.etichetta}</option>)}
          </select>
        </label>
        <button type="button" className={stili.secondaria} disabled={inCorso || voce.totale === 0} onClick={chiedi}>
          Anteprima
        </button>
      </div>

      {anteprima && (
        <div className={propri.anteprima} role="status">
          {anteprima.quanti === 0 ? (
            <p>Nessuna riga corrisponde.</p>
          ) : (
            <>
              <p>
                <strong>{anteprima.quanti.toLocaleString("it-IT")}</strong> {anteprima.quanti === 1 ? "riga" : "righe"}
                {" "}· dalla {data(anteprima.piu_vecchio)} alla {data(anteprima.piu_recente)}.
              </p>
              <p className={stili.riquadroNota}>Azione: {anteprima.azione}. Non si torna indietro.</p>
              <div className={propri.comandi}>
                <button type="button" className={stili.distruttiva} disabled={inCorso} onClick={esegui}>
                  {anteprima.azione} ({anteprima.quanti.toLocaleString("it-IT")})
                </button>
                <button type="button" className={stili.secondaria} disabled={inCorso} onClick={() => setAnteprima(null)}>
                  Annulla
                </button>
              </div>
            </>
          )}
        </div>
      )}
      {esito && <p className={stili.esito} role="status">{esito}</p>}
      {errore && <p className={stili.errore} role="alert">{errore}</p>}
    </section>
  );
}
