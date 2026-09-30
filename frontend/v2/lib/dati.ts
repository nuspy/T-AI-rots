/* Letture pubbliche dell'API per le pagine della v2 che non hanno una funzione già pronta in `lib/api.ts` (il
 * blog, soprattutto). Le pagine della v2 leggono i dati nel browser, nella lingua scelta: sono un'anteprima non
 * indicizzata, e la lingua può essere una qualunque delle quindici (il server conosce solo quella
 * dell'indirizzo). */

import { API, ErroreApi } from "@/lib/api";
import type {
  ArticoloBlog, ArticoloBreve, DettaglioSezione, ElencoArticoli, EtichettaConConteggio, NodoSezione,
} from "@/lib/blog";

export async function leggiPubblico<T>(percorso: string): Promise<T> {
  const r = await fetch(`${API}${percorso}`, { credentials: "include" });
  if (!r.ok) throw new ErroreApi(String(r.status), r.status);
  return (await r.json()) as T;
}

/** La lingua dei contenuti editoriali (blog): esistono in italiano e in inglese; le altre lingue leggono
 *  l'inglese, come nel sito. */
export const linguaContenuti = (lingua: string) => (lingua === "it" ? "it" : "en");

export const articoli = (lingua: string, parametri: Record<string, string | number | undefined> = {}) => {
  const p = new URLSearchParams({ lang: linguaContenuti(lingua) });
  for (const [k, v] of Object.entries(parametri)) if (v !== undefined && v !== "") p.set(k, String(v));
  return leggiPubblico<ElencoArticoli>(`/blog/posts?${p}`);
};

export const articolo = (slug: string) => leggiPubblico<ArticoloBlog>(`/blog/posts/${encodeURIComponent(slug)}`);

export const sezioni = () => leggiPubblico<NodoSezione[]>("/blog/sections");

export const sezione = (slug: string, lingua: string) =>
  leggiPubblico<DettaglioSezione>(`/blog/sections/${encodeURIComponent(slug)}?lang=${linguaContenuti(lingua)}`);

export const etichette = () => leggiPubblico<EtichettaConConteggio[]>("/blog/tags");

/** Gli articoli che parlano di una carta o di una stesa. */
export const articoliSu = (tipo: "carta" | "stesa", id: string) =>
  leggiPubblico<ArticoloBreve[]>(`/blog/links/${tipo}/${encodeURIComponent(id)}`);
