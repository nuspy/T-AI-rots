"use client";

/* I pulsanti di export (v8): la vista corrente in CSV o Excel (esattamente ciò che si vede, totali
 * compresi), oppure la collezione della pagina come Excel con un foglio per tabella. */

import { esportaCollezione, esportaVista, type Interrogazione } from "@/lib/analytics";
import { useAzione } from "@/lib/usa";
import comuni from "../comuni.module.css";

export function BottoniEsporta({ vista, collezione, giorni }: {
  vista?: Interrogazione | null;
  collezione?: string;
  giorni: number;
}) {
  const { esegui, inCorso, errore } = useAzione();
  return (
    <div className={comuni.riga} role="group" aria-label="Esporta">
      {vista && (
        <>
          <button className={comuni.secondaria} disabled={inCorso} onClick={() => esegui((t) => esportaVista(t, vista, "csv"))}>
            Scarica CSV
          </button>
          <button className={comuni.secondaria} disabled={inCorso} onClick={() => esegui((t) => esportaVista(t, vista, "xlsx"))}>
            Scarica Excel
          </button>
        </>
      )}
      {collezione && (
        <button className={comuni.secondaria} disabled={inCorso} onClick={() => esegui((t) => esportaCollezione(t, collezione, giorni))}>
          {inCorso ? "Preparazione…" : "Scarica tutte le tabelle (Excel)"}
        </button>
      )}
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
    </div>
  );
}
