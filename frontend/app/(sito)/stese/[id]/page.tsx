/* Una stesa, pubblica: lo schema con le posizioni numerate, il significato di ciascuna, come si legge. Il server
 * scrive tutto (titolo, descrizione, dati strutturati, contenuto): è la pagina che risponde a «how to read the
 * Celtic Cross». I passi delle posizioni diventano un `HowTo` per i motori di ricerca.
 *
 * L'indirizzo canonico usa lo slug nella lingua (`/spreads/celtic-cross`, `/it/stese/croce-celtica`). */

import type { Metadata } from "next";
import { notFound, permanentRedirect } from "next/navigation";
import type { Stesa } from "@/lib/api";
import type { ArticoloBreve } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { indirizzo } from "@/lib/percorsi";
import { alternative, anteprima, briciole, comeSiFa, domande, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { STESA, STESE, seoStesa } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "../../componenti/json-ld";
import { SchedaStesa } from "./scheda";

async function leggiStesa(id: string, lingua: string) {
  return leggiDalServer<Stesa>(`/spreads/${encodeURIComponent(id)}?lang=${lingua}`);
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const lingua = await linguaPagina();
  const s = await leggiStesa(id, lingua);
  if (!s) return { title: lingua === "it" ? "Stesa non trovata" : "Spread not found", robots: { index: false, follow: false } };
  const seo = seoStesa(s, s.nome);
  const titolo = STESA.title(lingua, seo);
  const descrizione = STESA.description(lingua, seo);
  const interni = { en: `/stese/${s.slugs?.en ?? s.id}`, it: `/stese/${s.slugs?.it ?? s.id}` };
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    alternates: alternative(lingua, interni),
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, interni[lingua]), tipo: "article" }),
  };
}

export default async function PaginaStesa({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const lingua = await linguaPagina();
  const s = await leggiStesa(id, lingua);
  if (!s) notFound();
  if (s.slug && id !== s.slug) permanentRedirect(indirizzo(lingua, `/stese/${s.slug}`));

  const [stessaCategoria, articoli] = await Promise.all([
    leggiDalServer<Stesa[]>(`/spreads?categoria=${s.categoria}&lang=${lingua}`),
    leggiDalServer<ArticoloBreve[]>(`/blog/links/stesa/${encodeURIComponent(s.id)}`),
  ]);

  const seo = seoStesa(s, s.nome);
  const url = urlPubblico(lingua, `/stese/${s.slug ?? s.id}`);
  const dati = grafo(
    briciole([
      { nome: NOME_MARCHIO, url: SITE_URL },
      { nome: STESE.h1(lingua), url: urlPubblico(lingua, "/stese") },
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
    <>
      <JsonLd dati={dati} />
      <SchedaStesa stesa={s} altre={(stessaCategoria ?? []).filter((x) => x.id !== s.id)} articoli={articoli ?? []} lingua={lingua} />
    </>
  );
}
