/* Una carta, pubblica: attribuzioni e significati. Il server scrive titolo, descrizione, dati strutturati e
 * contenuto: è la porta d'ingresso di chi cerca «The Star tarot card meaning».
 *
 * L'indirizzo canonico usa lo slug nella lingua (`/cards/the-star`, `/it/carte/la-stella`); l'id (`maj-17`) e lo slug
 * dell'altra lingua funzionano ancora e portano lì con un reindirizzamento permanente. */

import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import type { Carta } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { pubblico } from "@/lib/indirizzi";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { briciole, domande, grafo, urlPubblico } from "@/lib/seo";
import { CARTA, CARTE, seoCarta } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { Pagina } from "@/v2/componenti/pagina";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { NOINDEX, metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { SchedaCarta } from "@/v2/pagine/carte";

const leggiCarta = (id: string, lingua: string) => leggiDalServer<Carta>(P.carta(id, lingua), { obbligatorio: true });

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const lingua = await linguaPagina();
  const c = await leggiCarta(id, lingua);
  if (!c) return { title: lingua === "it" ? "Carta non trovata" : "Card not found", robots: NOINDEX };
  const s = seoCarta(c);
  return metaV2(CARTA.title(lingua, s), CARTA.description(lingua, s), `/cards/${c.slug ?? c.id}`, {
    interni: { en: `/cards/${c.slugs?.en ?? c.id}`, it: `/cards/${c.slugs?.it ?? c.id}` },
    tipo: "article",
    immagine: { url: `${SITE_URL}/cards/${c.id}.webp`, width: 360, height: 640, alt: c.nome ?? c.nome_it },
  });
}

export default async function PaginaCarta({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const lingua = await linguaPagina();
  const c = await leggiCarta(id, lingua);
  if (!c) notFound();
  if (c.slug && id !== c.slug) permanentRedirect(pubblico(lingua, `/cards/${c.slug}`));

  const valori = await precarica([P.carta(id, lingua), P.carte(lingua), P.nove({ carta: c.id })]);
  const s = seoCarta(c);
  const url = urlPubblico(lingua, `/cards/${c.slug ?? c.id}`);
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: CARTE.h1(lingua), url: urlPubblico(lingua, "/cards") },
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
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <SchedaCarta id={id} />
      </Pagina>
    </DatiIniziali>
  );
}
