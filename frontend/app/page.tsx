/* La soglia: la pagina d'ingresso. Il server scrive il titolo, i dati strutturati e, sotto la parte animata,
 * il testo che dice che cosa si fa qui (come funziona una lettura, perché il Tarocco di Thoth, le domande più
 * frequenti) con i collegamenti a carte, stese e articoli: è ciò che un motore di ricerca legge e con cui capisce
 * di che cosa parla il sito. */

import type { Metadata } from "next";
import type { Carta, Stesa } from "@/lib/api";
import type { ElencoArticoli } from "@/lib/blog";
import { linguaPagina } from "@/lib/lingua-server";
import { alternative, anteprima, applicazione, domande, grafo, organizzazione, sito, urlPubblico } from "@/lib/seo";
import { HOME } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "./componenti/json-ld";
import { SezioniSeo } from "./componenti/seo-home";
import { Soglia } from "./soglia";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  const titolo = HOME.titleCompleto(lingua);
  const descrizione = HOME.description(lingua);
  return {
    /* Assoluto: il titolo della soglia porta già il marchio, senza il modello del layout. */
    title: { absolute: titolo },
    description: descrizione,
    alternates: alternative(lingua, { en: "/", it: "/" }),
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, "/") }),
  };
}

export default async function Pagina() {
  const lingua = await linguaPagina();
  const [carte, stese, articoli] = await Promise.all([
    leggiDalServer<Carta[]>(`/cards?lang=${lingua}`),
    leggiDalServer<Stesa[]>(`/spreads?categoria=standard&lang=${lingua}`),
    leggiDalServer<ElencoArticoli>(`/blog/posts?per_pagina=3&lang=${lingua}`),
  ]);
  const dati = grafo(
    organizzazione(),
    sito(lingua),
    applicazione(lingua, HOME.description(lingua)),
    domande(HOME.domande(lingua)),
  );
  return (
    <>
      <JsonLd dati={dati} />
      <Soglia />
      <SezioniSeo lingua={lingua} carte={carte ?? []} stese={stese ?? []} articoli={articoli?.articoli ?? []} />
    </>
  );
}
