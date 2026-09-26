/* Le 78 carte, pubbliche. Il server scrive già l'elenco, i dati strutturati e i metadati. */

import type { Metadata } from "next";
import type { Carta } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, elenco, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { CARTE } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "../componenti/json-ld";
import { ElencoCarte } from "./elenco";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  const titolo = CARTE.title(lingua);
  const descrizione = CARTE.description(lingua);
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    alternates: alternative(lingua, { en: "/carte", it: "/carte" }),
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, "/carte") }),
  };
}

export default async function PaginaCarte() {
  const lingua = await linguaPagina();
  const carte = (await leggiDalServer<Carta[]>(`/cards?lang=${lingua}`)) ?? [];
  const url = urlPubblico(lingua, "/carte");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: CARTE.h1(lingua), url }]),
    elenco(carte.map((c) => ({
      nome: c.nome ?? c.nome_it,
      url: urlPubblico(lingua, `/carte/${c.slug ?? c.id}`),
      immagine: `${SITE_URL}/cards/${c.id}.webp`,
    }))),
  );
  return (
    <>
      <JsonLd dati={dati} />
      <ElencoCarte carte={carte} lingua={lingua} />
    </>
  );
}
