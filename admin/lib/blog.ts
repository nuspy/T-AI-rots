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
  /** Per `carte`: `{arcano: "maggiore"}`, `{seme: "coppe"}` o `{rango: "asso"}`; per `stese`: `{categoria: "coppia"}`. */
  filtro: Record<string, string> | null;
  ordine: number;
  visibile: boolean;
  immagine_id: string | null;
  /** L'indirizzo dell'immagine grande, e quello della miniatura per gli elenchi (v9.4). */
  immagine: string | null;
  immagine_mini: string | null;
  /** Il testo alternativo dell'immagine (v9.4); vuoto: il sito usa il nome della sezione. */
  immagine_alt: string | null;
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
  immagine_alt?: string | null;
  seo_titolo?: string | null;
  seo_descrizione?: string | null;
}

/** Il soggetto di un articolo (v9.4): la carta o la stesa di cui parla. In uscita porta anche nome e indirizzo
 *  nella lingua dell'articolo. */
export type TipoSoggetto = "carta" | "stesa";

export interface Soggetto {
  tipo: TipoSoggetto;
  /** L'id del catalogo: `maj-10`, `coppe-01`, `croce-celtica`. */
  ref: string;
  nome: string;
  slug: string;
}

/** Il soggetto da salvare: `{tipo, ref}`; `null` = nessuno; non mandarlo = lo sceglie il server dal titolo. */
export interface SoggettoIn {
  tipo: TipoSoggetto;
  ref: string;
}

/** Una domanda frequente: si vede in pagina e diventa dati strutturati FAQ. */
export interface DomandaFrequente {
  domanda: string;
  risposta: string;
}

/* I tetti che il server applica ai campi SEO (`blog_seo.py`): qui per dirlo mentre si scrive. */
export const FAQ_MAX = 10;
export const FAQ_DOMANDA_MAX = 200;
export const FAQ_RISPOSTA_MAX = 1200;
export const PAROLE_CHIAVE_MAX = 10;

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
  /** La carta o la stesa di cui parla (v9.4), o `null`. */
  soggetto: Soggetto | null;
  immagine_id: string | null;
  immagine: string | null;
  immagine_alt: string | null;
  tags: string[];
  in_evidenza: boolean;
  commenti_aperti: boolean;
  seo_titolo: string | null;
  seo_descrizione: string | null;
  /** La parola chiave principale (quella per cui si vuole essere trovati) e le secondarie. */
  seo_parola_chiave: string | null;
  seo_parole_chiave: string[];
  /** Vero: l'articolo resta leggibile ma i motori di ricerca non lo indicizzano né lo mettono nella mappa. */
  noindex: boolean;
  /** Se il testo vive altrove, l'indirizzo `https` della versione originale. */
  canonical_url: string | null;
  faq: DomandaFrequente[];
  /** Vale `null` per un articolo scritto in console; altrimenti la chiave applicativa che l'ha pubblicato. */
  creato_da_chiave_id: number | null;
  tempo_lettura: number;
  autore: { id: number; nome: string } | null;
  creato: string | null;
  aggiornato: string | null;
  /** Solo nel dettaglio: l'elenco non porta il testo. */
  testo?: string;
  /** Se questo articolo è una traduzione generata (v5): l'originale da cui è nato. */
  tradotto_da_id: string | null;
  /** Le sue traduzioni già generate (v5), qualunque sia il loro stato. */
  traduzioni: { id: string; lang: string; slug: string; stato: StatoArticolo }[];
}

export interface CampiArticolo {
  titolo?: string;
  sottotitolo?: string | null;
  testo?: string;
  slug?: string | null;
  lang?: string;
  sezione_id?: number | null;
  /** Assente: lo sceglie il server (solo se l'articolo non ne ha uno); `null`: nessuno. */
  soggetto?: SoggettoIn | null;
  immagine_id?: string | null;
  immagine_alt?: string | null;
  tags?: string[];
  in_evidenza?: boolean;
  commenti_aperti?: boolean;
  seo_titolo?: string | null;
  seo_descrizione?: string | null;
  seo_parola_chiave?: string | null;
  seo_parole_chiave?: string[];
  noindex?: boolean;
  canonical_url?: string | null;
  faq?: DomandaFrequente[];
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

/** Genera la traduzione di un articolo in un'altra lingua (v5): sempre una nuova bozza, mai pubblicata
 *  da sola — per la revisione editoriale prima che vada online. */
export const traduciArticolo = (t: string, id: string, lang: string) =>
  chiamata<Articolo>(t, `/admin/blog/posts/${encodeURIComponent(id)}/traduci`, {
    method: "POST",
    body: JSON.stringify({ lang }),
  });

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
  /** Gli altri nomi (inglese, Thoth, le altre lingue): per trovarla cercando. */
  altri?: string[];
}

/* Carte e stese non richiedono il ruolo: sono le stesse risposte del sito. */
export async function carteEStese(t: string): Promise<{ carte: Riferimento[]; stese: Riferimento[] }> {
  const [carte, stese] = await Promise.all([
    chiamata<{ id: string; nome_it: string; nome_thoth?: string | null; nomi?: Record<string, string> }[]>(t, "/cards"),
    chiamata<{ id: string; nome: string; nome_en?: string | null; nomi?: Record<string, string> }[]>(t, "/spreads"),
  ]);
  const altri = (...nomi: (string | null | undefined)[]) => nomi.filter((n): n is string => Boolean(n));
  return {
    carte: carte.map((c) => ({
      id: c.id,
      nome: c.nome_it,
      altri: altri(c.nomi?.en, c.nome_thoth, ...Object.values(c.nomi ?? {})),
    })),
    stese: stese.map((s) => ({ id: s.id, nome: s.nome, altri: altri(s.nome_en, ...Object.values(s.nomi ?? {})) })),
  };
}

/* ---- le immagini del catalogo (v9.4): le illustrazioni delle stese e le immagini delle sezioni ---- */

export type TipoCatalogo = "stesa" | "sezione";

/** Un'immagine come la mostra il sito: grande, miniatura e testo alternativo. */
export interface ImmagineRicca {
  url: string;
  mini: string;
  alt: string | null;
}

export interface VoceCatalogo {
  tipo: TipoCatalogo;
  /** L'id della stesa (`croce-celtica`) o l'indirizzo della sezione (`major-arcana`). */
  riferimento: string;
  nome: string;
  immagine_id: string | null;
  immagine: ImmagineRicca | null;
  aggiornata: string | null;
}

export const catalogoImmagini = (t: string, tipo?: TipoCatalogo) =>
  chiamata<VoceCatalogo[]>(t, `/admin/blog/catalogo-immagini${interrogazione({ tipo })}`);

/** Assegna (o cambia) l'immagine, già caricata fra le immagini del blog, e il suo testo alternativo. */
export const impostaImmagineCatalogo = (
  t: string,
  tipo: TipoCatalogo,
  riferimento: string,
  corpo: { immagine_id: string; alt?: string | null },
) =>
  chiamata<VoceCatalogo>(t, `/admin/blog/catalogo-immagini/${tipo}/${encodeURIComponent(riferimento)}`, {
    method: "PUT",
    body: JSON.stringify(corpo),
  });

/** Toglie l'immagine (che resta nella libreria). */
export const togliImmagineCatalogo = (t: string, tipo: TipoCatalogo, riferimento: string) =>
  chiamata<void>(t, `/admin/blog/catalogo-immagini/${tipo}/${encodeURIComponent(riferimento)}`, {
    method: "DELETE",
  });

/* ---- il controllo SEO ---- */

export type EsitoControllo = "ok" | "avviso" | "errore";

export interface ControlloSeo {
  id: string;
  esito: EsitoControllo;
  peso: number;
  messaggio: string;
  messaggio_it: string;
}

export interface RapportoSeo {
  /** Da 0 a 100: la somma pesata dei controlli. Non promette un posizionamento, dice dove migliorare. */
  punteggio: number;
  giudizio: "ottimo" | "buono" | "da_migliorare";
  controlli: ControlloSeo[];
  statistiche: {
    parole: number;
    titoli_h2: number;
    collegamenti_interni: number;
    collegamenti_esterni: number;
    faq: number;
    tempo_lettura: number;
  };
}

/** L'articolo com'è adesso, anche non salvato: il rapporto si calcola sul server, con le stesse regole della REST. */
export interface DatiControlloSeo {
  titolo: string;
  sottotitolo: string | null;
  testo: string;
  slug: string;
  seo_titolo: string | null;
  seo_descrizione: string | null;
  seo_parola_chiave: string | null;
  immagine_presente: boolean;
  immagine_alt: string | null;
  tags: string[];
  faq: DomandaFrequente[];
}

export const controlloSeo = (t: string, corpo: DatiControlloSeo) =>
  chiamata<RapportoSeo>(t, "/admin/blog/seo-check", { method: "POST", body: JSON.stringify(corpo) });

/* ---- le chiavi applicative (per gli agenti che pubblicano via REST) ---- */

export type PermessoChiave = "blog:write" | "blog:publish" | "blog:media";

export interface ChiaveApi {
  id: number;
  nome: string;
  /** I primi caratteri: per riconoscerla nell'elenco. La chiave intera non si rivede. */
  prefisso: string;
  scopes: PermessoChiave[];
  limite_minuto: number;
  limite_giorno: number;
  attiva: boolean;
  ultimo_uso: string | null;
  usi: number;
  creata: string | null;
  revocata: string | null;
}

export interface CampiChiave {
  nome: string;
  scopes: PermessoChiave[];
  limite_minuto: number;
  limite_giorno: number;
}

export const chiaviApi = (t: string) => chiamata<ChiaveApi[]>(t, "/admin/blog/api-keys");

/** La risposta porta la chiave completa, **una volta sola**. */
export const creaChiaveApi = (t: string, corpo: CampiChiave) =>
  chiamata<ChiaveApi & { chiave: string }>(t, "/admin/blog/api-keys", { method: "POST", body: JSON.stringify(corpo) });

export const revocaChiaveApi = (t: string, id: number) =>
  chiamata<void>(t, `/admin/blog/api-keys/${id}`, { method: "DELETE" });
