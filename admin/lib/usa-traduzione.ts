"use client";

/* Lo stato della traduzione automatica di una pagina (v9.5), per il riquadro che la annuncia.
 *
 * `useTraduzione(radici, lingua, { sorgente, chiave })` traduce il contenuto delle radici dalla lingua `sorgente` (o
 * da quella riconosciuta dal browser) alla `lingua` dell'interfaccia:
 *  - `nessuna`: niente da fare (browser senza Translator API, stessa lingua, coppia non disponibile);
 *  - `offerta`: il modello va scaricato, e Chrome lo scarica solo dopo un clic → «Traduci»;
 *  - `scarico` / `in_corso`: scaricamento del modello (con la percentuale) e traduzione;
 *  - `tradotta`, `originale` (la persona ha chiesto l'originale), `errore`.
 * Cambiando `lingua` o `chiave` (un altro articolo) si riparte dall'originale.
 *
 * Uguale in `admin/lib/usa-traduzione.ts` (controllato da `npm run controlla-traduzione`). */

import { useCallback, useEffect, useRef, useState, type RefObject } from "react";
import {
  TraduzionePagina, automaticaAttiva, base, disponibilita, impostaAutomatica, rilevaLingua, supportata, traduttore,
} from "./traduzione-auto";

export type FaseTraduzione = "nessuna" | "offerta" | "scarico" | "in_corso" | "tradotta" | "originale" | "errore";

export interface StatoTraduzione {
  fase: FaseTraduzione;
  /** La lingua di partenza (codice breve), quando è nota. */
  da: string | null;
  a: string;
  percento: number | null;
  traduci: () => void;
  mostraOriginale: () => void;
  /** «Non tradurre automaticamente»: torna all'originale e da ora chiede ogni volta. */
  nonPiu: () => void;
}

export function useTraduzione(
  radici: RefObject<HTMLElement | null>[],
  a: string,
  opzioni: { sorgente?: string | null; chiave?: string } = {},
): StatoTraduzione {
  const [fase, setFase] = useState<FaseTraduzione>("nessuna");
  const [da, setDa] = useState<string | null>(null);
  const [percento, setPercento] = useState<number | null>(null);
  const attiva = useRef<TraduzionePagina | null>(null);
  const daRef = useRef<string | null>(null);
  /* I riferimenti sono oggetti stabili (`useRef` di chi chiama): basta l'elenco del primo rendering. */
  const [fisse] = useState(radici);

  const elementi = useCallback(
    () => fisse.map((r) => r.current).filter((e): e is HTMLElement => e !== null), [fisse],
  );

  const ferma = () => {
    attiva.current?.ripristina();
    attiva.current = null;
  };

  /* Senza `await` prima di `traduttore()`: se il modello va scaricato, Chrome accetta la richiesta solo dentro il
   * gesto dell'utente che l'ha chiesta. */
  const avvia = useCallback((sorgente: string) => {
    ferma();
    setFase("in_corso");
    const richiesta = traduttore(sorgente, a, (p) => {
      setFase("scarico");
      setPercento(p);
    });
    void (async () => {
      try {
        const api = await richiesta;
        setFase("in_corso");
        const pagina = new TraduzionePagina(elementi(), sorgente, a, api);
        attiva.current = pagina;
        await pagina.avvia();
        if (attiva.current === pagina) setFase("tradotta");
      } catch {
        setFase("errore");
      }
    })();
  }, [a, elementi]);

  useEffect(() => {
    let annullato = false;
    ferma();
    // eslint-disable-next-line react-hooks/set-state-in-effect -- si riparte dall'originale a ogni pagina o lingua
    setFase("nessuna");
    setPercento(null);
    if (!supportata() || !elementi().length) return;
    void (async () => {
      const testo = elementi().map((e) => e.innerText).join("\n");
      const sorgente = opzioni.sorgente ? base(opzioni.sorgente) : await rilevaLingua(testo);
      if (annullato || !sorgente || sorgente === base(a)) return;
      daRef.current = sorgente;
      setDa(sorgente);
      const stato = await disponibilita(sorgente, a);
      if (annullato || stato === "unavailable") return;
      if (stato === "available" && automaticaAttiva()) avvia(sorgente);
      else setFase("offerta");
    })();
    return () => {
      annullato = true;
      ferma();
    };
  }, [a, opzioni.sorgente, opzioni.chiave, avvia, elementi]);

  return {
    fase,
    da,
    a,
    percento,
    traduci: () => {
      if (!daRef.current) return;
      impostaAutomatica(true);
      avvia(daRef.current);
    },
    mostraOriginale: () => {
      ferma();
      setFase("originale");
    },
    nonPiu: () => {
      impostaAutomatica(false);
      ferma();
      setFase("originale");
    },
  };
}
