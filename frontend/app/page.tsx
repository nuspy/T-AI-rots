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
import { BannerInterpreta } from "./componenti/banner-interpreta";
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

/** Sei articoli a caso, non i più recenti: un piccolo generatore con seme, ripetibile finché non cambia il seme
 *  (il giorno di oggi, UTC), così la scelta resta la stessa per tutta la giornata invece di cambiare a ogni
 *  richiesta — un motore di ricerca che passa due volte nello stesso giorno vede la stessa pagina. */
function seiACaso<T>(elenco: T[], seme: string): T[] {
  const N = 6;
  if (elenco.length <= N) return elenco;
  let h = 1779033703 ^ seme.length;
  for (let i = 0; i < seme.length; i++) {
    h = Math.imul(h ^ seme.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  const scelti = [...elenco];
  for (let i = scelti.length - 1; i > 0; i--) {
    h = Math.imul(h ^ (h >>> 15), 1 | h);
    h = (h + Math.imul(h ^ (h >>> 7), 61 | h)) ^ h;
    const j = ((h >>> 0) % (i + 1) + (i + 1)) % (i + 1);
    [scelti[i], scelti[j]] = [scelti[j], scelti[i]];
  }
  return scelti.slice(0, N);
}

export default async function Pagina() {
  const lingua = await linguaPagina();
  const [carte, stese, articoli] = await Promise.all([
    leggiDalServer<Carta[]>(`/cards?lang=${lingua}`),
    leggiDalServer<Stesa[]>(`/spreads?categoria=standard&lang=${lingua}`),
    leggiDalServer<ElencoArticoli>(`/blog/posts?per_pagina=24&lang=${lingua}`),
  ]);
  const oggi = new Date().toISOString().slice(0, 10);
  const articoliCasuali = seiACaso(articoli?.articoli ?? [], oggi);
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
      <BannerInterpreta />
      <SezioniSeo lingua={lingua} carte={carte ?? []} stese={stese ?? []} articoli={articoliCasuali} />
    </>
  );
}
