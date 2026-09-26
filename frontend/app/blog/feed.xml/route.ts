/* Il feed RSS del blog: gli ultimi trenta articoli pubblicati. Si scrive a ogni richiesta (l'elenco
 * cambia e in fase di build l'API non c'è). Il testo di ogni voce è l'estratto, non l'articolo intero:
 * chi vuole leggere viene sul sito. */

import { urlMedia, type ArticoloBreve, type ElencoArticoli } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";

const esci = (s: string) =>
  s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;" })[c] as string);

function voce(a: ArticoloBreve): string {
  const url = `${SITE_URL}/blog/${a.slug}`;
  const immagine = urlMedia(a.immagine?.url);
  return [
    "<item>",
    `<title>${esci(a.titolo)}</title>`,
    `<link>${esci(url)}</link>`,
    `<guid isPermaLink="true">${esci(url)}</guid>`,
    a.pubblicato_il ? `<pubDate>${new Date(a.pubblicato_il).toUTCString()}</pubDate>` : "",
    `<dc:creator>${esci(a.autore.nome)}</dc:creator>`,
    ...(a.sezione ? [`<category>${esci(a.sezione.nome)}</category>`] : []),
    ...a.tags.map((t) => `<category>${esci(t.nome)}</category>`),
    `<description>${esci(a.sottotitolo ? `${a.sottotitolo} — ${a.estratto}` : a.estratto)}</description>`,
    ...(immagine ? [`<enclosure url="${esci(immagine)}" type="image/webp" length="0"/>`] : []),
    "</item>",
  ].join("");
}

export async function GET() {
  const elenco = await leggiDalServer<ElencoArticoli>("/blog/posts?per_pagina=30", { secondi: 60 });
  const articoli = elenco?.articoli ?? [];
  const ultimo = articoli.find((a) => a.pubblicato_il)?.pubblicato_il;
  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom"><channel>',
    "<title>T·AI·rots — il blog dei tarocchi</title>",
    `<link>${SITE_URL}/blog</link>`,
    `<atom:link href="${SITE_URL}/blog/feed.xml" rel="self" type="application/rss+xml"/>`,
    "<description>Guide, approfondimenti e riflessioni sui tarocchi.</description>",
    "<language>it</language>",
    ultimo ? `<lastBuildDate>${new Date(ultimo).toUTCString()}</lastBuildDate>` : "",
    ...articoli.map(voce),
    "</channel></rss>",
  ].join("");
  return new Response(xml, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8", "Cache-Control": "public, max-age=300" },
  });
}
