/* La mappa del sito per i motori di ricerca: le pagine pubbliche — home, carte, stese, mazzo, prezzi, carta del
 * giorno e blog — nelle due lingue, ciascuna con le sue alternative (`hreflang`). Ogni indirizzo compare in inglese
 * (canonico) e in italiano; gli articoli del blog, che hanno una lingua sola, compaiono solo nella loro.
 * Non ci sono pagine `noindex` né pagine vuote. Si scrive a ogni richiesta (`no-store`), perché l'elenco cambia e in
 * fase di build l'API non c'è. */

import type { MetadataRoute } from "next";
import type { Carta, Stesa } from "@/lib/api";
import { linguaPubblica, type LinguaPubblica } from "@/lib/percorsi";
import { urlPubblico } from "@/lib/seo";
import { leggiDalServer } from "@/lib/server-api";

type Frequenza = "daily" | "weekly" | "monthly" | "yearly";
type Voce = MetadataRoute.Sitemap[number];

const LINGUE: LinguaPubblica[] = ["en", "it"];

interface Mappa {
  articoli: { slug: string; aggiornato: string; lang: string }[];
  sezioni: string[];
  tags: string[];
  sezioni_lingue?: Record<string, string[]>;
  tags_lingue?: Record<string, string[]>;
}

/** Una pagina che esiste nelle due lingue: due voci, ognuna con le alternative dell'altra. `interni` ha l'indirizzo
 *  interno per lingua (gli slug di carte e stese cambiano con la lingua). */
function coppia(
  interni: Partial<Record<LinguaPubblica, string>>, priorita: number, frequenza: Frequenza, aggiornato?: Date,
): Voce[] {
  const lingue: Record<string, string> = {};
  for (const l of LINGUE) if (interni[l]) lingue[l] = urlPubblico(l, interni[l]!);
  if (lingue.en) lingue["x-default"] = lingue.en;
  return LINGUE.filter((l) => interni[l]).map((l) => ({
    url: urlPubblico(l, interni[l]!),
    ...(aggiornato ? { lastModified: aggiornato } : {}),
    changeFrequency: frequenza,
    /* L'italiano è secondario: un gradino sotto. */
    priority: l === "en" ? priorita : Math.round((priorita - 0.1) * 10) / 10,
    alternates: { languages: lingue },
  }));
}

const stessa = (interno: string) => ({ en: interno, it: interno });

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [carte, stese, blog] = await Promise.all([
    leggiDalServer<Carta[]>("/cards?lang=en", { secondi: 300 }),
    leggiDalServer<Stesa[]>("/spreads?lang=en", { secondi: 300 }),
    leggiDalServer<Mappa>("/blog/mappa", { secondi: 300 }),
  ]);
  const inLingua = (mappa: Record<string, string[]> | undefined, slug: string): LinguaPubblica[] =>
    LINGUE.filter((l) => (mappa ? (mappa[slug] ?? []).includes(l) : true));
  const conLingue = (lingue: LinguaPubblica[], interno: string) =>
    Object.fromEntries(lingue.map((l) => [l, interno])) as Partial<Record<LinguaPubblica, string>>;

  return [
    ...coppia({ en: "/", it: "/" }, 1, "weekly"),
    ...coppia(stessa("/carte"), 0.9, "monthly"),
    ...coppia(stessa("/stese"), 0.9, "monthly"),
    ...coppia(stessa("/carta-del-giorno"), 0.8, "daily"),
    ...coppia(stessa("/mazzo"), 0.6, "monthly"),
    ...coppia(stessa("/piano"), 0.6, "monthly"),
    ...coppia(stessa("/blog"), 0.9, "weekly"),
    ...(blog?.sezioni ?? []).flatMap((s) =>
      coppia(conLingue(inLingua(blog?.sezioni_lingue, s), `/blog/sezione/${s}`), 0.7, "weekly")),
    ...(blog?.tags ?? []).flatMap((x) =>
      coppia(conLingue(inLingua(blog?.tags_lingue, x), `/blog/tag/${x}`), 0.4, "weekly")),
    ...(blog?.articoli ?? []).map((a): Voce => ({
      url: urlPubblico(linguaPubblica(a.lang), `/blog/${a.slug}`),
      lastModified: new Date(a.aggiornato),
      changeFrequency: "monthly",
      priority: 0.8,
    })),
    ...(carte ?? []).flatMap((c) =>
      coppia({ en: `/carte/${c.slugs?.en ?? c.slug ?? c.id}`, it: `/carte/${c.slugs?.it ?? c.id}` }, 0.7, "yearly")),
    ...(stese ?? []).flatMap((s) =>
      coppia({ en: `/stese/${s.slugs?.en ?? s.slug ?? s.id}`, it: `/stese/${s.slugs?.it ?? s.id}` }, 0.8, "yearly")),
  ];
}
