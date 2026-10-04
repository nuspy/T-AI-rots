"use client";

import type { AcquistoStore } from "@/lib/api";
import { quandoCompleto, soldi } from "@/lib/formato";
import comuni from "../../comuni.module.css";
import stili from "./dettaglio.module.css";

/* Gli acquisti nelle app (v9, Fase 4), nella scheda dell'utente: uno per incasso dello store (un pacchetto, il primo
 * periodo di un abbonamento, ogni rinnovo), come l'ha confermato Google Play o l'App Store.
 *
 * Qui non si rimborsa niente: un rimborso si fa nella console dello store, e la sua notifica (o la riconciliazione
 * notturna) storna i crediti da sola. «Prova» è un acquisto di prova (un tester o la App Review di Apple): accredita
 * ma non conta nei ricavi. «Doppio» vuol dire che lo store incassa un abbonamento mentre l'utente ne ha già un altro:
 * va detto all'utente di disdirlo nello store. */

const STATI: Record<AcquistoStore["stato"], { etichetta: string; classe: string }> = {
  in_attesa: { etichetta: "in attesa del pagamento", classe: comuni.neutro },
  accreditato: { etichetta: "accreditato", classe: comuni.positivo },
  rimborsato: { etichetta: "rimborsato", classe: comuni.negativo },
  revocato: { etichetta: "revocato", classe: comuni.negativo },
  scaduto: { etichetta: "scaduto", classe: comuni.spento },
};

export function AcquistiStore({ acquisti }: { acquisti: AcquistoStore[] }) {
  return (
    <section className={stili.sezione}>
      <h2 className={stili.sezioneTitolo}>Acquisti nelle app</h2>
      {acquisti.length === 0 ? (
        <div className={comuni.vuoto}>Nessun acquisto da Google Play o dall&apos;App Store.</div>
      ) : (
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead>
              <tr>
                <th>Quando</th>
                <th>Store</th>
                <th>Prodotto</th>
                <th>Stato</th>
                <th className={comuni.numero}>Prezzo nello store</th>
                <th>Transazione</th>
              </tr>
            </thead>
            <tbody>
              {acquisti.map((a) => {
                const s = STATI[a.stato] ?? { etichetta: a.stato, classe: comuni.neutro };
                return (
                  <tr key={a.id}>
                    <td className={comuni.mono}>{quandoCompleto(a.acquistato_il ?? a.creato_il)}</td>
                    <td>
                      {a.store}
                      {a.ambiente === "sandbox" && <div className={comuni.campoAiuto}>prova (sandbox): fuori dai ricavi</div>}
                    </td>
                    <td>
                      <span className={comuni.mono}>{a.product_id}</span>
                      <div className={comuni.campoAiuto}>
                        {a.tipo === "consumabile" ? "pacchetto di crediti" : "abbonamento"}
                        {a.prova ? " · periodo di prova" : ""}
                        {a.scade_il ? ` · fino al ${quandoCompleto(a.scade_il)}` : ""}
                      </div>
                    </td>
                    <td>
                      <span className={`${comuni.stato} ${s.classe}`}>{s.etichetta}</span>
                      {a.revocato_il && <div className={comuni.campoAiuto}>il {quandoCompleto(a.revocato_il)}</div>}
                      {a.stato === "accreditato" && !a.confermato && a.piattaforma === "android" && (
                        <div className={comuni.campoAiuto}>da confermare a Google (ci pensa il giro notturno)</div>
                      )}
                      {a.doppio && <div className={comuni.campoAiuto}>doppio: ha già un altro abbonamento</div>}
                    </td>
                    <td className={comuni.numero}>{a.importo !== null && a.valuta ? soldi(a.importo, a.valuta) : "—"}</td>
                    <td className={comuni.mono} title={a.transazione_originale ?? undefined}>{a.ordine ?? a.transazione}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
