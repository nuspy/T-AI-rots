/* Le 78 carte, pubbliche. Il server scrive l'elenco, i dati strutturati e i metadati. */

import type { Metadata } from "next";
import type { Carta } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { briciole, elenco, grafo, urlPubblico } from "@/lib/seo";
import { CARTE } from "@/lib/seo-testi";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { Biblioteca } from "@/v2/pagine/carte";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  return metaV2(CARTE.title(lingua), CARTE.description(lingua), "/cards");
}

export default async function PaginaCarte() {
  const lingua = await linguaPagina();
  const valori = await precarica([P.carte(lingua)]);
  const carte = (valori[P.carte(lingua)] as Carta[] | undefined) ?? [];
  const url = urlPubblico(lingua, "/cards");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: CARTE.h1(lingua), url }]),
    elenco(carte.map((c) => ({
      nome: c.nome ?? c.nome_it,
      url: urlPubblico(lingua, `/cards/${c.slug ?? c.id}`),
      immagine: `${SITE_URL}/cards/${c.id}.webp`,
    }))),
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <Sottotitolo sezione="carte" compatto />
        <Biblioteca />
      </Pagina>
    </DatiIniziali>
  );
}
