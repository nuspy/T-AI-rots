/* Il blog: l'ingresso. Il server scrive l'elenco, l'albero delle sezioni e le etichette; la ricerca è
 * un modulo GET (funziona senza JavaScript). */

import type { Metadata } from "next";
import { SITE_URL } from "@/lib/condivisione";
import type { ElencoArticoli, EtichettaConConteggio, NodoSezione } from "@/lib/blog";
import { leggiDalServer } from "@/lib/server-api";
import { VistaBlog } from "./viste";

type Parametri = Promise<{ q?: string; pagina?: string }>;

const pulisci = (sp: { q?: string; pagina?: string }) => ({
  q: (sp.q ?? "").trim().slice(0, 100),
  pagina: Math.max(1, Math.min(1000, parseInt(sp.pagina ?? "1", 10) || 1)),
});

export async function generateMetadata({ searchParams }: { searchParams: Parametri }): Promise<Metadata> {
  const { q, pagina } = pulisci(await searchParams);
  const descrizione =
    "Guide, approfondimenti e riflessioni sui tarocchi: le carte, le stese e i temi che le attraversano — amore, relazioni, lavoro, simboli.";
  return {
    title: q ? `Ricerca: ${q}` : pagina > 1 ? `Il blog dei tarocchi, pagina ${pagina}` : "Il blog dei tarocchi: guide, significati e approfondimenti",
    description: descrizione,
    /* Le ricerche non si indicizzano: sono infinite e sottili. */
    robots: q ? { index: false, follow: true } : undefined,
    alternates: {
      canonical: `${SITE_URL}/blog${pagina > 1 && !q ? `?pagina=${pagina}` : ""}`,
      types: { "application/rss+xml": `${SITE_URL}/blog/feed.xml` },
    },
    openGraph: { type: "website", siteName: "TAROTS chat", title: "Il blog dei tarocchi", description: descrizione, url: `${SITE_URL}/blog` },
  };
}

export default async function PaginaBlog({ searchParams }: { searchParams: Parametri }) {
  const { q, pagina } = pulisci(await searchParams);
  const params = new URLSearchParams({ per_pagina: "12", pagina: String(pagina) });
  if (q) params.set("q", q);
  const paginaUno = pagina === 1 && !q;
  const [elenco, albero, etichette, evidenza] = await Promise.all([
    leggiDalServer<ElencoArticoli>(`/blog/posts?${params}`),
    leggiDalServer<NodoSezione[]>("/blog/sections"),
    leggiDalServer<EtichettaConConteggio[]>("/blog/tags"),
    paginaUno ? leggiDalServer<ElencoArticoli>("/blog/posts?evidenza=true&per_pagina=1") : Promise.resolve(null),
  ]);
  const inEvidenza = evidenza?.articoli[0] ?? null;
  const articoli = (elenco?.articoli ?? []).filter((a) => a.slug !== inEvidenza?.slug);
  return (
    <VistaBlog
      q={q}
      pagina={pagina}
      pagine={elenco?.pagine ?? 1}
      totale={elenco?.totale ?? 0}
      inEvidenza={inEvidenza}
      articoli={articoli}
      albero={albero ?? []}
      etichette={etichette ?? []}
    />
  );
}
