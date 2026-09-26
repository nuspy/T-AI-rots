/* Un articolo del blog. Il server scrive tutto — titolo, descrizione, testo, dati strutturati —: è ciò
 * che leggono i motori di ricerca e le anteprime dei social. */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { Carta, Stesa } from "@/lib/api";
import type { ArticoloBlog } from "@/lib/blog";
import { urlMedia } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";
import type { Riferimenti } from "../componenti/blog-markdown";
import { VistaArticolo } from "./vista-articolo";

async function leggiArticolo(slug: string) {
  return leggiDalServer<ArticoloBlog>(`/blog/posts/${encodeURIComponent(slug)}`, { secondi: 10 });
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const a = await leggiArticolo(slug);
  if (!a) return { title: "Articolo non trovato", robots: { index: false, follow: false } };
  const titolo = a.seo_titolo || a.titolo;
  const immagine = urlMedia(a.immagine?.url);
  const url = `${SITE_URL}/blog/${a.slug}`;
  return {
    title: titolo,
    description: a.seo_descrizione,
    alternates: { canonical: url },
    authors: [{ name: a.autore.nome }],
    openGraph: {
      type: "article", siteName: "T·AI·rots", title: titolo, description: a.seo_descrizione, url,
      publishedTime: a.pubblicato_il ?? undefined, modifiedTime: a.aggiornato_il ?? undefined,
      images: immagine ? [{ url: immagine, width: a.immagine?.larghezza ?? undefined, height: a.immagine?.altezza ?? undefined, alt: a.immagine?.alt }] : undefined,
    },
    twitter: { card: immagine ? "summary_large_image" : "summary", title: titolo, description: a.seo_descrizione, images: immagine ? [immagine] : undefined },
  };
}

export default async function PaginaArticolo({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const a = await leggiArticolo(slug);
  if (!a) notFound();
  /* I nomi delle carte e delle stese per le scorciatoie del testo: nella lingua dell'articolo. */
  const [carte, stese] = await Promise.all([
    leggiDalServer<Carta[]>("/cards", { secondi: 300 }),
    leggiDalServer<Stesa[]>("/spreads", { secondi: 300 }),
  ]);
  const inItaliano = a.lang.startsWith("it");
  const riferimenti: Riferimenti = {
    carte: Object.fromEntries((carte ?? []).map((c) => [c.id, inItaliano ? c.nome_it : (c.nomi?.[a.lang.slice(0, 2)] ?? c.nomi?.en ?? c.nome_it)])),
    stese: Object.fromEntries((stese ?? []).map((s) => [s.id, inItaliano ? s.nome : (s.nomi?.[a.lang.slice(0, 2)] ?? s.nome_en ?? s.nome)])),
    articoli: Object.fromEntries(a.collegamenti.articoli.map((x) => [x.slug, x.titolo])),
  };
  return <VistaArticolo articolo={a} riferimenti={riferimenti} />;
}
