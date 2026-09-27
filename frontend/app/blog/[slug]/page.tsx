/* Un articolo del blog. Il server scrive tutto — titolo, descrizione, testo, dati strutturati —: è ciò
 * che leggono i motori di ricerca e le anteprime dei social.
 *
 * Ogni articolo ha una lingua e vive nell'indirizzo di quella lingua: `/blog/x` è inglese, `/it/blog/x` è italiano.
 * Chi apre l'altro indirizzo viene portato lì con un reindirizzamento permanente (una sola pagina per articolo,
 * niente contenuto doppio). `noindex` e `canonical_url`, se l'autore li ha impostati, si rispettano. */

import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import type { ArticoloBlog } from "@/lib/blog";
import { urlMedia } from "@/lib/blog";
import { linguaPagina } from "@/lib/lingua-server";
import { indirizzo, linguaPubblica, type LinguaPubblica } from "@/lib/percorsi";
import { alternative, anteprima, titoloPagina, urlPubblico } from "@/lib/seo";
import { leggiDalServer } from "@/lib/server-api";
import type { Riferimenti } from "../componenti/blog-markdown";
import { VistaArticolo } from "./vista-articolo";

async function leggiArticolo(slug: string) {
  return leggiDalServer<ArticoloBlog>(`/blog/posts/${encodeURIComponent(slug)}`, { secondi: 10 });
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const a = await leggiArticolo(slug);
  const lingua = await linguaPagina();
  if (!a) return { title: lingua === "it" ? "Articolo non trovato" : "Article not found", robots: { index: false, follow: false } };
  const la = linguaPubblica(a.lang);
  const titolo = a.seo_titolo || a.titolo;
  const immagine = urlMedia(a.immagine?.url);
  const url = urlPubblico(la, `/blog/${a.slug}`);
  const social = anteprima(la, {
    titolo, descrizione: a.seo_descrizione, url, tipo: "article",
    immagine: immagine ? { url: immagine, width: a.immagine?.larghezza ?? undefined, height: a.immagine?.altezza ?? undefined, alt: a.immagine?.alt } : undefined,
  });
  /* L'hreflang tra le due lingue esiste solo se una traduzione generata in console le ha collegate
   * (`gemella_lingua`): senza collegamento, solo il canonical, come sempre. Le lingue pubbliche sono
   * solo due (`LinguaPubblica`), quindi la gemella è per forza l'altra rispetto a `la`. */
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
  if (la !== lingua) permanentRedirect(indirizzo(la, `/blog/${a.slug}`));

  /* I nomi delle carte e delle stese citate, per ogni forma con cui il testo le nomina (id e slug in ogni lingua):
   * li manda il server dell'API nella lingua dell'articolo. */
  const forme = (id: string, slugs: Record<string, string>) => [id, ...Object.values(slugs)];
  const riferimenti: Riferimenti = {
    carte: Object.fromEntries(a.collegamenti.carte.flatMap((c) => forme(c.id, c.slugs).map((f) => [f, c.nome]))),
    stese: Object.fromEntries(a.collegamenti.stese.flatMap((s) => forme(s.id, s.slugs).map((f) => [f, s.nome]))),
    articoli: Object.fromEntries(a.collegamenti.articoli.map((x) => [x.slug, x.titolo])),
    idCarte: Object.fromEntries(a.collegamenti.carte.flatMap((c) => forme(c.id, c.slugs).map((f) => [f, c.id]))),
  };
  return <VistaArticolo articolo={a} riferimenti={riferimenti} lingua={la} />;
}
