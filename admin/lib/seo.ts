/* Notifica ai motori di ricerca (v8): cosa è configurato, cosa è partito, invio manuale. Il giro
 * normale lo fa un CronJob ogni notte a mezzanotte; qui si guarda e, se serve, si anticipa. */

import { chiamata } from "./api";

export type Canale = "indexnow" | "search_console" | "websub";
export type StatoCanale = "ok" | "errore" | "saltato";

export interface ConfigurazioneCanale {
  configurato: boolean;
  dettaglio: string;
}

export interface EsitoCanale {
  stato: StatoCanale;
  dettaglio: string;
}

export interface InvioMotori {
  id: string;
  avviata_il: string | null;
  finestra_da: string;
  manuale: boolean;
  url: string[];
  esiti: Partial<Record<Canale, EsitoCanale>>;
  riuscita: boolean;
}

export const notificheMotori = (t: string) =>
  chiamata<{ canali: Record<Canale, ConfigurazioneCanale>; invii: InvioMotori[] }>(t, "/admin/seo/notifiche");

export const inviaOraAiMotori = (t: string) =>
  chiamata<InvioMotori>(t, "/admin/seo/notifiche", { method: "POST" });
