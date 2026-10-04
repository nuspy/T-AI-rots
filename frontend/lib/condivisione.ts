/* La condivisione delle letture: l'indirizzo del sito, l'identità anonima del
 * browser, la memoria del link da cui si arriva e gli indirizzi dei pulsanti.
 *
 * Nessun sito può sapere se un utente ha davvero pubblicato un post: le
 * piattaforme non lo dicono. Si conta ciò che si può verificare, cioè che il link
 * sia stato aperto da qualcun altro dopo un clic di condivisione. Per farlo il
 * server distingue chi condivide da chi visita con un identificativo casuale del
 * browser (`idVisitatore`), che non è un dato personale e non viaggia mai da solo:
 * il server ne conserva soltanto un'impronta con sale. */

import type { CanaleCondivisione } from "./api";

/* Il sito che si vede nei link e sulle immagini. In sviluppo si cambia con
 * `NEXT_PUBLIC_SITE_URL`; senza, è quello di produzione. */
export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL ?? "https://tarots.chat").replace(/\/+$/, "");
export const DOMINIO = (() => {
  try {
    return new URL(SITE_URL).host;
  } catch {
    return "tarots.chat";
  }
})();

/* Le letture regalate a chi condivide per ogni persona che si iscrive dal suo link
 * (come `CREDITI_ISCRIZIONE` sul server; il contatore del profilo porta il valore vero). */
export const CREDITI_ISCRIZIONE = 5;

/* La lunghezza massima del testo personalizzato (come `LUNGHEZZA_TESTO` sul server). */
export const LUNGHEZZA_TESTO = 200;

export const urlCondivisione = (token: string) => `${SITE_URL}/s/${token}`;

/* ---- l'identità anonima del browser ---- */

const CHIAVE_VISITATORE = "tarots.visitatore";
let inMemoria: string | null = null;
/* GDPR, Fase 1: l'identificativo resta nella memoria del browser (localStorage) solo col consenso `statistiche`.
 * Senza, vive quanto la pagina: basta a distinguere chi condivide da chi apre il link nella stessa visita, e non
 * riconosce nessuno nei giorni successivi. Lo imposta `impostaConsensoAnalytics` (`lib/analytics.ts`). */
let memoriaConsentita = false;

/** Col consenso alle statistiche l'identificativo si salva nel browser; revocato, si cancella da lì (resta solo per
 *  questa pagina, finché il server non lo dimentica). */
export function consentiMemoriaVisitatore(consentita: boolean): void {
  memoriaConsentita = consentita;
  try {
    if (consentita) {
      const salvato = window.localStorage.getItem(CHIAVE_VISITATORE);
      if (!salvato && inMemoria) window.localStorage.setItem(CHIAVE_VISITATORE, inMemoria);
    } else {
      window.localStorage.removeItem(CHIAVE_VISITATORE);
    }
  } catch {
    /* memoria bloccata: l'identificativo resta solo per questa pagina */
  }
}

const nuovoId = () =>
  (globalThis.crypto?.randomUUID?.() ?? `${Date.now().toString(36)}${Math.random().toString(36).slice(2)}${Math.random().toString(36).slice(2)}`)
    .replace(/[^A-Za-z0-9]/g, "")
    .slice(0, 32)
    .padEnd(16, "0");

/** Un identificativo casuale per questo browser (16–64 caratteri alfanumerici): stabile fra le visite solo col
 *  consenso `statistiche`, altrimenti (o con la memoria del browser bloccata) dura quanto la pagina. */
export function idVisitatore(): string {
  try {
    const salvato = window.localStorage.getItem(CHIAVE_VISITATORE);
    if (salvato && /^[A-Za-z0-9_-]{16,64}$/.test(salvato)) return salvato;
    inMemoria ??= nuovoId();
    if (memoriaConsentita) window.localStorage.setItem(CHIAVE_VISITATORE, inMemoria);
    return inMemoria;
  } catch {
    inMemoria ??= nuovoId();
    return inMemoria;
  }
}

/* ---- il link da cui si arriva ---- */

const CHIAVE_ORIGINE = "tarots.origine";
const VALIDITA_ORIGINE_MS = 7 * 24 * 3600 * 1000;

/** Ricorda il link condiviso che questa persona ha aperto: se poi si iscrive, chi
 *  l'ha condiviso riceve le sue letture in regalo. */
export function ricordaOrigine(token: string): void {
  try {
    window.localStorage.setItem(CHIAVE_ORIGINE, JSON.stringify({ token, quando: Date.now() }));
  } catch {
    /* memoria bloccata: nessuna attribuzione, nient'altro */
  }
}

export function leggiOrigine(): string | null {
  try {
    const grezzo = window.localStorage.getItem(CHIAVE_ORIGINE);
    if (!grezzo) return null;
    const { token, quando } = JSON.parse(grezzo) as { token?: string; quando?: number };
    if (typeof token !== "string" || typeof quando !== "number" || Date.now() - quando > VALIDITA_ORIGINE_MS) {
      window.localStorage.removeItem(CHIAVE_ORIGINE);
      return null;
    }
    return token;
  } catch {
    return null;
  }
}

export function dimenticaOrigine(): void {
  try {
    window.localStorage.removeItem(CHIAVE_ORIGINE);
  } catch {
    /* niente da fare */
  }
}

/* ---- i pulsanti ---- */

export const CANALI: readonly Exclude<CanaleCondivisione, "nativo">[] = [
  "instagram", "facebook", "tiktok", "x", "email", "link",
];

/** L'indirizzo che apre la finestra di condivisione del canale, dove ne esiste una
 *  pubblica: Facebook e X leggono l'anteprima dal link (l'immagine è la nostra
 *  `og:image`), la posta apre il programma di posta. Instagram e TikTok non hanno
 *  un indirizzo di condivisione da un sito: si condividono dal foglio di
 *  condivisione del telefono (con l'immagine) o, sul computer, scaricando
 *  l'immagine. */
export function urlIntento(
  canale: CanaleCondivisione, { url, testo, oggetto }: { url: string; testo: string; oggetto: string },
): string | null {
  const c = encodeURIComponent;
  switch (canale) {
    case "facebook":
      return `https://www.facebook.com/sharer/sharer.php?u=${c(url)}`;
    case "x":
      return `https://x.com/intent/post?text=${c(testo)}&url=${c(url)}`;
    case "email":
      return `mailto:?subject=${c(oggetto)}&body=${c(testo ? `${testo}\n\n${url}` : url)}`;
    default:
      return null;
  }
}

/* Dove si carica l'immagine, sul computer, per i due social che non hanno un
 * indirizzo di condivisione. */
export const SITO_CANALE: Partial<Record<CanaleCondivisione, string>> = {
  instagram: "https://www.instagram.com/",
  tiktok: "https://www.tiktok.com/upload",
};

/** Vero se il dispositivo apre il foglio di condivisione del sistema con dei file:
 *  il telefono (puntatore «grossolano»). Sul computer Edge e Chrome dichiarano di
 *  saperlo fare, ma aprirebbero la condivisione di Windows invece di salvare. */
export function puoCondividereFile(file: File): boolean {
  try {
    return window.matchMedia("(pointer: coarse)").matches && !!navigator.canShare?.({ files: [file] });
  } catch {
    return false;
  }
}
