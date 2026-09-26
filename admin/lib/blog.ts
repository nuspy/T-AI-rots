/* Il blog, visto dalla console: sezioni, articoli, immagini, etichette, versioni.
 *
 * Le rotte sono sotto `/admin/blog` e valgono le stesse regole del resto del client: un token vuoto
 * vuol dire «autenticazione spenta». Le immagini si caricano come corpo grezzo (`Content-Type:
 * image/…`), non come JSON: il server le orienta, le porta a 1600 px e le riscrive in WebP. */

import { API, chiamata, interrogazione } from "./api";

export type TipoSezione = "articoli" | "carte" | "stese" | "contenitore";
export type StatoArticolo = "bozza" | "pubblicato" | "archiviato";

export interface Sezione {
  id: number;
  parent_id: number | null;
  slug: string;
  nome: string;
  descrizione: string | null;
  tipo: TipoSezione;
  /** Per `carte`: `{arcano: "maggiore"}` o `{seme: "coppe"}`; per `stese`: `{categoria: "coppia"}`. */
  filtro: Record<string, string> | null;
  ordine: number;
  visibile: boolean;
  immagine_id: string | null;
  immagine: string | null;
  seo_titolo: string | null;
  seo_descrizione: string | null;
  n_articoli: number;
}

export interface CampiSezione {
  nome: string;
  slug?: string | null;
  descrizione?: string | null;
  tipo?: TipoSezione;
  filtro?: Record<string, string> | null;
  parent_id?: number | null;
  ordine?: number;
  visibile?: boolean;
  immagine_id?: string | null;
  seo_titolo?: string | null;
  seo_descrizione?: string | null;
}

export interface Articolo {
  id: string;
  slug: string;
  titolo: string;
  sottotitolo: string | null;
  lang: string;
  stato: StatoArticolo;
  pubblicato_il: string | null;
  /** `pubblicato` con la data nel futuro: il pubblico non lo vede ancora. */
  programmato: boolean;
  sezione_id: number | null;
  immagine_id: string | null;
  immagine: string | null;
  immagine_alt: string | null;
  tags: string[];
  in_evidenza: boolean;
  commenti_aperti: boolean;
  seo_titolo: string | null;
  seo_descrizione: string | null;
  tempo_lettura: number;
  autore: { id: number; nome: string } | null;
  creato: string | null;
  aggiornato: string | null;
  /** Solo nel dettaglio: l'elenco non porta il testo. */
  testo?: string;
}

export interface CampiArticolo {
  titolo?: string;
  sottotitolo?: string | null;
  testo?: string;
  slug?: string | null;
  lang?: string;
  sezione_id?: number | null;
  immagine_id?: string | null;
  immagine_alt?: string | null;
  tags?: string[];
  in_evidenza?: boolean;
  commenti_aperti?: boolean;
  seo_titolo?: string | null;
  seo_descrizione?: string | null;
  stato?: StatoArticolo;
  pubblicato_il?: string | null;
}

export interface Revisione {
  id: number;
  titolo: string;
  sottotitolo: string | null;
  testo: string;
  quando: string;
}

export interface Immagine {
  id: string;
  url: string;
  larghezza: number;
  altezza: number;
  creata: string;
}

export interface Etichetta {
  id: number;
  slug: string;
  nome: string;
  n: number;
}

/** L'indirizzo con cui il browser scarica un'immagine (l'API risponde con il percorso relativo). */
export const urlMedia = (relativo: string | null | undefined): string | null =>
  relativo ? `${API}${relativo}` : null;

/** Il Markdown che inserisce un'immagine: percorso relativo, così il testo non dipende dall'host. */
export const markdownImmagine = (i: Pick<Immagine, "url">, alt = ""): string =>
  `![${alt.replace(/[[\]]/g, "")}](${i.url})`;

/* ---- sezioni ---- */

export const sezioni = (t: string) => chiamata<Sezione[]>(t, "/admin/blog/sections");

export const creaSezione = (t: string, corpo: CampiSezione) =>
  chiamata<Sezione>(t, "/admin/blog/sections", { method: "POST", body: JSON.stringify(corpo) });

export const modificaSezione = (t: string, id: number, corpo: Partial<CampiSezione>) =>
  chiamata<Sezione>(t, `/admin/blog/sections/${id}`, { method: "PATCH", body: JSON.stringify(corpo) });

export const riordinaSezioni = (
  t: string,
  voci: { id: number; parent_id: number | null; ordine: number }[],
) =>
  chiamata<{ aggiornate: number }>(t, "/admin/blog/sections/riordina", {
    method: "POST",
    body: JSON.stringify(voci),
  });

export const eliminaSezione = (t: string, id: number, forza: boolean) =>
  chiamata<void>(t, `/admin/blog/sections/${id}${interrogazione({ forza: forza ? "true" : undefined })}`, {
    method: "DELETE",
  });

/* ---- articoli ---- */

export const articoli = (
  t: string,
  filtri: { stato?: StatoArticolo; sezione_id?: number; q?: string; pagina?: number; per_pagina?: number } = {},
) =>
  chiamata<{ totale: number; pagina: number; per_pagina: number; articoli: Articolo[] }>(
    t,
    `/admin/blog/posts${interrogazione(filtri)}`,
  );

export const articolo = (t: string, id: string) => chiamata<Articolo>(t, `/admin/blog/posts/${encodeURIComponent(id)}`);

export const creaArticolo = (t: string, corpo: CampiArticolo) =>
  chiamata<Articolo>(t, "/admin/blog/posts", { method: "POST", body: JSON.stringify(corpo) });

export const modificaArticolo = (t: string, id: string, corpo: CampiArticolo) =>
  chiamata<Articolo>(t, `/admin/blog/posts/${encodeURIComponent(id)}`, {
    method: "PATCH",
    body: JSON.stringify(corpo),
  });

export const cambiaStato = (t: string, id: string, azione: "pubblica" | "archivia" | "bozza") =>
  chiamata<Articolo>(t, `/admin/blog/posts/${encodeURIComponent(id)}/${azione}`, { method: "POST" });

export const eliminaArticolo = (t: string, id: string) =>
  chiamata<void>(t, `/admin/blog/posts/${encodeURIComponent(id)}`, { method: "DELETE" });

export const revisioni = (t: string, id: string) =>
  chiamata<Revisione[]>(t, `/admin/blog/posts/${encodeURIComponent(id)}/revisions`);

export const ripristina = (t: string, id: string, revisione: number) =>
  chiamata<Articolo>(t, `/admin/blog/posts/${encodeURIComponent(id)}/revisions/${revisione}/restore`, {
    method: "POST",
  });

/* ---- immagini ---- */

export const immagini = (t: string) => chiamata<Immagine[]>(t, "/admin/blog/media?limite=200");

/* Il file è il corpo della richiesta: `Content-Type` è il suo tipo, non JSON. */
export const caricaImmagine = (t: string, file: File) =>
  chiamata<Immagine & { byte: number }>(t, "/admin/blog/media", {
    method: "POST",
    body: file,
    headers: { "Content-Type": file.type || "application/octet-stream" },
  });

export const eliminaImmagine = (t: string, id: string) =>
  chiamata<void>(t, `/admin/blog/media/${encodeURIComponent(id)}`, { method: "DELETE" });

/* ---- etichette ---- */

export const etichette = (t: string) => chiamata<Etichetta[]>(t, "/admin/blog/tags");

export const rinominaEtichetta = (t: string, id: number, nome: string) =>
  chiamata<{ id: number; slug: string; nome: string }>(t, `/admin/blog/tags/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ nome }),
  });

export const eliminaEtichetta = (t: string, id: number) =>
  chiamata<void>(t, `/admin/blog/tags/${id}`, { method: "DELETE" });

/* ---- il catalogo pubblico, per inserire le scorciatoie ---- */

export interface Riferimento {
  id: string;
  nome: string;
}

/* Carte e stese non richiedono il ruolo: sono le stesse risposte del sito. */
export async function carteEStese(t: string): Promise<{ carte: Riferimento[]; stese: Riferimento[] }> {
  const [carte, stese] = await Promise.all([
    chiamata<{ id: string; nome_it: string }[]>(t, "/cards"),
    chiamata<{ id: string; nome: string }[]>(t, "/spreads"),
  ]);
  return {
    carte: carte.map((c) => ({ id: c.id, nome: c.nome_it })),
    stese: stese.map((s) => ({ id: s.id, nome: s.nome })),
  };
}
