"use client";

/* Gli hook di caricamento della v2: gli stessi del sito (`lib/usa.ts`), con i messaggi del dizionario v2. */

import { useCallback, useEffect, useState } from "react";
import { ErroreApi } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { useLingua } from "./lingua";

interface Caricamento<T> {
  dati: T | null;
  errore: string | null;
  inCorso: boolean;
  ricarica: () => void;
}

/** Carica dati dall'API distinguendo in corso, riuscito e fallito. Senza `pubblico` aspetta una sessione. */
export function useCarica<T>(
  fetcher: (token: string | null) => Promise<T>,
  dipendenze: unknown[] = [],
  { pubblico = false }: { pubblico?: boolean } = {},
): Caricamento<T> {
  const sessione = useSessione();
  const { t } = useLingua();
  const token = sessione.token;
  const pronto = pubblico || sessione.autenticata;
  const [quando, setQuando] = useState(0);
  const ricarica = useCallback(() => setQuando((n) => n + 1), []);
  const chiave: unknown[] = [token, pronto, quando, ...(dipendenze.length ? dipendenze : [fetcher])];

  const [esito, setEsito] = useState<{ chiave: unknown[]; dati: T | null; errore: string | null } | null>(null);

  useEffect(() => {
    if (!pronto) return;
    let annullato = false;
    fetcher(token)
      .then((r) => { if (!annullato) setEsito({ chiave, dati: r, errore: null }); })
      .catch((e: unknown) => {
        if (annullato) return;
        const messaggio = e instanceof ErroreApi ? e.message : t.comune.err_generico;
        setEsito((prima) => ({ chiave, dati: prima?.dati ?? null, errore: messaggio }));
      });
    return () => { annullato = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, chiave);

  const aggiornato =
    esito !== null &&
    esito.chiave.length === chiave.length &&
    esito.chiave.every((v, i) => Object.is(v, chiave[i]));

  return {
    dati: esito?.dati ?? null,
    errore: aggiornato ? esito.errore : null,
    inCorso: !aggiornato,
    ricarica,
  };
}

/** Esegue un'azione che modifica (solo con una sessione), riportando l'esito. */
export function useAzione() {
  const sessione = useSessione();
  const { t } = useLingua();
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);

  const esegui = useCallback(
    async <T,>(azione: (t: string | null) => Promise<T>): Promise<T | null> => {
      if (!sessione.autenticata) return null;
      setInCorso(true);
      setErrore(null);
      try {
        return await azione(sessione.token);
      } catch (e: unknown) {
        setErrore(e instanceof ErroreApi ? e.message : t.comune.err_operazione);
        return null;
      } finally {
        setInCorso(false);
      }
    },
    [sessione, t],
  );

  return { esegui, inCorso, errore };
}

/** Vero se chi guarda preferisce meno movimento. */
export function useMenoMovimento(): boolean {
  const [meno, setMeno] = useState(false);
  useEffect(() => {
    const q = window.matchMedia("(prefers-reduced-motion: reduce)");
    const aggiorna = () => setMeno(q.matches);
    aggiorna();
    q.addEventListener("change", aggiorna);
    return () => q.removeEventListener("change", aggiorna);
  }, []);
  return meno;
}
