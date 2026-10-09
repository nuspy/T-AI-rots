"use client";

/* La lingua della traduzione automatica dei contenuti (v9.5, regola del 9/10).
 *
 * I contenuti che esistono in una lingua sola (articoli del blog, schede di carte, stese e mazzi) si traducono nel
 * browser (`usa-traduzione.ts`). Verso quale lingua: **quella del sito**, finché la persona non ne sceglie
 * un'altra nel riquadro della traduzione. Quella scelta sta in un cookie suo, `lingua_traduzione`, separato dal
 * cookie `lingua` del sito: si può leggere il sito in italiano e gli articoli in giapponese. Scegliere di nuovo la
 * lingua del sito toglie il cookie (si torna a seguire il sito); un gesto esplicito sulla lingua del sito
 * (`useCambiaLingua`) lo toglie pure.
 *
 * Le lingue della traduzione sono molte più delle quindici del sito: quelle che la Translator API di Chrome sa
 * tradurre. Una coppia che il browser non conosce semplicemente non si offre (`disponibilita` → `unavailable`).
 *
 * Il motore (`traduzione-auto.ts`, `usa-traduzione.ts`) resta uguale alla copia della console: qui solo la scelta. */

import { useCallback, useEffect, useState } from "react";
import { useLingua } from "./lingua";

const COOKIE = "lingua_traduzione";
const UN_ANNO = 365 * 24 * 60 * 60;
const EVENTO = "tarots:lingua-traduzione";

/** Le lingue della Translator API di Chrome (codici brevi: il motore usa la parte principale del codice). */
export const LINGUE_TRADUZIONE = [
  "ar", "bg", "bn", "cs", "da", "de", "el", "en", "es", "fi", "fr", "he", "hi", "hr", "hu", "id", "it", "ja", "kn",
  "ko", "lt", "mr", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl", "sv", "ta", "te", "th", "tr", "uk", "vi", "zh",
] as const;

const valida = (codice: string | null | undefined): string | null => {
  const c = (codice ?? "").toLowerCase();
  return (LINGUE_TRADUZIONE as readonly string[]).includes(c) ? c : null;
};

function leggi(): string | null {
  try {
    const m = document.cookie.match(new RegExp(`(?:^|;\\s*)${COOKIE}=([a-z]{2})`));
    return valida(m?.[1]);
  } catch {
    return null;
  }
}

function scrivi(codice: string | null): void {
  try {
    document.cookie = codice
      ? `${COOKIE}=${codice}; Path=/; Max-Age=${UN_ANNO}; SameSite=Lax`
      : `${COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
  } catch {
    /* resta la scelta di questa pagina */
  }
  window.dispatchEvent(new Event(EVENTO));
}

/** Si torna a tradurre nella lingua del sito (chi sceglie la lingua del sito dice anche questo). */
export function dimenticaLinguaTraduzione(): void {
  if (typeof document !== "undefined" && leggi() !== null) scrivi(null);
}

/** Il nome di una lingua nella lingua stessa, con l'iniziale maiuscola: «日本語», «Deutsch», «Italiano». */
export function nomeNativo(codice: string): string {
  try {
    const nome = new Intl.DisplayNames([codice], { type: "language" }).of(codice) ?? codice;
    return nome.charAt(0).toLocaleUpperCase(codice) + nome.slice(1);
  } catch {
    return codice;
  }
}

export interface LinguaTraduzione {
  /** La lingua verso cui tradurre: la scelta, o quella del sito. */
  lingua: string;
  /** Vero se la persona ha scelto una lingua diversa da quella del sito. */
  scelta: boolean;
  scegli: (codice: string) => void;
}

export function useLinguaTraduzione(): LinguaTraduzione {
  const { lingua: delSito } = useLingua();
  const [scelta, setScelta] = useState<string | null>(null);
  useEffect(() => {
    const aggiorna = () => setScelta(leggi());
    aggiorna();
    window.addEventListener(EVENTO, aggiorna);
    return () => window.removeEventListener(EVENTO, aggiorna);
  }, []);
  const scegli = useCallback((codice: string) => {
    const c = valida(codice);
    if (!c) return;
    scrivi(c === delSito ? null : c);
  }, [delSito]);
  const vale = scelta && scelta !== delSito ? scelta : null;
  return { lingua: vale ?? delSito, scelta: vale !== null, scegli };
}
