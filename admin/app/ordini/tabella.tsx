"use client";

import Link from "next/link";
import { aggiornaEvasione, type Ordine, type RigaOrdine, type StatoEvasione, type StatoOrdine } from "@/lib/api";
import { quandoCompleto, soldi } from "@/lib/formato";
import { useAzione } from "@/lib/usa";
import stili from "../comuni.module.css";

export const STATI_ORDINE: Record<StatoOrdine, { etichetta: string; classe: string }> = {
  aperto: { etichetta: "aperto", classe: stili.neutro },
  pagato: { etichetta: "pagato", classe: stili.positivo },
  annullato: { etichetta: "annullato", classe: stili.spento },
  scaduto: { etichetta: "scaduto", classe: stili.negativo },
};

const ETICHETTA_TIPO: Record<string, string> = { digitale: "digitale", pdf: "PDF", fisico: "fisico" };

const ETICHETTA_EVASIONE: Record<StatoEvasione, string> = {
  in_attesa: "in attesa",
  spedito: "spedito",
  consegnato: "consegnato",
};

export function TabellaOrdini({ ordini, suCambio }: { ordini: Ordine[]; suCambio: () => void }) {
  return (
    <div className={stili.contenitoreTabella}>
      <table className={stili.tabella}>
        <thead>
          <tr>
            <th>Creato</th>
            <th>Utente</th>
            <th>Mazzi</th>
            <th className={stili.numero}>Sconto scaglioni</th>
            <th className={stili.numero}>Totale</th>
            <th>Stato</th>
            <th>Concluso</th>
          </tr>
        </thead>
        <tbody>
          {ordini.map((o) => {
            const stato = STATI_ORDINE[o.status] ?? { etichetta: o.status, classe: stili.neutro };
            return (
              <tr key={o.id}>
                <td className={stili.mono} title={o.id}>{quandoCompleto(o.creato)}</td>
                <td>
                  <Link href={`/utenti/${o.user_id}`} className={stili.collegamento}>#{o.user_id}</Link>
                </td>
                <td>
                  <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "grid", gap: 6 }}>
                    {o.righe.map((r) => (
                      <RigaMazzo key={r.id} ordineId={o.id} riga={r} suCambio={suCambio} />
                    ))}
                  </ul>
                  {o.indirizzo_spedizione && (
                    <p className={stili.campoAiuto}>
                      spedizione: {o.indirizzo_spedizione.nome}, {o.indirizzo_spedizione.via},{" "}
                      {o.indirizzo_spedizione.cap} {o.indirizzo_spedizione.citta}, {o.indirizzo_spedizione.paese}
                    </p>
                  )}
                </td>
                <td className={stili.numero}>{o.sconto_scaglioni > 0 ? `−${soldi(o.sconto_scaglioni)}` : "—"}</td>
                <td className={stili.numero}>{soldi(o.importo_totale, o.valuta)}</td>
                <td><span className={`${stili.stato} ${stato.classe}`}>{stato.etichetta}</span></td>
                <td className={stili.mono}>{quandoCompleto(o.completato)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function RigaMazzo({ ordineId, riga, suCambio }: { ordineId: string; riga: RigaOrdine; suCambio: () => void }) {
  const { esegui, inCorso } = useAzione();
  return (
    <li>
      {riga.mazzo?.nome ?? `mazzo #${riga.deck_id}`} — {ETICHETTA_TIPO[riga.tipo] ?? riga.tipo}
      {riga.quantita > 1 ? ` × ${riga.quantita}` : ""}
      <span className={stili.campoAiuto}>
        {" "}{soldi(riga.prezzo_finale_unitario * riga.quantita)}
        {riga.prezzo_finale_unitario < riga.prezzo_pieno_unitario &&
          ` (listino ${soldi(riga.prezzo_pieno_unitario * riga.quantita)})`}
      </span>
      {riga.tipo === "fisico" && riga.stato_evasione && (
        <div style={{ marginTop: 2 }}>
          <select
            value={riga.stato_evasione} disabled={inCorso} className={stili.mono}
            onChange={async (e) => {
              const fatto = await esegui((t) => aggiornaEvasione(t, ordineId, riga.id, e.target.value as StatoEvasione));
              if (fatto) suCambio();
            }}
          >
            {(Object.keys(ETICHETTA_EVASIONE) as StatoEvasione[]).map((s) => (
              <option key={s} value={s}>{ETICHETTA_EVASIONE[s]}</option>
            ))}
          </select>
        </div>
      )}
    </li>
  );
}
