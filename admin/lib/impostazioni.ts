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
