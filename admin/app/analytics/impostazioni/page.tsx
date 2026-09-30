"use client";

/* Impostazioni degli analytics (v8): il contesto che l'interpretazione AI riceve a ogni analisi, il
 * calendario delle annotazioni e gli obiettivi. Il contesto: più è concreto (obiettivi, campagne in corso,
 * cambi recenti al sito), più le analisi sono utili. */

import { useState } from "react";
import { leggiImpostazioni, scriviImpostazioni } from "@/lib/analytics";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Calendario, Obiettivi } from "./calendario-obiettivi";

export default function ImpostazioniAnalytics() {
  const impostazioni = useDati(leggiImpostazioni);
  const { esegui, inCorso, errore } = useAzione();
  const [testo, setTesto] = useState<string | null>(null);
  const [salvato, setSalvato] = useState(false);
  const valore = testo ?? impostazioni.dati?.contesto_ai ?? "";

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Impostazioni degli analytics</h1>
          <p className={comuni.sottotitolo}>
            Il contesto del business che accompagna ogni interpretazione AI. Il modello da usare si sceglie in Modelli →
            «Interpretazione dei dati».
          </p>
        </div>
      </div>
      {(impostazioni.errore || errore) && <p className={comuni.errore} role="alert">{errore ?? impostazioni.errore}</p>}
      <section className={comuni.riquadro}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Contesto per l&apos;AI</span>
          <textarea className={comuni.area} rows={8} maxLength={4000} value={valore}
            placeholder="Obiettivi del trimestre, campagne in corso e dal quando, cambi al sito, prezzi, mercati su cui puntare…"
            onChange={(e) => { setTesto(e.target.value); setSalvato(false); }} />
          <span className={comuni.campoAiuto}>{valore.length} / 4000 caratteri. Non scrivere dati di singole persone.</span>
        </label>
        <div className={comuni.riga}>
          <button className={comuni.primaria} disabled={inCorso || testo === null} onClick={async () => {
            if (await esegui((t) => scriviImpostazioni(t, valore))) {
              setTesto(null);
              setSalvato(true);
              impostazioni.ricarica();
            }
          }}>
            Salva
          </button>
          {salvato && <span role="status">Salvato.</span>}
        </div>
      </section>
      <Calendario />
      <Obiettivi />
    </>
  );
}
