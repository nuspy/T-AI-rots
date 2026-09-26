/* Le quindici lingue dell'app.
 *
 * Due cose diverse portano il nome «lingua», e qui non si confondono:
 *
 *  - la lingua dell'INTERFACCIA: quella dei bottoni e dei titoli, che chi usa
 *    il sito sceglie dal selettore e il browser ricorda;
 *  - la lingua della LETTURA: quella in cui è scritto il quesito. La ricava il
 *    server, una volta, all'apertura della lettura, e la salva con essa: domande,
 *    interpretazioni e responso escono in quella lingua, anche se l'interfaccia
 *    è in un'altra. Si rinnova a ogni quesito.
 *
 * Le traduzioni vere dell'interfaccia sono tre (`TRADOTTE`); nelle altre dodici
 * i testi ricadono sull'inglese finché non le traduciamo. L'ordine è quello del
 * selettore.
 */

export const LINGUE = [
  { codice: "it", nome: "Italiano", locale: "it-IT", rtl: false },
  { codice: "hu", nome: "Magyar", locale: "hu-HU", rtl: false },
  { codice: "en", nome: "English", locale: "en-GB", rtl: false },
  { codice: "de", nome: "Deutsch", locale: "de-DE", rtl: false },
  { codice: "ru", nome: "Русский", locale: "ru-RU", rtl: false },
  { codice: "uk", nome: "Українська", locale: "uk-UA", rtl: false },
  { codice: "fr", nome: "Français", locale: "fr-FR", rtl: false },
  { codice: "es", nome: "Español", locale: "es-ES", rtl: false },
  { codice: "pt", nome: "Português", locale: "pt-PT", rtl: false },
  { codice: "ro", nome: "Română", locale: "ro-RO", rtl: false },
  { codice: "pl", nome: "Polski", locale: "pl-PL", rtl: false },
  { codice: "zh", nome: "中文", locale: "zh-CN", rtl: false },
  { codice: "hi", nome: "हिन्दी", locale: "hi-IN", rtl: false },
  { codice: "ko", nome: "한국어", locale: "ko-KR", rtl: false },
  { codice: "ar", nome: "العربية", locale: "ar", rtl: true },
] as const;

export type Lingua = (typeof LINGUE)[number]["codice"];

/** Le lingue con l'interfaccia tradotta davvero. */
export const TRADOTTE: readonly Lingua[] = ["it", "en", "hu"];

export const PREDEFINITA: Lingua = "it";

const CODICI: readonly string[] = LINGUE.map((l) => l.codice);

/** Un codice qualunque («pt-BR», «ZH_cn», «hu») come lingua supportata, o `null`. */
export function comeLingua(codice: string | null | undefined): Lingua | null {
  const base = (codice ?? "").trim().toLowerCase().replace("_", "-").split("-")[0];
  return CODICI.includes(base) ? (base as Lingua) : null;
}

/** La lingua che il browser preferisce fra quelle supportate; l'inglese se
 *  nessuna lo è (l'italiano è la lingua del sito solo per chi lo chiede). */
export function linguaDelBrowser(preferite: readonly string[]): Lingua {
  for (const p of preferite) {
    const l = comeLingua(p);
    if (l) return l;
  }
  return "en";
}

export function datiLingua(l: Lingua) {
  return LINGUE.find((x) => x.codice === l) ?? LINGUE[0];
}
