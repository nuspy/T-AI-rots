"use client";

/* Il contatore di Google (GA4) nelle pagine del sito (v8.6), **solo col consenso**.
 *
 * - L'ID di misurazione (`G-…`) lo decide la console (Analytics → Google) e il sito lo legge da un'impostazione
 *   pubblica (`/impostazioni-google`). Senza ID non si carica nulla.
 * - Lo script di Google non si scarica finché la persona non ha accettato la categoria `google_analytics` (GDPR,
 *   Fase 1: un consenso a sé, separato dalle statistiche del sito) su un'informativa che nomina Google Analytics
 *   (`VERSIONE_INFORMATIVA_V2` o successiva): chi aveva accettato il testo di prima rivede il banner (`daRinnovare`).
 * - Google Consent Mode v2: il consenso parte negato per tutto (`default`), poi si concede solo `analytics_storage`;
 *   pubblicità, dati utente per gli annunci e personalizzazione restano negati, i segnali Google spenti.
 * - Le pagine viste si mandano a mano a ogni cambio di percorso (è un'app a pagina singola), senza la query: può
 *   contenere dati personali. Restano solo i parametri `utm_*`, che servono a riconoscere le campagne.
 * - Il rifiuto, o la revoca dalla pagina privacy o dal profilo: il contatore si spegne (`ga-disable-…`, consenso negato) e i suoi
 *   cookie `_ga*` si cancellano.
 *
 * La v1 sotto `/old` ha il suo layout e non lo carica. */

import { usePathname } from "next/navigation";
import { useEffect, useRef, useSyncExternalStore } from "react";
import { leggiApi, statoConsensoGoogle } from "@/lib/api";
import { useSessione } from "@/lib/sessione";

/** L'informativa della v2 che nomina Google Analytics: la versione che si registra con la scelta sui cookie. */
export const VERSIONE_INFORMATIVA_V2 = "v2";

const ID_VALIDO = /^G-[A-Z0-9]{4,16}$/;

declare global {
  interface Window {
    dataLayer?: unknown[];
    [disattiva: `ga-disable-${string}`]: boolean | undefined;
  }
}

/* ---- lo stato condiviso (banner, privacy, contatore) ---- */

interface StatoGoogle {
  /** L'ID di misurazione configurato, o `null`: senza, niente contatore e niente banner da rinnovare. */
  misurazione: string | null;
  /** Consenso valido per Google Analytics. */
  attivo: boolean;
  /** Aveva accettato un'informativa che non nominava Google: il banner deve chiedere di nuovo. */
  daRinnovare: boolean;
}

const INIZIALE: StatoGoogle = { misurazione: null, attivo: false, daRinnovare: false };
let stato: StatoGoogle = INIZIALE;
const ascoltatori = new Set<() => void>();

function aggiorna(parziale: Partial<StatoGoogle>): void {
  stato = { ...stato, ...parziale };
  ascoltatori.forEach((f) => f());
}

function iscriviti(f: () => void): () => void {
  ascoltatori.add(f);
  return () => ascoltatori.delete(f);
}

export function useStatoGoogle(): StatoGoogle {
  return useSyncExternalStore(iscriviti, () => stato, () => INIZIALE);
}

/** Da chiamare dopo aver registrato una scelta sui cookie (banner o pagina privacy): vale subito, senza ricaricare. */
export function annunciaConsensoGoogle(accettato: boolean): void {
  aggiorna({ attivo: accettato, daRinnovare: false });
}

/* ---- gtag ---- */

/* gtag.js riconosce i comandi solo come oggetto `arguments`, non come array: la funzione è quella del frammento
 * ufficiale, tipizzata dopo. */
const gtag = function gtag() {
  window.dataLayer = window.dataLayer || [];
  // eslint-disable-next-line prefer-rest-params
  window.dataLayer.push(arguments);
} as unknown as (...argomenti: unknown[]) => void;

let caricato: string | null = null;

function carica(id: string): void {
  window[`ga-disable-${id}`] = false;
  if (caricato === id) {
    gtag("consent", "update", { analytics_storage: "granted" });
    return;
  }
  gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    functionality_storage: "denied",
    personalization_storage: "denied",
    security_storage: "granted",
  });
  gtag("consent", "update", { analytics_storage: "granted" });
  gtag("js", new Date());
  gtag("config", id, {
    send_page_view: false,
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
  });
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
  document.head.appendChild(script);
  caricato = id;
}

function spegni(id: string): void {
  window[`ga-disable-${id}`] = true;
  gtag("consent", "update", { analytics_storage: "denied" });
  const host = window.location.hostname;
  const radice = host.split(".").slice(-2).join(".");
  const domini = ["", host, `.${host}`, `.${radice}`];
  for (const voce of document.cookie.split(";")) {
    const nome = voce.split("=")[0]?.trim();
    if (!nome || !nome.startsWith("_ga")) continue;
    for (const d of domini) {
      document.cookie = `${nome}=; Max-Age=0; path=/${d ? `; domain=${d}` : ""}`;
    }
  }
}

/** L'indirizzo della pagina per Google: senza query, tranne i parametri delle campagne. */
function indirizzo(): string {
  const url = new URL(window.location.href);
  const utm = new URLSearchParams();
  url.searchParams.forEach((valore, chiave) => {
    if (chiave.startsWith("utm_")) utm.set(chiave, valore);
  });
  const q = utm.toString();
  return `${url.origin}${url.pathname}${q ? `?${q}` : ""}`;
}

/* ---- il componente ---- */

export function ContatoreGoogle() {
  const percorso = usePathname();
  const sessione = useSessione();
  const { misurazione, attivo } = useStatoGoogle();
  const ultimaVista = useRef<string | null>(null);

  /* L'ID configurato in console (un'impostazione pubblica, in cache per qualche minuto). */
  useEffect(() => {
    let annullato = false;
    leggiApi<{ ga4_misurazione_id: string | null }>("/impostazioni-google")
      .then((r) => {
        const id = (r.ga4_misurazione_id ?? "").toUpperCase();
        if (!annullato && ID_VALIDO.test(id)) aggiorna({ misurazione: id });
      })
      .catch(() => {});
    return () => {
      annullato = true;
    };
  }, []);

  /* Il consenso di questa persona: solo se c'è un contatore da caricare, e di nuovo quando entra o esce. */
  useEffect(() => {
    if (!misurazione || !sessione.pronta) return;
    let annullato = false;
    statoConsensoGoogle(sessione.token)
      .then((c) => {
        if (!annullato) aggiorna({ attivo: c.attivo, daRinnovare: c.da_rinnovare });
      })
      .catch(() => {});
    return () => {
      annullato = true;
    };
  }, [misurazione, sessione.pronta, sessione.token]);

  useEffect(() => {
    if (!misurazione) return;
    if (attivo) carica(misurazione);
    else if (caricato === misurazione) spegni(misurazione);
  }, [misurazione, attivo]);

  /* Una pagina vista a ogni cambio di percorso, dopo che il titolo della pagina nuova è al suo posto. */
  useEffect(() => {
    if (!misurazione || !attivo || caricato !== misurazione) return;
    const chiave = `${percorso}`;
    if (ultimaVista.current === chiave) return;
    const t = window.setTimeout(() => {
      ultimaVista.current = chiave;
      gtag("event", "page_view", { page_location: indirizzo(), page_title: document.title, send_to: misurazione });
    }, 300);
    return () => window.clearTimeout(t);
  }, [percorso, misurazione, attivo]);

  return null;
}
