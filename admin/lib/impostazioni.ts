/* I numeri del regalo d'iscrizione e del referral: una riga sola, non un elenco. */

import { chiamata } from "./api";

export interface ImpostazioniCrediti {
  crediti_iscrizione: number;
  crediti_invito: number;
  commissione_referral_percentuale: number;
}

export const impostazioniCrediti = (t: string) =>
  chiamata<ImpostazioniCrediti>(t, "/admin/impostazioni-crediti");

export const salvaImpostazioniCrediti = (t: string, corpo: Partial<ImpostazioniCrediti>) =>
  chiamata<ImpostazioniCrediti>(t, "/admin/impostazioni-crediti", {
    method: "PUT",
    body: JSON.stringify(corpo),
  });

/* La chat proattiva (v6, Fase E): una sola manopola, il timer di inattività. */
export interface ImpostazioniChat {
  proattiva_minuti_inattivita: number;
  /** v8.5: aperture automatiche dell'oracolo per visita (0 = mai da solo). */
  proattiva_max_per_visita: number;
}

export const impostazioniChat = (t: string) =>
  chiamata<ImpostazioniChat>(t, "/admin/impostazioni-chat");

export const salvaImpostazioniChat = (t: string, corpo: Partial<ImpostazioniChat>) =>
  chiamata<ImpostazioniChat>(t, "/admin/impostazioni-chat", {
    method: "PUT",
    body: JSON.stringify(corpo),
  });

/* Login persistente: la sessione offline di Keycloak, letta e cambiata direttamente lì. `inattivita_giorni`: dopo
 * quanti giorni senza mai aprire il sito si deve rientrare; `durata_massima_giorni`: tetto assoluto, 0 = nessuno
 * (dentro fino al logout). `null` quando Keycloak non risponde (il motivo è in `errore`). */
export interface ImpostazioniSessione {
  keycloak_raggiungibile: boolean;
  errore: string | null;
  inattivita_giorni: number | null;
  durata_massima_giorni: number | null;
}

export interface ImpostazioniSessioneModifica {
  inattivita_giorni: number;
  durata_massima_giorni: number;
}

export const impostazioniSessione = (t: string) =>
  chiamata<ImpostazioniSessione>(t, "/admin/impostazioni-sessione");

export const salvaImpostazioniSessione = (t: string, corpo: ImpostazioniSessioneModifica) =>
  chiamata<ImpostazioniSessione>(t, "/admin/impostazioni-sessione", {
    method: "PUT",
    body: JSON.stringify(corpo),
  });
