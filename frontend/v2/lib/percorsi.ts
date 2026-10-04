/* Gli indirizzi della v2, in un posto solo. Dalla v8.5 la v2 è il sito: stanno alla radice, coi nomi delle cartelle
 * (`/cards`, `/daily-card`, `/blog/sezione/…`). Quello che si vede cambia con la lingua (`/it/carte`,
 * `/card-of-the-day`): la traduzione la fa `lib/indirizzi.ts`, e qui la usano `LinkV2` e le navigazioni. */

import { interno, normalizza, pubblico } from "@/lib/indirizzi";

export const R = {
  home: "/",
  leggi: "/read",
  fisica: "/physical-reading",
  storia: "/my-story",
  lettura: (id: string) => `/my-story/${encodeURIComponent(id)}`,
  condivise: "/shared",
  condivisa: (token: string) => `/shared/${encodeURIComponent(token)}`,
  giorno: "/daily-card",
  carte: "/cards",
  carta: (id: string) => `/cards/${encodeURIComponent(id)}`,
  stese: "/spreads",
  stesa: (id: string) => `/spreads/${encodeURIComponent(id)}`,
  mazzi: "/decks",
  mazzo: (slug: string) => `/decks/${encodeURIComponent(slug)}`,
  voto: "/vote",
  negozio: "/shop",
  carrello: "/cart",
  prezzi: "/pricing",
  /** La prova gratuita (v9, Fase 2b): stesso nome in tutte le lingue, come le pagine nuove della v2. */
  prova: "/trial",
  esplora: "/explore",
  blog: "/blog",
  articolo: (slug: string) => `/blog/${encodeURIComponent(slug)}`,
  blogSezione: (slug: string) => `/blog/sezione/${encodeURIComponent(slug)}`,
  blogTag: (slug: string) => `/blog/tag/${encodeURIComponent(slug)}`,
  profilo: "/profile",
  privacy: "/privacy",
  /** La cancellazione dell'account (GDPR, Fase 1): una pagina pubblica, perché Google Play vuole un indirizzo da
   *  aprire anche senza l'app e senza essere entrati. */
  elimina: "/account/elimina",
} as const;

/** Un indirizzo interno della v2 → quello che si vede: in italiano (`/it/carte/…`) se la pagina è stata aperta così,
 *  altrimenti in inglese (`/card-of-the-day`). Esterni e ancore non cambiano. */
export function indirizzoV2(indirizzo: string, prefissoIt: boolean): string {
  return pubblico(prefissoIt ? "it" : "en", indirizzo);
}

/** Un indirizzo del sito scritto coi nomi della v1 (in un articolo del blog, per esempio: `/carte/maj-17`, `/leggi`)
 *  → quello interno della v2. Esterni, ancore e indirizzi già della v2 non cambiano. */
export const inV2 = (href: string): string => normalizza(href.startsWith("/it/") ? href.slice(3) : href === "/it" ? "/" : href);

/** Il percorso interno di un indirizzo visibile (`/it/carte/la-stella` → `/cards/la-stella`): per sapere in che
 *  sezione si è, in qualunque lingua. */
export const senzaPrefisso = (percorso: string) => interno(percorso);
