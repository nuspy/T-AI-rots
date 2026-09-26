/* Gli indirizzi pubblici del sito, in due lingue.
 *
 * **L'inglese è la lingua canonica** — l'SEO si fa in inglese — e sta alla radice: `/cards`, `/spreads`, `/deck`,
 * `/pricing`, `/card-of-the-day`, `/blog`. L'italiano sta sotto `/it` (`/it/carte`, `/it/stese`, …). Le due versioni
 * si dichiarano l'una all'altra con `hreflang`.
 *
 * Le cartelle dell'app non si spostano: mantengono i nomi italiani (`app/carte`, `app/stese`, `app/mazzo`,
 * `app/piano`, `app/carta-del-giorno`, `app/blog`) e il `proxy.ts` riscrive l'indirizzo che si vede in quello
 * della cartella. Qui sta la traduzione, in un posto solo, e serve a tre cose: il proxy (da indirizzo visibile a
 * cartella), il `Link` del sito (da cartella a indirizzo visibile nella lingua) e i metadati (indirizzi assoluti).
 *
 * Pura e senza dipendenze: gira nel proxy, sul server e nel browser. */

export type LinguaPubblica = "en" | "it";

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

/** La lingua pubblica di una lingua dell'interfaccia: `it` è italiano, tutto il resto ricade sull'inglese. */
export const linguaPubblica = (lingua: string | null | undefined): LinguaPubblica => (lingua === "it" ? "it" : "en");

/** Vero per le pagine che si indicizzano: la soglia, carte, stese, mazzo, piano, carta del giorno e blog. */
function indicizzabile(percorso: string): boolean {
  const primo = percorso.split("/")[1] ?? "";
  return percorso === "/" || IN_INGLESE.has(primo) || primo === "blog";
}

/**
 * Un indirizzo interno (coi nomi delle cartelle: `/carte/maj-17`, `/piano?ritorno=/leggi`) → quello che si vede
 * nella lingua. Gli indirizzi non pubblici (`/leggi`, `/profilo`, `#…`, esterni) restano come sono.
 */
export function indirizzo(lingua: string | null | undefined, interno: string): string {
  if (!interno.startsWith("/") || interno.startsWith("//")) return interno;
  const fine = interno.search(/[?#]/);
  const percorso = fine === -1 ? interno : interno.slice(0, fine);
  const coda = fine === -1 ? "" : interno.slice(fine);
  if (!indicizzabile(percorso)) return interno;
  if (linguaPubblica(lingua) === "it") return `/it${percorso === "/" ? "" : percorso}${coda}`;
  const parti = percorso.split("/");
  const inglese = IN_INGLESE.get(parti[1] ?? "");
  if (inglese) parti[1] = inglese;
  return parti.join("/") + coda;
}

export interface Risolto {
  lingua: LinguaPubblica;
  /** L'indirizzo con i nomi delle cartelle: quello che l'app sa servire. */
  interno: string;
  pubblica: boolean;
  /** Se l'indirizzo è vecchio (`/carte/…` senza `/it`): dove mandare chi lo visita, per sempre. */
  reindirizza: string | null;
}

/** Dall'indirizzo che si vede a quello interno, con la lingua. È ciò che fa il proxy. */
export function risolvi(percorso: string): Risolto {
  let lingua: LinguaPubblica = "en";
  let p = percorso;
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
    if (IN_INGLESE.has(primo)) return { lingua, interno: p, pubblica: true, reindirizza: `/it${p}` };
  }
  return { lingua, interno: p, pubblica: indicizzabile(p), reindirizza: null };
}
