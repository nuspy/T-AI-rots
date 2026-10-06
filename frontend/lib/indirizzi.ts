/* Gli indirizzi del sito (la v2, dalla v8.5): da cartella dell'app a indirizzo che si vede, e ritorno.
 *
 * **L'inglese è la lingua canonica** e sta alla radice; l'italiano sotto `/it`. Le pagine già indicizzate tengono i
 * loro indirizzi: `/cards/…` e `/it/carte/…`, `/spreads` e `/it/stese`, `/pricing` e `/it/piano`, `/card-of-the-day`
 * e `/it/carta-del-giorno`, `/blog/…` (con `/blog/sezione/…` e `/blog/tag/…`). Le pagine nuove hanno il nome della
 * v2 in tutte e due le lingue (`/read`, `/it/read`, `/decks`, `/shop`, `/my-story`, `/shared/…`).
 *
 * Le cartelle dell'app hanno i nomi inglesi della v2 (`app/(v2)/cards`, `app/(v2)/daily-card`…): il proxy riscrive
 * l'indirizzo visibile in quello della cartella, e qui sta la traduzione, in un posto solo. I vecchi indirizzi (quelli
 * della v1: `/leggi`, `/letture`, `/s/…`, `/deck`, `/interpreta`; quelli dell'anteprima: `/v2/…`) portano ai nuovi con
 * un reindirizzamento permanente. La v1 intera vive sotto `/old` (`lib/percorsi.ts`), fuori dall'indice.
 *
 * Pura e senza dipendenze: gira nel proxy, sul server e nel browser. */

export type LinguaPubblica = "en" | "it";

/** Cartella (primo segmento) → segmento visibile per lingua. Le cartelle che non stanno qui si vedono col loro nome. */
const SEGMENTI: Record<string, Record<LinguaPubblica, string>> = {
  cards: { en: "cards", it: "carte" },
  spreads: { en: "spreads", it: "stese" },
  pricing: { en: "pricing", it: "piano" },
  "daily-card": { en: "card-of-the-day", it: "carta-del-giorno" },
};

/** Segmento visibile → cartella, per lingua. */
const IN_CARTELLA: Record<LinguaPubblica, Map<string, string>> = {
  en: new Map(Object.entries(SEGMENTI).map(([c, v]) => [v.en, c])),
  it: new Map(Object.entries(SEGMENTI).map(([c, v]) => [v.it, c])),
};

/** I nomi della v1 (cartelle e indirizzi di allora) → la cartella della v2 che ne fa le veci. */
const DALLA_V1 = new Map<string, string>([
  ["carte", "cards"],
  ["stese", "spreads"],
  ["piano", "pricing"],
  ["carta-del-giorno", "daily-card"],
  ["mazzo", "decks"],
  ["deck", "decks"],
  ["leggi", "read"],
  ["letture", "my-story"],
  ["profilo", "profile"],
  ["s", "shared"],
  ["interpreta", "physical-reading"],
  ["vota-mazzo", "vote"],
]);

/** Le pagine personali o di servizio: non si indicizzano, e la lingua non la decide l'indirizzo da sola. */
const PRIVATE = new Set(["read", "read-chat", "read-classic", "my-story", "profile", "shared", "cart"]);

/** Vero per le pagine da indicizzare: home, carte, stese, prezzi, carta del giorno, mazzi, negozio, blog… */
export function indicizzabile(interno: string): boolean {
  const primo = interno.split(/[/?#]/)[1] ?? "";
  return !PRIVATE.has(primo);
}

/** La lingua pubblica di una lingua dell'interfaccia: `it` è italiano, tutto il resto ricade sull'inglese. */
export const linguaPubblica = (lingua: string | null | undefined): LinguaPubblica => (lingua === "it" ? "it" : "en");

/** Un indirizzo scritto coi nomi della v1 (`/carte/maj-17`, `/leggi?id=…`, `/blog/section/x`) → quello interno della v2. */
export function normalizza(interno: string): string {
  if (!interno.startsWith("/") || interno.startsWith("//")) return interno;
  const fine = interno.search(/[?#]/);
  const percorso = fine === -1 ? interno : interno.slice(0, fine);
  const coda = fine === -1 ? "" : interno.slice(fine);
  const parti = percorso.split("/");
  const v2 = DALLA_V1.get(parti[1] ?? "");
  if (v2) parti[1] = v2;
  if (parti[1] === "blog" && parti[2] === "section") parti[2] = "sezione";
  return parti.join("/") + coda;
}

/**
 * Un indirizzo interno (coi nomi delle cartelle: `/cards/maj-17`, `/pricing?ritorno=/read`, `/daily-card`) → quello
 * che si vede nella lingua: `/cards/maj-17` o `/it/carte/maj-17`, `/card-of-the-day` o `/it/carta-del-giorno`.
 * Esterni, ancore e indirizzi già tradotti passano senza danni; anche i nomi della v1 funzionano (`normalizza`).
 */
export function pubblico(lingua: LinguaPubblica, interno: string): string {
  if (!interno.startsWith("/") || interno.startsWith("//")) return interno;
  const n = normalizza(interno);
  const fine = n.search(/[?#]/);
  const percorso = fine === -1 ? n : n.slice(0, fine);
  const coda = fine === -1 ? "" : n.slice(fine);
  const parti = percorso.split("/");
  const segmento = SEGMENTI[parti[1] ?? ""];
  if (segmento) parti[1] = segmento[lingua];
  const visibile = parti.join("/") || "/";
  if (lingua === "it") return `/it${visibile === "/" ? "" : visibile}${coda}`;
  return visibile + coda;
}

export interface Risolto {
  lingua: LinguaPubblica;
  /** L'indirizzo con i nomi delle cartelle: quello che l'app sa servire. */
  interno: string;
  /** Pagina da indicizzare (la lingua è quella dell'indirizzo, i metadati la dichiarano). */
  pubblica: boolean;
  /** Se l'indirizzo è vecchio o scritto nell'altra lingua: dove mandare chi lo visita, per sempre. */
  reindirizza: string | null;
}

/** Dall'indirizzo che si vede (senza query) a quello interno, con la lingua. È ciò che fa il proxy. */
export function risolvi(percorso: string): Risolto {
  let lingua: LinguaPubblica = "en";
  let p = percorso;
  if (p === "/it" || p.startsWith("/it/")) {
    lingua = "it";
    p = p.slice(3) || "/";
  }
  const parti = p.split("/");
  const primo = parti[1] ?? "";
  const verso = (interno: string, l: LinguaPubblica = lingua): Risolto =>
    ({ lingua: l, interno, pubblica: indicizzabile(interno), reindirizza: pubblico(l, interno) });

  /* L'anteprima: `/v2/cards/x` → `/cards/x`, `/it/v2/daily-card` → `/it/carta-del-giorno`. */
  if (primo === "v2") return verso(normalizza(`/${parti.slice(2).join("/")}`));

  /* Il segmento visibile della lingua: la pagina. */
  const cartella = IN_CARTELLA[lingua].get(primo);
  if (cartella) {
    parti[1] = cartella;
    return { lingua, interno: parti.join("/"), pubblica: true, reindirizza: null };
  }

  /* Un vecchio indirizzo italiano senza `/it` (`/carte/…`, `/stese`, `/piano`, `/carta-del-giorno`): era la versione
   * italiana, e lì si va. */
  if (lingua === "en" && IN_CARTELLA.it.has(primo)) {
    parti[1] = IN_CARTELLA.it.get(primo)!;
    return verso(parti.join("/"), "it");
  }

  /* Il segmento dell'altra lingua (`/it/cards/…`) o il nome della cartella dove si vede un nome diverso
   * (`/daily-card`): lo stesso contenuto, all'indirizzo giusto. */
  const altra = IN_CARTELLA[lingua === "en" ? "it" : "en"].get(primo) ?? (SEGMENTI[primo] ? primo : undefined);
  if (altra) {
    parti[1] = altra;
    return verso(parti.join("/"));
  }

  /* I nomi della v1 e `/blog/section/…`. Il vecchio `/mazzo` senza `/it` era, come `/carte`, la pagina italiana. */
  if (lingua === "en" && primo === "mazzo") return verso(normalizza(p), "it");
  if (DALLA_V1.has(primo) || (primo === "blog" && parti[2] === "section")) return verso(normalizza(p));

  return { lingua, interno: p, pubblica: indicizzabile(p), reindirizza: null };
}

/** Il percorso interno di un indirizzo visibile (`/it/carte/la-stella` → `/cards/la-stella`): per sapere in che
 *  sezione si è, qualunque sia la lingua. */
export const interno = (percorso: string): string => {
  const r = risolvi(percorso);
  return r.reindirizza ? risolvi(r.reindirizza).interno : r.interno;
};
