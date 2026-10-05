/* Un articolo del blog. Il server scrive titolo, descrizione, dati strutturati e testo. Ogni articolo vive
 * all'indirizzo della sua lingua (`/blog/x` inglese, `/it/blog/x` italiano): l'altro indirizzo porta lì con un
 * reindirizzamento permanente. `noindex` e `canonical_url` dell'autore si rispettano. */

import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import { urlMedia, type ArticoloBlog } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPubblica, pubblico, type LinguaPubblica } from "@/lib/indirizzi";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { BLOG } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { Pagina } from "@/v2/componenti/pagina";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { NOINDEX } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { ArticoloDiario } from "@/v2/pagine/blog";

const leggiArticolo = (slug: string) => leggiDalServer<ArticoloBlog>(P.articolo(slug), { secondi: 10, obbligatorio: true });

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const a = await leggiArticolo(slug);
  const lingua = await linguaPagina();
  if (!a) return { title: lingua === "it" ? "Articolo non trovato" : "Article not found", robots: NOINDEX };
  const la = linguaPubblica(a.lang);
  const titolo = a.seo_titolo || a.titolo;
  const immagine = urlMedia(a.immagine?.url);
  const url = urlPubblico(la, `/blog/${a.slug}`);
  const social = anteprima(la, {
    titolo, descrizione: a.seo_descrizione, url, tipo: "article",
    immagine: immagine ? { url: immagine, width: a.immagine?.larghezza ?? undefined, height: a.immagine?.altezza ?? undefined, alt: a.immagine?.alt } : undefined,
  });
  const altra: LinguaPubblica = la === "it" ? "en" : "it";
  const alternate = a.gemella_lingua && a.gemella_lingua.lang === altra
    ? alternative(la, { [la]: `/blog/${a.slug}`, [altra]: `/blog/${a.gemella_lingua.slug}` } as Record<LinguaPubblica, string>)
    : { canonical: a.canonical_url ?? url };
  return {
    title: titoloPagina(titolo),
    description: a.seo_descrizione,
    keywords: [a.seo_parola_chiave, ...a.parole_chiave, ...a.tags.map((t) => t.nome)].filter((k): k is string => !!k),
    alternates: a.canonical_url ? { canonical: a.canonical_url } : alternate,
    ...(a.noindex ? { robots: { index: false, follow: true } } : {}),
    authors: [{ name: a.autore.nome }],
    ...social,
    openGraph: {
      ...social.openGraph,
      type: "article",
      publishedTime: a.pubblicato_il ?? undefined,
      modifiedTime: a.aggiornato_il ?? undefined,
      section: a.sezione?.nome,
      tags: a.tags.map((t) => t.nome),
    },
  };
}

export default async function PaginaArticolo({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const a = await leggiArticolo(slug);
  if (!a) notFound();
  const lingua = await linguaPagina();
  const la = linguaPubblica(a.lang);
  if (la !== lingua || a.slug !== slug) permanentRedirect(pubblico(la, `/blog/${a.slug}`));

  // Le scelte nella lingua dell'articolo, per pertinenza (`DiarioNove` con `lang`, v9.4).
  const valori = await precarica([P.articolo(slug), P.nove({ articolo: slug, lang: a.lang })], 10);
  const url = urlPubblico(la, `/blog/${a.slug}`);
  const immagine = urlMedia(a.immagine?.url);
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: BLOG.h1(la), url: urlPubblico(la, "/blog") },
      ...(a.sezione ? [{ nome: a.sezione.nome, url: urlPubblico(la, `/blog/sezione/${a.sezione.slug}`) }] : []),
      { nome: a.titolo, url },
    ]),
    {
      "@type": "BlogPosting",
      headline: a.titolo,
      description: a.seo_descrizione,
      url,
      mainEntityOfPage: url,
      inLanguage: la === "it" ? "it-IT" : "en",
      ...(immagine ? { image: immagine } : {}),
      datePublished: a.pubblicato_il ?? undefined,
      dateModified: a.aggiornato_il ?? a.pubblicato_il ?? undefined,
      author: { "@type": "Person", name: a.autore.nome },
      publisher: { "@id": `${SITE_URL}/#organization` },
      keywords: [a.seo_parola_chiave, ...a.parole_chiave].filter(Boolean).join(", ") || undefined,
      ...(a.pubblicato_il ? { copyrightYear: Number(a.pubblicato_il.slice(0, 4)) } : {}),
      copyrightHolder: { "@id": `${SITE_URL}/#organization` },
    },
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <ArticoloDiario slug={slug} />
      </Pagina>
    </DatiIniziali>
  );
}
