/* I dizionari della v2: separati da quelli del sito (`lib/i18n`), con la voce della v2.
 *
 * Le lingue sono le stesse quindici del sito (`lib/i18n/lingue.ts`, che qui si riusa: sono i metadati delle
 * lingue, non testi). Tradotte davvero: inglese (la base), italiano e ungherese. Le altre dodici sono cartelle
 * copiate dall'inglese (`copia-inglese.mjs`), pronte da tradurre: tradurre una lingua vuol dire riscrivere i
 * file della sua cartella e togliere la riga «COPIA DELL'INGLESE» in cima, così lo script non la sovrascrive più.
 *
 * Ogni cartella ha una sezione per pagina (`comune`, `home`, `lettura`, …) e un `index.ts` che le riunisce. Il
 * tipo è quello dell'inglese: una chiave che manca in una lingua è un errore di compilazione, non un buco
 * nell'interfaccia.
 *
 * I testi sono dati puri, senza funzioni: i valori variabili si scrivono `{nome}` e si riempiono con `f()`.
 * Così un dizionario si può anche mandare dal server al browser, e chi traduce vede la frase intera.
 *
 * L'inglese e l'italiano sono sempre nel pacchetto (sono le lingue in cui il server scrive la pagina); le
 * altre si caricano quando servono, una sola volta. */

import type { Lingua } from "@/lib/i18n/lingue";
import { en } from "./en";
import { it } from "./it";

export type Dizionario = typeof en;
export type { Lingua };
export { LINGUE, TRADOTTE, PREDEFINITA, comeLingua, datiLingua, linguaDelBrowser } from "@/lib/i18n/lingue";

const PRONTI: Partial<Record<Lingua, Dizionario>> = { en, it };

/* Le lingue tradotte esportano una costante col proprio codice (`it`, `hu`); le copie sono copie esatte
 * dell'inglese, anche nel nome, ed esportano `en`. Chi traduce una copia può lasciarle quel nome. */
const CARICATORI: Record<Lingua, () => Promise<Dizionario>> = {
  en: async () => en,
  it: async () => it,
  hu: () => import("./hu").then((m) => m.hu),
  de: () => import("./de").then((m) => m.en),
  ru: () => import("./ru").then((m) => m.en),
  uk: () => import("./uk").then((m) => m.en),
  fr: () => import("./fr").then((m) => m.en),
  es: () => import("./es").then((m) => m.en),
  pt: () => import("./pt").then((m) => m.en),
  ro: () => import("./ro").then((m) => m.en),
  pl: () => import("./pl").then((m) => m.en),
  zh: () => import("./zh").then((m) => m.en),
  hi: () => import("./hi").then((m) => m.en),
  ko: () => import("./ko").then((m) => m.en),
  ar: () => import("./ar").then((m) => m.en),
};

/** Il dizionario di una lingua, se è già nel pacchetto (inglese, italiano, o una lingua già caricata). */
export function dizionarioPronto(lingua: Lingua): Dizionario | null {
  return PRONTI[lingua] ?? null;
}

/** Il dizionario di una lingua, caricandolo se serve. Un errore di rete ricade sull'inglese. */
export async function caricaDizionario(lingua: Lingua): Promise<Dizionario> {
  const pronto = PRONTI[lingua];
  if (pronto) return pronto;
  try {
    const d = await CARICATORI[lingua]();
    PRONTI[lingua] = d;
    return d;
  } catch {
    return en;
  }
}

/** Riempie i segnaposto `{nome}` di un testo. Un segnaposto senza valore resta com'è: si vede, non sparisce. */
export function f(testo: string, valori: Record<string, string | number>): string {
  return testo.replace(/\{(\w+)\}/g, (tutto, nome: string) => (nome in valori ? String(valori[nome]) : tutto));
}

/** Uno o molti: `{ uno: "1 card", molti: "{n} cards" }`. Basta per le tre lingue tradotte; le lingue con più
 *  forme plurali (polacco, russo…) lo sostituiranno quando si tradurranno. */
export function plurale(n: number, forme: { uno: string; molti: string }): string {
  return f(n === 1 ? forme.uno : forme.molti, { n });
}
