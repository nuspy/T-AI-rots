/* Gli articoli con una certa etichetta, nella lingua dell'indirizzo. Un'etichetta senza articoli in quella
 * lingua non si indicizza. */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ElencoArticoli, EtichettaConConteggio, NodoSezione } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { BLOG } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "../../../componenti/json-ld";
import { VistaEtichetta } from "../../viste";

type Parametri = { params: Promise<{ slug: string }>; searchParams: Promise<{ pagina?: string }> };

const numeroPagina = (v?: string) => Math.max(1, Math.min(1000, parseInt(v ?? "1", 10) || 1));

const leggiArticoli = (slug: string, lingua: string, pagina: number) =>
  leggiDalServer<ElencoArticoli>(
    `/blog/posts?tag=${encodeURIComponent(slug)}&per_pagina=12&pagina=${pagina}&lang=${lingua}`,
  );

export async function generateMetadata({ params, searchParams }: Parametri): Promise<Metadata> {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).pagina);
  const lingua = await linguaPagina();
  const tutte = (await leggiDalServer<EtichettaConConteggio[]>("/blog/tags")) ?? [];
  const e = tutte.find((x) => x.slug === slug);
  if (!e) return { title: lingua === "it" ? "Etichetta non trovata" : "Tag not found", robots: { index: false, follow: false } };
  const elenco = await leggiArticoli(slug, lingua, pagina);
  const titolo = pagina > 1
    ? `${BLOG.etichettaTitolo(lingua, e.nome)} — ${lingua === "it" ? "pagina" : "page"} ${pagina}`
    : BLOG.etichettaTitolo(lingua, e.nome);
  const descrizione = BLOG.etichettaDescrizione(lingua, e.nome);
  const url = urlPubblico(lingua, `/blog/tag/${e.slug}`);
  const lingue = alternative(lingua, { en: `/blog/tag/${e.slug}`, it: `/blog/tag/${e.slug}` });
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    robots: (elenco?.totale ?? 0) === 0 ? { index: false, follow: true } : undefined,
    alternates: {
      ...lingue,
      canonical: pagina > 1 ? `${url}?pagina=${pagina}` : url,
      ...(pagina > 1 ? { languages: undefined } : {}),
    },
    ...anteprima(lingua, { titolo, descrizione, url }),
  };
}

export default async function PaginaEtichetta({ params, searchParams }: Parametri) {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).pagina);
  const lingua = await linguaPagina();
  const [etichette, albero, elenco] = await Promise.all([
    leggiDalServer<EtichettaConConteggio[]>("/blog/tags"),
    leggiDalServer<NodoSezione[]>("/blog/sections"),
    leggiArticoli(slug, lingua, pagina),
  ]);
  const e = (etichette ?? []).find((x) => x.slug === slug);
  if (!e) notFound();
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: BLOG.h1(lingua), url: urlPubblico(lingua, "/blog") },
      { nome: e.nome, url: urlPubblico(lingua, `/blog/tag/${e.slug}`) },
    ]),
  );
  return (
    <>
      <JsonLd dati={dati} />
      <VistaEtichetta
        etichetta={e.nome}
        slug={e.slug}
        articoli={elenco?.articoli ?? []}
        pagina={pagina}
        pagine={elenco?.pagine ?? 1}
        albero={albero ?? []}
        etichette={etichette ?? []}
      />
    </>
  );
}
