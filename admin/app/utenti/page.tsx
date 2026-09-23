"use client";

import Link from "next/link";
import { useCallback, useState } from "react";
import { elencoUtenti } from "@/lib/api";
import { giorno } from "@/lib/formato";
import { useDati } from "@/lib/usa";
import stili from "../comuni.module.css";

/* Gli utenti.
 *
 * La ricerca parte all'invio e non a ogni tasto: il backend la fa sul
 * database, e dieci richieste per scrivere un indirizzo sono nove richieste
 * di troppo — con risposte che possono arrivare in disordine e mostrare i
 * risultati di una parola vecchia.
 */

const PER_PAGINA = 50;

export default function Utenti() {
  const [scritto, setScritto] = useState("");
  const [cercato, setCercato] = useState("");
  const [offset, setOffset] = useState(0);

  const { dati, errore, inCorso } = useDati(
    useCallback(
      (t: string) => elencoUtenti(t, { q: cercato, limite: PER_PAGINA, offset }),
      [cercato, offset],
    ),
  );

  const cerca = (e: React.FormEvent) => {
    e.preventDefault();
    setCercato(scritto.trim());
    /* Una ricerca nuova riparte dalla prima pagina: restare a pagina 4 di
     * un elenco che ora ne ha una sola mostrerebbe il vuoto. */
    setOffset(0);
  };

  const totale = dati?.totale ?? 0;
  const dal = totale === 0 ? 0 : offset + 1;
  const al = Math.min(offset + PER_PAGINA, totale);

  return (
    <>
      <div className={stili.intestazione}>
        <div>
          <h1 className={stili.titolo}>Utenti</h1>
          <p className={stili.sottotitolo}>
            Chi è iscritto, con quale piano e con quanti crediti. Dal
            dettaglio si sospende un account o si rettifica un saldo; le
            letture restano private anche da qui.
          </p>
        </div>
      </div>

      <form className={stili.riga} onSubmit={cerca} role="search" style={{ marginBottom: "1.25rem" }}>
        <label className={stili.campo} style={{ marginBottom: 0 }}>
          <span className="solo-lettori">Cerca</span>
          <input
            className={stili.ingresso}
            type="search"
            value={scritto}
            onChange={(e) => setScritto(e.target.value)}
            placeholder="Email, nome o codice invito"
          />
        </label>
        <button className={stili.secondaria} type="submit">
          Cerca
        </button>
      </form>

      {errore && <p className={stili.errore}>{errore}</p>}
      {!dati && inCorso && <p className={stili.caricamento}>Caricamento…</p>}

      {dati && dati.utenti.length === 0 && (
        <div className={stili.vuoto}>
          {cercato ? `Nessun utente corrisponde a «${cercato}».` : "Nessun utente iscritto."}
        </div>
      )}

      {dati && dati.utenti.length > 0 && (
        <div className={inCorso ? stili.inRicarica : undefined}>
          <div className={stili.contenitoreTabella}>
            <table className={stili.tabella}>
              <thead>
                <tr>
                  <th>Utente</th>
                  <th>Piano</th>
                  <th className={stili.numero}>Crediti</th>
                  <th>Lingua</th>
                  <th>Iscritto</th>
                  <th>Invito</th>
                  <th>Stato</th>
                </tr>
              </thead>
              <tbody>
                {dati.utenti.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <Link href={`/utenti/${u.id}`} className={stili.collegamento}>
                        {u.display_name || u.email || `#${u.id}`}
                      </Link>
                      {u.display_name && u.email && (
                        <div className={stili.campoAiuto}>{u.email}</div>
                      )}
                    </td>
                    <td className={stili.mono}>{u.piano ?? "—"}</td>
                    <td className={`${stili.numero} ${u.saldo < 0 ? stili.negativo : ""}`}>{u.saldo}</td>
                    <td className={stili.mono}>{u.locale ?? "—"}</td>
                    <td className={stili.mono}>{giorno(u.creato)}</td>
                    <td className={stili.mono}>
                      {u.referral_code ?? "—"}
                      {u.invitato_da !== null && (
                        <div className={stili.campoAiuto}>
                          invitato da{" "}
                          <Link href={`/utenti/${u.invitato_da}`} className={stili.collegamento}>
                            #{u.invitato_da}
                          </Link>
                        </div>
                      )}
                    </td>
                    <td>
                      <span className={`${stili.stato} ${u.attivo ? stili.positivo : stili.spento}`}>
                        {u.attivo ? "attivo" : "disattivato"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className={stili.paginazione}>
            <span>
              {dal}–{al} di {totale}
            </span>
            <div className={stili.paginazioneComandi}>
              <button
                className={stili.secondaria}
                disabled={offset === 0 || inCorso}
                onClick={() => setOffset((o) => Math.max(0, o - PER_PAGINA))}
              >
                Precedenti
              </button>
              <button
                className={stili.secondaria}
                disabled={offset + PER_PAGINA >= totale || inCorso}
                onClick={() => setOffset((o) => o + PER_PAGINA)}
              >
                Successivi
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
