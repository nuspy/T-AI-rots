/* Una carta, pubblica: attribuzioni e significati. Il server scrive titolo, descrizione, dati strutturati e
 * contenuto: è la porta d'ingresso di chi cerca «The Star tarot card meaning».
 *
 * L'indirizzo canonico usa lo slug nella lingua (`/cards/the-star`, `/it/carte/la-stella`); l'id (`maj-17`) e lo slug
 * dell'altra lingua funzionano ancora e portano lì con un reindirizzamento permanente. */

import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import type { Carta } from "@/lib/api";
import type { ArticoloBreve } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { indirizzo } from "@/lib/percorsi";
import { alternative, anteprima, briciole, domande, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { CARTA, CARTE, seoCarta } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "../../componenti/json-ld";
import { SchedaCarta } from "./scheda";

async function leggiCarta(id: string, lingua: string) {
  return leggiDalServer<Carta>(`/cards/${encodeURIComponent(id)}?lang=${lingua}`);
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const lingua = await linguaPagina();
  const c = await leggiCarta(id, lingua);
  if (!c) return { title: lingua === "it" ? "Carta non trovata" : "Card not found", robots: { index: false, follow: false } };
  const s = seoCarta(c);
  const titolo = CARTA.title(lingua, s);
  const descrizione = CARTA.description(lingua, s);
  const interni = { en: `/carte/${c.slugs?.en ?? c.id}`, it: `/carte/${c.slugs?.it ?? c.id}` };
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    alternates: alternative(lingua, interni),
    ...anteprima(lingua, {
      titolo, descrizione, url: urlPubblico(lingua, interni[lingua]), tipo: "article",
      immagine: { url: `${SITE_URL}/cards/${c.id}.webp`, width: 360, height: 640, alt: c.nome ?? c.nome_it },
    }),
  };
}

export default async function PaginaCarta({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const lingua = await linguaPagina();
  const c = await leggiCarta(id, lingua);
  if (!c) notFound();
  if (c.slug && id !== c.slug) permanentRedirect(indirizzo(lingua, `/carte/${c.slug}`));

  const [articoli, tutte] = await Promise.all([
    leggiDalServer<ArticoloBreve[]>(`/blog/links/carta/${encodeURIComponent(c.id)}`),
    leggiDalServer<Carta[]>(`/cards?lang=${lingua}`),
  ]);
  const elenco = tutte ?? [];
  const posizione = elenco.findIndex((x) => x.id === c.id);
  const vicina = (x: Carta | undefined) => (x?.slug ? { slug: x.slug, nome: x.nome ?? x.nome_it } : null);

  const s = seoCarta(c);
  const url = urlPubblico(lingua, `/carte/${c.slug ?? c.id}`);
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: CARTE.h1(lingua), url: urlPubblico(lingua, "/carte") },
      { nome: c.nome ?? c.nome_it, url },
    ]),
    {
      "@type": "Article",
      headline: CARTA.h1(lingua, s),
      description: CARTA.description(lingua, s),
      image: `${SITE_URL}/cards/${c.id}.webp`,
      inLanguage: lingua === "it" ? "it-IT" : "en",
      author: { "@type": "Organization", name: NOME_MARCHIO },
      publisher: { "@id": `${SITE_URL}/#organization` },
      mainEntityOfPage: url,
      about: { "@type": "Thing", name: c.nome ?? c.nome_it },
    },
    ...(CARTA.domande(lingua, s).length ? [domande(CARTA.domande(lingua, s))] : []),
  );

  return (
    <>
      <JsonLd dati={dati} />
      <SchedaCarta
        carta={c}
        articoli={articoli ?? []}
        lingua={lingua}
        precedente={posizione > 0 ? vicina(elenco[posizione - 1]) : null}
        successiva={posizione >= 0 ? vicina(elenco[posizione + 1]) : null}
      />
    </>
  );
}
