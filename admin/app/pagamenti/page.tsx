"use client";

import { useCallback, useState } from "react";
import { elencoPagamenti, type StatoPagamento } from "@/lib/api";
import { soldi } from "@/lib/formato";
import { useDati } from "@/lib/usa";
import stili from "../comuni.module.css";
import { STATI, TabellaPagamenti } from "./tabella";

/* I pagamenti, dal più recente.
 *
 * Un pagamento «aperto» non è un incasso: è qualcuno che è andato alla cassa.
 * Diventa «pagato» solo quando il fornitore lo conferma con un evento
 * firmato, e solo allora nasce l'abbonamento o arrivano i crediti.
 */

const PER_PAGINA = 100;
const FILTRI: ("" | StatoPagamento)[] = ["", "aperto", "pagato", "annullato", "scaduto"];

export default function Pagamenti() {
  const [stato, setStato] = useState<"" | StatoPagamento>("");
  const [offset, setOffset] = useState(0);

  const { dati, errore, inCorso } = useDati(
    useCallback(
      (t: string) => elencoPagamenti(t, { stato, limite: PER_PAGINA, offset }),
      [stato, offset],
    ),
  );

  const totale = dati?.totale ?? 0;

  return (
    <>
      <div className={stili.intestazione}>
        <div>
          <h1 className={stili.titolo}>Pagamenti</h1>
          <p className={stili.sottotitolo}>
            Ogni passaggio alla cassa, concluso o no. Gli importi sono quelli
            del momento del pagamento: cambiare un prezzo in catalogo non li
            tocca.
          </p>
        </div>
      </div>

      <p className={stili.avviso}>
        <strong>Pagamenti simulati.</strong> Il fornitore configurato è quello
        di prova (<code>mock</code>): nessuna carta viene addebitata, e
        «pagato» significa che qualcuno ha premuto il pulsante di conferma
        nella cassa finta. Gli incassi mostrati non sono denaro reale.
      </p>

      <div className={stili.filtri} role="group" aria-label="Stato del pagamento">
        {FILTRI.map((f) => (
          <button
            key={f || "tutti"}
            className={f === stato ? stili.filtroScelto : stili.filtro}
            aria-pressed={f === stato}
            onClick={() => {
              setStato(f);
              setOffset(0);
            }}
          >
            {f ? STATI[f].etichetta : "Tutti"}
          </button>
        ))}
      </div>

      {errore && <p className={stili.errore}>{errore}</p>}
      {!dati && inCorso && <p className={stili.caricamento}>Caricamento…</p>}

      {dati && (
        <div className={inCorso ? stili.inRicarica : undefined}>
          {/* L'incassato è di sempre e non dipende dal filtro: il backend lo
              somma sui soli pagamenti conclusi. */}
          <p className={stili.riquadroNota}>
            {totale} {totale === 1 ? "pagamento" : "pagamenti"}
            {stato ? ` in stato «${STATI[stato].etichetta}»` : ""} · incassato in
            totale <strong>{soldi(dati.incassato)}</strong>
          </p>

          {dati.pagamenti.length === 0 ? (
            <div className={stili.vuoto}>Nessun pagamento.</div>
          ) : (
            <>
              <TabellaPagamenti pagamenti={dati.pagamenti} />
              <div className={stili.paginazione}>
                <span>
                  {offset + 1}–{Math.min(offset + PER_PAGINA, totale)} di {totale}
                </span>
                <div className={stili.paginazioneComandi}>
                  <button
                    className={stili.secondaria}
                    disabled={offset === 0 || inCorso}
                    onClick={() => setOffset((o) => Math.max(0, o - PER_PAGINA))}
                  >
                    Precedenti
                  </button>
                  <button
                    className={stili.secondaria}
                    disabled={offset + PER_PAGINA >= totale || inCorso}
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
