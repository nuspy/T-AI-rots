/* I contenuti di un utente (v9.5): letture, chat, memorie e profilazione, solo dopo un motivo.
 * Backend: `api/routers/admin_contenuti_utente.py`. Ogni lettura resta nel registro, con chi l'ha fatta. */
import { chiamata } from "./api";

export type Scheda = "letture" | "chat" | "memorie" | "profilo";

export interface Accesso {
  accesso: string;
  scade: string;
  minuti: number;
}

export interface LetturaUtente {
  id: string;
  stesa: string;
  stato: string;
  lingua: string;
  consumo: string;
  manuale: boolean;
  creata: string | null;
  completata: string | null;
  domanda: string;
  intervista: { ruolo: "oracolo" | "utente"; testo: string; quando: string | null }[];
  quadro: string | null;
  carte: { posizione: number; carta: string; rovescio: boolean; calcolata: boolean; interpretazione: string | null }[];
  sintesi: string | null;
  anteprima: string | null;
  guardrail: string | null;
  memorie_usate: { contenuto?: string; tipo?: string }[];
  persone: Record<string, unknown> | null;
  diario: { esito: string; nota: string | null; quando: string | null } | null;
  condivisa: boolean;
  testo_condivisione: string | null;
}

export interface Pagina {
  totale: number;
  pagina: number;
  per_pagina: number;
}

export interface Letture extends Pagina {
  letture: LetturaUtente[];
  carte_del_giorno: { giorno: string | null; carta: string; rovescio: boolean; testo: string | null }[];
}

export interface Chat extends Pagina {
  messaggi: { ordine: number; ruolo: "ai" | "utente"; testo: string; proposta: Record<string, unknown> | null; quando: string | null }[];
}

export interface Memorie {
  stato_sintetico: { voci: Record<string, unknown>[]; aggiornato: string | null } | null;
  memorie: {
    id: string; contenuto: string; tipo: string; campo: string; fonte: string;
    lettura: string | null; sostituita_da: string | null; creata: string | null;
  }[];
}

export interface Profilo {
  persona: Record<string, unknown>;
  consensi: { tipo: string; valore: string; informativa: string; origine: string; aggiornato: string | null }[];
  storico_consensi: { tipo: string; valore: string; informativa: string; origine: string; quando: string | null }[];
  notifiche: Record<string, unknown> | null;
  dispositivi: Record<string, unknown>[];
}

export interface VoceAccesso {
  quando: string | null;
  chi: string | number | null;
  azione: "accesso" | "lettura";
  motivo: string | null;
  scheda: Scheda | null;
  pagina: number | null;
}

const base = (id: number) => `/admin/users/${id}/contenuti`;

export const apriAccesso = (t: string, id: number, motivo: string) =>
  chiamata<Accesso>(t, `${base(id)}/accesso`, { method: "POST", body: JSON.stringify({ motivo }) });

export const leggiLetture = (t: string, id: number, accesso: string, pagina = 1) =>
  chiamata<Letture>(t, `${base(id)}/letture?accesso=${encodeURIComponent(accesso)}&pagina=${pagina}&per_pagina=10`);

export const leggiChat = (t: string, id: number, accesso: string, pagina = 1) =>
  chiamata<Chat>(t, `${base(id)}/chat?accesso=${encodeURIComponent(accesso)}&pagina=${pagina}&per_pagina=50`);

export const leggiMemorie = (t: string, id: number, accesso: string) =>
  chiamata<Memorie>(t, `${base(id)}/memorie?accesso=${encodeURIComponent(accesso)}`);

export const leggiProfilo = (t: string, id: number, accesso: string) =>
  chiamata<Profilo>(t, `${base(id)}/profilo?accesso=${encodeURIComponent(accesso)}`);

export const accessiUtente = (t: string, id: number) =>
  chiamata<{ accessi: VoceAccesso[] }>(t, `${base(id)}/accessi`);
