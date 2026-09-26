/* La mappa del sito per i motori di ricerca: le pagine pubbliche — carte, stese, il mazzo
 * e, quando ci sono, gli articoli del blog. Si scrive a ogni richiesta (`no-store`), perché
 * l'elenco cambia e in fase di build l'API non c'è. */

import type { MetadataRoute } from "next";
import type { Carta, Stesa } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [carte, stese] = await Promise.all([
    leggiDalServer<Carta[]>("/cards", { secondi: 300 }),
    leggiDalServer<Stesa[]>("/spreads", { secondi: 300 }),
  ]);
  const pagina = (percorso: string, priorita: number, frequenza: "weekly" | "monthly" | "yearly") => ({
    url: `${SITE_URL}${percorso}`,
    changeFrequency: frequenza,
    priority: priorita,
  });
  return [
    pagina("", 1, "weekly"),
    pagina("/carte", 0.9, "monthly"),
    pagina("/stese", 0.9, "monthly"),
    pagina("/mazzo", 0.6, "monthly"),
    ...(carte ?? []).map((c) => pagina(`/carte/${c.id}`, 0.7, "yearly")),
    ...(stese ?? []).map((s) => pagina(`/stese/${s.id}`, 0.8, "yearly")),
  ];
}
