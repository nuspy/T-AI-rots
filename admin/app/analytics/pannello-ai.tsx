"use client";

/* L'interpretazione AI di una sezione (v8).
 *
 * Un clic, una chiamata al modello scelto in «Modelli → Interpretazione dei dati». Il modello riceve
 * solo fatti numerati già calcolati (aggregati, gruppi di almeno 5 persone) e deve citarli: ogni voce
 * dice se i suoi numeri tornano con i fatti («verificata») o no. Una voce non verificata resta
 * visibile ma segnata, e non entra nel rapporto email.
 *
 * Il giudizio (utile / non utile) e l'azione decisa restano con l'analisi: l'azione rientra nel
 * contesto della prossima analisi della stessa sezione, così il modello sa cosa si è già provato.
 */

import { useCallback, useState } from "react";
import {
  analizza, annotaAnalisi, storicoAnalisi, type Analisi, type Interrogazione, type VoceAnalisi,
} from "@/lib/analytics";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";

const TITOLI: [keyof Pick<NonNullable<Analisi["risposta"]>, "osservazioni" | "collegamenti" | "ipotesi" | "azioni">, string][] = [
  ["collegamenti", "Collegamenti fra i dati"],
  ["osservazioni", "Osservazioni"],
  ["ipotesi", "Ipotesi da verificare"],
  ["azioni", "Azioni proposte"],
];

function Voce({ voce, fatti }: { voce: VoceAnalisi; fatti: Map<string, string> }) {
  const etichette = [
    voce.importanza && `importanza ${voce.importanza}`,
    voce.confidenza && `confidenza ${voce.confidenza}`,
    voce.impatto && `impatto ${voce.impatto}`,
    voce.sforzo && `sforzo ${voce.sforzo}`,
  ].filter(Boolean);
  return (
    <li style={{ marginBottom: "0.75rem" }}>
      {voce.titolo && <strong>{voce.titolo}. </strong>}
      {voce.testo}{" "}
      <span className={`${comuni.stato} ${voce.verificato ? comuni.positivo : comuni.negativo}`}>
        {voce.verificato ? "✓ verificata" : "✗ da verificare"}
      </span>
      {etichette.length > 0 && <span className={comuni.etichetta}> · {etichette.join(" · ")}</span>}
      {voce.verifica && <div className={comuni.riquadroNota}>Come verificarla: {voce.verifica}</div>}
      {voce.metrica && <div className={comuni.riquadroNota}>Metrica: {voce.metrica}</div>}
      {voce.numeri_non_trovati.length > 0 && (
        <div className={comuni.riquadroNota}>Numeri non presenti nei dati: {voce.numeri_non_trovati.join(", ")}</div>
      )}
      {voce.fatti.length > 0 && (
        <details>
          <summary className={comuni.etichetta}>Dati citati ({voce.fatti.join(", ")})</summary>
          <ul style={{ margin: "0.25rem 0 0", paddingLeft: "1.25rem" }}>
            {voce.fatti.map((id) => <li key={id}><span className={comuni.mono}>{id}</span> {fatti.get(id)}</li>)}
          </ul>
        </details>
      )}
    </li>
  );
}

export function PannelloAI({ sezione, giorni, vista, titolo }: {
  sezione: string;
  giorni: number;
  vista?: Interrogazione;
  titolo: string;
}) {
  const storico = useDati(useCallback((t: string) => storicoAnalisi(t, sezione), [sezione]));
  const { esegui, inCorso, errore } = useAzione();
  const [nuova, setNuova] = useState<Analisi | null>(null);
  const [azione, setAzione] = useState<string | null>(null);
  const analisi = nuova ?? storico.dati?.[0] ?? null;
  const r = analisi?.risposta;
  const fatti = new Map((analisi?.fatti ?? []).map((f) => [f.id, `(${f.sezione}) ${f.testo}`]));

  const chiedi = async () => {
    const esito = await esegui((t) => analizza(t, { sezione, giorni, vista }));
    if (esito) {
      setNuova(esito);
      setAzione(null);
    }
  };
  const annota = async (a: { giudizio?: -1 | 1 | null; azione_adottata?: string | null }) => {
    if (!analisi) return;
    const esito = await esegui((t) => annotaAnalisi(t, analisi.id, a));
    if (esito) setNuova(esito);
  };

  return (
    <section className={comuni.riquadro} aria-labelledby={`ai-${sezione}`} style={{ marginTop: "1.5rem" }}>
      <div className={comuni.intestazione} style={{ marginBottom: "0.5rem" }}>
        <div>
          <h2 id={`ai-${sezione}`} className={comuni.riquadroTitolo}>Interpretazione AI · {titolo}</h2>
          <p className={comuni.riquadroNota}>
            Il modello scelto in Modelli → «Interpretazione dei dati» legge i numeri di questa sezione ({giorni} giorni,
            col periodo precedente) e li mette in relazione. Riceve solo totali di gruppi di almeno 5 persone.
          </p>
        </div>
        <button className={comuni.primaria} onClick={chiedi} disabled={inCorso}>
          {inCorso ? "Analisi in corso…" : analisi ? "Nuova analisi" : "Analizza con AI"}
        </button>
      </div>

      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {!analisi && !storico.inCorso && !inCorso && (
        <div className={comuni.vuoto}>Nessuna analisi ancora per questa sezione.</div>
      )}
      {analisi && (
        <div className={inCorso ? comuni.inRicarica : undefined} aria-live="polite">
          <p className={comuni.etichetta}>
            {quandoCompleto(analisi.creata_il)} · dal {analisi.parametri.da} al {analisi.parametri.a}
            {analisi.modello ? ` · ${analisi.modello}` : ""}
            {analisi.durata_ms ? ` · ${(analisi.durata_ms / 1000).toFixed(1)} s` : ""}
            {r ? ` · ${r.verifica.verificate} voci verificate su ${r.verifica.voci}` : ""}
          </p>
          {analisi.errore && <p className={comuni.errore}>Il modello non ha risposto: {analisi.errore}</p>}
          {r && (
            <>
              <p style={{ fontSize: "1.05rem" }}>
                {r.sintesi}{" "}
                {!r.sintesi_verificata && <span className={`${comuni.stato} ${comuni.negativo}`}>✗ numeri da verificare</span>}
              </p>
              {TITOLI.map(([chiave, etichetta]) => r[chiave].length > 0 && (
                <div key={chiave}>
                  <h3 className={comuni.campoEtichetta} style={{ marginTop: "1rem" }}>{etichetta}</h3>
                  <ul style={{ paddingLeft: "1.25rem", margin: 0 }}>
                    {r[chiave].map((v, i) => <Voce key={i} voce={v} fatti={fatti} />)}
                  </ul>
                </div>
              ))}
              {r.dati_mancanti.length > 0 && (
                <>
                  <h3 className={comuni.campoEtichetta} style={{ marginTop: "1rem" }}>Cosa manca nei dati</h3>
                  <ul style={{ paddingLeft: "1.25rem", margin: 0 }}>{r.dati_mancanti.map((d, i) => <li key={i}>{d}</li>)}</ul>
                </>
              )}
              {r.avvertenze.length > 0 && (
                <>
                  <h3 className={comuni.campoEtichetta} style={{ marginTop: "1rem" }}>Avvertenze</h3>
                  <ul style={{ paddingLeft: "1.25rem", margin: 0 }}>{r.avvertenze.map((d, i) => <li key={i}>{d}</li>)}</ul>
                </>
              )}
              <details style={{ marginTop: "1rem" }}>
                <summary className={comuni.etichetta}>Tutti i dati dati al modello ({analisi.fatti.length})</summary>
                <ul style={{ paddingLeft: "1.25rem" }}>
                  {analisi.fatti.map((f) => <li key={f.id}><span className={comuni.mono}>{f.id}</span> ({f.sezione}) {f.testo}</li>)}
                </ul>
              </details>

              <div className={comuni.riga} role="group" aria-label="Giudizio sull'analisi" style={{ marginTop: "1rem" }}>
                <button className={analisi.giudizio === 1 ? comuni.primaria : comuni.secondaria} aria-pressed={analisi.giudizio === 1}
                  disabled={inCorso} onClick={() => annota({ giudizio: analisi.giudizio === 1 ? null : 1 })}>
                  Utile
                </button>
                <button className={analisi.giudizio === -1 ? comuni.primaria : comuni.secondaria} aria-pressed={analisi.giudizio === -1}
                  disabled={inCorso} onClick={() => annota({ giudizio: analisi.giudizio === -1 ? null : -1 })}>
                  Non utile
                </button>
              </div>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Cosa hai deciso di fare (entra nella prossima analisi)</span>
                <textarea className={comuni.area} maxLength={1000} rows={2}
                  value={azione ?? analisi.azione_adottata ?? ""} onChange={(e) => setAzione(e.target.value)} />
              </label>
              <button className={comuni.secondaria} disabled={inCorso || azione === null}
                onClick={() => annota({ azione_adottata: azione })}>
                Salva la decisione
              </button>
            </>
          )}
        </div>
      )}
    </section>
  );
}
