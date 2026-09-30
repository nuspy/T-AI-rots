/* Gli indirizzi della v2, in un posto solo. Tutti sotto `/v2`: nessun collegamento della v2 porta al sito (v1)
 * quando la v2 ha la pagina corrispondente (specifica v2, §2). In italiano gli stessi indirizzi portano il
 * prefisso `/it` (`/it/v2/read`): lo aggiunge `LinkV2` quando la pagina è stata aperta così. */

export const V2 = "/v2";

export const R = {
  home: V2,
  leggi: `${V2}/read`,
  fisica: `${V2}/physical-reading`,
  storia: `${V2}/my-story`,
  lettura: (id: string) => `${V2}/my-story/${encodeURIComponent(id)}`,
  condivisa: (token: string) => `${V2}/shared/${encodeURIComponent(token)}`,
  giorno: `${V2}/daily-card`,
  carte: `${V2}/cards`,
  carta: (id: string) => `${V2}/cards/${encodeURIComponent(id)}`,
  stese: `${V2}/spreads`,
  stesa: (id: string) => `${V2}/spreads/${encodeURIComponent(id)}`,
  mazzi: `${V2}/decks`,
  mazzo: (slug: string) => `${V2}/decks/${encodeURIComponent(slug)}`,
  voto: `${V2}/vote`,
  negozio: `${V2}/shop`,
  carrello: `${V2}/cart`,
  prezzi: `${V2}/pricing`,
  esplora: `${V2}/explore`,
  blog: `${V2}/blog`,
  articolo: (slug: string) => `${V2}/blog/${encodeURIComponent(slug)}`,
  blogSezione: (slug: string) => `${V2}/blog/section/${encodeURIComponent(slug)}`,
  blogTag: (slug: string) => `${V2}/blog/tag/${encodeURIComponent(slug)}`,
  profilo: `${V2}/profile`,
  privacy: `${V2}/privacy`,
} as const;

/** Un indirizzo della v2 con il prefisso italiano, se serve. Gli indirizzi esterni o fuori dalla v2 non
 *  cambiano. */
export function indirizzoV2(interno: string, prefissoIt: boolean): string {
  if (!prefissoIt || !(interno === V2 || interno.startsWith(`${V2}/`) || interno.startsWith(`${V2}?`))) return interno;
  return `/it${interno}`;
}

/* Le sezioni del sito (in italiano e in inglese) → le pagine corrispondenti della v2. */
const DAL_SITO: [RegExp, string][] = [
  [/^\/(carte|cards)(\/|$)/, `${V2}/cards$2`],
  [/^\/(stese|spreads)(\/|$)/, `${V2}/spreads$2`],
  [/^\/blog\/sezione\//, `${V2}/blog/section/`],
  [/^\/blog\/tag\//, `${V2}/blog/tag/`],
  [/^\/blog(\/|$)/, `${V2}/blog$1`],
  [/^\/leggi(\/|$)/, `${V2}/read$1`],
  [/^\/interpreta(\/|$)/, `${V2}/physical-reading$1`],
  [/^\/(carta-del-giorno|card-of-the-day)(\/|$)/, `${V2}/daily-card$2`],
  [/^\/(piano|pricing)(\/|$)/, `${V2}/pricing$2`],
  [/^\/(mazzo|deck)(\/|$)/, `${V2}/shop$2`],
  [/^\/vota-mazzo(\/|$)/, `${V2}/vote$1`],
  [/^\/letture(\/|$)/, `${V2}/my-story$1`],
  [/^\/profilo(\/|$)/, `${V2}/profile$1`],
  [/^\/privacy(\/|$)/, `${V2}/privacy$1`],
  [/^\/s\//, `${V2}/shared/`],
];

/** Un indirizzo interno del sito (scritto in un articolo del blog, per esempio) → quello della v2, perché nessun
 *  collegamento della v2 porti al sito quando la v2 ha la pagina (specifica v2, §2). Esterni e ancore non cambiano;
 *  un indirizzo del sito senza corrispondente resta com'è. */
export function inV2(href: string): string {
  if (!href.startsWith("/") || href.startsWith("//") || href === V2 || href.startsWith(`${V2}/`)) return href;
  const p = href === "/it" ? "/" : href.startsWith("/it/") ? href.slice(3) : href;
  if (p === "/" || p.startsWith("/?")) return `${V2}${p.slice(1)}`;
  for (const [da, a] of DAL_SITO) if (da.test(p)) return p.replace(da, a);
  return href;
}

/** Il percorso senza il prefisso `/it`: per sapere in che sezione si è. */
export const senzaPrefisso = (percorso: string) =>
  percorso === "/it" ? "/" : percorso.startsWith("/it/") ? percorso.slice(3) : percorso;
