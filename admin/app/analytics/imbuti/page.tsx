"use client";

/* Imbuti (v8): quante visite (o iscritti) compiono ogni passo, in ordine, e dove si perdono.
 * Un passo conta solo se avviene dopo il precedente. Il passo con la perdita più grande è scritto
 * in chiaro sopra il grafico: è la prima cosa da guardare. */

import { useCallback, useState } from "react";
import { calcolaImbuto, leggiCatalogo } from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Barre, percento } from "../../grafici";
import { FiltriPeriodo, formatta, usePeriodo } from "../comuni";
import { PannelloAI } from "../pannello-ai";

const SEGMENTI: Record<string, string> = {
  "": "Nessuno",
  canale: "Canale",
  dispositivo: "Dispositivo",
  paese: "Paese",
  utm_campagna: "Campagna",
  lingua: "Lingua",
};

export default function Imbuti() {
  const { giorni, da, a, imposta } = usePeriodo();
  const catalogo = useDati(leggiCatalogo);
  const [scelto, setScelto] = useState("lettura");
  const [segmento, setSegmento] = useState("");
  const per = catalogo.dati?.imbuti[scelto]?.per ?? "sessione";
  const esito = useDati(
    useCallback(
      (t: string) => calcolaImbuto(t, { imbuto: scelto, da, a, segmento: per === "sessione" && segmento ? segmento : null }),
      [scelto, da, a, segmento, per],
    ),
  );

  const passi = esito.dati?.passi ?? [];
  const perdita = passi
    .map((p, i) => ({ i, p, calo: i && p.dal_precedente !== null ? 1 - p.dal_precedente : -1 }))
    .filter((x) => x.i > 0)
    .sort((x, y) => y.calo - x.calo)[0];

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Imbuti</h1>
          <p className={comuni.sottotitolo}>
            Quante {per === "sessione" ? "visite" : "persone iscritte"} arrivano a ogni passo, nell&apos;ordine. Le fasi
            della lettura vengono dal browser: chi blocca gli script non c&apos;è.
          </p>
        </div>
      </div>
      <FiltriPeriodo giorni={giorni} imposta={imposta} />

      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Imbuto</span>
          <select className={comuni.selezione} value={scelto} onChange={(e) => setScelto(e.target.value)}>
            {Object.entries(catalogo.dati?.imbuti ?? { lettura: { etichetta: "Lettura" } }).map(([k, v]) => (
              <option key={k} value={k}>{v.etichetta}</option>
            ))}
          </select>
        </label>
        {per === "sessione" && (
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Dividi per</span>
            <select className={comuni.selezione} value={segmento} onChange={(e) => setSegmento(e.target.value)}>
              {Object.entries(SEGMENTI).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </label>
        )}
      </div>

      {esito.errore && <p className={comuni.errore} role="alert">{esito.errore}</p>}
      {!esito.dati && esito.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {esito.dati && (
        <div className={esito.inCorso ? comuni.inRicarica : undefined}>
          {passi[0]?.n ? (
            perdita && perdita.calo > 0 && (
              <p className={comuni.avviso} role="status">
                <strong>La perdita più grande</strong>: da «{passi[perdita.i - 1].etichetta}» a «{perdita.p.etichetta}» si
                ferma il {percento(perdita.calo)} ({formatta(passi[perdita.i - 1].n - perdita.p.n)} su {formatta(passi[perdita.i - 1].n)}).
              </p>
            )
          ) : (
            <div className={comuni.vuoto}>Nessuno ha iniziato questo percorso nel periodo.</div>
          )}

          <Barre
            titolo={esito.dati.etichetta}
            descrizione={`Conteggio per passo; accanto la quota rispetto al primo passo e al precedente.`}
            unita={per === "sessione" ? "visite" : "persone"}
            barre={passi.map((p, i) => ({
              chiave: `${i}`,
              etichetta: p.etichetta,
              valore: p.n,
              dettaglio: i === 0 ? "partenza" : `${percento(p.dal_primo)} dal primo · ${percento(p.dal_precedente)} dal precedente`,
            }))}
          />

          {esito.dati.segmenti && esito.dati.segmenti.length > 0 && (
            <section className={comuni.riquadro} aria-labelledby="titolo-segmenti">
              <h2 id="titolo-segmenti" className={comuni.riquadroTitolo}>Per {SEGMENTI[segmento]?.toLowerCase()}</h2>
              <p className={comuni.riquadroNota}>Arrivo all&apos;ultimo passo rispetto al primo, per ogni valore.</p>
              <div className={comuni.contenitoreTabella}>
                <table className={comuni.tabella}>
                  <thead>
                    <tr>
                      <th>{SEGMENTI[segmento]}</th>
                      {passi.map((p, i) => <th key={i} className={comuni.numero}>{p.etichetta}</th>)}
                      <th className={comuni.numero}>Fino in fondo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {esito.dati.segmenti.map((s) => (
                      <tr key={s.valore}>
                        <td>{s.valore}</td>
                        {s.passi.map((p, i) => <td key={i} className={comuni.numero}>{formatta(p.n)}</td>)}
                        <td className={comuni.numero}>{percento(s.passi[s.passi.length - 1]?.dal_primo)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </div>
      )}
      <PannelloAI sezione="imbuti" titolo="Imbuti" giorni={giorni} />
    </>
  );
}
