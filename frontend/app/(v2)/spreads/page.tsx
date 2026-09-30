/* Le stese, pubbliche: il server scrive l'elenco, i dati strutturati e i metadati. */

import type { Metadata } from "next";
import type { Stesa } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { briciole, elenco, grafo, urlPubblico } from "@/lib/seo";
import { STESE } from "@/lib/seo-testi";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { ElencoStese } from "@/v2/pagine/stese";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  return metaV2(STESE.title(lingua), STESE.description(lingua), "/spreads");
}

export default async function PaginaStese() {
  const lingua = await linguaPagina();
  const valori = await precarica([P.stese(lingua)]);
  const stese = (valori[P.stese(lingua)] as Stesa[] | undefined) ?? [];
  const url = urlPubblico(lingua, "/spreads");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: STESE.h1(lingua), url }]),
    elenco(stese.map((s) => ({ nome: s.nome, url: urlPubblico(lingua, `/spreads/${s.slug ?? s.id}`) }))),
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <Sottotitolo sezione="stese" compatto />
        <ElencoStese />
      </Pagina>
    </DatiIniziali>
  );
}
