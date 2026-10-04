/* Reddit dalla console (v8.6): l'account che pubblica, dove, la prova senza pubblicare, i post fatti e da fare.
 * Il secret dell'app e la password entrano e non escono: la console sa solo se ci sono. */

import { chiamata } from "./api";

export interface EsitoProvaReddit {
  accesso?: { ok: boolean; messaggio: string; karma?: number; giorni?: number };
  destinazione?: { ok: boolean; messaggio: string; gallerie?: boolean; flair?: { id: string; testo: string }[] };
}

export interface ConfigReddit {
  client_id: string | null;
  client_secret_impostato: boolean;
  client_secret_fine: string | null;
  utente: string | null;
  password_impostata: boolean;
  subreddit: string | null;
  flair_id: string | null;
  attivo: boolean;
  attivo_dal: string | null;
  lingue: string[];
  intervallo_minuti: number;
  ultima_prova_il: string | null;
  esito_prova: EsitoProvaReddit;
  mancano: string[];
  user_agent: string;
}

export type StatoPostReddit = "in_coda" | "in_corso" | "pubblicato" | "errore" | "saltato";

export interface PostReddit {
  id: string;
  articolo_id: string;
  stato: StatoPostReddit;
  tipo: "galleria" | "link" | null;
  subreddit: string | null;
  reddit_id: string | null;
  url: string | null;
  errore: string | null;
  tentativi: number;
  riprova_dopo: string | null;
  pubblicato_il: string | null;
  creato_il: string | null;
  articolo: { titolo: string; slug: string; lang: string; url: string } | null;
}

export interface StatoReddit {
  config: ConfigReddit;
  post: PostReddit[];
}

export interface ModificaReddit {
  client_id?: string;
  client_secret?: string;
  utente?: string;
  password?: string;
  subreddit?: string;
  flair_id?: string;
  attivo?: boolean;
  lingue?: string[];
  intervallo_minuti?: number;
}

export const statoReddit = (t: string) => chiamata<StatoReddit>(t, "/admin/reddit");

export const configuraReddit = (t: string, dati: ModificaReddit) =>
  chiamata<StatoReddit>(t, "/admin/reddit", { method: "PUT", body: JSON.stringify(dati) });

export const provaReddit = (t: string) => chiamata<StatoReddit>(t, "/admin/reddit/prova", { method: "POST" });

export const giroReddit = (t: string) => chiamata<{ avviato: boolean }>(t, "/admin/reddit/invia", { method: "POST" });

export const riprovaPostReddit = (t: string, id: string) =>
  chiamata<PostReddit>(t, `/admin/reddit/post/${id}/riprova`, { method: "POST" });

export const articoliSenzaReddit = (t: string) =>
  chiamata<{ id: string; titolo: string; slug: string; lang: string; pubblicato_il: string | null }[]>(t, "/admin/reddit/articoli");

export const portaSuReddit = (t: string, articoloId: string) =>
  chiamata<PostReddit>(t, `/admin/reddit/articoli/${articoloId}`, { method: "POST" });
