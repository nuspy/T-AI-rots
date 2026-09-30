/* Una lettura condivisa nella v2. Il server scrive le anteprime per i social (Open Graph, Twitter Card): chi
 * condivide dalla v2 manda questo indirizzo, e l'anteprima deve esserci senza JavaScript. Non si indicizza. */

import type { Metadata } from "next";
import type { LetturaCondivisa } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { sintesiDelResponso } from "@/lib/sintesi";
import { Pagina } from "@/v2/componenti/pagina";
import { Condivisa } from "@/v2/pagine/condivisa";

const PUBBLICA = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";
const INTERNA = process.env.API_INTERNAL_URL ?? PUBBLICA;

async function leggi(token: string): Promise<LetturaCondivisa | null> {
  try {
    const r = await fetch(`${INTERNA}/shared/${encodeURIComponent(token)}`, { cache: "no-store", signal: AbortSignal.timeout(4000) });
    return r.ok ? ((await r.json()) as LetturaCondivisa) : null;
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ token: string }> }): Promise<Metadata> {
  const { token } = await params;
  const l = await leggi(token);
  if (!l) return { title: "TAROTS chat", robots: { index: false, follow: false } };
  const titolo = `«${l.question}»`;
  const descrizione = l.share_text || sintesiDelResponso(l.synthesis, 200) || "TAROTS chat";
  const url = `${SITE_URL}/v2/shared/${token}`;
  const immagine = l.immagine
    ? [{ url: `${PUBBLICA}/shared/${encodeURIComponent(token)}/image.webp`, width: 400, height: 300, alt: titolo }]
    : undefined;
  return {
    title: titolo,
    description: descrizione,
    robots: { index: false, follow: false },
    alternates: { canonical: url },
    openGraph: { type: "article", siteName: "TAROTS chat", title: titolo, description: descrizione, url, images: immagine },
    twitter: { card: immagine ? "summary_large_image" : "summary", title: titolo, description: descrizione, images: immagine?.map((i) => i.url) },
  };
}

export default async function PaginaCondivisa({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  return (
    <Pagina>
      <Condivisa token={token} />
    </Pagina>
  );
}
