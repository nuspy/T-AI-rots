"use client";

/* Esploratore (v8): l'incrocio libero dei dati, per gli studi che le altre pagine non prevedono.
 *
 * Si sceglie una sorgente, fino a sei misure e fino a tre dimensioni; i filtri si aggiungono a mano o
 * toccando un valore nella tabella (drill-down: il valore diventa un filtro e la dimensione lascia il
 * posto alla successiva). Tutta la vista sta nell'indirizzo, quindi si salva e si condivide con un link.
 */

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { leggiCatalogo, type Filtro, type Interrogazione, type Operatore } from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Barre, Colonne } from "../../grafici";
import { FiltriPeriodo, formatta, serie, usePeriodo, useRisultato } from "../comuni";
import { BottoniEsporta } from "../esporta";
import { PannelloAI } from "../pannello-ai";

type Vista = Omit<Interrogazione, "da" | "a">;

const PREDEFINITA: Vista = { sorgente: "visite", misure: ["sessioni", "visitatori"], dimensioni: ["canale"], filtri: [] };

const OPERATORI: Record<Operatore, string> = {
  uguale: "è",
  diverso: "non è",
  in: "è uno fra",
  non_in: "non è fra",
  contiene: "contiene",
  vuoto: "è vuoto",
  non_vuoto: "non è vuoto",
};

function leggiVista(grezza: string | null): Vista {
  if (!grezza) return PREDEFINITA;
  try {
    const v = JSON.parse(grezza) as Vista;
    return v && typeof v.sorgente === "string" && Array.isArray(v.misure) ? { filtri: [], dimensioni: [], ...v } : PREDEFINITA;
  } catch {
    return PREDEFINITA;
  }
}

export default function Esploratore() {
  const { giorni, da, a, imposta } = usePeriodo();
  const parametri = useSearchParams();
  const router = useRouter();
  const percorso = usePathname();
  const catalogo = useDati(leggiCatalogo);
  const vista = leggiVista(parametri.get("q"));
  const [nuovoFiltro, setNuovoFiltro] = useState<Filtro>({ dimensione: "", operatore: "uguale", valori: [] });
  const [proprieta, setProprieta] = useState("");

  const sorgente = catalogo.dati?.sorgenti[vista.sorgente];
  const risultato = useRisultato(sorgente ? { ...vista, da, a, limite: 200 } : null);

  const cambia = (v: Partial<Vista>) => {
    const nuova = { ...vista, ...v };
    const p = new URLSearchParams(parametri.toString());
    p.set("q", JSON.stringify(nuova));
    router.replace(`${percorso}?${p.toString()}`, { scroll: false });
  };

  const dimensioni = vista.dimensioni ?? [];
  const filtri = vista.filtri ?? [];
  const etichettaDim = (d: string) => sorgente?.dimensioni[d]?.etichetta ?? (d.startsWith("prop:") ? `proprietà «${d.slice(5)}»` : d);

  /* Il drill-down: il valore toccato diventa filtro, la dimensione esce dal raggruppamento. */
  const approfondisci = (d: string, valore: string) =>
    cambia({
      dimensioni: dimensioni.filter((x) => x !== d),
      filtri: [...filtri.filter((f) => f.dimensione !== d), { dimensione: d, operatore: "uguale", valori: [valore] }],
    });

  const cambiaSorgente = (s: string) => {
    const nuova = catalogo.dati?.sorgenti[s];
    if (!nuova) return;
    cambia({ sorgente: s, misure: Object.keys(nuova.misure).slice(0, 2), dimensioni: [], filtri: [], granularita: null });
  };

  const r = risultato.dati;
  const primaMisura = vista.misure[0];
  const formatoDi = (m: string) => sorgente?.misure[m]?.formato ?? "intero";

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Esploratore</h1>
          <p className={comuni.sottotitolo}>
            Incrocia misure e dimensioni di una sorgente. Tocca un valore della tabella per filtrarlo e scendere di livello; la
            vista resta nell&apos;indirizzo della pagina.
          </p>
        </div>
      </div>
      <FiltriPeriodo giorni={giorni} imposta={imposta} />
      {catalogo.errore && <p className={comuni.errore} role="alert">{catalogo.errore}</p>}

      {catalogo.dati && (
        <section className={comuni.riquadro} aria-label="Composizione della vista">
          <div className={comuni.riga}>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Sorgente</span>
              <select className={comuni.selezione} value={vista.sorgente} onChange={(e) => cambiaSorgente(e.target.value)}>
                {Object.entries(catalogo.dati.sorgenti).map(([k, s]) => <option key={k} value={k}>{s.etichetta}</option>)}
              </select>
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Andamento</span>
              <select className={comuni.selezione} value={vista.granularita ?? ""}
                onChange={(e) => cambia({ granularita: (e.target.value || null) as Vista["granularita"] })}>
                <option value="">Nessuno</option>
                <option value="giorno">Per giorno</option>
                <option value="settimana">Per settimana</option>
                <option value="mese">Per mese</option>
              </select>
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Confronto</span>
              <select className={comuni.selezione} value={vista.confronto ?? ""}
                onChange={(e) => cambia({ confronto: (e.target.value || null) as Vista["confronto"] })}>
                <option value="">Nessuno</option>
                <option value="precedente">Periodo precedente</option>
                <option value="anno_prima">Stesso periodo, anno prima</option>
              </select>
            </label>
          </div>
          {sorgente?.descrizione && <p className={comuni.riquadroNota}>{sorgente.descrizione}</p>}

          <fieldset style={{ border: 0, padding: 0, margin: "0.75rem 0" }}>
            <legend className={comuni.campoEtichetta}>Misure (fino a sei)</legend>
            <div className={comuni.filtri}>
              {Object.entries(sorgente?.misure ?? {}).map(([k, m]) => {
                const scelta = vista.misure.includes(k);
                return (
                  <button key={k} type="button" className={scelta ? comuni.filtroScelto : comuni.filtro} aria-pressed={scelta}
                    title={m.descrizione || undefined}
                    disabled={!scelta && vista.misure.length >= 6}
                    onClick={() => cambia({ misure: scelta ? vista.misure.filter((x) => x !== k).concat(vista.misure.length === 1 ? [k] : []) : [...vista.misure, k] })}>
                    {m.etichetta}
                  </button>
                );
              })}
            </div>
          </fieldset>

          <fieldset style={{ border: 0, padding: 0, margin: "0.75rem 0" }}>
            <legend className={comuni.campoEtichetta}>Dimensioni (fino a tre)</legend>
            <div className={comuni.filtri}>
              {Object.entries(sorgente?.dimensioni ?? {}).map(([k, d]) => {
                const scelta = dimensioni.includes(k);
                return (
                  <button key={k} type="button" className={scelta ? comuni.filtroScelto : comuni.filtro} aria-pressed={scelta}
                    title={d.personale ? "Dimensione personale: nelle analisi AI e negli export le celle con meno di 5 persone non compaiono" : d.descrizione || undefined}
                    disabled={!scelta && dimensioni.length >= 3}
                    onClick={() => cambia({ dimensioni: scelta ? dimensioni.filter((x) => x !== k) : [...dimensioni, k] })}>
                    {d.etichetta}{d.personale ? " •" : ""}
                  </button>
                );
              })}
              {dimensioni.filter((d) => d.startsWith("prop:")).map((d) => (
                <button key={d} type="button" className={comuni.filtroScelto} aria-pressed
                  onClick={() => cambia({ dimensioni: dimensioni.filter((x) => x !== d) })}>
                  {etichettaDim(d)} ✕
                </button>
              ))}
            </div>
            {sorgente?.proprieta && dimensioni.length < 3 && (
              <div className={comuni.riga}>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Proprietà dell&apos;evento</span>
                  <input className={comuni.ingresso} value={proprieta} placeholder="fase, stesa, piano…" maxLength={40}
                    onChange={(e) => setProprieta(e.target.value.replace(/[^a-zA-Z0-9_]/g, ""))} />
                </label>
                <button type="button" className={comuni.secondaria} disabled={!/^[a-zA-Z]/.test(proprieta)}
                  onClick={() => { cambia({ dimensioni: [...dimensioni, `prop:${proprieta}`] }); setProprieta(""); }}>
                  Aggiungi come dimensione
                </button>
              </div>
            )}
          </fieldset>

          <fieldset style={{ border: 0, padding: 0, margin: "0.75rem 0 0" }}>
            <legend className={comuni.campoEtichetta}>Filtri</legend>
            {filtri.length > 0 && (
              <div className={comuni.filtri}>
                {filtri.map((f, i) => (
                  <button key={i} type="button" className={comuni.filtroScelto}
                    aria-label={`Togli il filtro ${etichettaDim(f.dimensione)} ${OPERATORI[f.operatore]} ${f.valori.join(", ")}`}
                    onClick={() => cambia({ filtri: filtri.filter((_, j) => j !== i) })}>
                    {etichettaDim(f.dimensione)} {OPERATORI[f.operatore]} {f.valori.join(", ")} ✕
                  </button>
                ))}
              </div>
            )}
            <div className={comuni.riga}>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Dimensione</span>
                <select className={comuni.selezione} value={nuovoFiltro.dimensione}
                  onChange={(e) => setNuovoFiltro({ ...nuovoFiltro, dimensione: e.target.value })}>
                  <option value="">—</option>
                  {Object.entries(sorgente?.dimensioni ?? {}).map(([k, d]) => <option key={k} value={k}>{d.etichetta}</option>)}
                </select>
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Condizione</span>
                <select className={comuni.selezione} value={nuovoFiltro.operatore}
                  onChange={(e) => setNuovoFiltro({ ...nuovoFiltro, operatore: e.target.value as Operatore })}>
                  {Object.entries(OPERATORI).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                </select>
              </label>
              {!["vuoto", "non_vuoto"].includes(nuovoFiltro.operatore) && (
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Valore (più valori separati da virgola)</span>
                  <input className={comuni.ingresso} maxLength={200} value={nuovoFiltro.valori.join(",")}
                    onChange={(e) => setNuovoFiltro({ ...nuovoFiltro, valori: e.target.value.split(",").map((x) => x.trim()).filter(Boolean) })} />
                </label>
              )}
              <button type="button" className={comuni.secondaria}
                disabled={!nuovoFiltro.dimensione || (!["vuoto", "non_vuoto"].includes(nuovoFiltro.operatore) && !nuovoFiltro.valori.length)}
                onClick={() => { cambia({ filtri: [...filtri, nuovoFiltro] }); setNuovoFiltro({ dimensione: "", operatore: "uguale", valori: [] }); }}>
                Aggiungi filtro
              </button>
            </div>
          </fieldset>
        </section>
      )}

      {risultato.errore && <p className={comuni.errore} role="alert">{risultato.errore}</p>}
      {!r && risultato.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {r && (
        <div className={risultato.inCorso ? comuni.inRicarica : undefined}>
          {vista.granularita === "giorno" && dimensioni.length === 0 && (
            <Colonne titolo={sorgente?.misure[primaMisura]?.etichetta ?? primaMisura} unita={sorgente?.misure[primaMisura]?.etichetta ?? ""}
              punti={serie(r.righe, primaMisura, da, a)} />
          )}
          {!vista.granularita && dimensioni.length === 1 && (
            <Barre titolo={`${sorgente?.misure[primaMisura]?.etichetta} per ${etichettaDim(dimensioni[0]).toLowerCase()}`}
              unita={sorgente?.misure[primaMisura]?.etichetta ?? ""} formato={(n) => formatta(n, formatoDi(primaMisura))}
              barre={r.righe.slice(0, 15).map((riga) => ({ chiave: String(riga[dimensioni[0]]), etichetta: String(riga[dimensioni[0]]), valore: riga[primaMisura] === null ? null : Number(riga[primaMisura]) }))}
              onScegli={(v) => approfondisci(dimensioni[0], v)} />
          )}

          <section className={comuni.riquadro} aria-labelledby="titolo-risultato">
            <h2 id="titolo-risultato" className={comuni.riquadroTitolo}>Risultato</h2>
            <p className={comuni.riquadroNota}>
              {r.righe.length} {r.righe.length === 1 ? "riga" : "righe"}
              {r.troncato ? " (troncato: restringi con un filtro)" : ""}
              {r.confronto ? ` · confronto dal ${r.confronto.da} al ${r.confronto.a}` : ""}
            </p>
            <div className={comuni.contenitoreTabella}>
              <table className={comuni.tabella}>
                <thead>
                  <tr>
                    {r.colonne.map((c) => (
                      <th key={c.nome} className={c.tipo === "misura" ? comuni.numero : undefined}>
                        {c.tipo === "periodo" ? "Periodo" : c.etichetta}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    {r.colonne.map((c, i) => (
                      <td key={c.nome} className={c.tipo === "misura" ? comuni.numero : undefined}>
                        <strong>{c.tipo === "misura" ? formatta(r.totali[c.nome], c.formato) : i === 0 ? "Totale" : ""}</strong>
                        {c.tipo === "misura" && r.confronto && (
                          <><br /><span className={comuni.etichetta}>prima {formatta(r.confronto.totali[c.nome], c.formato)}</span></>
                        )}
                      </td>
                    ))}
                  </tr>
                  {r.righe.map((riga, i) => (
                    <tr key={i}>
                      {r.colonne.map((c) => (
                        <td key={c.nome} className={c.tipo === "misura" ? comuni.numero : undefined}>
                          {c.tipo === "dimensione" ? (
                            <button type="button" className={comuni.collegamento}
                              style={{ background: "none", border: 0, padding: 0, font: "inherit", cursor: "pointer", minHeight: 44, textAlign: "left" }}
                              onClick={() => approfondisci(c.nome, String(riga[c.nome]))}>
                              {String(riga[c.nome])}
                            </button>
                          ) : c.tipo === "periodo" ? String(riga.periodo).slice(0, 10) : formatta(riga[c.nome] as number | null, c.formato)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}
      {sorgente && (
        <>
          <BottoniEsporta vista={{ ...vista, da, a, limite: 1000 }} giorni={giorni} />
          <PannelloAI sezione="vista" titolo="questa vista" giorni={giorni} vista={{ ...vista, da, a }} />
        </>
      )}
    </>
  );
}
