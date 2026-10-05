/* Una sezione del blog (`/blog/sezione/…`, l'indirizzo già indicizzato). Le sezioni di articoli mostrano la stessa
 * lista in ogni lingua: niente hreflang, canonical all'inglese. Le sezioni «carte» e «stese» sono cataloghi tradotti
 * e tengono l'hreflang. Una sezione vuota non si indicizza. */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { DettaglioSezione, ElencoArticoli } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, grafo, soloInglese, titoloPagina, urlPubblico } from "@/lib/seo";
import { BLOG } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { Pagina } from "@/v2/componenti/pagina";
import { P, PER_PAGINA_BLOG } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { NOINDEX } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { SezioneDiario } from "@/v2/pagine/blog";

type Parametri = { params: Promise<{ slug: string }>; searchParams: Promise<{ page?: string }> };

const numeroPagina = (v?: string) => Math.max(1, Math.min(1000, parseInt(v ?? "1", 10) || 1));
const leggiSezione = (slug: string, lingua: string) => leggiDalServer<DettaglioSezione>(P.sezione(slug, lingua), { obbligatorio: true });
const percorsoArticoli = (slug: string, lingua: string, pagina: number) =>
  P.articoli(lingua, { sezione: slug, pagina, per_pagina: PER_PAGINA_BLOG });

export async function generateMetadata({ params, searchParams }: Parametri): Promise<Metadata> {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).page);
  const lingua = await linguaPagina();
  const s = await leggiSezione(slug, lingua);
  if (!s) return { title: lingua === "it" ? "Sezione non trovata" : "Section not found", robots: NOINDEX };
  const elenco = await leggiDalServer<ElencoArticoli>(percorsoArticoli(slug, lingua, pagina));
  // Vuota: niente articoli nel ramo e nessun catalogo (carte, stese) né nella sezione né sotto. Un contenitore di
  // sole sezioni vuote è vuoto anche lui; uno con i semi dentro no. (Senza `n_carte`/`n_stese`, API più vecchia,
  // una sezione con sotto-sezioni non si considera vuota.)
  const catalogo = s.tipo === "carte" || s.tipo === "stese" || (s.n_carte ?? 0) + (s.n_stese ?? 0) > 0
    || (s.n_carte === undefined && s.figli.length > 0);
  const vuota = (elenco?.totale ?? 0) === 0 && !catalogo;
  const base = s.seo_titolo || BLOG.sezioneTitolo(lingua, s.nome);
  const titolo = pagina > 1 ? `${base} — ${lingua === "it" ? "pagina" : "page"} ${pagina}` : base;
  const descrizione = s.seo_descrizione || s.descrizione || BLOG.sezioneDescrizione(lingua, s.nome);
  const interno = `/blog/sezione/${s.slug}`;
  const tradotta = s.tipo === "carte" || s.tipo === "stese";
  const lingue = tradotta ? alternative(lingua, { en: interno, it: interno }) : soloInglese(lingua, interno);
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    robots: vuota ? { index: false, follow: true } : undefined,
    alternates: {
      ...lingue,
      canonical: pagina > 1 ? `${lingue.canonical}?page=${pagina}` : lingue.canonical,
      ...(pagina > 1 ? { languages: undefined } : {}),
    },
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, interno) }),
  };
}

export default async function PaginaSezione({ params, searchParams }: Parametri) {
  const { slug } = await params;
  const pagina = numeroPagina((await searchParams).page);
  const lingua = await linguaPagina();
  const sezione = await leggiSezione(slug, lingua);
  if (!sezione) notFound();
  const valori = await precarica([
    P.sezione(slug, lingua), percorsoArticoli(slug, lingua, pagina), P.sezioni(), P.etichette(),
    pagina === 1 ? P.nove({ sezione: slug, recenti: PER_PAGINA_BLOG, scelti: 10, completa: false }) : null,
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
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <SezioneDiario slug={slug} />
      </Pagina>
    </DatiIniziali>
  );
}
