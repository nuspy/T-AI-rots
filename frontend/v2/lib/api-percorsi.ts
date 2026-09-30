/* I percorsi dell'API delle letture pubbliche della v2, in un posto solo e senza React: li usano il componente nel
 * browser (`usePubblico`, `useCarica` con `iniziale`) e la pagina sul server (`precarica`). Lo stesso percorso vuol
 * dire gli stessi dati: il componente li trova già pronti e l'HTML esce col contenuto. */

/** La lingua dei contenuti (carte, stese, sezioni del blog): esistono in italiano e in inglese; le altre lingue
 *  leggono l'inglese, come nel sito. */
export const linguaContenuti = (lingua: string) => (lingua === "it" ? "it" : "en");

/** Articoli per pagina negli elenchi del blog. */
export const PER_PAGINA_BLOG = 12;

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
  /** Gli articoli che parlano di una carta o di una stesa. */
  articoliSu: (tipo: "carta" | "stesa", id: string) => `/blog/links/${tipo}/${encodeURIComponent(id)}`,
};
