/* I percorsi dell'API delle letture pubbliche della v2, in un posto solo e senza React: li usano il componente nel
 * browser (`usePubblico`, `useCarica` con `iniziale`) e la pagina sul server (`precarica`). Lo stesso percorso vuol
 * dire gli stessi dati: il componente li trova già pronti e l'HTML esce col contenuto. */

/** La lingua dei contenuti (carte, stese, sezioni del blog): esistono in italiano e in inglese; le altre lingue
 *  leggono l'inglese, come nel sito. */
export const linguaContenuti = (lingua: string) => (lingua === "it" ? "it" : "en");

/** Articoli per pagina negli elenchi del Journal (indice, sezione, etichetta) e negli elenchi completi delle pagine di
 *  carte e stese (v9.4): 25, e chi legge può scegliere 10 o 50 (`?per=`). Le altre pagine del sito non cambiano. */
export const PER_PAGINA_BLOG = 25;
export const SCELTE_PER_PAGINA = [10, 25, 50] as const;

/** Il numero di articoli per pagina da `?per=`: solo una delle scelte, altrimenti quello predefinito. */
export function perPagina(valore: string | null | undefined): number {
  const n = Number(valore);
  return (SCELTE_PER_PAGINA as readonly number[]).includes(n) ? n : PER_PAGINA_BLOG;
}

/** Il numero di pagina da `?page=` (1–1000). */
export function numeroPagina(valore: string | null | undefined): number {
  return Math.max(1, Math.min(1000, parseInt(valore ?? "1", 10) || 1));
}

/** Le «recenti» che `/blog/nove` esclude dai 10 a caso delle pagine del Journal: la prima pagina dell'elenco, ma
 *  l'API ne accetta al più 12 (il resto della prima pagina lo toglie il browser, `SceltiACaso`). */
export const recentiDiario = (per: number) => Math.min(per, 12);

type Parametri = Record<string, string | number | undefined>;

export const P = {
  carte: (lingua: string) => `/cards?lang=${linguaContenuti(lingua)}`,
  carta: (id: string, lingua: string) => `/cards/${encodeURIComponent(id)}?lang=${linguaContenuti(lingua)}`,
  stese: (lingua: string) => `/spreads?lang=${linguaContenuti(lingua)}`,
  stesa: (id: string, lingua: string) => `/spreads/${encodeURIComponent(id)}?lang=${linguaContenuti(lingua)}`,
  oggi: (lingua: string) => `/daily-card/today?lang=${linguaContenuti(lingua)}`,
  mazzi: (lingua: string) => `/decks?lang=${lingua}`,
  piani: (lingua: string) => `/plans?lang=${lingua}`,
  impostazioni: () => "/impostazioni-pubbliche",
  /** I dati del titolare e i fornitori dell'AI attivi, per l'informativa (v9, Fase 2c: dalla console). */
  titolare: () => "/privacy/titolare",
  voto: () => "/voto/home",
  condivisa: (token: string) => `/shared/${encodeURIComponent(token)}`,
  /** Gli elenchi degli articoli non si filtrano per lingua (v8: gli articoli si vedono in qualunque lingua
   *  dell'interfaccia; ognuno vive all'indirizzo della sua). `_lingua` resta per chiarezza nelle chiamate. */
  articoli: (_lingua: string, parametri: Parametri = {}) => {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(parametri)) if (v !== undefined && v !== "") p.set(k, String(v));
    const q = p.toString();
    return q ? `/blog/posts?${q}` : "/blog/posts";
  },
  articolo: (slug: string) => `/blog/posts/${encodeURIComponent(slug)}`,
  sezioni: () => "/blog/sections",
  sezione: (slug: string, lingua: string) => `/blog/sections/${encodeURIComponent(slug)}?lang=${linguaContenuti(lingua)}`,
  etichette: () => "/blog/tags",
  /** I nove articoli di ogni pagina (v8.5): 3 recenti + 6 attinenti al contesto, scelti a caso per la giornata.
   *  `completa: false` (pagine di sezione e di etichetta del Diario): niente articoli presi da fuori del contesto,
   *  così la pagina mostra tanti articoli quanti ne conta l'albero delle sezioni. `lang` (v9.4) tiene solo gli
   *  articoli in quella lingua: le pagine di articolo, carta e stesa, dove le scelte vanno per pertinenza. */
  nove: (contesto: {
    carta?: string; stesa?: string; sezione?: string; articolo?: string; tag?: string; recenti?: number; scelti?: number;
    completa?: boolean; lang?: string;
  } = {}) => {
    const p = new URLSearchParams();
    for (const k of ["carta", "stesa", "sezione", "articolo", "tag", "recenti", "scelti", "completa", "lang"] as const) {
      if (contesto[k] !== undefined && contesto[k] !== "") p.set(k, String(contesto[k]));
    }
    const q = p.toString();
    return q ? `/blog/nove?${q}` : "/blog/nove";
  },
  /** L'elenco completo e paginato degli articoli su una carta o una stesa (v9.4, in fondo alla sua pagina): prima
   *  quelli che l'hanno come soggetto, poi quelli che la citano. */
  elencoSu: (tipo: "carta" | "stesa", id: string, pagina: number, per: number): string =>
    P.articoli("", { [tipo]: id, pagina, per_pagina: per }),
  /** Gli articoli che parlano di una carta o di una stesa. */
  articoliSu: (tipo: "carta" | "stesa", id: string) => `/blog/links/${tipo}/${encodeURIComponent(id)}`,
};
