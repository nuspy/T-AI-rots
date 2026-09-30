"use client";

/* I dati che il server ha già letto per la pagina (v8.5, la v2 è il sito): le pagine pubbliche li leggono dall'API
 * sul server (`precarica`) e li passano qui, indicizzati per percorso dell'API (`/cards?lang=en`). `usePubblico`
 * li trova al primo rendering: l'HTML esce con il contenuto (motori di ricerca, primo caricamento veloce) e il
 * browser non ripete la richiesta. Se la pagina chiede un percorso diverso (un'altra lingua scelta nel browser, una
 * pagina successiva del blog) la richiesta parte come sempre. */

import { createContext, useContext, useMemo } from "react";

const Contesto = createContext<Readonly<Record<string, unknown>>>({});

export function DatiIniziali({ valori, children }: { valori: Record<string, unknown>; children: React.ReactNode }) {
  const sopra = useContext(Contesto);
  const tutti = useMemo(() => ({ ...sopra, ...valori }), [sopra, valori]);
  return <Contesto.Provider value={tutti}>{children}</Contesto.Provider>;
}

/** Il valore già letto dal server per questo percorso, se c'è (`undefined` altrimenti). */
export function useIniziale(percorso: string | null | undefined): unknown {
  const valori = useContext(Contesto);
  return percorso && Object.prototype.hasOwnProperty.call(valori, percorso) ? valori[percorso] : undefined;
}
