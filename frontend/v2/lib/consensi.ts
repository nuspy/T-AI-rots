"use client";

/* Lo stato dei consensi della v2 (GDPR, Fase 1), uno per pagina: il banner, la pagina privacy, la sezione «Privacy e
 * consensi» del profilo e la richiesta del consenso ai dati particolari accanto alla casella «persona trans» leggono e
 * scrivono lo stesso stato, così una scelta fatta in un punto vale subito negli altri.
 *
 * Si rilegge dal server a ogni cambio di sessione (entrare, uscire): le scelte di un account non sono quelle del
 * browser anonimo di prima, anche se all'iscrizione quelle del banner passano all'account. Ogni scelta si applica
 * subito dove serve: `statistiche` all'osservatore e all'identificativo del browser, `google_analytics` al contatore
 * di Google, `pubblicita` agli spazi pubblicitari. */

import { useCallback, useEffect, useSyncExternalStore } from "react";
import { leggiConsenso, type TipoConsenso, type ValoreConsenso } from "@/lib/api";
import { dimenticaAnalytics, impostaConsensoAnalytics } from "@/lib/analytics";
import { registraConsensi, type StatoConsensi, VERSIONE_CONSENSI } from "@/lib/privacy";
import { useSessione } from "@/lib/sessione";
import { annunciaConsensoGoogle } from "@/v2/componenti/contatore-google";
import { annunciaConsensoPubblicita } from "@/v2/componenti/pubblicita";

interface Stato {
  /** Il token con cui si è letto lo stato (`""` per chi non è entrato): cambia → si rilegge. */
  di: string | null;
  dati: StatoConsensi | null;
}

let stato: Stato = { di: null, dati: null };
const ascoltatori = new Set<() => void>();
let inLettura: string | null = null;

function aggiorna(nuovo: Stato): void {
  stato = nuovo;
  ascoltatori.forEach((f) => f());
}

function iscriviti(f: () => void): () => void {
  ascoltatori.add(f);
  return () => ascoltatori.delete(f);
}

const INIZIALE: Stato = { di: null, dati: null };

/** Applica le scelte a ciò che dipende da esse nel browser. `prima`: lo stato precedente, per sapere se è una revoca. */
function applica(dati: StatoConsensi, prima: StatoConsensi | null): void {
  if (prima?.statistiche === "accettato" && dati.statistiche !== "accettato") dimenticaAnalytics();
  else impostaConsensoAnalytics(dati.statistiche);
  annunciaConsensoGoogle(dati.google_analytics === "accettato");
  if (dati.pubblicita !== null) annunciaConsensoPubblicita(dati.pubblicita);
}

export function useConsensi() {
  const sessione = useSessione();
  const corrente = useSyncExternalStore(iscriviti, () => stato, () => INIZIALE);
  const chiave = sessione.pronta ? (sessione.token ?? "") : null;

  useEffect(() => {
    if (chiave === null || stato.di === chiave || inLettura === chiave) return;
    inLettura = chiave;
    leggiConsenso(sessione.token)
      .then((d) => {
        const dati = d as unknown as StatoConsensi;
        aggiorna({ di: chiave, dati });
        impostaConsensoAnalytics(dati.statistiche);
      })
      .catch(() => {})
      .finally(() => {
        if (inLettura === chiave) inLettura = null;
      });
  }, [chiave, sessione.token]);

  /** Registra più scelte insieme e le applica. Solleva l'errore del server (il chiamante lo mostra). */
  const scegli = useCallback(
    async (scelte: Partial<Record<TipoConsenso, ValoreConsenso>>, versione: string = VERSIONE_CONSENSI) => {
      const prima = stato.dati;
      const dati = await registraConsensi(sessione.token, scelte, versione);
      aggiorna({ di: sessione.pronta ? (sessione.token ?? "") : stato.di, dati });
      applica(dati, prima);
      return dati;
    },
    [sessione.token, sessione.pronta],
  );

  return { dati: corrente.di === chiave ? corrente.dati : null, scegli };
}
