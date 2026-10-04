/* Gli spazi pubblicitari, senza React: i tipi di ciò che l'API manda al sito (`/impostazioni-pubblicita`), il cookie
 * che ricorda il consenso agli annunci, e i calcoli delle posizioni. Li usano il layout sul server (che legge le
 * impostazioni e il cookie, così l'HTML esce già con lo spazio riservato: niente salti) e i componenti nel browser
 * (`v2/componenti/pubblicita.tsx`). */

/** Le tre posizioni di ogni pagina: a un terzo del contenuto, a due terzi, alla fine prima della chiusura. */
export type Posizione = "terzo" | "due_terzi" | "fine";
export type FormatoAnnuncio = "auto" | "rectangle" | "horizontal" | "vertical";

export interface SpazioPubblicita {
  slot: string;
  formato: FormatoAnnuncio;
}

/** Ciò che serve al sito, e nient'altro: i dati d'iscrizione ad AdSense restano nella console. */
export interface ImpostazioniPubblicita {
  attiva: boolean;
  fornitore?: "google";
  /** Solo le posizioni accese in console, ognuna col suo slot. */
  posizioni?: Partial<Record<Posizione, SpazioPubblicita>>;
  pagine_escluse?: string[];
  google?: { editore: string; responsive: boolean; prova: boolean; personalizzati: boolean };
}

export const PERCORSO_PUBBLICITA = "/impostazioni-pubblicita";
export const SPENTA: ImpostazioniPubblicita = { attiva: false };

/** Il cookie (del sito, non dell'API) che ricorda «ha accettato gli annunci»: lo legge il server per riservare lo
 *  spazio già nell'HTML. È solo un promemoria della scelta, non un identificativo: la scelta vera sta sul server
 *  (`/consenso`), e gli annunci si caricano solo dopo averla riletta. */
export const COOKIE_PUBBLICITA = "tarots_pubblicita";

/** La versione dell'informativa che nomina Google AdSense: quella che si registra col consenso agli annunci. */
export const VERSIONE_INFORMATIVA_PUBBLICITA = "v3";

/** Vero se l'indirizzo è fra quelli esclusi dalla console (per prefisso: `/pricing` esclude anche `/pricing/x`). */
export function esclusa(percorso: string | null, escluse: string[] | undefined): boolean {
  if (!percorso || !escluse?.length) return false;
  return escluse.some((p) => percorso === p || percorso.startsWith(p === "/" ? "/" : `${p}/`));
}

/** Dove vanno gli spazi in una sequenza di `n` blocchi: dopo quanti blocchi. La fine è sempre dopo l'ultimo; un terzo
 *  e due terzi si arrotondano, e si saltano se cadrebbero accanto a un altro spazio (mai due annunci di fila). Le
 *  posizioni non dipendono dalle caselle della console: spegnere un banner non sposta gli altri. */
export function posizioniPer(n: number): Map<number, Posizione> {
  const dove = new Map<number, Posizione>();
  if (n < 1) return dove;
  const terzo = Math.round(n / 3);
  const dueTerzi = Math.round((2 * n) / 3);
  if (terzo > 0 && terzo < n) dove.set(terzo, "terzo");
  if (dueTerzi > terzo && dueTerzi < n) dove.set(dueTerzi, "due_terzi");
  dove.set(n, "fine");
  return dove;
}

/** Un elenco in tre parti per una griglia, tagliato dove finiscono le righe: per multipli di 12 (righe piene a 2, 3,
 *  4 e 6 colonne), poi di 6 e di 2, e solo per ultimo dove capita. */
export function inTerzi<T>(elenco: T[]): [T[], T[], T[]] {
  const n = elenco.length;
  for (const m of [12, 6, 2, 1]) {
    const a = Math.round(n / 3 / m) * m;
    const b = Math.round((2 * n) / 3 / m) * m;
    if (a > 0 && a < b && b < n) return [elenco.slice(0, a), elenco.slice(a, b), elenco.slice(b)];
  }
  return [elenco, [], []];
}
