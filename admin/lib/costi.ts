/* I costi delle inferenze (pagina «Costi»): i consumi registrati per ogni chiamata ai modelli (`llm_consumi`) e i
 * listini con cui tradurli in dollari. I listini si scrivono da qui. */

import { chiamata } from "./api";

export interface Listino {
  id: number;
  nome: string;
  /** Dollari per milione di token. */
  prezzo_ingresso: number;
  prezzo_cache: number;
  prezzo_uscita: number;
  /** Fra 0 e 1: la quota dell'ingresso cacheabile (il prefisso stabile) che si stima trovata in cache. */
  cache_hit: number;
  /** Il fornitore in uso: per lui vale la cache che ha riportato davvero. */
  attuale: boolean;
  nota: string;
}

export type NuovoListino = Omit<Listino, "id">;

export interface Somme {
  chiamate: number;
  errori: number;
  /** Chiamate senza `usage` dal fornitore: i token si stimano dai caratteri. */
  stimate: number;
  ingresso: number;
  cache: number;
  uscita: number;
  ragionamento: number;
  cacheabile: number;
  durata_media_ms: number;
}

export interface RigaCompito extends Somme { compito: string; fase: string; costi: Record<string, number> }
export interface RigaGiorno extends Somme { giorno: string; compito: string; costi: Record<string, number> }
export interface RigaFuori extends Somme { riferimento: string; compito: string; costi: Record<string, number> }
export interface RigaLetture extends Somme {
  stato: "completata" | "abbandonata" | "annullata" | "cancellata";
  letture: number;
  costi_per_lettura: Record<string, number>;
  per_lettura: { chiamate: number; ingresso: number; uscita: number; ragionamento: number };
}

export interface Costi {
  giorni: number;
  dal: string;
  caratteri_per_token: number;
  listini: Listino[];
  totali: Somme & { costi: Record<string, number> };
  per_compito: RigaCompito[];
  per_giorno: RigaGiorno[];
  letture: RigaLetture[];
  fuori_lettura: RigaFuori[];
}

export const costi = (t: string, giorni: number) => chiamata<Costi>(t, `/admin/costi?giorni=${giorni}`);
export const creaListino = (t: string, v: NuovoListino) =>
  chiamata<Listino>(t, "/admin/costi/listini", { method: "POST", body: JSON.stringify(v) });
export const modificaListino = (t: string, id: number, v: NuovoListino) =>
  chiamata<Listino>(t, `/admin/costi/listini/${id}`, { method: "PUT", body: JSON.stringify(v) });
export const eliminaListino = (t: string, id: number) =>
  chiamata<void>(t, `/admin/costi/listini/${id}`, { method: "DELETE" });

/** I nomi dei compiti come li legge chi non conosce il codice. */
export const NOMI_FASE: Record<string, string> = {
  intervista: "Intervista: la domanda",
  "intervista.riassunto": "Intervista: il riassunto",
  validazione: "Controllo delle domande",
  interpretazione: "Interpretazione delle carte (una per carta, o ripiego)",
  interpretazione_unica: "Interpretazione delle carte (tutte insieme)",
  sintesi: "Responso finale",
  "sintesi.revisione": "Responso riscritto dopo il giudizio",
  giudizio: "Giudice del responso",
  teaser: "Anteprima per chi non è registrato",
  chat_proattiva: "Oracolo (chat)",
  memoria_estrazione: "Estrazione delle memorie",
  embedding: "Vettori per la memoria",
  traduzione_articolo: "Traduzione del blog",
  analisi_dati: "Analisi dei dati",
};

export function nomeFase(compito: string, fase: string): string {
  return NOMI_FASE[fase] ?? NOMI_FASE[compito] ?? (fase || compito || "senza compito");
}
