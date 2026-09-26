/* Una carta, pubblica: attribuzioni e significati. Il server scrive titolo, descrizione e
 * contenuto: è la porta d'ingresso di chi cerca «significato del Tre di Spade». */

import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { Carta } from "@/lib/api";
import type { ArticoloBreve } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";
import { SchedaCarta } from "./scheda";

async function leggiCarta(id: string) {
  return leggiDalServer<Carta>(`/cards/${encodeURIComponent(id)}`);
}

/* Una descrizione di 160 caratteri circa, tagliata a fine parola. */
function breve(testo: string, massimo = 160): string {
  if (testo.length <= massimo) return testo;
  const taglio = testo.slice(0, massimo);
  return `${taglio.slice(0, Math.max(taglio.lastIndexOf(" "), massimo * 0.6)).trimEnd()}…`;
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const c = await leggiCarta(id);
  if (!c) return { title: "Carta non trovata", robots: { index: false, follow: false } };
  const titolo = `${c.nome_it}: significato nel Tarocco di Thoth`;
  const descrizione = breve(`${c.nome_thoth}${c.titolo_thoth ? ` — ${c.titolo_thoth}` : ""}. ${c.parole_chiave.join(", ")}. ${c.dritto ?? ""}`);
  const url = `${SITE_URL}/carte/${c.id}`;
  return {
    title: titolo,
    description: descrizione,
    alternates: { canonical: url },
    openGraph: {
      type: "article", siteName: "T·AI·rots", title: titolo, description: descrizione, url,
      images: [{ url: `${SITE_URL}/cards/${c.id}.webp`, width: 360, height: 640, alt: c.nome_it }],
    },
    twitter: { card: "summary", title: titolo, description: descrizione },
  };
}

export default async function PaginaCarta({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const c = await leggiCarta(id);
  if (!c) notFound();
  const articoli = (await leggiDalServer<ArticoloBreve[]>(`/blog/links/carta/${encodeURIComponent(c.id)}`)) ?? [];
  return <SchedaCarta carta={c} articoli={articoli} />;
}
