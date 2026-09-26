/* Una sezione del blog: articoli, sotto-sezioni e — per le sezioni «carte» e «stese» — le pagine del
 * catalogo. Il server scrive tutto. Gli articoli sono quelli della lingua dell'indirizzo; una sezione che in
 * quella lingua non ha ancora nulla da mostrare non si indicizza (sarebbe una pagina vuota). */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { DettaglioSezione, ElencoArticoli, EtichettaConConteggio, NodoSezione } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { BLOG } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "../../../componenti/json-ld";
import { VistaSezione } from "../../viste";

type Parametri = { params: Promise<{ slug: string }>; searchParams: Promise<{ pagina?: string }> };

const numeroPagina = (v?: string) => Math.max(1, Math.min(1000, parseInt(v ?? "1", 10) || 1));

const leggiSezione = (slug: string, lingua: string) =>
  leggiDalServer<DettaglioSezione>(`/blog/sections/${encodeURIComponent(slug)}?lang=${lingua}`);

const leggiArticoli = (slug: string, lingua: string, pagina: number) =>
  leggiDalServer<ElencoArticoli>(
    `/blog/posts?sezione=${encodeURIComponent(slug)}&per_pagina=12&pagina=${pagina}&lang=${lingua}`,
  );

export async function generateMetadata({ params, searchParams }: Parametri): Promise<Metadata> {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).pagina);
  const lingua = await linguaPagina();
  const s = await leggiSezione(slug, lingua);
  if (!s) return { title: lingua === "it" ? "Sezione non trovata" : "Section not found", robots: { index: false, follow: false } };
  const elenco = await leggiArticoli(slug, lingua, pagina);
  const vuota = (elenco?.totale ?? 0) === 0 && s.tipo !== "carte" && s.tipo !== "stese" && s.figli.length === 0;
  const base = s.seo_titolo || BLOG.sezioneTitolo(lingua, s.nome);
  const titolo = pagina > 1 ? `${base} — ${lingua === "it" ? "pagina" : "page"} ${pagina}` : base;
  const descrizione = s.seo_descrizione || s.descrizione || BLOG.sezioneDescrizione(lingua, s.nome);
  const url = urlPubblico(lingua, `/blog/sezione/${s.slug}`);
  const lingue = alternative(lingua, { en: `/blog/sezione/${s.slug}`, it: `/blog/sezione/${s.slug}` });
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    robots: vuota ? { index: false, follow: true } : undefined,
    alternates: {
      ...lingue,
      canonical: pagina > 1 ? `${url}?pagina=${pagina}` : url,
      ...(pagina > 1 ? { languages: undefined } : {}),
    },
    ...anteprima(lingua, { titolo, descrizione, url }),
  };
}

export default async function PaginaSezione({ params, searchParams }: Parametri) {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).pagina);
  const lingua = await linguaPagina();
  const sezione = await leggiSezione(slug, lingua);
  if (!sezione) notFound();
  const [elenco, albero, etichette] = await Promise.all([
    leggiArticoli(slug, lingua, pagina),
    leggiDalServer<NodoSezione[]>("/blog/sections"),
    leggiDalServer<EtichettaConConteggio[]>("/blog/tags"),
  ]);
  const url = urlPubblico(lingua, `/blog/sezione/${sezione.slug}`);
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: BLOG.h1(lingua), url: urlPubblico(lingua, "/blog") },
      ...sezione.briciole.map((b) => ({ nome: b.nome, url: urlPubblico(lingua, `/blog/sezione/${b.slug}`) })),
    ]),
    {
      "@type": "CollectionPage",
      name: sezione.nome,
      description: sezione.seo_descrizione || sezione.descrizione || undefined,
      url,
      inLanguage: lingua === "it" ? "it-IT" : "en",
      isPartOf: { "@id": `${SITE_URL}/#website` },
    },
  );
  return (
    <>
      <JsonLd dati={dati} />
      <VistaSezione
        sezione={sezione}
        articoli={elenco?.articoli ?? []}
        pagina={pagina}
        pagine={elenco?.pagine ?? 1}
        albero={albero ?? []}
        etichette={etichette ?? []}
      />
    </>
  );
}
