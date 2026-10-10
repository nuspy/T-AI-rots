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
  /** L'impronta delle immagini caricate dalla console (vedi «le immagini del mazzo nel sito» in fondo); `null`: il
   * mazzo usa i file del sito. */
  immagini_versione?: string | null;
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

/* `?elenco=1` (10/10/2026): fino al 9/10 il gateway rispondeva a `/api/admin/decks` con un 301 permanente verso un
 * indirizzo `http://`, che i browser tengono in cache e la pagina https blocca («Il servizio non risponde.») anche dopo
 * la correzione del gateway. Un indirizzo appena diverso non trova quel redirect in cache; l'API ignora il parametro. */
export const mazzi = (t: string) => chiamata<Mazzo[]>(t, "/admin/decks?elenco=1");

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

/* ---- le immagini del mazzo nel sito (ZIP o cartella, subito online) ----
 * Diverso dall'archivio qui sopra: le immagini si convertono in WebP alla misura web, si conservano nel database e
 * il sito le mostra subito (`/cards/<slug>/<id>.webp` → API), senza rilascio. Stesse regole di
 * `tools/installa_mazzo.py`: il nome del file senza estensione è l'id della carta (`maj-00`, `bastoni-06`), più
 * `dorso`. Le regole per riconoscere i file sono le stesse del server (`tarot/immagini_mazzo.py`): la console le
 * applica a una cartella prima di caricarla, così si sa subito cosa manca. */

export interface RiepilogoImmagini {
  installate: number;
  avanzano: string[];
  ignorati: number;
}

export interface StatoImmagini {
  slug: string;
  /** L'impronta della serie pubblicata; `null`: il mazzo usa i file del sito (o non ha immagini). */
  versione: string | null;
  attese: number;
  pubblicate: number;
  bozza: number;
  mancanti_bozza: string[];
  ids_attesi: string[];
  riepilogo?: RiepilogoImmagini;
}

/** Un rifiuto con gli elenchi del server: cosa manca, cosa avanza, i doppioni, i percorsi non ammessi. */
export class ErroreImmagini extends ErroreApi {
  constructor(
    message: string,
    stato: number,
    readonly mancanti: string[] = [],
    readonly avanzano: string[] = [],
    readonly doppioni: string[] = [],
    readonly rifiutati: string[] = [],
  ) {
    super(message, stato, message);
  }
}

function erroreDa(stato: number, corpo: unknown): ErroreImmagini {
  const detail = (corpo as { detail?: unknown } | null)?.detail;
  const elenco = (v: unknown) => (Array.isArray(v) ? v.map(String) : []);
  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    const d = detail as Record<string, unknown>;
    return new ErroreImmagini(
      String(d.messaggio ?? "Caricamento non riuscito."), stato,
      elenco(d.mancanti), elenco(d.avanzano), elenco(d.doppioni), elenco(d.rifiutati),
    );
  }
  if (typeof detail === "string") return new ErroreImmagini(detail, stato);
  if (Array.isArray(detail) && detail.length) {
    return new ErroreImmagini(String((detail[0] as { msg?: string }).msg ?? "Richiesta non valida."), stato);
  }
  return new ErroreImmagini(
    stato === 413 ? "Il file è troppo grande per il server." : stato === 403 ? "Il tuo account non ha il ruolo di amministratore." : "Caricamento non riuscito.",
    stato,
  );
}

const percorsoImmagini = (slug: string) => `/admin/decks/${encodeURIComponent(slug)}/immagini`;

export const statoImmagini = (t: string, slug: string) => chiamata<StatoImmagini>(t, percorsoImmagini(slug));

/** Lo ZIP intero in una richiesta, con l'avanzamento dell'invio (0-1): `fetch` non lo dà, `XMLHttpRequest` sì. */
export function caricaZipImmagini(
  t: string, slug: string, file: File, onAvanzamento: (frazione: number) => void,
): Promise<StatoImmagini> {
  return new Promise((risolvi, rifiuta) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API}${percorsoImmagini(slug)}/zip`);
    if (t) xhr.setRequestHeader("Authorization", `Bearer ${t}`);
    xhr.setRequestHeader("Content-Type", "application/zip");
    xhr.upload.onprogress = (e) => { if (e.lengthComputable) onAvanzamento(e.loaded / e.total); };
    xhr.onload = () => {
      let corpo: unknown = null;
      try { corpo = JSON.parse(xhr.responseText); } catch { /* non JSON: basta lo stato */ }
      if (xhr.status >= 200 && xhr.status < 300) risolvi(corpo as StatoImmagini);
      else rifiuta(erroreDa(xhr.status, corpo));
    };
    xhr.onerror = () => rifiuta(new ErroreImmagini("Connessione interrotta durante il caricamento.", 0));
    xhr.send(file);
  });
}

/** Un file di una cartella, nella bozza: `percorso` è il suo nome con la cartella (`Lovers/Web/maj-00.webp`). */
export async function caricaFileImmagine(t: string, slug: string, percorso: string, file: File): Promise<{ carta: string; bozza: number }> {
  const risposta = await fetch(`${API}${percorsoImmagini(slug)}/file?percorso=${encodeURIComponent(percorso)}`, {
    method: "POST",
    body: file,
    headers: { ...(t ? { Authorization: `Bearer ${t}` } : {}), "Content-Type": file.type || "application/octet-stream" },
  });
  let corpo: unknown = null;
  try { corpo = await risposta.json(); } catch { /* non JSON */ }
  if (!risposta.ok) throw erroreDa(risposta.status, corpo);
  return corpo as { carta: string; bozza: number };
}

export const scartaBozzaImmagini = (t: string, slug: string) =>
  chiamata<void>(t, `${percorsoImmagini(slug)}/bozza`, { method: "DELETE" });

export async function pubblicaBozzaImmagini(t: string, slug: string): Promise<StatoImmagini> {
  const risposta = await fetch(`${API}${percorsoImmagini(slug)}/pubblica`, {
    method: "POST", headers: t ? { Authorization: `Bearer ${t}` } : {},
  });
  let corpo: unknown = null;
  try { corpo = await risposta.json(); } catch { /* non JSON */ }
  if (!risposta.ok) throw erroreDa(risposta.status, corpo);
  return corpo as StatoImmagini;
}

export const eliminaImmagini = (t: string, slug: string) =>
  chiamata<void>(t, percorsoImmagini(slug), { method: "DELETE" });

/** L'anteprima di una carta pubblicata, dall'API (con la versione: cambia a ogni nuova serie). */
export const urlCartaMazzo = (slug: string, id: string, versione: string) =>
  `${API}/decks/${encodeURIComponent(slug)}/cards/${id}.webp?v=${encodeURIComponent(versione)}`;

export interface FileRiconosciuti {
  /** id della carta → indice del file scelto. */
  scelti: Map<string, number>;
  avanzano: string[];
  ignorati: string[];
  doppioni: Map<string, string[]>;
}

const ESTENSIONI = [".webp", ".png", ".jpg", ".jpeg"];
const DI_SISTEMA = new Set([".ds_store", "thumbs.db", "desktop.ini"]);

/** Come `tarot/immagini_mazzo.py::riconosci`: il nome senza estensione è l'id; non contano le cartelle che
 * cominciano con `_` o `.` (`_staging/`), i file di sistema, ciò che non è un'immagine; fra due copie vince quella
 * in una cartella `Web`, altrimenti è un doppione. */
export function riconosciFile(percorsi: string[], validi: Set<string>): FileRiconosciuti {
  const esito: FileRiconosciuti = { scelti: new Map(), avanzano: [], ignorati: [], doppioni: new Map() };
  const candidati = new Map<string, number[]>();
  const parti = (p: string) => p.replace(/\\/g, "/").split("/").filter((x) => x && x !== ".");
  percorsi.forEach((percorso, i) => {
    const pezzi = parti(percorso);
    const nome = pezzi[pezzi.length - 1] ?? "";
    const punto = nome.lastIndexOf(".");
    const estensione = punto > 0 ? nome.slice(punto).toLowerCase() : "";
    if (!nome || nome.startsWith(".") || DI_SISTEMA.has(nome.toLowerCase())
      || pezzi.slice(0, -1).some((p) => p.startsWith(".") || p.startsWith("_")) || !ESTENSIONI.includes(estensione)) {
      esito.ignorati.push(percorso);
      return;
    }
    const id = nome.slice(0, punto).trim().toLowerCase();
    if (!validi.has(id)) { esito.avanzano.push(percorso); return; }
    candidati.set(id, [...(candidati.get(id) ?? []), i]);
  });
  for (const [id, indici] of candidati) {
    if (indici.length === 1) { esito.scelti.set(id, indici[0]); continue; }
    const inWeb = indici.filter((i) => {
      const pezzi = parti(percorsi[i]);
      return pezzi.length > 1 && pezzi[pezzi.length - 2].toLowerCase() === "web";
    });
    if (inWeb.length === 1) esito.scelti.set(id, inWeb[0]);
    else esito.doppioni.set(id, indici.map((i) => percorsi[i]).sort());
  }
  return esito;
}
