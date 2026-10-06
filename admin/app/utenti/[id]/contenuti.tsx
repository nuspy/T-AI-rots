"use client";

import { useCallback, useEffect, useState } from "react";
import {
  accessiUtente, apriAccesso, leggiChat, leggiLetture, leggiMemorie, leggiProfilo,
  type Chat, type Letture, type Memorie, type Profilo, type Scheda,
} from "@/lib/contenuti";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "./dettaglio.module.css";

/* I contenuti di un utente (v9.5): letture, chat con l'oracolo, memorie, profilazione.
 *
 * Per ragioni di sicurezza (segnalazioni, abusi, supporto) chi amministra può leggerli, ma solo dopo aver scritto
 * il motivo: apre un accesso di 30 minuti per questo utente, e ogni scheda aperta resta nel registro con il tuo nome.
 * Sotto, «Accessi ai contenuti» mostra chi li ha aperti, quando e perché. */

const SCHEDE: [Scheda, string][] = [
  ["letture", "Letture"],
  ["chat", "Chat"],
  ["memorie", "Memorie"],
  ["profilo", "Profilazione"],
];

type Dati =
  | { scheda: "letture"; d: Letture }
  | { scheda: "chat"; d: Chat }
  | { scheda: "memorie"; d: Memorie }
  | { scheda: "profilo"; d: Profilo };

export function ContenutiUtente({ id }: { id: number }) {
  const { esegui, inCorso, errore } = useAzione();
  const [motivo, setMotivo] = useState("");
  const [accesso, setAccesso] = useState<{ codice: string; scade: string } | null>(null);
  const [scheda, setScheda] = useState<Scheda>("letture");
  const [pagina, setPagina] = useState(1);
  const [dati, setDati] = useState<Dati | null>(null);
  const registro = useDati(useCallback((t: string) => accessiUtente(t, id), [id]));

  const apri = async (e: React.FormEvent) => {
    e.preventDefault();
    const fatto = await esegui((t) => apriAccesso(t, id, motivo.trim()));
    if (fatto) {
      setAccesso({ codice: fatto.accesso, scade: fatto.scade });
      setMotivo("");
    }
  };

  const carica = useCallback(async () => {
    if (!accesso) return;
    if (new Date(accesso.scade).getTime() < Date.now()) {
      setAccesso(null);
      setDati(null);
      return;
    }
    const c = accesso.codice;
    const nuovo = await esegui(async (t): Promise<Dati> => {
      if (scheda === "letture") return { scheda, d: await leggiLetture(t, id, c, pagina) };
      if (scheda === "chat") return { scheda, d: await leggiChat(t, id, c, pagina) };
      if (scheda === "memorie") return { scheda, d: await leggiMemorie(t, id, c) };
      return { scheda, d: await leggiProfilo(t, id, c) };
    });
    if (nuovo) setDati(nuovo);
    registro.ricarica();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- registro.ricarica è stabile
  }, [accesso, scheda, pagina, id, esegui]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- carica legge dal server quando cambiano accesso, scheda o pagina
    void carica();
  }, [carica]);

  const cambiaScheda = (s: Scheda) => {
    setScheda(s);
    setPagina(1);
    setDati(null);
  };

  return (
    <section className={comuni.riquadro}>
      <h2 className={comuni.riquadroTitolo}>Contenuti dell&apos;utente</h2>
      <p className={comuni.riquadroNota}>
        Letture, chat con l&apos;oracolo, memorie estratte e dati di profilazione. Sono dati intimi: si aprono solo
        per ragioni di sicurezza, scrivendo il motivo. L&apos;accesso vale 30 minuti per questo utente, e ogni scheda
        aperta resta nel registro con il tuo nome.
      </p>

      {!accesso ? (
        <form className={comuni.riga} onSubmit={apri}>
          <label className={comuni.campo} style={{ flex: "1 1 20rem" }}>
            <span className={comuni.campoEtichetta}>Motivo dell&apos;accesso (obbligatorio)</span>
            <input
              className={comuni.ingresso}
              value={motivo}
              onChange={(e) => setMotivo(e.target.value)}
              placeholder="es. segnalazione di abuso, richiesta di supporto"
              minLength={5}
              maxLength={300}
              required
            />
          </label>
          <button className={comuni.primaria} type="submit" disabled={motivo.trim().length < 5 || inCorso}
                  style={{ marginBottom: "0.9rem", minHeight: 44 }}>
            Apri i contenuti
          </button>
        </form>
      ) : (
        <>
          <p className={comuni.campoAiuto}>Accesso aperto fino alle {quandoCompleto(accesso.scade)}.</p>
          <div className={comuni.riga} role="tablist" aria-label="Contenuti dell'utente" style={{ flexWrap: "wrap", gap: "0.5rem" }}>
            {SCHEDE.map(([s, nome]) => (
              <button
                key={s}
                type="button"
                role="tab"
                aria-selected={scheda === s}
                className={scheda === s ? comuni.primaria : comuni.secondaria}
                style={{ minHeight: 44 }}
                onClick={() => cambiaScheda(s)}
              >
                {nome}
              </button>
            ))}
          </div>
          {inCorso && !dati && <p className={comuni.caricamento}>Caricamento…</p>}
          {dati?.scheda === "letture" && <SchedaLetture d={dati.d} pagina={pagina} setPagina={setPagina} />}
          {dati?.scheda === "chat" && <SchedaChat d={dati.d} pagina={pagina} setPagina={setPagina} />}
          {dati?.scheda === "memorie" && <SchedaMemorie d={dati.d} />}
          {dati?.scheda === "profilo" && <SchedaProfilo d={dati.d} />}
        </>
      )}
      {errore && <p className={comuni.errore}>{errore}</p>}

      <details style={{ marginTop: "1.25rem" }}>
        <summary className={stili.sezioneTitolo} style={{ cursor: "pointer", minHeight: 44 }}>
          Accessi ai contenuti ({registro.dati?.accessi.length ?? 0})
        </summary>
        {registro.dati && registro.dati.accessi.length === 0 && <div className={comuni.vuoto}>Nessun accesso.</div>}
        {registro.dati && registro.dati.accessi.length > 0 && (
          <div className={comuni.contenitoreTabella}>
            <table className={comuni.tabella}>
              <thead><tr><th>Quando</th><th>Chi</th><th>Cosa</th><th>Motivo</th></tr></thead>
              <tbody>
                {registro.dati.accessi.map((a, i) => (
                  <tr key={i}>
                    <td>{a.quando ? quandoCompleto(a.quando) : "—"}</td>
                    <td>{a.chi ?? "—"}</td>
                    <td>{a.azione === "accesso" ? "accesso aperto" : `${a.scheda}${a.pagina && a.pagina > 1 ? `, pagina ${a.pagina}` : ""}`}</td>
                    <td>{a.motivo ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </details>
    </section>
  );
}

function Pagine({ totale, per, pagina, setPagina }: { totale: number; per: number; pagina: number; setPagina: (n: number) => void }) {
  const ultime = Math.max(1, Math.ceil(totale / per));
  if (ultime <= 1) return null;
  return (
    <div className={comuni.riga} style={{ alignItems: "center", gap: "0.5rem" }}>
      <button type="button" className={comuni.secondaria} style={{ minHeight: 44 }} disabled={pagina <= 1}
              onClick={() => setPagina(pagina - 1)}>← Precedenti</button>
      <span className={comuni.campoAiuto}>pagina {pagina} di {ultime}</span>
      <button type="button" className={comuni.secondaria} style={{ minHeight: 44 }} disabled={pagina >= ultime}
              onClick={() => setPagina(pagina + 1)}>Successivi →</button>
    </div>
  );
}

const testo = { whiteSpace: "pre-wrap" as const, overflowWrap: "anywhere" as const, margin: "0.35rem 0" };

function SchedaLetture({ d, pagina, setPagina }: { d: Letture; pagina: number; setPagina: (n: number) => void }) {
  return (
    <>
      <p className={comuni.campoAiuto}>{d.totale} letture, dalla più recente.</p>
      {d.letture.length === 0 && <div className={comuni.vuoto}>Nessuna lettura.</div>}
      {d.letture.map((l) => (
        <details key={l.id} className={stili.sezione} style={{ borderTop: "1px solid var(--filo)", paddingTop: "0.6rem" }}>
          <summary style={{ cursor: "pointer", minHeight: 44 }}>
            <strong>{l.creata ? quandoCompleto(l.creata) : "—"}</strong> · {l.stesa} · {l.stato}
            <div style={testo}>{l.domanda}</div>
          </summary>
          {l.intervista.length > 0 && (
            <>
              <h3 className={comuni.campoEtichetta}>Intervista</h3>
              {l.intervista.map((t, i) => (
                <p key={i} style={testo}><strong>{t.ruolo === "oracolo" ? "Oracolo" : "Utente"}:</strong> {t.testo}</p>
              ))}
            </>
          )}
          {l.quadro && (<><h3 className={comuni.campoEtichetta}>Quadro emerso</h3><p style={testo}>{l.quadro}</p></>)}
          {l.carte.length > 0 && (
            <>
              <h3 className={comuni.campoEtichetta}>Carte</h3>
              {l.carte.map((c) => (
                <p key={c.posizione} style={testo}>
                  <strong>{c.posizione}. {c.carta}{c.rovescio ? " (rovesciata)" : ""}{c.calcolata ? " (calcolata)" : ""}</strong>
                  {c.interpretazione ? ` — ${c.interpretazione}` : ""}
                </p>
              ))}
            </>
          )}
          {l.sintesi && (<><h3 className={comuni.campoEtichetta}>Sintesi</h3><p style={testo}>{l.sintesi}</p></>)}
          {l.diario && (<p className={comuni.campoAiuto}>Diario: {l.diario.esito}{l.diario.nota ? ` — ${l.diario.nota}` : ""}</p>)}
          <p className={comuni.campoAiuto}>
            Lingua {l.lingua} · {l.consumo}{l.guardrail ? ` · guardrail ${l.guardrail}` : ""}{l.condivisa ? " · condivisa" : ""}
            {l.memorie_usate.length > 0 ? ` · ${l.memorie_usate.length} memorie usate` : ""}
          </p>
        </details>
      ))}
      <Pagine totale={d.totale} per={d.per_pagina} pagina={pagina} setPagina={setPagina} />
      {d.carte_del_giorno.length > 0 && (
        <details style={{ marginTop: "0.8rem" }}>
          <summary style={{ cursor: "pointer", minHeight: 44 }}>Carte del giorno ({d.carte_del_giorno.length})</summary>
          {d.carte_del_giorno.map((c, i) => (
            <p key={i} style={testo}><strong>{c.giorno}</strong> · {c.carta}{c.rovescio ? " (rovesciata)" : ""}{c.testo ? ` — ${c.testo}` : ""}</p>
          ))}
        </details>
      )}
    </>
  );
}

function SchedaChat({ d, pagina, setPagina }: { d: Chat; pagina: number; setPagina: (n: number) => void }) {
  const inOrdine = [...d.messaggi].reverse();
  return (
    <>
      <p className={comuni.campoAiuto}>{d.totale} messaggi; qui {d.messaggi.length}, in ordine di conversazione.</p>
      {inOrdine.length === 0 && <div className={comuni.vuoto}>Nessun messaggio.</div>}
      {inOrdine.map((m) => (
        <p key={m.ordine} style={testo}>
          <span className={comuni.campoAiuto}>{m.quando ? quandoCompleto(m.quando) : ""}</span>{" "}
          <strong>{m.ruolo === "ai" ? "Oracolo" : "Utente"}:</strong> {m.testo}
          {m.proposta ? <span className={comuni.campoAiuto}> (propone una lettura: {String(m.proposta.argomento ?? "")})</span> : null}
        </p>
      ))}
      <Pagine totale={d.totale} per={d.per_pagina} pagina={pagina} setPagina={setPagina} />
    </>
  );
}

function SchedaMemorie({ d }: { d: Memorie }) {
  return (
    <>
      {d.stato_sintetico && (
        <>
          <h3 className={comuni.campoEtichetta}>Stato sintetico della memoria</h3>
          <pre style={{ ...testo, fontSize: "0.85rem" }}>{JSON.stringify(d.stato_sintetico.voci, null, 2)}</pre>
        </>
      )}
      <h3 className={comuni.campoEtichetta}>Fatti estratti ({d.memorie.length})</h3>
      {d.memorie.length === 0 && <div className={comuni.vuoto}>Nessuna memoria.</div>}
      {d.memorie.length > 0 && (
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead><tr><th>Quando</th><th>Fatto</th><th>Tipo</th><th>Ambito</th><th>Da</th></tr></thead>
            <tbody>
              {d.memorie.map((m) => (
                <tr key={m.id} style={m.sostituita_da ? { opacity: 0.6 } : undefined}>
                  <td>{m.creata ? quandoCompleto(m.creata) : "—"}</td>
                  <td>{m.contenuto}{m.sostituita_da ? " (sostituita)" : ""}</td>
                  <td>{m.tipo}</td>
                  <td>{m.campo}</td>
                  <td>{m.fonte}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function SchedaProfilo({ d }: { d: Profilo }) {
  return (
    <>
      <h3 className={comuni.campoEtichetta}>Persona</h3>
      <pre style={{ ...testo, fontSize: "0.85rem" }}>{JSON.stringify(d.persona, null, 2)}</pre>
      <h3 className={comuni.campoEtichetta}>Consensi in vigore</h3>
      {d.consensi.length === 0 ? <div className={comuni.vuoto}>Nessun consenso registrato.</div> : (
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead><tr><th>Tipo</th><th>Valore</th><th>Informativa</th><th>Da</th><th>Aggiornato</th></tr></thead>
            <tbody>
              {d.consensi.map((c) => (
                <tr key={c.tipo}><td>{c.tipo}</td><td>{c.valore}</td><td>{c.informativa}</td><td>{c.origine}</td>
                  <td>{c.aggiornato ? quandoCompleto(c.aggiornato) : "—"}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <details>
        <summary style={{ cursor: "pointer", minHeight: 44 }}>Storico dei consensi ({d.storico_consensi.length})</summary>
        {d.storico_consensi.map((c, i) => (
          <p key={i} style={testo}>{c.quando ? quandoCompleto(c.quando) : "—"} · {c.tipo}: {c.valore} ({c.origine}, informativa {c.informativa})</p>
        ))}
      </details>
      <h3 className={comuni.campoEtichetta}>Notifiche e dispositivi</h3>
      <pre style={{ ...testo, fontSize: "0.85rem" }}>{JSON.stringify({ preferenze: d.notifiche, dispositivi: d.dispositivi }, null, 2)}</pre>
    </>
  );
}
