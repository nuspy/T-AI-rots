/* Una sezione del blog: articoli, sotto-sezioni e — per le sezioni «carte» e «stese» — le pagine del
 * catalogo. Il server scrive tutto. */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { DettaglioSezione, ElencoArticoli, EtichettaConConteggio, NodoSezione } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";
import { VistaSezione } from "../../viste";

type Parametri = { params: Promise<{ slug: string }>; searchParams: Promise<{ pagina?: string }> };

const numeroPagina = (v?: string) => Math.max(1, Math.min(1000, parseInt(v ?? "1", 10) || 1));

export async function generateMetadata({ params, searchParams }: Parametri): Promise<Metadata> {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).pagina);
  const s = await leggiDalServer<DettaglioSezione>(`/blog/sections/${encodeURIComponent(slug)}`);
  if (!s) return { title: "Sezione non trovata", robots: { index: false, follow: false } };
  const titolo = `${s.seo_titolo || s.nome}${pagina > 1 ? ` — pagina ${pagina}` : ""}`;
  const descrizione = s.seo_descrizione || s.descrizione || `${s.nome}: articoli, carte e stese dei tarocchi.`;
  return {
    title: titolo,
    description: descrizione,
    alternates: { canonical: `${SITE_URL}/blog/sezione/${s.slug}${pagina > 1 ? `?pagina=${pagina}` : ""}` },
    openGraph: { type: "website", siteName: "T·AI·rots", title: titolo, description: descrizione, url: `${SITE_URL}/blog/sezione/${s.slug}` },
  };
}

export default async function PaginaSezione({ params, searchParams }: Parametri) {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).pagina);
  const sezione = await leggiDalServer<DettaglioSezione>(`/blog/sections/${encodeURIComponent(slug)}`);
  if (!sezione) notFound();
  const [elenco, albero, etichette] = await Promise.all([
    leggiDalServer<ElencoArticoli>(`/blog/posts?sezione=${encodeURIComponent(slug)}&per_pagina=12&pagina=${pagina}`),
    leggiDalServer<NodoSezione[]>("/blog/sections"),
    leggiDalServer<EtichettaConConteggio[]>("/blog/tags"),
  ]);
  return (
    <VistaSezione
      sezione={sezione}
      articoli={elenco?.articoli ?? []}
      pagina={pagina}
      pagine={elenco?.pagine ?? 1}
      albero={albero ?? []}
      etichette={etichette ?? []}
    />
  );
}
