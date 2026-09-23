"use client";

import Link from "next/link";
import type { Pagamento, StatoPagamento } from "@/lib/api";
import { quandoCompleto, soldi } from "@/lib/formato";
import stili from "../comuni.module.css";

/* La tabella dei pagamenti, una sola per due pagine: l'elenco generale e il
 * dettaglio di un utente. Due tabelle scritte a mano finirebbero per dire la
 * stessa cosa in due modi, e il dubbio che siano dati diversi viene subito. */

export const STATI: Record<StatoPagamento, { etichetta: string; classe: string }> = {
  aperto: { etichetta: "aperto", classe: stili.neutro },
  pagato: { etichetta: "pagato", classe: stili.positivo },
  annullato: { etichetta: "annullato", classe: stili.spento },
  scaduto: { etichetta: "scaduto", classe: stili.negativo },
};

export function TabellaPagamenti({
  pagamenti,
  senzaUtente = false,
}: {
  pagamenti: Pagamento[];
  /** Nel dettaglio di un utente la colonna direbbe sempre lo stesso nome. */
  senzaUtente?: boolean;
}) {
  return (
    <div className={stili.contenitoreTabella}>
      <table className={stili.tabella}>
        <thead>
          <tr>
            <th>Creato</th>
            {!senzaUtente && <th>Utente</th>}
            <th>Piano</th>
            <th>Periodo</th>
            <th className={stili.numero}>Importo</th>
            <th>Stato</th>
            <th>Fornitore</th>
            <th>Concluso</th>
          </tr>
        </thead>
        <tbody>
          {pagamenti.map((p) => {
            const stato = STATI[p.stato] ?? { etichetta: p.stato, classe: stili.neutro };
            return (
              <tr key={p.id}>
                <td className={stili.mono} title={p.id}>
                  {quandoCompleto(p.creato)}
                </td>
                {!senzaUtente && (
                  <td>
                    <Link href={`/utenti/${p.user_id}`} className={stili.collegamento}>
                      #{p.user_id}
                    </Link>
                  </td>
                )}
                <td>
                  {p.nome}
                  <div className={stili.campoAiuto}>{p.tipo}</div>
                </td>
                <td className={stili.mono}>
                  {p.tipo === "pacchetto" ? "una tantum" : p.annuale ? "annuale" : "mensile"}
                </td>
                <td className={stili.numero}>{soldi(p.importo, p.valuta)}</td>
                <td>
                  <span className={`${stili.stato} ${stato.classe}`}>{stato.etichetta}</span>
                </td>
                <td className={stili.mono}>{p.fornitore}</td>
                <td className={stili.mono}>{quandoCompleto(p.completato)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
