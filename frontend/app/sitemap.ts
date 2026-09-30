/* La mappa del sito per i motori di ricerca (v8.5, la v2 è il sito): home, carte, stese, carta del giorno, mazzi,
 * prezzi, negozio, lettura con le proprie carte, esplora, privacy e blog, ciascuna con le sue alternative
 * (`hreflang`) quando esiste in due lingue. Gli elenchi del blog e le etichette sono la stessa lista in ogni lingua
 * (canonical all'inglese): compaiono solo in inglese; gli articoli solo nella loro lingua. `/old` non c'è. Si scrive
 * a ogni richiesta, perché l'elenco cambia e in fase di build l'API non c'è. */

import type { MetadataRoute } from "next";
import type { Carta, Mazzo, Stesa } from "@/lib/api";
import { linguaPubblica, type LinguaPubblica } from "@/lib/indirizzi";
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
}

/** Una pagina nelle lingue in cui esiste: una voce per lingua, ognuna con le alternative delle altre. */
function coppia(
  interni: Partial<Record<LinguaPubblica, string>>, priorita: number, frequenza: Frequenza, aggiornato?: Date,
): Voce[] {
  const lingue: Record<string, string> = {};
  for (const l of LINGUE) if (interni[l]) lingue[l] = urlPubblico(l, interni[l]!);
  if (lingue.en) lingue["x-default"] = lingue.en;
  const piu = Object.keys(lingue).length > 2;
  return LINGUE.filter((l) => interni[l]).map((l) => ({
    url: urlPubblico(l, interni[l]!),
    ...(aggiornato ? { lastModified: aggiornato } : {}),
    changeFrequency: frequenza,
    priority: l === "en" ? priorita : Math.round((priorita - 0.1) * 10) / 10,
    ...(piu ? { alternates: { languages: lingue } } : {}),
  }));
}

const stessa = (interno: string) => ({ en: interno, it: interno });
const soloEn = (interno: string) => ({ en: interno });

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [carte, stese, mazzi, blog] = await Promise.all([
    leggiDalServer<Carta[]>("/cards?lang=en", { secondi: 300 }),
    leggiDalServer<Stesa[]>("/spreads?lang=en", { secondi: 300 }),
    leggiDalServer<Mazzo[]>("/decks?lang=en", { secondi: 300 }),
    leggiDalServer<Mappa>("/blog/mappa", { secondi: 300 }),
  ]);
  const inLingua = (mappa: Record<string, string[]> | undefined, slug: string): LinguaPubblica[] =>
    LINGUE.filter((l) => (mappa ? (mappa[slug] ?? []).includes(l) : l === "en"));
  const conLingue = (lingue: LinguaPubblica[], interno: string) =>
    Object.fromEntries(lingue.map((l) => [l, interno])) as Partial<Record<LinguaPubblica, string>>;

  return [
    ...coppia(stessa("/"), 1, "weekly"),
    ...coppia(stessa("/cards"), 0.9, "monthly"),
    ...coppia(stessa("/spreads"), 0.9, "monthly"),
    ...coppia(stessa("/daily-card"), 0.8, "daily"),
    ...coppia(stessa("/decks"), 0.6, "monthly"),
    ...coppia(stessa("/pricing"), 0.6, "monthly"),
    ...coppia(stessa("/shop"), 0.6, "monthly"),
    ...coppia(stessa("/physical-reading"), 0.6, "monthly"),
    ...coppia(stessa("/explore"), 0.5, "weekly"),
    ...coppia(stessa("/privacy"), 0.2, "yearly"),
    ...((blog?.articoli ?? []).length ? coppia(soloEn("/blog"), 0.9, "weekly") : []),
    ...(blog?.sezioni ?? []).flatMap((s) =>
      coppia(conLingue(inLingua(blog?.sezioni_lingue, s), `/blog/sezione/${s}`), 0.7, "weekly")),
    ...(blog?.tags ?? []).flatMap((x) => coppia(soloEn(`/blog/tag/${x}`), 0.4, "weekly")),
    ...(blog?.articoli ?? []).map((a): Voce => ({
      url: urlPubblico(linguaPubblica(a.lang), `/blog/${a.slug}`),
      lastModified: new Date(a.aggiornato),
      changeFrequency: "monthly",
      priority: 0.8,
    })),
    ...(carte ?? []).flatMap((c) =>
      coppia({ en: `/cards/${c.slugs?.en ?? c.slug ?? c.id}`, it: `/cards/${c.slugs?.it ?? c.id}` }, 0.7, "yearly")),
    ...(stese ?? []).flatMap((s) =>
      coppia({ en: `/spreads/${s.slugs?.en ?? s.slug ?? s.id}`, it: `/spreads/${s.slugs?.it ?? s.id}` }, 0.8, "yearly")),
    ...(mazzi ?? []).flatMap((m) => coppia(stessa(`/decks/${m.slug}`), 0.5, "monthly")),
  ];
}
