/* Il blog: i tipi di ciò che risponde l'API e qualche aiuto per mostrarlo.
 *
 * Le pagine del blog escono dal server (`lib/server-api.ts`); il browser usa le stesse forme per
 * i commenti e le azioni di chi è registrato. */

import { API } from "./api";

export interface ImmagineBreve {
  url: string;
  alt: string;
}

export interface ImmagineArticolo extends ImmagineBreve {
  larghezza: number | null;
  altezza: number | null;
}

export interface AutoreBlog {
  id: number | null;
  nome: string;
  avatar: string | null;
}

export interface EtichettaBlog {
  slug: string;
  nome: string;
}

export interface ArticoloBreve {
  slug: string;
  titolo: string;
  sottotitolo: string | null;
  estratto: string;
  immagine: ImmagineBreve | null;
  sezione: { slug: string; nome: string } | null;
  autore: AutoreBlog;
  pubblicato_il: string | null;
  aggiornato_il: string | null;
  tempo_lettura: number;
  tags: EtichettaBlog[];
  lang: string;
  in_evidenza: boolean;
}

export interface ArticoloBlog extends Omit<ArticoloBreve, "immagine"> {
  testo: string;
  immagine: ImmagineArticolo | null;
  seo_titolo: string | null;
  seo_descrizione: string;
  /* I campi SEO scritti da chi pubblica: la parola chiave principale, le secondarie, `noindex`, l'indirizzo canonico
   * (se il testo vive altrove) e le domande frequenti (diventano dati strutturati FAQ). */
  seo_parola_chiave: string | null;
  parole_chiave: string[];
  noindex: boolean;
  canonical_url: string | null;
  faq: { domanda: string; risposta: string }[];
  commenti_aperti: boolean;
  briciole: { slug: string; nome: string }[];
  /* Carte e stese citate: l'id canonico, il nome e lo slug nella lingua dell'articolo, gli slug in ogni lingua. */
  collegamenti: {
    carte: { id: string; nome_it: string; nome: string; slug: string; slugs: Record<string, string> }[];
    stese: { id: string; nome: string; slug: string; slugs: Record<string, string> }[];
    articoli: ArticoloBreve[];
  };
  correlati: ArticoloBreve[];
  precedente: ArticoloBreve | null;
  successivo: ArticoloBreve | null;
}

export type TipoSezione = "articoli" | "carte" | "stese" | "contenitore";

export interface NodoSezione {
  id: number;
  slug: string;
  nome: string;
  descrizione: string | null;
  tipo: TipoSezione;
  filtro: Record<string, string> | null;
  immagine: string | null;
  n_articoli: number;
  /* Per le sezioni «carte» e «stese»: quante ce ne sono nel catalogo. */
  n_elementi: number | null;
  figli: NodoSezione[];
}

export interface DettaglioSezione extends NodoSezione {
  seo_titolo: string | null;
  seo_descrizione: string | null;
  briciole: { slug: string; nome: string }[];
  /* Carte o stese del catalogo, per le sezioni di quei tipi. */
  elementi: Record<string, unknown>[];
}

export interface ElencoArticoli {
  totale: number;
  pagina: number;
  per_pagina: number;
  pagine: number;
  articoli: ArticoloBreve[];
}

export interface EtichettaConConteggio extends EtichettaBlog {
  n: number;
}

/** L'indirizzo pubblico di un'immagine del blog (l'API risponde con il percorso relativo). */
export const urlMedia = (relativo: string | null | undefined): string | null =>
  relativo ? `${API}${relativo}` : null;

/** Una data in forma leggibile, sempre in UTC: server e browser devono scrivere lo stesso testo,
 *  o l'idratazione non coincide (vedi «preventing flash before hydration» nella guida di Next). */
export function dataLeggibile(iso: string | null | undefined, locale: string): string {
  if (!iso) return "";
  try {
    return new Intl.DateTimeFormat(locale, { dateStyle: "long", timeZone: "UTC" }).format(new Date(iso));
  } catch {
    return iso.slice(0, 10);
  }
}
