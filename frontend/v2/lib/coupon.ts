"use client";

/* I codici sconto sul sito (v9, Fase 2d).
 *
 * **Il link applica il codice da solo.** `/pricing?coupon=CODICE` (e `/it/piano?coupon=CODICE`): il codice si conserva
 * per la sessione del browser (`sessionStorage`, la scheda): sopravvive al giro per la pagina di accesso di Keycloak e
 * alla registrazione, e si precompila al pagamento e alla prova. Si toglie a pagamento avvenuto o a mano.
 *
 * **I conti li fa il server** (`POST /coupon/anteprima`, anche senza account): per ogni offerta e variante (mensile o
 * annuale, con o senza rinnovo automatico, la prova) il prezzo con il coupon, lo sconto che vince secondo il cumulo e
 * quanto si risparmia. Sono gli stessi che farà il pagamento: la pagina non ricalcola niente. */

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { chiama } from "@/lib/api";

export type DurataCoupon = "una_volta" | "periodi" | "sempre";

export interface CouponPubblico {
  codice: string;
  tipo: "percentuale" | "importo";
  valore: number;
  durata: DurataCoupon;
  periodi: number | null;
  cumulabile: boolean;
  piani: string[];
  valido_fino: string | null;
}

/** Un'offerta con il coupon: il prezzo, oppure perché il codice non vale lì (`motivo`). */
export interface VoceCoupon {
  piano: string;
  annuale: boolean;
  rinnovo: boolean;
  prova: boolean;
  motivo?: string;
  listino?: number;
  sconto_base?: number;
  sconto_coupon?: number;
  sconto?: number;
  importo?: number;
  risparmio?: number;
  /** Quale sconto vale: il coupon, entrambi sommati, o lo sconto del rinnovo/della prova (il codice non si somma). */
  vince?: "coupon" | "entrambi" | "rinnovo" | "prova" | null;
  applicato?: boolean;
  cumulabile?: boolean;
  /** Lo sconto con cui partono i rinnovi, e quanti rinnovi avranno ancora il coupon (`null`: tutti). */
  sconto_ricorrente?: number;
  rinnovi_coupon?: number | null;
  nota?: string | null;
}

export interface AnteprimaCouponPubblica {
  coupon: CouponPubblico;
  offerte: VoceCoupon[];
}

export const anteprimaCouponPubblica = (token: string | null, codice: string) =>
  chiama<AnteprimaCouponPubblica>(token, "/coupon/anteprima", { method: "POST", body: { codice } });

const CHIAVE = "tarots.coupon";

/** Maiuscolo e senza spazi, come il server: chi lo scrive non deve indovinare le maiuscole. */
export const normalizzaCodice = (s: string) => s.replace(/\s+/g, "").toUpperCase();

function leggi(): string | null {
  try {
    return window.sessionStorage.getItem(CHIAVE);
  } catch {
    return null;
  }
}

function scrivi(codice: string | null) {
  try {
    if (codice) window.sessionStorage.setItem(CHIAVE, codice);
    else window.sessionStorage.removeItem(CHIAVE);
  } catch {
    /* archiviazione non disponibile: vale per questa pagina */
  }
}

/** Dimentica il codice (a pagamento avvenuto: un codice d'una volta non si ripropone). */
export const dimenticaCoupon = () => scrivi(null);

/** Il codice attivo nella sessione: quello del link (`?coupon=`), se no quello conservato. `imposta(null)` lo toglie.
 *  Va usato dentro un `Suspense` (legge i parametri dell'indirizzo). */
export function useCouponAttivo(): [string | null, (codice: string | null) => void] {
  const parametri = useSearchParams();
  const dalLink = parametri.get("coupon");
  const [codice, setCodice] = useState<string | null>(null);
  useEffect(() => {
    const scelto = dalLink ? normalizzaCodice(dalLink) : leggi();
    if (dalLink && scelto) scrivi(scelto);
    // Le preferenze del browser si leggono dopo il montaggio: sul server non ci sono.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setCodice(scelto || null);
  }, [dalLink]);
  const imposta = useCallback((nuovo: string | null) => {
    const c = nuovo ? normalizzaCodice(nuovo) : null;
    scrivi(c);
    setCodice(c);
  }, []);
  return [codice, imposta];
}

/** La variante che la pagina mostra. */
export function voceCoupon(
  anteprima: AnteprimaCouponPubblica | null | undefined, piano: string, annuale: boolean, rinnovo: boolean, prova = false,
): VoceCoupon | null {
  return anteprima?.offerte.find(
    (o) => o.piano === piano && o.annuale === annuale && o.rinnovo === rinnovo && o.prova === prova,
  ) ?? null;
}

/** Giorni di calendario alla scadenza, nell'ora di chi guarda (0 = scade oggi, 1 = domani), o `null` se non scade o è
 *  lontana (oltre `entro` giorni). La console fa scadere i codici a fine giornata: contano i giorni, non le ore. */
export function giorniAllaScadenza(validoFino: string | null, entro = 7): number | null {
  if (!validoFino) return null;
  const fine = new Date(validoFino);
  const adesso = new Date();
  if (!Number.isFinite(fine.getTime()) || fine.getTime() < adesso.getTime()) return null;
  const giorno = (d: Date) => Date.UTC(d.getFullYear(), d.getMonth(), d.getDate());
  const giorni = Math.round((giorno(fine) - giorno(adesso)) / 86_400_000);
  return giorni <= entro ? giorni : null;
}
