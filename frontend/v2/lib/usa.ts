"use client";

/* Gli hook di caricamento della v2: gli stessi del sito (`lib/usa.ts`), con i messaggi del dizionario v2. */

import { useCallback, useEffect, useState } from "react";
import { ErroreApi, leggiApi } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { useIniziale } from "./iniziali";
import { useLingua } from "./lingua";

interface Caricamento<T> {
  dati: T | null;
  errore: string | null;
  inCorso: boolean;
  ricarica: () => void;
}

/** Carica dati dall'API distinguendo in corso, riuscito e fallito. Senza `pubblico` aspetta una sessione.
 *
 *  `iniziale`: il percorso dell'API che il fetcher legge. Se il server l'ha già letto per la pagina (`DatiIniziali`),
 *  i dati ci sono dal primo rendering e la richiesta non parte (finché non si chiede `ricarica`). Solo per letture
 *  pubbliche: il server le fa senza sessione, e la sessione che arriva dopo non le cambia. */
export function useCarica<T>(
  fetcher: (token: string | null) => Promise<T>,
  dipendenze: unknown[] = [],
  { pubblico = false, iniziale }: { pubblico?: boolean; iniziale?: string | null } = {},
): Caricamento<T> {
  const sessione = useSessione();
  const { t } = useLingua();
  const dalServer = useIniziale(pubblico ? iniziale : null) as T | undefined;
  const token = dalServer !== undefined ? null : sessione.token;
  const pronto = pubblico || sessione.autenticata;
  const [quando, setQuando] = useState(0);
  const ricarica = useCallback(() => setQuando((n) => n + 1), []);
  const giaPronti = dalServer !== undefined && quando === 0;
  const chiave: unknown[] = [token, pronto, quando, giaPronti, ...(dipendenze.length ? dipendenze : [fetcher])];

  const [esito, setEsito] = useState<{ chiave: unknown[]; dati: T | null; errore: string | null } | null>(null);

  useEffect(() => {
    if (!pronto || giaPronti) return;
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

  if (giaPronti) return { dati: dalServer ?? null, errore: null, inCorso: false, ricarica };

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

/** Una lettura pubblica dell'API per percorso (`/cards?lang=en`), con i dati del server se la pagina li ha già
 *  (vedi `useCarica`, opzione `iniziale`). `null` come percorso: niente da leggere (ancora). */
export function usePubblico<T>(percorso: string | null): Caricamento<T> {
  return useCarica<T>(
    () => (percorso ? leggiApi<T>(percorso) : Promise.resolve(null as T)),
    [percorso],
    { pubblico: true, iniziale: percorso },
  );
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

/** Vero sugli schermi stretti (il telefono): alcune scelte si fanno in un dialogo invece che nella pagina. */
export function useStretto(massimo = 760): boolean {
  const [stretto, setStretto] = useState(false);
  useEffect(() => {
    const q = window.matchMedia(`(max-width: ${massimo}px)`);
    const aggiorna = () => setStretto(q.matches);
    aggiorna();
    q.addEventListener("change", aggiorna);
    return () => q.removeEventListener("change", aggiorna);
  }, [massimo]);
  return stretto;
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
