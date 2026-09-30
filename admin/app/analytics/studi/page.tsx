"use client";

/* Studi (v8): Google Colab e qualunque notebook. Si crea un token (visibile una volta sola), si scarica
 * il notebook già pronto per una collezione, lo si apre in Colab (File → Carica notebook) e si incolla
 * il token quando lo chiede. I risultati rimandati dal notebook compaiono qui sotto. */

import { useState } from "react";
import { creaToken, leggiStudi, revocaToken, scaricaNotebook, togliRisultato } from "@/lib/analytics";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";

export default function StudiPagina() {
  const studi = useDati(leggiStudi);
  const { esegui, inCorso, errore } = useAzione();
  const [nome, setNome] = useState("Colab");
  const [giorni, setGiorni] = useState(30);
  const [nuovo, setNuovo] = useState<string | null>(null);
  const [copiato, setCopiato] = useState(false);
  const [collezione, setCollezione] = useState("traffico");
  const s = studi.dati;

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Studi con Colab</h1>
          <p className={comuni.sottotitolo}>
            Per le analisi che la console non fa: scarica un notebook già pronto, aprilo in Google Colab (File → Carica
            notebook) e incolla il token quando lo chiede. Il notebook riceve solo aggregati (gruppi di almeno 5 persone) e
            può rimandare qui i suoi risultati, che l&apos;interpretazione AI usa per 90 giorni.
          </p>
        </div>
      </div>
      {(studi.errore || errore) && <p className={comuni.errore} role="alert">{errore ?? studi.errore}</p>}

      <section className={comuni.riquadro} aria-labelledby="titolo-notebook">
        <h2 id="titolo-notebook" className={comuni.riquadroTitolo}>1 · Scarica il notebook</h2>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Dati</span>
            <select className={comuni.selezione} value={collezione} onChange={(e) => setCollezione(e.target.value)}>
              {Object.entries(s?.collezioni ?? { traffico: "Traffico" }).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </label>
          <button className={comuni.secondaria} disabled={inCorso} onClick={() => esegui((t) => scaricaNotebook(t, collezione, 90))}>
            Scarica il notebook (.ipynb)
          </button>
          <a className={comuni.collegamento} href="https://colab.research.google.com/" target="_blank" rel="noreferrer"
            style={{ minHeight: 44, display: "inline-flex", alignItems: "center" }}>
            Apri Google Colab
          </a>
        </div>
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-token">
        <h2 id="titolo-token" className={comuni.riquadroTitolo}>2 · Crea un token</h2>
        <form className={comuni.riga} onSubmit={async (e) => {
          e.preventDefault();
          const r = await esegui((t) => creaToken(t, { nome, giorni, ambiti: ["esporta", "importa"] }));
          if (r) {
            setNuovo(r.token);
            setCopiato(false);
            studi.ricarica();
          }
        }}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Nome</span>
            <input className={comuni.ingresso} value={nome} maxLength={120} onChange={(e) => setNome(e.target.value)} required />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Valido per (giorni)</span>
            <input className={comuni.ingresso} type="number" min={1} max={365} value={giorni}
              onChange={(e) => setGiorni(Math.max(1, Math.min(365, Number(e.target.value) || 1)))} />
          </label>
          <button className={comuni.primaria} type="submit" disabled={inCorso}>Crea il token</button>
        </form>
        {nuovo && (
          <div className={comuni.avviso} role="status">
            <strong>Copialo ora: non sarà più visibile.</strong>
            <div className={comuni.mono} style={{ overflowWrap: "anywhere", margin: "0.5rem 0" }}>{nuovo}</div>
            <button className={comuni.secondaria} onClick={async () => {
              await navigator.clipboard?.writeText(nuovo);
              setCopiato(true);
            }}>
              {copiato ? "Copiato" : "Copia"}
            </button>
          </div>
        )}
        {s && s.token.length > 0 && (
          <div className={comuni.contenitoreTabella} style={{ marginTop: "0.75rem" }}>
            <table className={comuni.tabella}>
              <thead><tr><th>Nome</th><th>Scade</th><th>Ultimo uso</th><th /></tr></thead>
              <tbody>
                {s.token.map((t) => (
                  <tr key={t.id}>
                    <td>{t.nome}</td>
                    <td>{t.revocato_il ? "revocato" : quandoCompleto(t.scade_il)}</td>
                    <td>{t.ultimo_uso ? quandoCompleto(t.ultimo_uso) : "mai"}</td>
                    <td>
                      {!t.revocato_il && (
                        <button className={comuni.secondaria} disabled={inCorso}
                          onClick={async () => { await esegui((x) => revocaToken(x, t.id)); studi.ricarica(); }}>
                          Revoca
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-risultati">
        <h2 id="titolo-risultati" className={comuni.riquadroTitolo}>3 · Risultati rimandati dai notebook</h2>
        {!s?.risultati.length && <div className={comuni.vuoto}>Nessun risultato ancora. Nel notebook: <span className={comuni.mono}>rimanda(df, &quot;titolo&quot;)</span>.</div>}
        {s?.risultati.map((r) => (
          <details key={r.id} style={{ marginBottom: "0.75rem" }}>
            <summary>
              <strong>{r.titolo}</strong> · {quandoCompleto(r.creato_il)} · {r.totale_righe} righe
            </summary>
            {r.descrizione && <p className={comuni.riquadroNota}>{r.descrizione}</p>}
            <div className={comuni.contenitoreTabella}>
              <table className={comuni.tabella}>
                <thead><tr>{r.colonne.map((c) => <th key={c}>{c}</th>)}</tr></thead>
                <tbody>
                  {r.righe.slice(0, 50).map((riga, i) => (
                    <tr key={i}>{riga.map((v, j) => <td key={j}>{v === null ? "—" : String(v)}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
            <button className={comuni.secondaria} disabled={inCorso}
              onClick={async () => { await esegui((t) => togliRisultato(t, r.id)); studi.ricarica(); }}>
              Elimina il risultato
            </button>
          </details>
        ))}
      </section>
    </>
  );
}
