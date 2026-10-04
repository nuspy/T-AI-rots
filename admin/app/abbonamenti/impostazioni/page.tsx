"use client";

import { useCallback, useState } from "react";
import { ErroreApi } from "@/lib/api";
import { leggiImpostazioniAbbonamenti, scriviImpostazioniAbbonamenti, type ImpostazioniAbbonamenti } from "@/lib/abbonamenti";
import { useDati, useToken } from "@/lib/usa";
import stili from "../../comuni.module.css";
import propri from "../abbonamenti.module.css";

/* Le regole degli abbonamenti (v9, Fase 2b). Valgono da adesso: un abbonamento già aperto tiene lo sconto che ha
 * (presso Stripe è un coupon sull'abbonamento), una prova già partita la sua durata. Ogni salvataggio resta nel
 * Registro con il prima e il dopo. */

type Campo = Exclude<keyof ImpostazioniAbbonamenti, "banner_prova">;

const CAMPI: { campo: Campo; etichetta: string; aiuto: string; min: number; max: number; unita: string }[] = [
  { campo: "sconto_rinnovo", etichetta: "Sconto del rinnovo automatico", aiuto: "Sul prezzo di ogni periodo finché il rinnovo automatico è acceso. Predefinito 20%.", min: 0, max: 90, unita: "%" },
  { campo: "sconto_prova", etichetta: "Sconto della prova, per sempre", aiuto: "L'annuale in cui si converte la prova gratuita. Predefinito 50%.", min: 0, max: 90, unita: "%" },
  { campo: "giorni_prova", etichetta: "Durata della prova", aiuto: "Giorni gratuiti col metodo di pagamento registrato. Predefinito 14.", min: 1, max: 60, unita: "giorni" },
  { campo: "giorni_promemoria_prova", etichetta: "Promemoria prima della fine della prova", aiuto: "L'email (e la notifica, dalla Fase 5) con data e importo. Predefinito 2.", min: 1, max: 7, unita: "giorni" },
  { campo: "giorni_tolleranza", etichetta: "Tolleranza dopo un pagamento fallito", aiuto: "Letture comprese ancora attive; solleciti al 3° e al 6° giorno, poi la sospensione. Tenerla allineata ai tentativi impostati nel Dashboard di Stripe. Predefinito 7.", min: 1, max: 30, unita: "giorni" },
  { campo: "condoni_per_periodo", etichetta: "Letture regalate oltre un limite", aiuto: "Per ogni limite (giorno, settimana, mese, totali) e per ogni suo periodo. Predefinito 2.", min: 0, max: 10, unita: "letture" },
];

export default function ImpostazioniAbbonamentiPagina() {
  const { dati, errore, inCorso, ricarica } = useDati(useCallback((t: string) => leggiImpostazioniAbbonamenti(t), []));
  return (
    <>
      {errore && <p className={stili.errore}>{errore}</p>}
      {!dati && inCorso && <p className={stili.caricamento}>Caricamento…</p>}
      {dati && <Modulo iniziali={dati} suSalvato={ricarica} />}
    </>
  );
}

function Modulo({ iniziali, suSalvato }: { iniziali: ImpostazioniAbbonamenti; suSalvato: () => void }) {
  const token = useToken();
  const [valori, setValori] = useState<Record<Campo, string>>(
    () => Object.fromEntries(CAMPI.map((c) => [c.campo, String(iniziali[c.campo])])) as Record<Campo, string>,
  );
  const [banner, setBanner] = useState(iniziali.banner_prova);
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);
  const [esito, setEsito] = useState<string | null>(null);

  const salva = async () => {
    if (token === null) return;
    const campi: Partial<ImpostazioniAbbonamenti> = { banner_prova: banner };
    for (const c of CAMPI) {
      const n = Number(valori[c.campo]);
      if (!Number.isInteger(n) || n < c.min || n > c.max) {
        setErrore(`«${c.etichetta}»: un intero da ${c.min} a ${c.max}.`);
        return;
      }
      campi[c.campo] = n;
    }
    setInCorso(true); setErrore(null); setEsito(null);
    try {
      await scriviImpostazioniAbbonamenti(token, campi);
      setEsito("Salvato. Vale da adesso per i nuovi pagamenti e i rinnovi.");
      suSalvato();
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "Salvataggio non riuscito");
    } finally {
      setInCorso(false);
    }
  };

  return (
    <section className={stili.riquadro} aria-labelledby="regole-t">
      <h2 id="regole-t" className={stili.riquadroTitolo}>Regole degli abbonamenti</h2>
      <div className={propri.griglia}>
        {CAMPI.map((c) => (
          <label key={c.campo} className={stili.campo}>
            <span className={stili.campoEtichetta}>{c.etichetta} ({c.unita})</span>
            <input className={stili.ingresso} type="number" inputMode="numeric" min={c.min} max={c.max} value={valori[c.campo]}
              onChange={(e) => setValori((v) => ({ ...v, [c.campo]: e.target.value }))} />
            <span className={stili.campoAiuto}>{c.aiuto}</span>
          </label>
        ))}
      </div>
      <label className={propri.interruttore}>
        <input type="checkbox" checked={banner} onChange={(e) => setBanner(e.target.checked)} />
        <span>
          <strong>Banner della prova su tutte le pagine del sito</strong>
          <span className={stili.campoAiuto}> — per i visitatori e per chi non ha un abbonamento né ha già usato la prova. Non compare finché i pagamenti non sono attivi.</span>
        </span>
      </label>
      {errore && <p className={stili.errore}>{errore}</p>}
      {esito && <p className={stili.esito} role="status">{esito}</p>}
      <div className={stili.riga}>
        <button type="button" className={stili.primaria} disabled={inCorso} onClick={salva}>Salva</button>
      </div>
    </section>
  );
}
