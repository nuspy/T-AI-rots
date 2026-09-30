"use client";

/* Gli obiettivi configurati in Impostazioni (v8): quante visite li raggiungono, che quota delle visite
 * sono, e il confronto col periodo precedente di pari durata. */

import Link from "next/link";
import { useCallback } from "react";
import { risultatiObiettivi } from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import { formatta } from "./comuni";

export function RiquadroObiettivi({ giorni }: { giorni: number }) {
  const r = useDati(useCallback((t: string) => risultatiObiettivi(t, giorni), [giorni]), [giorni]);
  const elenco = r.dati?.obiettivi ?? [];
  return (
    <section className={comuni.riquadro} aria-labelledby="titolo-obiettivi" style={{ marginTop: "1.5rem" }}>
      <h2 id="titolo-obiettivi" className={comuni.riquadroTitolo}>Obiettivi</h2>
      {r.errore && <p className={comuni.errore}>{r.errore}</p>}
      {r.dati && elenco.length === 0 && (
        <div className={comuni.vuoto}>
          Nessun obiettivo: definiscine uno (una pagina o un evento) in{" "}
          <Link className={comuni.collegamento} href="/analytics/impostazioni">Impostazioni</Link>.
        </div>
      )}
      {elenco.length > 0 && (
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead>
              <tr>
                <th>Obiettivo</th><th className={comuni.numero}>Visite</th><th className={comuni.numero}>Quota</th>
                <th className={comuni.numero}>Periodo prima</th><th className={comuni.numero}>Completamenti</th>
              </tr>
            </thead>
            <tbody>
              {elenco.map((o) => (
                <tr key={o.id}>
                  <td>{o.nome}</td>
                  <td className={comuni.numero}>{formatta(o.sessioni)}</td>
                  <td className={comuni.numero}>{formatta(o.tasso, "percento")}</td>
                  <td className={comuni.numero}>
                    {formatta(o.sessioni_prima)}{o.tasso_prima !== null ? ` (${formatta(o.tasso_prima, "percento")})` : ""}
                  </td>
                  <td className={comuni.numero}>{formatta(o.completamenti)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
