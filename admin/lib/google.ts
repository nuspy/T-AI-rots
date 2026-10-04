/* Google dalla console (v8.6): il service account (Search Console e GA4), la verifica guidata, le statistiche GA4
 * e l'ID di misurazione del contatore del sito. La chiave del service account entra una volta e non torna mai: la
 * console vede l'email, il progetto e gli ultimi caratteri dell'id della chiave. */

import { chiamata } from "./api";

export type PassoVerifica = "credenziali" | "search_console" | "sitemap" | "ga4" | "contatore";

export interface EsitoPasso {
  ok: boolean;
  messaggio: string;
  /** Non provato perché dipende da un passo non riuscito o da un dato mancante. */
  saltato?: boolean;
  livello?: string;
}

export interface StatoGoogle {
  credenziali: {
    presenti: boolean;
    /** `console` (caricate qui, cifrate) o `file` (il file montato sul server, il ripiego). */
    origine: "console" | "file" | null;
    client_email: string | null;
    project_id: string | null;
    chiave_fine: string | null;
  };
  sc_proprieta: string;
  sc_proprieta_personalizzata: boolean;
  ga4_proprieta_id: string | null;
  ga4_misurazione_id: string | null;
  sitemap: string;
  verificato_il: string | null;
  esito_verifica: Partial<Record<PassoVerifica, EsitoPasso>>;
}

export interface StatisticheGoogle {
  pronto: boolean;
  mancano?: string[];
  errore?: string;
  misurazione?: string | null;
  proprieta?: string;
  da?: string;
  a?: string;
  totali?: Record<string, number>;
  precedente?: Record<string, number> | null;
  giorni?: { giorno: string; utenti: number; sessioni: number; visualizzazioni: number }[];
  pagine?: { pagina: string; visualizzazioni: number; utenti: number }[];
  sorgenti?: { sorgente: string; sessioni: number; utenti: number }[];
  canali?: { canale: string; sessioni: number }[];
  aggiornato_il?: string;
}

export const statoGoogle = (t: string) => chiamata<StatoGoogle>(t, "/admin/google");

export const caricaServiceAccount = (t: string, json: string) =>
  chiamata<StatoGoogle>(t, "/admin/google/credenziali", {
    method: "POST",
    body: JSON.stringify({ json_service_account: json }),
  });

export const togliServiceAccount = (t: string) => chiamata<StatoGoogle>(t, "/admin/google/credenziali", { method: "DELETE" });

export const impostaGoogle = (
  t: string,
  dati: { sc_proprieta?: string; ga4_proprieta_id?: string; ga4_misurazione_id?: string },
) => chiamata<StatoGoogle>(t, "/admin/google/impostazioni", { method: "PUT", body: JSON.stringify(dati) });

export const verificaGoogle = (t: string) => chiamata<StatoGoogle>(t, "/admin/google/verifica", { method: "POST" });

export const statisticheGoogle = (t: string, giorni: number) =>
  chiamata<StatisticheGoogle>(t, `/admin/google/statistiche?giorni=${giorni}`);
