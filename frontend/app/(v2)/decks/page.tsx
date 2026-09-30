/* I mazzi (`/decks`, dove porta anche il vecchio `/deck`): il server scrive l'elenco e i dati strutturati. */

import type { Metadata } from "next";
import type { Mazzo } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { briciole, elenco, grafo, urlPubblico } from "@/lib/seo";
import { MAZZO } from "@/lib/seo-testi";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { Mazzi } from "@/v2/pagine/mazzi";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  return metaV2(MAZZO.title(lingua), MAZZO.description(lingua), "/decks", {
    immagine: { url: `${SITE_URL}/cards/maj-17.webp`, width: 360, height: 640, alt: "The Star" },
  });
}

export default async function PaginaMazzi() {
  const lingua = await linguaPagina();
  const valori = await precarica([P.mazzi(lingua)]);
  const mazzi = (valori[P.mazzi(lingua)] as Mazzo[] | undefined) ?? [];
  const url = urlPubblico(lingua, "/decks");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: MAZZO.title(lingua), url }]),
    elenco(mazzi.map((m) => ({ nome: m.nome, url: urlPubblico(lingua, `/decks/${m.slug}`) }))),
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <Sottotitolo sezione="mazzi" compatto />
        <Mazzi />
      </Pagina>
    </DatiIniziali>
  );
}
