/* «Conservazione dati» (GDPR, Fase 1): quanto c'è e di che età, per voce, e la cancellazione manuale con anteprima.
 * Il backend è `api/routers/admin_conservazione.py`: niente pulizie automatiche (decisione dell'operatore), ogni
 * esecuzione ripete il numero mostrato dall'anteprima e resta nel registro. */

import { chiamata } from "./api";

export type ChiaveVoce =
  | "letture_anonime" | "chat_proattiva" | "ip_audit" | "account_in_cancellazione" | "consensi_storici";

export interface Fascia {
  etichetta: string;
  da_giorni: number;
  a_giorni: number | null;
  quanti: number;
}

export interface VoceConservazione {
  chiave: ChiaveVoce;
  titolo: string;
  descrizione: string;
  azione: string;
  totale: number;
  fasce: Fascia[];
}

export interface Riepilogo {
  voci: VoceConservazione[];
  giorni_ripensamento: number;
}

export interface Anteprima {
  voce: ChiaveVoce;
  giorni: number;
  azione: string;
  quanti: number;
  piu_vecchio: string | null;
  piu_recente: string | null;
}

export interface Esito {
  voce: ChiaveVoce;
  fatti: number;
  falliti?: { utente: number; errore: string }[];
}

export const leggiConservazione = (token: string) => chiamata<Riepilogo>(token, "/admin/conservazione");

export const anteprimaConservazione = (token: string, voce: ChiaveVoce, giorni: number) =>
  chiamata<Anteprima>(token, `/admin/conservazione/${voce}/anteprima`, {
    method: "POST", body: JSON.stringify({ giorni }),
  });

export const eseguiConservazione = (token: string, voce: ChiaveVoce, giorni: number, attesi: number) =>
  chiamata<Esito>(token, `/admin/conservazione/${voce}/esegui`, {
    method: "POST", body: JSON.stringify({ giorni, attesi }),
  });
