import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Esplora } from "@/v2/pagine/blog";
import { linguaPagina } from "@/lib/lingua-server";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { precarica } from "@/v2/lib/precarica";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.blog.esplora_meta_titolo, t.blog.esplora_meta_descrizione, "/explore");
}

export default async function PaginaEsplora() {
  const lingua = await linguaPagina();
  const valori = await precarica([P.articoli(lingua, { per_pagina: 3 })]);
  return (
    <DatiIniziali valori={valori}>
    <Pagina>
      <Esplora />
    </Pagina>
    </DatiIniziali>
  );
}
