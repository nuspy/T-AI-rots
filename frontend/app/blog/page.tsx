/* Il blog: l'ingresso. Il server scrive l'elenco, l'albero delle sezioni e le etichette; la ricerca è
 * un modulo GET (funziona senza JavaScript).
 *
 * `/blog` è il blog inglese, `/it/blog` quello italiano: ognuno elenca gli articoli della sua lingua e i due
 * si dichiarano con `hreflang`. Le ricerche non si indicizzano (sono infinite e sottili); le pagine successive
 * alla prima sì, ciascuna col proprio indirizzo. */

import type { Metadata } from "next";
import type { ElencoArticoli, EtichettaConConteggio, NodoSezione } from "@/lib/blog";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { BLOG } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "../componenti/json-ld";
import { VistaBlog } from "./viste";

type Parametri = Promise<{ q?: string; pagina?: string }>;

const pulisci = (sp: { q?: string; pagina?: string }) => ({
  q: (sp.q ?? "").trim().slice(0, 100),
  pagina: Math.max(1, Math.min(1000, parseInt(sp.pagina ?? "1", 10) || 1)),
});

export async function generateMetadata({ searchParams }: { searchParams: Parametri }): Promise<Metadata> {
  const { q, pagina } = pulisci(await searchParams);
  const lingua = await linguaPagina();
  const it = lingua === "it";
  const descrizione = BLOG.description(lingua);
  const titolo = q
    ? `${it ? "Ricerca" : "Search"}: ${q}`
    : pagina > 1
      ? `${BLOG.title(lingua)} — ${it ? "pagina" : "page"} ${pagina}`
      : BLOG.title(lingua);
  const url = urlPubblico(lingua, "/blog");
  const lingue = alternative(lingua, { en: "/blog", it: "/blog" });
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    keywords: BLOG.parole(lingua),
    /* Le ricerche non si indicizzano; le pagine successive alla prima hanno il proprio canonical. */
    robots: q ? { index: false, follow: true } : undefined,
    alternates: {
      ...lingue,
      canonical: pagina > 1 && !q ? `${url}?pagina=${pagina}` : url,
      ...(pagina > 1 || q ? { languages: undefined } : {}),
      types: { "application/rss+xml": urlPubblico(lingua, "/blog/feed.xml") },
    },
    ...anteprima(lingua, { titolo, descrizione, url }),
  };
}

export default async function PaginaBlog({ searchParams }: { searchParams: Parametri }) {
  const { q, pagina } = pulisci(await searchParams);
  const lingua = await linguaPagina();
  const params = new URLSearchParams({ per_pagina: "12", pagina: String(pagina), lang: lingua });
  if (q) params.set("q", q);
  const paginaUno = pagina === 1 && !q;
  const [elenco, albero, etichette, evidenza] = await Promise.all([
    leggiDalServer<ElencoArticoli>(`/blog/posts?${params}`),
    leggiDalServer<NodoSezione[]>("/blog/sections"),
    leggiDalServer<EtichettaConConteggio[]>("/blog/tags"),
    paginaUno ? leggiDalServer<ElencoArticoli>(`/blog/posts?evidenza=true&per_pagina=1&lang=${lingua}`) : Promise.resolve(null),
  ]);
  const inEvidenza = evidenza?.articoli[0] ?? null;
  const articoli = (elenco?.articoli ?? []).filter((a) => a.slug !== inEvidenza?.slug);
  const url = urlPubblico(lingua, "/blog");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: BLOG.h1(lingua), url }]),
    {
      "@type": "Blog",
      "@id": `${url}#blog`,
      name: BLOG.h1(lingua),
      description: BLOG.description(lingua),
      url,
      inLanguage: lingua === "it" ? "it-IT" : "en",
      publisher: { "@id": `${SITE_URL}/#organization` },
      blogPost: [inEvidenza, ...articoli].filter((a) => a !== null).map((a) => ({
        "@type": "BlogPosting", headline: a.titolo, url: urlPubblico(lingua, `/blog/${a.slug}`),
        datePublished: a.pubblicato_il ?? undefined,
      })),
    },
  );
  return (
    <>
      <JsonLd dati={dati} />
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
    </>
  );
}
