"use client";

import { useCallback, useState } from "react";
import { elencoOrdini, type StatoOrdine } from "@/lib/api";
import { soldi } from "@/lib/formato";
import { useDati } from "@/lib/usa";
import stili from "../comuni.module.css";
import { STATI_ORDINE, TabellaOrdini } from "./tabella";

/* Gli ordini del negozio mazzi, dal più recente.
 *
 * Un ordine «aperto» non è un incasso: è un carrello per cui si è aperta la
 * pagina di pagamento. Diventa «pagato» solo quando il fornitore lo conferma
 * con un evento firmato — stessa regola dei pagamenti dei piani. */

const PER_PAGINA = 100;
const FILTRI: ("" | StatoOrdine)[] = ["", "aperto", "pagato", "annullato", "scaduto"];

export default function Ordini() {
  const [stato, setStato] = useState<"" | StatoOrdine>("");
  const [offset, setOffset] = useState(0);

  const { dati, errore, inCorso, ricarica } = useDati(
    useCallback((t: string) => elencoOrdini(t, { status: stato, limite: PER_PAGINA, offset }), [stato, offset]),
  );

  const totale = dati?.totale ?? 0;

  return (
    <>
      <div className={stili.intestazione}>
        <div>
          <h1 className={stili.titolo}>Ordini</h1>
          <p className={stili.sottotitolo}>
            Ogni carrello del negozio mazzi, dall&apos;apertura al pagamento. Gli
            importi sono quelli del momento dell&apos;ordine: uno sconto o un
            prezzo cambiati dopo non li toccano.
          </p>
        </div>
      </div>

      <div className={stili.filtri} role="group" aria-label="Stato dell'ordine">
        {FILTRI.map((f) => (
          <button
            key={f || "tutti"}
            className={f === stato ? stili.filtroScelto : stili.filtro}
            aria-pressed={f === stato}
            onClick={() => { setStato(f); setOffset(0); }}
          >
            {f ? STATI_ORDINE[f].etichetta : "Tutti"}
          </button>
        ))}
      </div>

      {errore && <p className={stili.errore}>{errore}</p>}
      {!dati && inCorso && <p className={stili.caricamento}>Caricamento…</p>}

      {dati && (
        <div className={inCorso ? stili.inRicarica : undefined}>
          <p className={stili.riquadroNota}>
            {totale} {totale === 1 ? "ordine" : "ordini"}
            {stato ? ` in stato «${STATI_ORDINE[stato].etichetta}»` : ""} · incassato in
            totale <strong>{soldi(dati.incassato)}</strong>
          </p>

          {dati.ordini.length === 0 ? (
            <div className={stili.vuoto}>Nessun ordine.</div>
          ) : (
            <>
              <TabellaOrdini ordini={dati.ordini} suCambio={ricarica} />
              <div className={stili.paginazione}>
                <span>{offset + 1}–{Math.min(offset + PER_PAGINA, totale)} di {totale}</span>
                <div className={stili.paginazioneComandi}>
                  <button
                    className={stili.secondaria} disabled={offset === 0 || inCorso}
                    onClick={() => setOffset((o) => Math.max(0, o - PER_PAGINA))}
                  >
                    Precedenti
                  </button>
                  <button
                    className={stili.secondaria} disabled={offset + PER_PAGINA >= totale || inCorso}
                    onClick={() => setOffset((o) => o + PER_PAGINA)}
                  >
                    Successivi
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}
