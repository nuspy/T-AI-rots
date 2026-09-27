/* I mazzi in vendita (v5, Fase B): metadati commerciali soltanto — l'artwork è file statici nel
 * frontend, non passa da qui. Un mazzo posseduto o già usato non si elimina: si disattiva. */

import { chiamata } from "./api";

export interface Mazzo {
  id: number;
  slug: string;
  nome: string;
  descrizione: string | null;
  predefinito: boolean;
  attivo: boolean;
  attivo_ora: boolean;
  attivazione_da: string | null;
  attivazione_fino: string | null;
  prezzo_digitale: number | null;
  prezzo_stampa: number | null;
  prezzo_fisico: number | null;
  richiede_spedizione: boolean;
  valuta: string;
  rank: number;
  /** Presenti solo quando arriva da un elenco/dettaglio che unisce anche il prezzo (sempre, in console). */
  prezzo_digitale_scontato: number | null;
  offerta_attiva: boolean;
  offerta_valido_fino: string | null;
}

export interface NuovoMazzo {
  slug: string;
  nome: string;
  descrizione?: string;
  predefinito?: boolean;
  attivo?: boolean;
  attivazione_da?: string | null;
  attivazione_fino?: string | null;
  prezzo_digitale?: number | null;
  prezzo_stampa?: number | null;
  prezzo_fisico?: number | null;
  richiede_spedizione?: boolean;
  valuta?: string;
  rank?: number;
}

export type ModificaMazzo = Partial<Omit<NuovoMazzo, "slug" | "predefinito" | "valuta">>;

export const mazzi = (t: string) => chiamata<Mazzo[]>(t, "/admin/decks");

export const creaMazzo = (t: string, corpo: NuovoMazzo) =>
  chiamata<Mazzo>(t, "/admin/decks", { method: "POST", body: JSON.stringify(corpo) });

export const modificaMazzo = (t: string, slug: string, corpo: ModificaMazzo) =>
  chiamata<Mazzo>(t, `/admin/decks/${encodeURIComponent(slug)}`, { method: "PUT", body: JSON.stringify(corpo) });

export const eliminaMazzo = (t: string, slug: string) =>
  chiamata<void>(t, `/admin/decks/${encodeURIComponent(slug)}`, { method: "DELETE" });

export type TipoOfferta = "percentuale" | "importo";

export interface OffertaIn {
  tipo: TipoOfferta;
  valore: number;
  valido_dal?: string | null;
  valido_fino?: string | null;
}

export const impostaOfferta = (t: string, slug: string, corpo: OffertaIn) =>
  chiamata<Mazzo>(t, `/admin/decks/${encodeURIComponent(slug)}/offerta`, { method: "PUT", body: JSON.stringify(corpo) });

export const rimuoviOfferta = (t: string, slug: string) =>
  chiamata<void>(t, `/admin/decks/${encodeURIComponent(slug)}/offerta`, { method: "DELETE" });
