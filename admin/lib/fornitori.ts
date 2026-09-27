/* I fornitori LLM: indirizzo, modello e chiave, configurati da qui — non nell'ambiente del servizio.
 *
 * La chiave non torna mai in chiaro: `has_key` dice solo se c'è. Un fornitore nuovo o modificato è subito
 * assegnabile in «Modelli» (il backend rilegge l'elenco appena questa pagina scrive). */

import { chiamata } from "./api";

export interface TipoFornitore {
  tipo: string;
  label: string;
  provider: "openai-compatible" | "anthropic";
  auth: "api_key" | "none";
  base_url: string;
  nota: string;
}

export interface Fornitore {
  id: number;
  nome: string;
  tipo: string;
  provider: "openai-compatible" | "anthropic";
  base_url: string;
  model: string;
  embed_model: string;
  has_key: boolean;
  motore: string;
  ragiona: boolean;
  parametri: Record<string, unknown>;
  senza_filtri: boolean;
  descrizione: string;
  attivo: boolean;
  aggiornato: string | null;
}

export interface NuovoFornitore {
  nome: string;
  tipo: string;
  base_url?: string;
  model?: string;
  embed_model?: string;
  api_key?: string;
  motore?: string;
  ragiona?: boolean;
  parametri?: Record<string, unknown>;
  senza_filtri?: boolean;
  descrizione?: string;
  attivo?: boolean;
}

/** Ogni campo assente non si tocca. `api_key`: assente = non si tocca, `""` = la svuota (server senza chiave). */
export type ModificaFornitore = Partial<Omit<NuovoFornitore, "nome" | "tipo">>;

export interface EsitoProva {
  ok: boolean;
  modelli: string[];
  errore: string | null;
}

export const fornitori = (t: string) =>
  chiamata<{ fornitori: Fornitore[]; catalogo: TipoFornitore[] }>(t, "/admin/llm/providers");

export const creaFornitore = (t: string, corpo: NuovoFornitore) =>
  chiamata<Fornitore>(t, "/admin/llm/providers", { method: "POST", body: JSON.stringify(corpo) });

export const modificaFornitore = (t: string, id: number, corpo: ModificaFornitore) =>
  chiamata<Fornitore>(t, `/admin/llm/providers/${id}`, { method: "PUT", body: JSON.stringify(corpo) });

export const eliminaFornitore = (t: string, id: number) =>
  chiamata<void>(t, `/admin/llm/providers/${id}`, { method: "DELETE" });

export const provaFornitore = (t: string, id: number) =>
  chiamata<EsitoProva>(t, `/admin/llm/providers/${id}/prova`, { method: "POST" });
