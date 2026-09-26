/* Gli articoli con una certa etichetta. */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ElencoArticoli, EtichettaConConteggio, NodoSezione } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";
import { VistaEtichetta } from "../../viste";

type Parametri = { params: Promise<{ slug: string }>; searchParams: Promise<{ pagina?: string }> };

const numeroPagina = (v?: string) => Math.max(1, Math.min(1000, parseInt(v ?? "1", 10) || 1));

export async function generateMetadata({ params }: Parametri): Promise<Metadata> {
  const { slug } = await params;
  const tutte = (await leggiDalServer<EtichettaConConteggio[]>("/blog/tags")) ?? [];
  const e = tutte.find((x) => x.slug === slug);
  if (!e) return { title: "Etichetta non trovata", robots: { index: false, follow: false } };
  return {
    title: `${e.nome}: articoli sui tarocchi`,
    description: `Gli articoli del blog sull'argomento «${e.nome}».`,
    alternates: { canonical: `${SITE_URL}/blog/tag/${e.slug}` },
  };
}

export default async function PaginaEtichetta({ params, searchParams }: Parametri) {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).pagina);
  const [etichette, albero, elenco] = await Promise.all([
    leggiDalServer<EtichettaConConteggio[]>("/blog/tags"),
    leggiDalServer<NodoSezione[]>("/blog/sections"),
    leggiDalServer<ElencoArticoli>(`/blog/posts?tag=${encodeURIComponent(slug)}&per_pagina=12&pagina=${pagina}`),
  ]);
  const e = (etichette ?? []).find((x) => x.slug === slug);
  if (!e) notFound();
  return (
    <VistaEtichetta
      etichetta={e.nome}
      slug={e.slug}
      articoli={elenco?.articoli ?? []}
      pagina={pagina}
      pagine={elenco?.pagine ?? 1}
      albero={albero ?? []}
      etichette={etichette ?? []}
    />
  );
}
