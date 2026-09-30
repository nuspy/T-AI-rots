/* I mazzi in vendita (v5, Fase B): metadati commerciali soltanto — l'artwork è file statici nel
 * frontend, non passa da qui. Un mazzo posseduto o già usato non si elimina: si disattiva. */

import { API, ErroreApi, chiamata } from "./api";

export interface Mazzo {
  id: number;
  slug: string;
  nome: string;
  descrizione: string | null;
  nomi?: Record<string, string>;
  descrizioni?: Record<string, string>;
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
  prezzo_stampa_scontato?: number | null;
  prezzo_fisico_scontato?: number | null;
  offerta_formati?: FormatoOfferta[];
  offerta_attiva: boolean;
  offerta_valido_dal?: string | null;
  offerta_valido_fino: string | null;
}

/** I prodotti a cui un'offerta si applica (v8.5). */
export type FormatoOfferta = "digitale" | "pdf" | "fisico";

export interface NuovoMazzo {
  slug: string;
  nome: string;
  descrizione?: string | null;
  nomi?: Record<string, string>;
  descrizioni?: Record<string, string>;
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
  formati?: FormatoOfferta[];
}

export const impostaOfferta = (t: string, slug: string, corpo: OffertaIn) =>
  chiamata<Mazzo>(t, `/admin/decks/${encodeURIComponent(slug)}/offerta`, { method: "PUT", body: JSON.stringify(corpo) });

export const rimuoviOfferta = (t: string, slug: string) =>
  chiamata<void>(t, `/admin/decks/${encodeURIComponent(slug)}/offerta`, { method: "DELETE" });

/* ---- upload dell'artwork (v7, Fase I) ----
 * Automatizza solo la ricezione e la validazione dei file (nomi corretti, tutte le carte
 * presenti): l'artwork finale resta statico nel frontend, un mazzo nuovo richiede comunque un
 * rilascio — l'amministratore scarica lo ZIP validato e lo estrae a mano nel repository. */

export interface ArtworkUpload {
  id: string;
  file_count: number;
  creato_il: string;
}

export const elencoArtwork = (t: string, slug: string) =>
  chiamata<ArtworkUpload[]>(t, `/admin/decks/${encodeURIComponent(slug)}/artwork`);

/** Il body è lo ZIP grezzo, non JSON: si sovrascrive il `Content-Type` di default. */
export const caricaArtwork = (t: string, slug: string, file: File) =>
  chiamata<ArtworkUpload>(t, `/admin/decks/${encodeURIComponent(slug)}/artwork`, {
    method: "POST",
    body: file,
    headers: { "Content-Type": "application/zip" },
  });

/** Scarica lo ZIP con la sessione autenticata del browser, come i CSV di `scaricaReport`. */
export async function scaricaArtwork(t: string, slug: string, uploadId: string): Promise<void> {
  const risposta = await fetch(
    `${API}/admin/decks/${encodeURIComponent(slug)}/artwork/${uploadId}`,
    { headers: t ? { Authorization: `Bearer ${t}` } : {} },
  );
  if (!risposta.ok) throw new ErroreApi("Impossibile scaricare l'artwork", risposta.status);
  const indirizzo = URL.createObjectURL(await risposta.blob());
  try {
    const a = document.createElement("a");
    a.href = indirizzo;
    a.download = `${slug}-artwork.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } finally {
    setTimeout(() => URL.revokeObjectURL(indirizzo), 0);
  }
}

export const eliminaArtwork = (t: string, slug: string, uploadId: string) =>
  chiamata<void>(t, `/admin/decks/${encodeURIComponent(slug)}/artwork/${uploadId}`, { method: "DELETE" });
