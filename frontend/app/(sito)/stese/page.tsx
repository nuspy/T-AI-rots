/* Le stese, pubbliche: gli schemi con cui si dispongono le carte, senza account.
 * Il server scrive già l'elenco (chi cerca «Celtic Cross spread» non aspetta JavaScript). */

import type { Metadata } from "next";
import type { Stesa } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, elenco, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { STESE } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "../componenti/json-ld";
import { ElencoStese } from "./elenco";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  const titolo = STESE.title(lingua);
  const descrizione = STESE.description(lingua);
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    alternates: alternative(lingua, { en: "/stese", it: "/stese" }),
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, "/stese") }),
  };
}

export default async function PaginaStese() {
  const lingua = await linguaPagina();
  const stese = (await leggiDalServer<Stesa[]>(`/spreads?lang=${lingua}`)) ?? [];
  const url = urlPubblico(lingua, "/stese");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: STESE.h1(lingua), url }]),
    elenco(stese.map((s) => ({ nome: s.nome, url: urlPubblico(lingua, `/stese/${s.slug ?? s.id}`) }))),
  );
  return (
    <>
      <JsonLd dati={dati} />
      <ElencoStese stese={stese} lingua={lingua} />
    </>
  );
}
