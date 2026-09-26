/* Il mazzo di TAROTS chat: la pagina di anteprima del prodotto (in preparazione).
 * Il server scrive titolo, descrizione, dati strutturati e le carte in vetrina.
 *
 * Il `Product` non porta un'offerta: il mazzo non è in vendita e non ha un prezzo, e non se ne inventa uno. Quando
 * ci sarà, qui si aggiunge `offers` con prezzo, valuta e disponibilità. */

import type { Metadata } from "next";
import type { Carta } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { MAZZO } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "../componenti/json-ld";
import { PaginaMazzo } from "./mazzo";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  const titolo = MAZZO.title(lingua);
  const descrizione = MAZZO.description(lingua);
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    alternates: alternative(lingua, { en: "/mazzo", it: "/mazzo" }),
    ...anteprima(lingua, {
      titolo, descrizione, url: urlPubblico(lingua, "/mazzo"),
      immagine: { url: `${SITE_URL}/cards/maj-17.webp`, width: 360, height: 640, alt: "The Star" },
    }),
  };
}

/* Le carte in vetrina: il Matto, il Mago, la Sacerdotessa, la Lussuria, la Stella, il Sole. */
const VETRINA = ["maj-00", "maj-01", "maj-02", "maj-11", "maj-17", "maj-19"];

export default async function Pagina() {
  const lingua = await linguaPagina();
  const tutte = (await leggiDalServer<Carta[]>(`/cards?lang=${lingua}`)) ?? [];
  const carte = VETRINA.map((id) => tutte.find((c) => c.id === id)).filter((c): c is Carta => !!c);
  const url = urlPubblico(lingua, "/mazzo");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: MAZZO.title(lingua), url }]),
    {
      "@type": "Product",
      name: MAZZO.title(lingua),
      description: MAZZO.description(lingua),
      url,
      image: carte.map((c) => `${SITE_URL}/cards/${c.id}.webp`),
      brand: { "@type": "Brand", name: NOME_MARCHIO },
      category: lingua === "it" ? "Mazzi di tarocchi" : "Tarot decks",
    },
  );
  return (
    <>
      <JsonLd dati={dati} />
      <PaginaMazzo carte={carte} />
    </>
  );
}
