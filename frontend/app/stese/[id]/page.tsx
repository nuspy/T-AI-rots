/* Una stesa, pubblica: lo schema con le posizioni numerate, il significato di ciascuna,
 * come si legge. Il server scrive tutto (titolo, descrizione, contenuto): è la pagina
 * che risponde a «come si legge la croce celtica». */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { Stesa } from "@/lib/api";
import type { ArticoloBreve } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";
import { SchedaStesa } from "./scheda";

async function leggiStesa(id: string) {
  return leggiDalServer<Stesa>(`/spreads/${encodeURIComponent(id)}`);
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const s = await leggiStesa(id);
  if (!s) return { title: "Stesa non trovata", robots: { index: false, follow: false } };
  const titolo = `${s.nome}: significato delle posizioni`;
  const descrizione = s.descrizione;
  const url = `${SITE_URL}/stese/${s.id}`;
  return {
    title: titolo,
    description: descrizione,
    alternates: { canonical: url },
    openGraph: { type: "article", siteName: "T·AI·rots", title: titolo, description: descrizione, url },
    twitter: { card: "summary", title: titolo, description: descrizione },
  };
}

export default async function PaginaStesa({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const s = await leggiStesa(id);
  if (!s) notFound();
  const stessaCategoria = (await leggiDalServer<Stesa[]>(`/spreads?categoria=${s.categoria}`)) ?? [];
  const articoli = (await leggiDalServer<ArticoloBreve[]>(`/blog/links/stesa/${encodeURIComponent(s.id)}`)) ?? [];
  return <SchedaStesa stesa={s} altre={stessaCategoria.filter((x) => x.id !== s.id)} articoli={articoli} />;
}
