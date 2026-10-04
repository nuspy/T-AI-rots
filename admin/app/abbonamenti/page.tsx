"use client";

import Link from "next/link";
import { useCallback, useState } from "react";
import { ErroreApi } from "@/lib/api";
import {
  FORNITORI_ABBONAMENTO, azioneAbbonamento, elencoAbbonamenti, type AbbonamentoConsole, type AzioneAbbonamento,
  type StatoAbbonamento,
} from "@/lib/abbonamenti";
import { quandoCompleto, soldi } from "@/lib/formato";
import { useDati, useToken } from "@/lib/usa";
import stili from "../comuni.module.css";
import propri from "./abbonamenti.module.css";

/* L'elenco degli abbonamenti (v9, Fase 2b), dal più recente, filtrabile per stato e per email.
 *
 * «In tolleranza» (`in_sospeso`) è chi ha un pagamento fallito e ha ancora le letture comprese: i solleciti partono da
 * soli al terzo e al sesto giorno, e alla fine il cron sospende. Le azioni chiedono un motivo, che resta nel Registro
 * con il prima e il dopo. Gli abbonamenti degli store non hanno azioni: si gestiscono nelle console degli store, e il
 * loro stato segue le notifiche dello store (Fase 4). Il filtro «canale» mostra solo quelli di un fornitore. */

const PER_PAGINA = 50;

const STATI: Record<StatoAbbonamento, { etichetta: string; classe: string }> = {
  in_prova: { etichetta: "in prova", classe: stili.neutro },
  attivo: { etichetta: "attivo", classe: stili.positivo },
  in_sospeso: { etichetta: "in tolleranza", classe: stili.negativo },
  sospeso: { etichetta: "sospeso", classe: stili.negativo },
  disdetto: { etichetta: "disdetto", classe: stili.spento },
  scaduto: { etichetta: "scaduto", classe: stili.spento },
};
const FILTRI: ("" | StatoAbbonamento)[] = ["", "in_prova", "attivo", "in_sospeso", "sospeso", "disdetto", "scaduto"];

const AZIONI: Record<AzioneAbbonamento, { etichetta: string; distruttiva?: boolean; giorni?: boolean }> = {
  rinnovo_spento: { etichetta: "Spegni il rinnovo" },
  rinnovo_acceso: { etichetta: "Riaccendi il rinnovo" },
  sospendi: { etichetta: "Chiudi la tolleranza", distruttiva: true },
  proroga: { etichetta: "Proroga", giorni: true },
  chiudi: { etichetta: "Chiudi subito", distruttiva: true },
};

export default function Abbonamenti() {
  const [stato, setStato] = useState<"" | StatoAbbonamento>("");
  const [provider, setProvider] = useState("");
  const [cerca, setCerca] = useState("");
  const [q, setQ] = useState("");
  const [offset, setOffset] = useState(0);
  const [aperto, setAperto] = useState<{ abbonamento: AbbonamentoConsole; azione: AzioneAbbonamento } | null>(null);

  const { dati, errore, inCorso, ricarica } = useDati(
    useCallback(
      (t: string) => elencoAbbonamenti(t, { stato, q, provider, limite: PER_PAGINA, offset }), [stato, q, provider, offset],
    ),
  );
  const totale = dati?.totale ?? 0;
  // v9, Fase 4: chi incassa. Si mostrano i fornitori che hanno almeno un abbonamento, più quello scelto.
  const fornitori = Object.keys(FORNITORI_ABBONAMENTO).filter((p) => (dati?.per_fornitore?.[p] ?? 0) > 0 || p === provider);

  return (
    <>
      {fornitori.length > 0 && (
        <div className={stili.filtri} role="group" aria-label="Chi incassa l'abbonamento">
          {["", ...fornitori].map((p) => (
            <button key={p || "tutti"} className={p === provider ? stili.filtroScelto : stili.filtro} aria-pressed={p === provider}
              onClick={() => { setProvider(p); setOffset(0); }}>
              {p ? FORNITORI_ABBONAMENTO[p] : "Ogni canale"}
              {p && dati?.per_fornitore ? ` · ${dati.per_fornitore[p] ?? 0}` : ""}
            </button>
          ))}
        </div>
      )}
      <div className={stili.filtri} role="group" aria-label="Stato dell'abbonamento">
        {FILTRI.map((f) => (
          <button key={f || "tutti"} className={f === stato ? stili.filtroScelto : stili.filtro} aria-pressed={f === stato}
            onClick={() => { setStato(f); setOffset(0); }}>
            {f ? STATI[f].etichetta : "Tutti"}
            {f && dati ? ` · ${dati.conteggi[f] ?? 0}` : ""}
          </button>
        ))}
      </div>
      <form className={propri.ricerca} onSubmit={(e) => { e.preventDefault(); setQ(cerca.trim()); setOffset(0); }}>
        <label className={stili.campo}>
          <span className={stili.campoEtichetta}>Cerca per email</span>
          <input className={stili.ingresso} value={cerca} onChange={(e) => setCerca(e.target.value)} type="search" maxLength={200} />
        </label>
        <button className={stili.secondaria} type="submit">Cerca</button>
      </form>

      {errore && <p className={stili.errore}>{errore}</p>}
      {!dati && inCorso && <p className={stili.caricamento}>Caricamento…</p>}
      {dati && (
        <div className={inCorso ? stili.inRicarica : undefined}>
          <p className={stili.riquadroNota}>{totale} {totale === 1 ? "abbonamento" : "abbonamenti"}</p>
          {dati.abbonamenti.length === 0 ? (
            <div className={stili.vuoto}>Nessun abbonamento.</div>
          ) : (
            <div className={stili.contenitoreTabella}>
              <table className={stili.tabella}>
                <thead>
                  <tr>
                    <th>Utente</th>
                    <th>Piano</th>
                    <th>Stato</th>
                    <th>Periodo</th>
                    <th>Rinnovo</th>
                    <th className={stili.numero}>Pagato</th>
                    <th>Fornitore</th>
                    <th>Azioni</th>
                  </tr>
                </thead>
                <tbody>
                  {dati.abbonamenti.map((a) => {
                    const s = STATI[a.stato] ?? { etichetta: a.stato, classe: stili.neutro };
                    return (
                      <tr key={a.id}>
                        <td>
                          <Link href={`/utenti/${a.utente.id}`} className={stili.collegamento}>{a.utente.email ?? `#${a.utente.id}`}</Link>
                        </td>
                        <td>
                          {a.nome}
                          <div className={stili.campoAiuto}>{a.annuale ? "annuale" : "mensile"}{a.prova ? " · dalla prova" : ""}</div>
                        </td>
                        <td>
                          <span className={`${stili.stato} ${s.classe}`}>{s.etichetta}</span>
                          {a.stato === "in_sospeso" && a.fine_tolleranza && (
                            <div className={stili.campoAiuto}>fino al {quandoCompleto(a.fine_tolleranza)}</div>
                          )}
                          {a.fattura_aperta && <div className={stili.campoAiuto}>fattura aperta</div>}
                        </td>
                        <td className={stili.mono}>{quandoCompleto(a.periodo_inizio)} → {quandoCompleto(a.periodo_fine)}</td>
                        <td>
                          {a.rinnovo_automatico ? `sì · ${soldi(a.prossimo_rinnovo, a.valuta)}` : "no"}
                          {a.piano_successivo && <div className={stili.campoAiuto}>poi {a.piano_successivo.nome}</div>}
                        </td>
                        <td className={stili.numero}>{soldi(a.importo_periodo, a.valuta)}</td>
                        <td>{FORNITORI_ABBONAMENTO[a.provider] ?? a.provider}</td>
                        <td>
                          <div className={propri.azioni}>
                            {a.azioni.length === 0 && <span className={stili.campoAiuto}>{a.store ? "nello store" : "—"}</span>}
                            {a.azioni.map((z) => (
                              <button key={z} type="button" className={AZIONI[z].distruttiva ? stili.distruttiva : stili.secondaria}
                                onClick={() => setAperto({ abbonamento: a, azione: z })}>{AZIONI[z].etichetta}</button>
                            ))}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          <div className={stili.paginazione}>
            <span>{totale ? `${offset + 1}–${Math.min(offset + PER_PAGINA, totale)} di ${totale}` : ""}</span>
            <div className={stili.paginazioneComandi}>
              <button className={stili.secondaria} disabled={offset === 0 || inCorso} onClick={() => setOffset((o) => Math.max(0, o - PER_PAGINA))}>Precedenti</button>
              <button className={stili.secondaria} disabled={offset + PER_PAGINA >= totale || inCorso} onClick={() => setOffset((o) => o + PER_PAGINA)}>Successivi</button>
            </div>
          </div>
        </div>
      )}

      {aperto && (
        <Azione abbonamento={aperto.abbonamento} azione={aperto.azione}
          onChiudi={() => setAperto(null)} onFatto={() => { setAperto(null); ricarica(); }} />
      )}
    </>
  );
}

function Azione({ abbonamento, azione, onChiudi, onFatto }: {
  abbonamento: AbbonamentoConsole; azione: AzioneAbbonamento; onChiudi: () => void; onFatto: () => void;
}) {
  const token = useToken();
  const [motivo, setMotivo] = useState("");
  const [giorni, setGiorni] = useState("7");
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);
  const dati = AZIONI[azione];

  const conferma = async () => {
    if (token === null) return;
    setInCorso(true); setErrore(null);
    try {
      await azioneAbbonamento(token, abbonamento.id, azione, motivo.trim(), dati.giorni ? Number(giorni) : undefined);
      onFatto();
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "Azione non riuscita");
    } finally {
      setInCorso(false);
    }
  };

  return (
    <section className={`${stili.riquadro} ${propri.azione}`} aria-labelledby="azione-t">
      <h2 id="azione-t" className={stili.riquadroTitolo}>{dati.etichetta} · {abbonamento.utente.email ?? `#${abbonamento.utente.id}`} · {abbonamento.nome}</h2>
      {azione === "chiudi" && (
        <p className={stili.avviso}>Chiude adesso, presso il fornitore e qui, <strong>senza rimborso</strong>: se è dovuto, si fa dal Dashboard del fornitore.</p>
      )}
      {azione === "rinnovo_spento" && <p className={stili.riquadroNota}>L&apos;utente riceve l&apos;email di conferma della disdetta.</p>}
      {dati.giorni && (
        <label className={stili.campo}>
          <span className={stili.campoEtichetta}>Giorni in più</span>
          <input className={stili.ingresso} type="number" min={1} max={366} value={giorni} onChange={(e) => setGiorni(e.target.value)} />
        </label>
      )}
      <label className={stili.campo}>
        <span className={stili.campoEtichetta}>Motivo (resta nel Registro)</span>
        <input className={stili.ingresso} value={motivo} onChange={(e) => setMotivo(e.target.value)} maxLength={500} />
      </label>
      {errore && <p className={stili.errore}>{errore}</p>}
      <div className={stili.riga}>
        <button type="button" className={dati.distruttiva ? stili.distruttiva : stili.primaria} disabled={inCorso || motivo.trim().length < 3}
          onClick={conferma}>Conferma</button>
        <button type="button" className={stili.secondaria} onClick={onChiudi}>Annulla</button>
      </div>
    </section>
  );
}
