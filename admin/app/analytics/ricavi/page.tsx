"use client";

/* Ricavi (v8): quanto entra, da cosa, da chi — e le coorti: di chi si è iscritto in un mese, quanti
 * tornano a leggere (o quanto spendono) nei mesi dopo.
 *
 * I ricavi vengono dalle tabelle dei pagamenti, non dagli eventi: sono la verità contabile (importi
 * dopo gli sconti). I rinnovi automatici degli abbonamenti non sono ancora conteggiati qui.
 */

import { useCallback, useState } from "react";
import { calcolaCoorti } from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Barre, Colonne, Tessera, percento } from "../../grafici";
import grafici from "../../grafici.module.css";
import stili from "../../statistiche.module.css";
import { FiltriPeriodo, barreDa, etichettaPeriodo, formatta, serie, useApprofondisci, usePeriodo, useRisultato, useSegni } from "../comuni";
import { BottoniEsporta } from "../esporta";
import { PannelloAI } from "../pannello-ai";

const euro = (n: number) => formatta(n, "euro");

const TIPI_COORTE: Record<string, string> = {
  letture: "Tornano a leggere",
  visite: "Tornano sul sito",
  spesa: "Spesa cumulata (€)",
};

export default function Ricavi() {
  const { giorni, da, a, imposta } = usePeriodo();
  const segni = useSegni(da, a);
  const approfondisci = useApprofondisci(giorni);
  const acquisti = useRisultato({ da, a, sorgente: "acquisti", misure: ["ricavi", "acquisti", "clienti", "valore_medio", "sconti"], confronto: "precedente" });
  const ordini = useRisultato({ da, a, sorgente: "ordini", misure: ["ricavi", "ordini", "clienti"], confronto: "precedente" });
  const andamentoA = useRisultato({ da, a, sorgente: "acquisti", misure: ["ricavi"], granularita: "giorno", limite: 400 });
  const andamentoO = useRisultato({ da, a, sorgente: "ordini", misure: ["ricavi"], granularita: "giorno", limite: 400 });
  const perPiano = useRisultato({ da, a, sorgente: "acquisti", misure: ["ricavi", "acquisti"], dimensioni: ["piano"], limite: 12 });
  const perCanale = useRisultato({ da, a, sorgente: "acquisti", misure: ["ricavi"], dimensioni: ["primo_canale"], limite: 12 });
  const perEta = useRisultato({ da, a, sorgente: "acquisti", misure: ["ricavi"], dimensioni: ["fascia_eta"], limite: 12 });

  const [tipo, setTipo] = useState("letture");
  const coorti = useDati(useCallback((t: string) => calcolaCoorti(t, { tipo, granularita: "mese", periodi: 12 }), [tipo]));

  const ta = acquisti.dati?.totali;
  const pa = acquisti.dati?.confronto?.totali;
  const to = ordini.dati?.totali;
  const po = ordini.dati?.confronto?.totali;
  const totale = ta && to ? Number(ta.ricavi) + Number(to.ricavi) : null;
  const totalePrima = pa && po ? Number(pa.ricavi) + Number(po.ricavi) : null;

  const puntiA = serie(andamentoA.dati?.righe, "ricavi", da, a);
  const puntiO = serie(andamentoO.dati?.righe, "ricavi", da, a);
  const punti = puntiA.map((p, i) => ({ ...p, valore: Math.round((p.valore + (puntiO[i]?.valore ?? 0)) * 100) / 100 }));

  const tocca = (d: string) => (v: string) => approfondisci("acquisti", ["ricavi", "acquisti", "clienti"], d, v, d === "piano" ? "primo_canale" : "piano");

  // Il colore delle celle dice la quota rispetto alla coorte (un tono solo, più scuro = di più); il numero
  // resta scritto in ogni cella, perché il colore da solo non basta.
  const massimoSpesa = Math.max(1, ...(coorti.dati?.coorti ?? []).flatMap((c) => c.valori.map((v) => v / Math.max(1, c.dimensione))));
  const intensita = (v: number, n: number) => (coorti.dati?.somma ? v / n / massimoSpesa : v / Math.max(1, n));

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Ricavi</h1>
          <p className={comuni.sottotitolo}>
            Pacchetti, abbonamenti e ordini del negozio pagati nel periodo, dopo gli sconti. I rinnovi automatici non sono
            ancora conteggiati.
          </p>
        </div>
      </div>
      <FiltriPeriodo giorni={giorni} imposta={imposta} />
      {(acquisti.errore || ordini.errore) && <p className={comuni.errore} role="alert">{acquisti.errore ?? ordini.errore}</p>}
      {!acquisti.dati && acquisti.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {ta && to && (
        <div className={acquisti.inCorso ? comuni.inRicarica : undefined}>
          <div className={grafici.tessere}>
            <Tessera etichetta="Ricavi totali" valore={totale} precedente={totalePrima} formato={euro} />
            <Tessera etichetta="Pacchetti e abbonamenti" valore={Number(ta.ricavi)} precedente={pa ? Number(pa.ricavi) : null}
              formato={euro} nota={`${formatta(Number(ta.acquisti))} acquisti`} />
            <Tessera etichetta="Negozio" valore={Number(to.ricavi)} precedente={po ? Number(po.ricavi) : null}
              formato={euro} nota={`${formatta(Number(to.ordini))} ordini`} />
            <Tessera etichetta="Clienti" valore={Number(ta.clienti)} precedente={pa ? Number(pa.clienti) : null}
              nota="di pacchetti e abbonamenti" />
            <Tessera etichetta="Valore medio" valore={ta.valore_medio === null ? null : Number(ta.valore_medio)}
              precedente={pa?.valore_medio ?? null} formato={euro} />
            <Tessera etichetta="Sconti concessi" valore={Number(ta.sconti)} precedente={pa ? Number(pa.sconti) : null}
              formato={euro} meglio="giu" />
          </div>

          <Colonne segni={segni} titolo="Ricavi al giorno (€)" descrizione={`${etichettaPeriodo(giorni)}, pacchetti, abbonamenti e negozio insieme.`}
            unita="€" punti={punti} />

          <div className={stili.coppie}>
            <Barre titolo="Per piano" unita="€" formato={euro} barre={barreDa(perPiano.dati, "piano", "ricavi")} onScegli={tocca("piano")}
              colonneTabella={[{ titolo: "acquisti", valori: (perPiano.dati?.righe ?? []).map((r) => formatta(Number(r.acquisti))) }]} />
            <Barre titolo="Per primo canale del cliente" unita="€" formato={euro}
              barre={barreDa(perCanale.dati, "primo_canale", "ricavi")} onScegli={tocca("primo_canale")} />
            <Barre titolo="Per fascia d'età" unita="€" formato={euro} barre={barreDa(perEta.dati, "fascia_eta", "ricavi")}
              onScegli={tocca("fascia_eta")} />
          </div>
        </div>
      )}

      <section className={comuni.riquadro} aria-labelledby="titolo-coorti">
        <h2 id="titolo-coorti" className={comuni.riquadroTitolo}>Coorti di iscrizione</h2>
        <p className={comuni.riquadroNota}>
          Una riga per mese d&apos;iscrizione; le colonne sono i mesi successivi (0 = il mese stesso).
          {coorti.dati?.somma ? " Ogni cella: euro spesi in quel mese dagli iscritti della riga." : " Ogni cella: quanti degli iscritti della riga sono attivi in quel mese."}
        </p>
        <div className={comuni.filtri} role="group" aria-label="Tipo di coorte">
          {Object.entries(TIPI_COORTE).map(([k, v]) => (
            <button key={k} className={k === tipo ? comuni.filtroScelto : comuni.filtro} aria-pressed={k === tipo} onClick={() => setTipo(k)}>
              {v}
            </button>
          ))}
        </div>
        {coorti.errore && <p className={comuni.errore} role="alert">{coorti.errore}</p>}
        {coorti.dati && coorti.dati.coorti.length === 0 && <p className={comuni.vuoto}>Nessun iscritto ancora.</p>}
        {coorti.dati && coorti.dati.coorti.length > 0 && (
          <div className={`${comuni.contenitoreTabella} ${coorti.inCorso ? comuni.inRicarica : ""}`}>
            <table className={comuni.tabella}>
              <thead>
                <tr>
                  <th>Mese</th>
                  <th className={comuni.numero}>Iscritti</th>
                  {coorti.dati.coorti[0].valori.map((_, i) => <th key={i} className={comuni.numero}>+{i}</th>)}
                </tr>
              </thead>
              <tbody>
                {coorti.dati.coorti.map((c) => (
                  <tr key={c.coorte}>
                    <td>{c.coorte.slice(0, 7)}</td>
                    <td className={comuni.numero}>{formatta(c.dimensione)}</td>
                    {c.valori.map((v, i) => (
                      <td key={i} className={comuni.numero}
                        style={v ? { background: `color-mix(in srgb, var(--rubrica) ${Math.round(Math.min(1, intensita(v, c.dimensione)) * 55)}%, transparent)` } : undefined}
                        title={coorti.dati!.somma ? euro(v) : `${v} su ${c.dimensione} (${percento(v / Math.max(1, c.dimensione))})`}>
                        {v ? (coorti.dati!.somma ? euro(v) : percento(v / Math.max(1, c.dimensione))) : "·"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <BottoniEsporta collezione="ricavi" giorni={giorni} />
      <PannelloAI sezione="ricavi" titolo="Ricavi" giorni={giorni} />
    </>
  );
}
