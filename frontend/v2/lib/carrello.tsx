"use client";

/* Il carrello della v2: quali mazzi, in quale formato, quante copie. Vive nel browser (`localStorage`), così resta al
 * ricaricamento, tra le pagine e prima dell'accesso: chi compone il carrello senza account lo ritrova dopo essere
 * entrato. Solo gli identificativi: prezzi, sconti e totale li dice sempre il server (`POST /shop/quote`), mai il
 * browser. Se il browser non lascia salvare (navigazione privata, dati bloccati) il carrello funziona lo stesso,
 * solo non sopravvive al ricaricamento. */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { TipoVoceOrdine } from "@/lib/api";

export interface VoceCarrello { deckId: number; tipo: TipoVoceOrdine; quantita: number }

const CHIAVE = "tarots.v2.carrello";
const MAX_QUANTITA = 20;
const TIPI: TipoVoceOrdine[] = ["digitale", "pdf", "fisico"];

interface Carrello {
  voci: VoceCarrello[];
  /* Il numero di pezzi (per il segno sull'icona). */
  pezzi: number;
  /* Vero dopo la lettura dal browser: prima, un carrello vuoto non vuol dire ancora «vuoto». */
  pronto: boolean;
  aggiungi: (deckId: number, tipo: TipoVoceOrdine) => void;
  quantita: (deckId: number, tipo: TipoVoceOrdine, n: number) => void;
  togli: (deckId: number, tipo: TipoVoceOrdine) => void;
  svuota: () => void;
}

const Contesto = createContext<Carrello | null>(null);

function leggi(): VoceCarrello[] {
  try {
    const grezzo = JSON.parse(window.localStorage.getItem(CHIAVE) ?? "[]") as unknown;
    if (!Array.isArray(grezzo)) return [];
    return grezzo.flatMap((v) => {
      const x = v as Partial<VoceCarrello>;
      const q = Math.min(MAX_QUANTITA, Math.max(1, Math.floor(Number(x.quantita) || 1)));
      return typeof x.deckId === "number" && TIPI.includes(x.tipo as TipoVoceOrdine)
        ? [{ deckId: x.deckId, tipo: x.tipo as TipoVoceOrdine, quantita: x.tipo === "digitale" ? 1 : q }]
        : [];
    });
  } catch {
    return [];
  }
}

export function ProviderCarrello({ children }: { children: React.ReactNode }) {
  const [voci, setVoci] = useState<VoceCarrello[]>([]);
  const [pronto, setPronto] = useState(false);

  useEffect(() => {
    // Una sola lettura all'avvio: `localStorage` non esiste durante il rendering sul server.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setVoci(leggi());
    setPronto(true);
    /* Un'altra scheda aperta sullo stesso sito cambia il carrello: qui si segue. */
    const altrove = (e: StorageEvent) => { if (e.key === CHIAVE) setVoci(leggi()); };
    window.addEventListener("storage", altrove);
    return () => window.removeEventListener("storage", altrove);
  }, []);

  const scrivi = useCallback((cambia: (prima: VoceCarrello[]) => VoceCarrello[]) => {
    setVoci((prima) => {
      const dopo = cambia(prima);
      try { window.localStorage.setItem(CHIAVE, JSON.stringify(dopo)); } catch { /* il carrello resta in memoria */ }
      return dopo;
    });
  }, []);

  const valore = useMemo<Carrello>(() => ({
    voci,
    pezzi: voci.reduce((s, v) => s + v.quantita, 0),
    pronto,
    aggiungi: (deckId, tipo) => scrivi((prima) => {
      const c = prima.find((v) => v.deckId === deckId && v.tipo === tipo);
      /* Un mazzo digitale si possiede una volta sola: una seconda copia non ha senso. */
      if (c) return prima.map((v) => (v === c ? { ...v, quantita: tipo === "digitale" ? 1 : Math.min(MAX_QUANTITA, v.quantita + 1) } : v));
      return [...prima, { deckId, tipo, quantita: 1 }];
    }),
    quantita: (deckId, tipo, n) => scrivi((prima) => prima.flatMap((v) => {
      if (v.deckId !== deckId || v.tipo !== tipo) return [v];
      const q = Math.min(tipo === "digitale" ? 1 : MAX_QUANTITA, Math.floor(n));
      return q >= 1 ? [{ ...v, quantita: q }] : [];
    })),
    togli: (deckId, tipo) => scrivi((prima) => prima.filter((v) => v.deckId !== deckId || v.tipo !== tipo)),
    svuota: () => scrivi(() => []),
  }), [voci, pronto, scrivi]);

  return <Contesto.Provider value={valore}>{children}</Contesto.Provider>;
}

export function useCarrello(): Carrello {
  const c = useContext(Contesto);
  if (!c) throw new Error("useCarrello fuori da ProviderCarrello");
  return c;
}
