/* Le letture pubbliche dell'API per le pagine della v2, per percorso.
 *
 * I percorsi stanno in `P`, in un posto solo, perché li usano in due: il componente nel browser (`usePubblico`) e la
 * pagina sul server, che li legge prima (`precarica`) e li passa con `DatiIniziali`. Lo stesso percorso vuol dire gli
 * stessi dati: il componente li trova già pronti e l'HTML esce col contenuto. */

import { API, ErroreApi, leggiConto } from "@/lib/api";
import type { Mazzo, Piano } from "@/lib/api";
import type {
  ArticoloBlog, ArticoloBreve, DettaglioSezione, ElencoArticoli, EtichettaConConteggio, NodoSezione,
} from "@/lib/blog";
import { useLingua } from "@/v2/lib/lingua";
import { useCarica, usePubblico } from "@/v2/lib/usa";
import { P } from "./api-percorsi";

export async function leggiPubblico<T>(percorso: string): Promise<T> {
  const r = await fetch(`${API}${percorso}`, { credentials: "include" });
  if (!r.ok) throw new ErroreApi(String(r.status), r.status);
  return (await r.json()) as T;
}

export { P, PER_PAGINA_BLOG, linguaContenuti } from "./api-percorsi";

type Parametri = Record<string, string | number | undefined>;

/* Le stesse letture come funzioni, per chi le chiama fuori da un hook. */
export const articoli = (lingua: string, parametri: Parametri = {}) => leggiPubblico<ElencoArticoli>(P.articoli(lingua, parametri));
export const articolo = (slug: string) => leggiPubblico<ArticoloBlog>(P.articolo(slug));
export const sezioni = () => leggiPubblico<NodoSezione[]>(P.sezioni());
export const sezione = (slug: string, lingua: string) => leggiPubblico<DettaglioSezione>(P.sezione(slug, lingua));
export const etichette = () => leggiPubblico<EtichettaConConteggio[]>(P.etichette());
export const articoliSu = (tipo: "carta" | "stesa", id: string) => leggiPubblico<ArticoloBreve[]>(P.articoliSu(tipo, id));

/* I mazzi e i piani nella lingua della pagina (v8.5): nomi e descrizioni tradotti dal server. */
export function useMazzi() {
  const { lingua } = useLingua();
  return usePubblico<Mazzo[]>(P.mazzi(lingua));
}

export function usePiani() {
  const { lingua } = useLingua();
  return usePubblico<Piano[]>(P.piani(lingua));
}

/* Il conto (saldo, abbonamento): il nome del piano nella lingua della pagina. `dipendenze` per rileggerlo. */
export function useConto(dipendenze: unknown[] = []) {
  const { lingua } = useLingua();
  return useCarica((tok) => leggiConto(tok, lingua), [lingua, ...dipendenze]);
}
