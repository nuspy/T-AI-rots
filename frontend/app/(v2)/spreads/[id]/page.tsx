/* Una stesa, pubblica: lo schema, le posizioni, come si legge. Le posizioni diventano un `HowTo` per i motori di
 * ricerca. L'indirizzo canonico usa lo slug nella lingua (`/spreads/celtic-cross`, `/it/stese/croce-celtica`). */

import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import type { Stesa } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { pubblico } from "@/lib/indirizzi";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { briciole, comeSiFa, domande, grafo, urlPubblico } from "@/lib/seo";
import { STESA, STESE, seoStesa } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { Pagina } from "@/v2/componenti/pagina";
import { P, numeroPagina, perPagina } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { NOINDEX, metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { SchedaStesa } from "@/v2/pagine/stese";

const leggiStesa = (id: string, lingua: string) => leggiDalServer<Stesa>(P.stesa(id, lingua), { obbligatorio: true });

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const lingua = await linguaPagina();
  const s = await leggiStesa(id, lingua);
  if (!s) return { title: lingua === "it" ? "Stesa non trovata" : "Spread not found", robots: NOINDEX };
  const seo = seoStesa(s, s.nome);
  return metaV2(STESA.title(lingua, seo), STESA.description(lingua, seo), `/spreads/${s.slug ?? s.id}`, {
    interni: { en: `/spreads/${s.slugs?.en ?? s.id}`, it: `/spreads/${s.slugs?.it ?? s.id}` },
    tipo: "article",
  });
}

export default async function PaginaStesa({ params, searchParams }: {
  params: Promise<{ id: string }>; searchParams: Promise<{ page?: string; per?: string }>;
}) {
  const { id } = await params;
  const sp = await searchParams;
  const lingua = await linguaPagina();
  const s = await leggiStesa(id, lingua);
  if (!s) notFound();
  if (s.slug && id !== s.slug) permanentRedirect(pubblico(lingua, `/spreads/${s.slug}`));

  // In fondo, l'elenco completo degli articoli su questa stesa (v9.4, `ArticoliSu`), con la sua paginazione.
  const valori = await precarica([
    P.stese(lingua), P.nove({ stesa: s.id }), P.elencoSu("stesa", s.id, numeroPagina(sp.page), perPagina(sp.per)),
  ]);
  const seo = seoStesa(s, s.nome);
  const url = urlPubblico(lingua, `/spreads/${s.slug ?? s.id}`);
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: STESE.h1(lingua), url: urlPubblico(lingua, "/spreads") },
      { nome: s.nome, url },
    ]),
    comeSiFa({
      nome: lingua === "it" ? `Come si legge la stesa ${s.nome}` : `How to read the ${s.nome} tarot spread`,
      descrizione: s.descrizione,
      url,
      lingua,
      passi: s.posizioni.map((p) => ({ nome: p.nome, testo: p.significato })),
    }),
    domande(STESA.domande(lingua, seo)),
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <SchedaStesa id={id} />
      </Pagina>
    </DatiIniziali>
  );
}
