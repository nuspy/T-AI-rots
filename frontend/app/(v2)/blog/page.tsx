/* Il blog: l'ingresso. Gli articoli si vedono in qualunque lingua dell'interfaccia (v8): `/blog` e `/it/blog`
 * elencano la stessa lista, niente `hreflang`, in italiano il canonical punta all'inglese. Le ricerche non si
 * indicizzano; le pagine successive alla prima hanno il proprio canonical (`?page=`). */

import type { Metadata } from "next";
import type { ElencoArticoli } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPubblica } from "@/lib/indirizzi";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { anteprima, briciole, grafo, soloInglese, titoloPagina, urlPubblico } from "@/lib/seo";
import { BLOG } from "@/lib/seo-testi";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { P, PER_PAGINA_BLOG } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { precarica } from "@/v2/lib/precarica";
import { Diario } from "@/v2/pagine/blog";

type Parametri = { searchParams: Promise<{ q?: string; page?: string }> };

const pulisci = (sp: { q?: string; page?: string }) => ({
  q: (sp.q ?? "").trim().slice(0, 100),
  pagina: Math.max(1, Math.min(1000, parseInt(sp.page ?? "1", 10) || 1)),
});

/* Gli stessi percorsi che chiede la pagina nel browser (`Diario`). */
const percorsi = (lingua: string, q: string, pagina: number) => ({
  elenco: P.articoli(lingua, { q, pagina, per_pagina: PER_PAGINA_BLOG }),
  evidenza: q || pagina > 1 ? null : P.articoli(lingua, { evidenza: "true", per_pagina: 1 }),
});

export async function generateMetadata({ searchParams }: Parametri): Promise<Metadata> {
  const { q, pagina } = pulisci(await searchParams);
  const lingua = await linguaPagina();
  const it = lingua === "it";
  const descrizione = BLOG.description(lingua);
  const titolo = q ? `${it ? "Ricerca" : "Search"}: ${q}`
    : pagina > 1 ? `${BLOG.title(lingua)} — ${it ? "pagina" : "page"} ${pagina}` : BLOG.title(lingua);
  const lingue = soloInglese(lingua, "/blog");
  const elenco = (await precarica([percorsi(lingua, q, pagina).elenco]))[percorsi(lingua, q, pagina).elenco] as ElencoArticoli | undefined;
  const vuoto = !q && (elenco?.totale ?? 0) === 0;
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    keywords: BLOG.parole(lingua),
    robots: q || vuoto ? { index: false, follow: true } : undefined,
    alternates: {
      ...lingue,
      canonical: pagina > 1 && !q ? `${lingue.canonical}?page=${pagina}` : lingue.canonical,
      types: { "application/rss+xml": urlPubblico(lingua, "/blog/feed.xml") },
    },
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, "/blog") }),
  };
}

export default async function PaginaDiario({ searchParams }: Parametri) {
  const { q, pagina } = pulisci(await searchParams);
  const lingua = await linguaPagina();
  const p = percorsi(lingua, q, pagina);
  const valori = await precarica([
    p.elenco, p.evidenza, P.sezioni(), P.etichette(),
    !q && pagina === 1 ? P.nove({ recenti: PER_PAGINA_BLOG, scelti: 10 }) : null,
  ]);
  const elenco = valori[p.elenco] as ElencoArticoli | undefined;
  const evidenza = p.evidenza ? (valori[p.evidenza] as ElencoArticoli | undefined) : undefined;
  const url = urlPubblico(lingua, "/blog");
  const articoli = [...(evidenza?.articoli ?? []), ...(elenco?.articoli ?? [])]
    .filter((a, i, tutti) => tutti.findIndex((x) => x.slug === a.slug) === i);
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
      blogPost: articoli.map((a) => ({
        "@type": "BlogPosting", headline: a.titolo, url: urlPubblico(linguaPubblica(a.lang), `/blog/${a.slug}`),
        datePublished: a.pubblicato_il ?? undefined,
      })),
    },
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <Sottotitolo sezione="blog" compatto />
        <Diario />
      </Pagina>
    </DatiIniziali>
  );
}
