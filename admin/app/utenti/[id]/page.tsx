"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useState } from "react";
import {
  dettaglioUtente,
  impostaAttivo,
  rettificaCrediti,
  type UtenteDettaglio,
} from "@/lib/api";
import { giorno, quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { TabellaPagamenti } from "../../pagamenti/tabella";
import stili from "./dettaglio.module.css";

/* Un utente, visto da chi amministra.
 *
 * Si vede il conto — saldo, abbonamento, movimenti, pagamenti — e quante
 * letture ha fatto, mai che cosa ha chiesto. Si può fare due cose soltanto:
 * sospendere l'account e rettificare il saldo. Entrambe finiscono nel
 * registro, con chi le ha fatte.
 */

const MOTIVI: Record<string, string> = {
  accredito_piano: "Rinnovo del piano",
  acquisto: "Acquisto",
  consumo: "Lettura",
  rimborso: "Rimborso",
  rettifica: "Rettifica manuale",
  scadenza: "Scadenza",
  omaggio: "Omaggio",
};

const STATI_LETTURA: Record<string, string> = {
  completata: "completate",
};

export default function DettaglioUtente() {
  const { id } = useParams<{ id: string }>();
  const numero = Number(id);

  const { dati, errore, inCorso, ricarica } = useDati(
    useCallback((t: string) => dettaglioUtente(t, numero), [numero]),
  );

  if (!Number.isInteger(numero)) {
    return <p className={comuni.errore}>Identificativo non valido.</p>;
  }

  return (
    <>
      <p className={stili.briciole}>
        <Link href="/utenti" className={comuni.collegamento}>
          ← Utenti
        </Link>
      </p>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {!dati && inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {dati && <Scheda utente={dati} ricarica={ricarica} />}
    </>
  );
}

function Scheda({ utente, ricarica }: { utente: UtenteDettaglio; ricarica: () => void }) {
  const letture = Object.entries(utente.letture).sort(([, a], [, b]) => b - a);
  const totaleLetture = letture.reduce((s, [, n]) => s + n, 0);

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>
            {utente.display_name || utente.email || `Utente #${utente.id}`}
          </h1>
          <p className={comuni.sottotitolo}>
            <span className={comuni.mono}>#{utente.id}</span>
            {utente.email && <> · {utente.email}</>}
            {" · "}iscritto il {giorno(utente.creato)}
            {utente.locale && <> · lingua {utente.locale}</>}
          </p>
        </div>
        <Attivazione utente={utente} ricarica={ricarica} />
      </div>

      <div className={stili.sommario}>
        <div className={stili.voce}>
          <div className={stili.voceEtichetta}>Saldo</div>
          <div className={`${stili.voceValore} ${utente.saldo < 0 ? comuni.negativo : ""}`}>
            {utente.saldo} <small>crediti</small>
          </div>
        </div>
        <div className={stili.voce}>
          <div className={stili.voceEtichetta}>Abbonamento</div>
          {utente.abbonamento ? (
            <>
              <div className={stili.voceValore}>{utente.abbonamento.nome}</div>
              <div className={comuni.campoAiuto}>
                {utente.abbonamento.stato} · fino al {giorno(utente.abbonamento.fine)}
              </div>
            </>
          ) : (
            <div className={stili.voceValore}>—</div>
          )}
        </div>
        <div className={stili.voce}>
          <div className={stili.voceEtichetta}>Letture</div>
          <div className={stili.voceValore}>{totaleLetture}</div>
          {letture.length > 0 && (
            <div className={comuni.campoAiuto}>
              {letture.map(([s, n]) => `${n} ${STATI_LETTURA[s] ?? s}`).join(" · ")}
            </div>
          )}
        </div>
        <div className={stili.voce}>
          <div className={stili.voceEtichetta}>Invito</div>
          <div className={`${stili.voceValore} ${comuni.mono}`}>{utente.referral_code ?? "—"}</div>
          {utente.invitato_da !== null && (
            <div className={comuni.campoAiuto}>
              invitato da{" "}
              <Link href={`/utenti/${utente.invitato_da}`} className={comuni.collegamento}>
                #{utente.invitato_da}
              </Link>
            </div>
          )}
        </div>
      </div>

      <Rettifica utente={utente} ricarica={ricarica} />

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>Movimenti dei crediti</h2>
        <p className={comuni.riquadroNota}>
          Gli ultimi cinquanta, dal più recente. Il registro non si corregge:
          un errore si ripara con una rettifica che lo compensa.
        </p>
        {utente.movimenti.length === 0 ? (
          <div className={comuni.vuoto}>Nessun movimento.</div>
        ) : (
          <div className={comuni.contenitoreTabella}>
            <table className={comuni.tabella}>
              <thead>
                <tr>
                  <th>Quando</th>
                  <th>Motivo</th>
                  <th className={comuni.numero}>Crediti</th>
                  <th>Nota</th>
                  <th>Lettura</th>
                </tr>
              </thead>
              <tbody>
                {utente.movimenti.map((m, i) => (
                  <tr key={`${m.quando}-${i}`}>
                    <td className={comuni.mono}>{quandoCompleto(m.quando)}</td>
                    <td>{MOTIVI[m.reason] ?? m.reason}</td>
                    <td className={`${comuni.numero} ${m.delta > 0 ? comuni.positivo : comuni.negativo}`}>
                      {m.delta > 0 ? `+${m.delta}` : `−${Math.abs(m.delta)}`}
                    </td>
                    <td>{m.note ?? <span className={comuni.campoAiuto}>—</span>}</td>
                    {/* Solo l'identificativo: la lettura è dell'utente, e la
                        console non la apre. */}
                    <td className={comuni.mono}>{m.reading_id ? m.reading_id.slice(0, 8) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>Pagamenti</h2>
        {utente.pagamenti.length === 0 ? (
          <div className={comuni.vuoto}>Nessun pagamento.</div>
        ) : (
          <TabellaPagamenti pagamenti={utente.pagamenti} senzaUtente />
        )}
      </section>
    </>
  );
}

/* Sospendere e riattivare.
 *
 * Una conferma prima di sospendere, nessuna prima di riattivare: il primo
 * gesto chiude fuori una persona, il secondo la lascia rientrare. */
function Attivazione({ utente, ricarica }: { utente: UtenteDettaglio; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();

  const cambia = async () => {
    if (
      utente.attivo &&
      !window.confirm(
        "Disattivare l'account? L'utente non potrà più accedere finché non verrà riattivato.",
      )
    ) {
      return;
    }
    const fatto = await esegui((t) => impostaAttivo(t, utente.id, !utente.attivo));
    if (fatto) ricarica();
  };

  return (
    <div className={stili.attivazione}>
      <span className={`${comuni.stato} ${utente.attivo ? comuni.positivo : comuni.spento}`}>
        {utente.attivo ? "attivo" : "disattivato"}
      </span>
      <button
        className={utente.attivo ? comuni.distruttiva : comuni.secondaria}
        onClick={cambia}
        disabled={inCorso}
      >
        {utente.attivo ? "Disattiva" : "Riattiva"}
      </button>
      {errore && <p className={comuni.errore}>{errore}</p>}
    </div>
  );
}

/* La rettifica del saldo.
 *
 * Il motivo è obbligatorio, e non per burocrazia: sei mesi dopo, una riga
 * «+10» senza spiegazione è indistinguibile da un errore, e nessuno sa più
 * perché quel saldo è cambiato. */
function Rettifica({ utente, ricarica }: { utente: UtenteDettaglio; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [delta, setDelta] = useState("");
  const [motivo, setMotivo] = useState("");
  const [esito, setEsito] = useState<string | null>(null);

  const numero = Number(delta);
  const valido =
    delta.trim() !== "" && Number.isInteger(numero) && numero !== 0 && motivo.trim().length >= 3;

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valido) return;
    setEsito(null);
    const fatto = await esegui((t) =>
      rettificaCrediti(t, utente.id, { delta: numero, motivo: motivo.trim() }),
    );
    if (fatto) {
      setEsito(
        `${fatto.delta > 0 ? "Accreditati" : "Tolti"} ${Math.abs(fatto.delta)} crediti: saldo ora ${fatto.saldo}.`,
      );
      setDelta("");
      setMotivo("");
      ricarica();
    }
  };

  return (
    <section className={comuni.riquadro}>
      <h2 className={comuni.riquadroTitolo}>Rettifica dei crediti</h2>
      <p className={comuni.riquadroNota}>
        Un numero positivo accredita, uno negativo toglie. Diventa una riga nuova
        del registro con il motivo scritto qui, e resta nel registro delle
        operazioni con il tuo nome.
      </p>
      <form className={comuni.riga} onSubmit={invia}>
        <label className={comuni.campo} style={{ flex: "0 1 9rem" }}>
          <span className={comuni.campoEtichetta}>Crediti</span>
          <input
            className={comuni.ingresso}
            type="number"
            step={1}
            inputMode="numeric"
            value={delta}
            onChange={(e) => setDelta(e.target.value)}
            placeholder="es. 5 o −3"
            required
          />
        </label>
        <label className={comuni.campo} style={{ flex: "1 1 20rem" }}>
          <span className={comuni.campoEtichetta}>Motivo (obbligatorio)</span>
          <input
            className={comuni.ingresso}
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            placeholder="es. rimborso per lettura interrotta da un guasto"
            minLength={3}
            maxLength={500}
            required
          />
        </label>
        <button
          className={comuni.primaria}
          type="submit"
          disabled={!valido || inCorso}
          style={{ marginBottom: "0.9rem" }}
        >
          Applica
        </button>
      </form>
      {errore && <p className={comuni.errore}>{errore}</p>}
      {esito && <p className={comuni.esito}>{esito}</p>}
    </section>
  );
}
