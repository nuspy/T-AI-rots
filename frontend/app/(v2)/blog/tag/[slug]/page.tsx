/* Gli articoli con una certa etichetta. Le etichette non hanno una lingua propria: niente hreflang, canonical
 * all'inglese. Un'etichetta senza articoli non si indicizza. */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ElencoArticoli, EtichettaConConteggio } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { anteprima, briciole, grafo, soloInglese, titoloPagina, urlPubblico } from "@/lib/seo";
import { BLOG } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { Pagina } from "@/v2/componenti/pagina";
import { P, PER_PAGINA_BLOG } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { NOINDEX } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { EtichettaDiario } from "@/v2/pagine/blog";

type Parametri = { params: Promise<{ slug: string }>; searchParams: Promise<{ page?: string }> };

const numeroPagina = (v?: string) => Math.max(1, Math.min(1000, parseInt(v ?? "1", 10) || 1));
const percorsoArticoli = (slug: string, lingua: string, pagina: number) =>
  P.articoli(lingua, { tag: slug, pagina, per_pagina: PER_PAGINA_BLOG });
const leggiEtichette = () => leggiDalServer<EtichettaConConteggio[]>(P.etichette(), { obbligatorio: true });

export async function generateMetadata({ params, searchParams }: Parametri): Promise<Metadata> {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).page);
  const lingua = await linguaPagina();
  const e = ((await leggiEtichette()) ?? []).find((x) => x.slug === slug);
  if (!e) return { title: lingua === "it" ? "Etichetta non trovata" : "Tag not found", robots: NOINDEX };
  const elenco = await leggiDalServer<ElencoArticoli>(percorsoArticoli(slug, lingua, pagina));
  const titolo = pagina > 1
    ? `${BLOG.etichettaTitolo(lingua, e.nome)} — ${lingua === "it" ? "pagina" : "page"} ${pagina}`
    : BLOG.etichettaTitolo(lingua, e.nome);
  const descrizione = BLOG.etichettaDescrizione(lingua, e.nome);
  const lingue = soloInglese(lingua, `/blog/tag/${e.slug}`);
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    robots: (elenco?.totale ?? 0) === 0 ? { index: false, follow: true } : undefined,
    alternates: { ...lingue, canonical: pagina > 1 ? `${lingue.canonical}?page=${pagina}` : lingue.canonical },
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, `/blog/tag/${e.slug}`) }),
  };
}

export default async function PaginaEtichetta({ params, searchParams }: Parametri) {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).page);
  const lingua = await linguaPagina();
  const e = ((await leggiEtichette()) ?? []).find((x) => x.slug === slug);
  if (!e) notFound();
  const valori = await precarica([
    P.etichette(), percorsoArticoli(slug, lingua, pagina), P.sezioni(),
    pagina === 1 ? P.nove({ tag: slug, recenti: PER_PAGINA_BLOG, scelti: 10 }) : null,
  ]);
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: BLOG.h1(lingua), url: urlPubblico(lingua, "/blog") },
      { nome: e.nome, url: urlPubblico(lingua, `/blog/tag/${e.slug}`) },
    ]),
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <EtichettaDiario slug={slug} />
      </Pagina>
    </DatiIniziali>
  );
}
