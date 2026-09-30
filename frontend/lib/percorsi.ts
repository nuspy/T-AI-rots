/* Gli indirizzi della v1, che dalla v8.5 vive sotto `/old` (il sito è la v2: `lib/indirizzi.ts`).
 *
 * Dentro `/old` tutto è come prima: l'inglese alla radice (`/old/cards`, `/old/spreads`, `/old/deck`, `/old/pricing`,
 * `/old/card-of-the-day`, `/old/blog`), l'italiano sotto `/old/it` (`/old/it/carte`, …). Le cartelle della v1 hanno i
 * nomi italiani (`app/(old)/old/carte`, `…/stese`, `…/mazzo`, `…/piano`, `…/carta-del-giorno`) e il proxy riscrive
 * l'indirizzo visibile in quello della cartella.
 *
 * Nel codice della v1 gli indirizzi si scrivono ancora coi nomi delle cartelle e senza `/old` (`/carte/maj-17`,
 * `/leggi`): `indirizzo()` aggiunge `/old` e la lingua, `risolvi()` li toglie. `/old` non si indicizza (intestazione
 * `X-Robots-Tag` dal proxy e `noindex` nel layout).
 *
 * Pura e senza dipendenze: gira nel proxy, sul server e nel browser. */

import type { LinguaPubblica } from "./indirizzi";

export type { LinguaPubblica } from "./indirizzi";
export { linguaPubblica } from "./indirizzi";

/** Dove sta la v1. */
export const VECCHIO = "/old";

/* Nome della cartella (italiano) → segmento inglese. */
const IN_INGLESE = new Map<string, string>([
  ["carte", "cards"],
  ["stese", "spreads"],
  ["mazzo", "deck"],
  ["piano", "pricing"],
  ["carta-del-giorno", "card-of-the-day"],
]);

/* Segmento inglese → nome della cartella. */
const IN_CARTELLA = new Map<string, string>([...IN_INGLESE].map(([cartella, inglese]) => [inglese, cartella]));

/** Vero per le pagine che nella v1 erano pubbliche: la soglia, carte, stese, mazzo, piano, carta del giorno e blog. */
function indicizzabile(percorso: string): boolean {
  const primo = percorso.split("/")[1] ?? "";
  return percorso === "/" || IN_INGLESE.has(primo) || primo === "blog";
}

/** Un indirizzo della v1 senza lingua (`/leggi`, `/letture/…`): con `/old` davanti. */
export const vecchio = (interno: string): string =>
  !interno.startsWith("/") || interno.startsWith("//") || interno === VECCHIO || interno.startsWith(`${VECCHIO}/`)
    ? interno
    : `${VECCHIO}${interno === "/" ? "" : interno}`;

/**
 * Un indirizzo interno della v1 (coi nomi delle cartelle: `/carte/maj-17`, `/piano?ritorno=/leggi`) → quello che si
 * vede, sotto `/old` e nella lingua. Gli indirizzi non pubblici (`/leggi`, `/profilo`) prendono solo `/old`; esterni
 * e ancore restano come sono.
 */
export function indirizzo(lingua: string | null | undefined, interno: string): string {
  if (!interno.startsWith("/") || interno.startsWith("//")) return interno;
  if (interno === VECCHIO || interno.startsWith(`${VECCHIO}/`)) return interno;
  const fine = interno.search(/[?#]/);
  const percorso = fine === -1 ? interno : interno.slice(0, fine);
  const coda = fine === -1 ? "" : interno.slice(fine);
  if (!indicizzabile(percorso)) return vecchio(interno);
  if (lingua === "it") return `${VECCHIO}/it${percorso === "/" ? "" : percorso}${coda}`;
  const parti = percorso.split("/");
  const inglese = IN_INGLESE.get(parti[1] ?? "");
  if (inglese) parti[1] = inglese;
  return vecchio(parti.join("/") + coda);
}

export interface Risolto {
  lingua: LinguaPubblica;
  /** L'indirizzo con i nomi delle cartelle della v1, **senza** `/old`: quello che il codice della v1 conosce. */
  interno: string;
  pubblica: boolean;
  /** Se l'indirizzo è vecchio (`/old/carte/…` senza `/it`): dove mandare chi lo visita, per sempre (con `/old`). */
  reindirizza: string | null;
}

/** Dall'indirizzo che si vede (con o senza `/old`) a quello interno della v1, con la lingua. */
export function risolvi(percorso: string): Risolto {
  let p = percorso === VECCHIO ? "/" : percorso.startsWith(`${VECCHIO}/`) ? percorso.slice(VECCHIO.length) : percorso;
  let lingua: LinguaPubblica = "en";
  if (p === "/it" || p.startsWith("/it/")) {
    lingua = "it";
    p = p.slice(3) || "/";
  }
  const parti = p.split("/");
  const primo = parti[1] ?? "";
  if (lingua === "en") {
    const cartella = IN_CARTELLA.get(primo);
    if (cartella) {
      parti[1] = cartella;
      return { lingua, interno: parti.join("/"), pubblica: true, reindirizza: null };
    }
    /* Il vecchio indirizzo italiano senza prefisso: stesso contenuto, ma è la versione italiana. */
    if (IN_INGLESE.has(primo)) return { lingua, interno: p, pubblica: true, reindirizza: `${VECCHIO}/it${p}` };
  }
  return { lingua, interno: p, pubblica: indicizzabile(p), reindirizza: null };
}
