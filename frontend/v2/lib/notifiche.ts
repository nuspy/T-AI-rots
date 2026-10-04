/* Le notifiche del sito (v9, Fase 5): Web Push nel browser, preferenze, fuso orario.
 *
 * Il permesso si chiede **solo dopo un gesto della persona** e mai al caricamento: dopo aver girato la carta del
 * giorno («vuoi che te la ricordiamo ogni mattina?») o dal profilo. Prima l'invito del sito (nostro, cortese,
 * rifiutabile), poi — se dice sì — la finestra del browser: un «no» del browser è difficile da ritirare, e chiederlo a
 * freddo lo rende quasi certo.
 *
 * Il percorso: si registra il service worker (`/sw.js`, solo notifiche), si chiede al server la chiave pubblica
 * VAPID, il browser crea la sottoscrizione presso il suo servizio push e la si manda a `POST /me/dispositivi` con la
 * lingua e il fuso. Togliere le notifiche dal profilo cancella la sottoscrizione nel browser e sul server.
 *
 * iPhone e iPad: Safari riceve il Web Push solo dal sito aggiunto alla schermata Home (iOS 16.4+). In una scheda
 * normale `PushManager` non c'è: lo si dice, con le istruzioni, invece di un pulsante che non può funzionare. */

import { chiama, type CartaDelGiorno } from "@/lib/api";

export interface DispositivoNotifiche {
  id: number;
  canale: "fcm" | "webpush";
  piattaforma: "android" | "ios" | "web";
  attivo: boolean;
  lingua: string | null;
  versione_app: string | null;
  registrato_il: string | null;
  ultimo_visto: string | null;
}

export interface PreferenzeNotifiche {
  carta_giorno: boolean;
  ora_carta: string;
  silenzio: boolean;
  silenzio_dal: string;
  silenzio_al: string;
  promemoria: boolean;
  tetto_promozioni_settimana: number;
  tetto_massimo: number;
  promozioni: boolean;
  fuso_orario: string | null;
  personalizzate: boolean;
  dispositivi: DispositivoNotifiche[];
}

export type ModificaPreferenze = Partial<Pick<PreferenzeNotifiche,
  "carta_giorno" | "ora_carta" | "silenzio" | "silenzio_dal" | "silenzio_al" | "promemoria" | "tetto_promozioni_settimana">>;

/** Il fuso del browser (IANA), o `null` se il browser non lo dice. */
export function fusoDelBrowser(): string | null {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || null;
  } catch {
    return null;
  }
}

export const leggiPreferenze = (token: string | null) => chiama<PreferenzeNotifiche>(token, "/me/preferenze-notifica");
export const salvaPreferenze = (token: string | null, corpo: ModificaPreferenze) =>
  chiama<PreferenzeNotifiche>(token, "/me/preferenze-notifica", { method: "PUT", body: corpo });
export const salvaFuso = (token: string | null, fuso: string) =>
  chiama<{ fuso_orario: string }>(token, "/me/fuso-orario", { method: "PUT", body: { fuso_orario: fuso } });

/** La carta del giorno personale sul giorno **locale**: il fuso del browser viaggia con la richiesta (e si salva). */
export function cartaDelGiornoLocale(token: string | null): Promise<CartaDelGiorno> {
  const fuso = fusoDelBrowser();
  return chiama<CartaDelGiorno>(token, fuso ? `/me/daily-card?fuso=${encodeURIComponent(fuso)}` : "/me/daily-card");
}

/* ---- il browser ---- */

export type Disponibilita = "si" | "ios_home" | "no";

function suIos(): boolean {
  if (typeof navigator === "undefined") return false;
  /* iPadOS si presenta come un Mac: lo tradisce il tocco. */
  return /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
}

function inStandalone(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia?.("(display-mode: standalone)").matches
    || (navigator as Navigator & { standalone?: boolean }).standalone === true;
}

/** Se questo browser può ricevere notifiche dal sito: sì, solo dalla schermata Home (iPhone e iPad), o no. */
export function disponibilita(): Disponibilita {
  if (typeof window === "undefined") return "no";
  const ha = "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
  if (ha) return "si";
  return suIos() && !inStandalone() ? "ios_home" : "no";
}

export function permesso(): NotificationPermission | "non_supportato" {
  return typeof Notification === "undefined" ? "non_supportato" : Notification.permission;
}

function chiaveDaBase64(base64: string): Uint8Array<ArrayBuffer> {
  const pulita = (base64 + "=".repeat((4 - (base64.length % 4)) % 4)).replace(/-/g, "+").replace(/_/g, "/");
  const grezza = atob(pulita);
  const fuori = new Uint8Array(new ArrayBuffer(grezza.length));
  for (let i = 0; i < grezza.length; i++) fuori[i] = grezza.charCodeAt(i);
  return fuori;
}

async function registrazione(): Promise<ServiceWorkerRegistration> {
  const r = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
  return navigator.serviceWorker.ready.then(() => r);
}

/** L'iscrizione di questo browser, se c'è già (senza chiedere niente). */
export async function iscrizioneAttuale(): Promise<PushSubscription | null> {
  if (disponibilita() !== "si") return null;
  const r = await navigator.serviceWorker.getRegistration("/");
  return r ? r.pushManager.getSubscription() : null;
}

export type EsitoAttivazione = "attive" | "negato" | "non_supportato" | "errore";

/** Chiede il permesso (deve partire da un tocco), iscrive il browser e lo registra sul server. */
export async function attiva(token: string | null, lingua: string): Promise<EsitoAttivazione> {
  if (disponibilita() !== "si") return "non_supportato";
  const scelta = Notification.permission === "granted" ? "granted" : await Notification.requestPermission();
  if (scelta !== "granted") return "negato";
  try {
    const r = await registrazione();
    const { chiave } = await chiama<{ chiave: string }>(null, "/notifiche/vapid");
    let iscrizione = await r.pushManager.getSubscription();
    if (!iscrizione) {
      iscrizione = await r.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: chiaveDaBase64(chiave) });
    }
    const j = iscrizione.toJSON();
    await chiama(token, "/me/dispositivi", {
      method: "POST",
      body: {
        canale: "webpush", piattaforma: "web", endpoint: j.endpoint, p256dh: j.keys?.p256dh, auth: j.keys?.auth,
        lingua, fuso_orario: fusoDelBrowser(),
      },
    });
    return "attive";
  } catch {
    return "errore";
  }
}

/** Toglie le notifiche da questo browser: la sottoscrizione sparisce dal browser e dal server. */
export async function disattiva(token: string | null): Promise<void> {
  const iscrizione = await iscrizioneAttuale();
  if (!iscrizione) return;
  const endpoint = iscrizione.endpoint;
  await iscrizione.unsubscribe().catch(() => undefined);
  await chiama(token, "/me/dispositivi", { method: "DELETE", body: { canale: "webpush", endpoint } });
}

/* ---- l'invito dopo la carta del giorno ---- */

const CHIAVE_INVITO = "tarots.invitoNotifiche";
/** Dopo un «non ora», l'invito torna fra un mese. */
const RIPOSO = 30 * 24 * 60 * 60 * 1000;

export function invitoDaMostrare(): boolean {
  try {
    const il = Number(window.localStorage.getItem(CHIAVE_INVITO) ?? 0);
    return !il || Date.now() - il > RIPOSO;
  } catch {
    return true;
  }
}

export function invitoChiuso(): void {
  try {
    window.localStorage.setItem(CHIAVE_INVITO, String(Date.now()));
  } catch {
    /* memoria bloccata: l'invito tornerà, pazienza */
  }
}
