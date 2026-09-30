/* Il blog: l'ingresso. Il server scrive l'elenco, l'albero delle sezioni e le etichette; la ricerca è
 * un modulo GET (funziona senza JavaScript).
 *
 * Gli articoli sono solo in inglese (v8) e si vedono a prescindere dalla lingua dell'interfaccia:
 * `/blog` e `/it/blog` elencano la stessa lista, niente `hreflang` fra i due — in italiano il
 * canonical punta all'inglese. Le ricerche non si indicizzano (sono infinite e sottili); le pagine
 * successive alla prima sì, ciascuna col proprio indirizzo. */

import type { Metadata } from "next";
import type { ElencoArticoli, EtichettaConConteggio, NodoSezione } from "@/lib/blog";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { linguaPubblica } from "@/lib/percorsi";
import { anteprima, briciole, grafo, soloInglese, titoloPagina, urlPubblico } from "@/lib/seo";
import { BLOG } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
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
  /* Gli articoli sono solo in inglese e si vedono in qualunque lingua dell'interfaccia (v8): niente
   * hreflang fra "/blog" e "/it/blog" (non sono una traduzione, sono la stessa lista) — in italiano
   * il canonical punta all'inglese, così non si indicizzano due indirizzi con lo stesso contenuto. */
  const lingue = soloInglese(lingua, "/blog");
  const canonicalPagina = pagina > 1 && !q ? `${lingue.canonical}?pagina=${pagina}` : lingue.canonical;
  /* Un blog senza ancora nessun articolo è una pagina vuota: non si indicizza (finché non ne ha). */
  const vuoto = !q && ((await leggiDalServer<ElencoArticoli>("/blog/posts?per_pagina=1"))?.totale ?? 0) === 0;
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    keywords: BLOG.parole(lingua),
    /* Le ricerche non si indicizzano; le pagine successive alla prima hanno il proprio canonical. */
    robots: q || vuoto ? { index: false, follow: true } : undefined,
    alternates: {
      ...lingue,
      canonical: canonicalPagina,
      types: { "application/rss+xml": urlPubblico(lingua, "/blog/feed.xml") },
    },
    ...anteprima(lingua, { titolo, descrizione, url }),
  };
}

export default async function PaginaBlog({ searchParams }: { searchParams: Parametri }) {
  const { q, pagina } = pulisci(await searchParams);
  const lingua = await linguaPagina();
  /* Niente `lang`: gli articoli sono solo in inglese e si vedono in qualunque lingua dell'interfaccia (v8). */
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
        /* L'indirizzo vero dell'articolo è nella SUA lingua, non in quella della pagina che lo
         * elenca (gli articoli sono in inglese anche quando la lista si legge in italiano). */
        "@type": "BlogPosting", headline: a.titolo, url: urlPubblico(linguaPubblica(a.lang), `/blog/${a.slug}`),
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
