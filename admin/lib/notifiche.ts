/* «Notifications» (v9, Fase 5): campagne push verso un segmento di utenti, notifiche automatiche, consegne e
 * aperture, impostazioni (Firebase, chiavi VAPID, ore di silenzio, tetti).
 *
 * Il service account di Firebase entra e non torna: la console vede solo progetto, email e l'esito della prova. */

import { chiamata } from "./api";

export type Lingua = "en" | "it" | "hu" | "ru" | "uk" | "es";
export type Canale = "fcm" | "webpush";
export type Piattaforma = "android" | "ios" | "web";
export type TipoCampagna = "servizio" | "promozione";
export type StatoCampagna = "bozza" | "programmata" | "in_invio" | "inviata" | "annullata";

export const NOMI_LINGUA: Record<Lingua, string> = {
  it: "Italiano", en: "Inglese", hu: "Ungherese", ru: "Russo", uk: "Ucraino", es: "Spagnolo",
};
export const LINGUE: Lingua[] = ["it", "en", "hu", "ru", "uk", "es"];
export const NOMI_CANALE: Record<Canale, string> = { fcm: "App (Android e iOS, via Firebase)", webpush: "Sito (Web Push)" };
export const NOMI_PIATTAFORMA: Record<Piattaforma, string> = { android: "Android", ios: "iPhone e iPad", web: "Browser" };
export const NOMI_TIPO: Record<TipoCampagna, string> = { servizio: "Servizio", promozione: "Promozione" };
export const NOMI_STATO: Record<StatoCampagna, string> = {
  bozza: "Bozza", programmata: "Programmata", in_invio: "In invio", inviata: "Inviata", annullata: "Annullata",
};

export interface Testo {
  titolo: string;
  corpo: string;
}
export type Testi = Partial<Record<Lingua, Testo>>;

export interface Filtro {
  lingue?: string[];
  paesi?: string[];
  fasce_eta?: string[];
  primi_canali?: string[];
  attivi_negli_ultimi_giorni?: number | null;
  inattivi_da_giorni?: number | null;
  ultima_lettura_almeno_giorni?: number | null;
  ultima_lettura_al_massimo_giorni?: number | null;
  ha_acquistato?: boolean | null;
  piani?: string[];
  abbonamento_attivo?: boolean | null;
  in_prova?: boolean | null;
  crediti_min?: number | null;
  crediti_max?: number | null;
  piattaforme?: Piattaforma[];
}

export interface Campagna {
  id: number;
  nome: string;
  tipo: TipoCampagna;
  testi: Testi;
  lingua_base: Lingua;
  deep_link: string;
  immagine: string | null;
  filtro: Filtro;
  canali: Canale[];
  rispetta_silenzio: boolean;
  stato: StatoCampagna;
  programmata_il: string | null;
  iniziata_il: string | null;
  finita_il: string | null;
  contatori: { destinatari: number; inviati: number; errori: number; saltati: number; aperti: number };
  creata_il: string | null;
  modificata_il: string | null;
}

export type CampagnaIn = Pick<
  Campagna, "nome" | "tipo" | "testi" | "lingua_base" | "deep_link" | "immagine" | "filtro" | "canali" | "rispetta_silenzio"
>;

export interface Automatica {
  tipo: string;
  nome: string;
  spiegazione: string;
  attiva: boolean;
  ora: string | null;
  ha_ora: boolean;
  link: string;
  testi: Record<Lingua, Testo>;
  personalizzati: Lingua[];
}

export interface StatoNotifiche {
  firebase: {
    presente: boolean;
    progetto: string | null;
    email: string | null;
    caricato_il: string | null;
    prova_il: string | null;
    esito: { ok?: boolean; messaggio?: string };
  };
  vapid: { presente: boolean; pubblica: string | null; creata_il: string | null; contatto: string };
  impostazioni: {
    ora_carta: string;
    silenzio_dal: string | null;
    silenzio_al: string | null;
    tetto_promozioni_settimana: number;
    limite_al_minuto: number;
    vapid_contatto: string;
  };
  automatiche: Automatica[];
  dispositivi: Record<Piattaforma, { attivi: number; disattivati: number }>;
  catalogo: {
    lingue: Lingua[];
    canali: Canale[];
    piattaforme: Piattaforma[];
    fasce_eta: string[];
    piani: { slug: string; nome: string }[];
  };
}

export interface Conteggio {
  corrispondono: number;
  senza_consenso: number;
  senza_dispositivo: number;
  destinatari: number;
  per_piattaforma: Record<Piattaforma, number>;
}

export interface EsitoInviaAMe {
  esito: string;
  messaggio: string;
  dettagli: { dispositivo: number; canale: Canale; piattaforma: Piattaforma; esito: string; messaggio: string }[];
}

export interface RigaStatistica {
  invii: number;
  consegnati: number;
  errori: number;
  token_invalidi: number;
  aperti: number;
  tasso_apertura: number | null;
}

export interface Statistiche {
  giorni: number;
  totali: RigaStatistica;
  per_tipo: (RigaStatistica & { tipo: string; nome: string })[];
  per_giorno: (RigaStatistica & { giorno: string })[];
  dispositivi_disattivati: number;
}

const json = (corpo: unknown): RequestInit => ({ body: JSON.stringify(corpo) });

export const statoNotifiche = (t: string) => chiamata<StatoNotifiche>(t, "/admin/notifiche");
export const salvaImpostazioni = (t: string, corpo: Record<string, unknown>) =>
  chiamata<StatoNotifiche>(t, "/admin/notifiche/impostazioni", { method: "PUT", ...json(corpo) });
export const caricaFirebase = (t: string, testo: string) =>
  chiamata<StatoNotifiche>(t, "/admin/notifiche/firebase", { method: "PUT", ...json({ service_account_json: testo }) });
export const togliFirebase = (t: string) => chiamata<StatoNotifiche>(t, "/admin/notifiche/firebase", { method: "DELETE" });
export const provaFirebase = (t: string) => chiamata<StatoNotifiche>(t, "/admin/notifiche/firebase/prova", { method: "POST" });
export const salvaAutomatica = (t: string, tipo: string, corpo: { attiva?: boolean; ora?: string; testi?: Testi }) =>
  chiamata<StatoNotifiche>(t, `/admin/notifiche/automatiche/${encodeURIComponent(tipo)}`, { method: "PUT", ...json(corpo) });

export const traduci = (t: string, base: Lingua, testo: Testo, lingue: Lingua[]) =>
  chiamata<{ testi: Testi }>(t, "/admin/notifiche/traduci", { method: "POST", ...json({ base, ...testo, lingue }) });
export const conta = (t: string, tipo: TipoCampagna, filtro: Filtro, canali: Canale[]) =>
  chiamata<Conteggio>(t, "/admin/notifiche/conteggio", { method: "POST", ...json({ tipo, filtro, canali }) });

export const elencoCampagne = (t: string) => chiamata<{ campagne: Campagna[] }>(t, "/admin/notifiche/campagne");
export const leggiCampagna = (t: string, id: number) => chiamata<Campagna>(t, `/admin/notifiche/campagne/${id}`);
export const creaCampagna = (t: string, c: CampagnaIn) =>
  chiamata<Campagna>(t, "/admin/notifiche/campagne", { method: "POST", ...json(c) });
export const modificaCampagna = (t: string, id: number, c: CampagnaIn) =>
  chiamata<Campagna>(t, `/admin/notifiche/campagne/${id}`, { method: "PUT", ...json(c) });
export const eliminaCampagna = (t: string, id: number) =>
  chiamata<{ eliminata: number }>(t, `/admin/notifiche/campagne/${id}`, { method: "DELETE" });
export const programmaCampagna = (t: string, id: number, quando: string | null) =>
  chiamata<Campagna>(t, `/admin/notifiche/campagne/${id}/programma`, { method: "POST", ...json({ quando }) });
export const annullaCampagna = (t: string, id: number) =>
  chiamata<Campagna>(t, `/admin/notifiche/campagne/${id}/annulla`, { method: "POST" });
export const duplicaCampagna = (t: string, id: number) =>
  chiamata<Campagna>(t, `/admin/notifiche/campagne/${id}/duplica`, { method: "POST" });
export const inviaAMe = (t: string, id: number) =>
  chiamata<EsitoInviaAMe>(t, `/admin/notifiche/campagne/${id}/invia-a-me`, { method: "POST" });

export const statistiche = (t: string, giorni: number) =>
  chiamata<Statistiche>(t, `/admin/notifiche/statistiche?giorni=${giorni}`);

/** Il filtro senza i campi vuoti: quello che il server salva e quello che si confronta. */
export function filtroPulito(f: Filtro): Filtro {
  const fuori: Filtro = {};
  for (const [k, v] of Object.entries(f) as [keyof Filtro, unknown][]) {
    if (v === null || v === undefined || v === "" || (Array.isArray(v) && v.length === 0)) continue;
    (fuori as Record<string, unknown>)[k] = v;
  }
  return fuori;
}
