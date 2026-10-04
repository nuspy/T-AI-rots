"use client";

/* La prova gratuita e il suo banner (v9, Fase 2b): le impostazioni pubbliche (acceso, giorni, sconti) lette dal
 * server nel layout, così il banner esce già nell'HTML e non sposta la pagina comparendo dopo; e il ricordo, nel
 * browser, di chi l'ha chiuso (torna dopo qualche giorno) o di chi non può più usarla.
 *
 * Il ricordo sta in localStorage (`CHIAVE_BANNER`: `{ fino: <ms> }`). Uno script minimo nel layout lo legge prima che
 * la pagina si disegni e mette `data-prova-nascosta` su `<html>`: il CSS nasconde il banner da subito, senza lampi. */

import { createContext, useContext } from "react";
import { PERCORSO_PUBBLICO_ABBONAMENTI, type ImpostazioniPubblicheAbbonamenti } from "@/lib/abbonamenti";
import { usePubblico } from "./usa";

export const CHIAVE_BANNER = "tarots.prova.banner";
/** Chi chiude il banner lo rivede dopo cinque giorni. */
export const GIORNI_CHIUSO = 5;
/** Chi non può più usare la prova (già usata, o abbonato): si ricontrolla dopo un giorno. */
export const GIORNI_NON_IDONEO = 1;

/** Lo script del layout: gira prima del disegno, legge il ricordo e nasconde il banner. Niente dipendenze. */
export const SCRIPT_BANNER_PROVA =
  `try{var v=JSON.parse(localStorage.getItem(${JSON.stringify(CHIAVE_BANNER)})||"null");` +
  `if(v&&v.fino>Date.now())document.documentElement.setAttribute("data-prova-nascosta","1")}catch(e){}`;

export function ricordaNascosto(giorni: number) {
  try {
    window.localStorage.setItem(CHIAVE_BANNER, JSON.stringify({ fino: Date.now() + giorni * 86400000 }));
  } catch {
    /* senza localStorage il banner torna alla pagina successiva: meglio che un errore */
  }
  document.documentElement.setAttribute("data-prova-nascosta", "1");
}

export function nascostoOra(): boolean {
  try {
    const v = JSON.parse(window.localStorage.getItem(CHIAVE_BANNER) ?? "null") as { fino?: number } | null;
    return !!v && typeof v.fino === "number" && v.fino > Date.now();
  } catch {
    return false;
  }
}

const Contesto = createContext<ImpostazioniPubblicheAbbonamenti | null>(null);

/** Le impostazioni lette dal server nel layout. */
export function ProvaIniziale({ valore, children }: { valore: ImpostazioniPubblicheAbbonamenti | null; children: React.ReactNode }) {
  return <Contesto.Provider value={valore}>{children}</Contesto.Provider>;
}

/** Le impostazioni pubbliche della prova: quelle del layout, o lette qui se la pagina non le ha. */
export function useImpostazioniProva(): ImpostazioniPubblicheAbbonamenti | null {
  const dalLayout = useContext(Contesto);
  const letti = usePubblico<ImpostazioniPubblicheAbbonamenti>(dalLayout ? null : PERCORSO_PUBBLICO_ABBONAMENTI);
  return dalLayout ?? letti.dati;
}
