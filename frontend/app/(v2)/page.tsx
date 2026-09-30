/* La home: la pagina d'ingresso del sito. Il server scrive titolo, dati strutturati (organizzazione, sito,
 * applicazione, domande frequenti — le stesse che la pagina mostra) e il contenuto, coi dati già letti. */

import type { Metadata } from "next";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { applicazione, domande, grafo, organizzazione, sito } from "@/lib/seo";
import { HOME } from "@/lib/seo-testi";
import { Pagina } from "@/v2/componenti/pagina";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { Home } from "@/v2/pagine/home";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  return metaV2(HOME.titleCompleto(lingua), HOME.description(lingua), "/", { assoluto: true });
}

export default async function PaginaHome() {
  const lingua = await linguaPagina();
  const t = await testiServer();
  const valori = await precarica([P.impostazioni(), P.mazzi(lingua), P.articoli(lingua, { per_pagina: 3 })]);
  const dati = grafo(organizzazione(), sito(lingua), applicazione(lingua, HOME.description(lingua)), domande(t.home.faq));
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <Home />
      </Pagina>
    </DatiIniziali>
  );
}
