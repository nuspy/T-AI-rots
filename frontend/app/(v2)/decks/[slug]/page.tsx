/* Un mazzo: nome, descrizione e prezzi dal server. Il `Product` porta le offerte solo dei formati che hanno un prezzo
 * (nessun prezzo inventato). */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { Mazzo } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { breve, briciole, grafo, urlPubblico } from "@/lib/seo";
import { MAZZO } from "@/lib/seo-testi";
import { Pagina } from "@/v2/componenti/pagina";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { NOINDEX, metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { SchedaMazzo } from "@/v2/pagine/mazzi";

async function leggi(slug: string, lingua: string) {
  const valori = await precarica([P.mazzi(lingua)]);
  const mazzo = ((valori[P.mazzi(lingua)] as Mazzo[] | undefined) ?? []).find((m) => m.slug === slug) ?? null;
  return { valori, mazzo };
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const lingua = await linguaPagina();
  const { mazzo } = await leggi(slug, lingua);
  if (!mazzo) return { title: MAZZO.title(lingua), robots: NOINDEX };
  return metaV2(`${mazzo.nome} — ${lingua === "it" ? "mazzo di tarocchi" : "tarot deck"}`,
    breve(mazzo.descrizione || MAZZO.description(lingua)), `/decks/${mazzo.slug}`);
}

export default async function PaginaMazzo({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const lingua = await linguaPagina();
  const { valori, mazzo } = await leggi(slug, lingua);
  if (!mazzo) notFound();
  const url = urlPubblico(lingua, `/decks/${mazzo.slug}`);
  const valuta = mazzo.valuta.toUpperCase();
  const offerta = (nome: string, centesimi: number | null | undefined) =>
    centesimi == null ? [] : [{ "@type": "Offer", name: nome, price: (centesimi / 100).toFixed(2), priceCurrency: valuta, url }];
  const offerte = [
    ...offerta("PDF", mazzo.prezzo_stampa_scontato ?? mazzo.prezzo_stampa),
    ...offerta(lingua === "it" ? "Mazzo fisico" : "Physical deck", mazzo.prezzo_fisico_scontato ?? mazzo.prezzo_fisico),
  ];
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: MAZZO.title(lingua), url: urlPubblico(lingua, "/decks") },
      { nome: mazzo.nome, url },
    ]),
    offerte.length
      ? {
          "@type": "Product",
          name: mazzo.nome,
          description: mazzo.descrizione ?? undefined,
          url,
          brand: { "@type": "Brand", name: NOME_MARCHIO },
          category: lingua === "it" ? "Mazzi di tarocchi" : "Tarot decks",
          offers: offerte,
        }
      : {
          // Senza prezzo niente "Product": Google richiede offers/review/aggregateRating
          // e non vogliamo inventare un'offerta.
          "@type": "CreativeWork",
          name: mazzo.nome,
          description: mazzo.descrizione ?? undefined,
          url,
        },
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <SchedaMazzo slug={slug} />
      </Pagina>
    </DatiIniziali>
  );
}
