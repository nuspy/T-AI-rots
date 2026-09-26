/* Una lettura condivisa: la porta d'ingresso di chi riceve il link.
 *
 * Questa parte gira sul server e ha un solo compito: scrivere nell'`<head>` le
 * anteprime (Open Graph e Twitter Card) che Facebook, X, WhatsApp, Telegram e gli
 * altri leggono senza eseguire JavaScript — perciò il testo e l'immagine devono
 * stare qui e non nella pagina che disegna il browser (`condivisa.tsx`).
 *
 * L'immagine dell'anteprima è quella composta dal browser di chi ha condiviso,
 * ridotta dal server a un WebP 400×300 molto compresso (`GET /shared/{token}/image.webp`). Le letture condivise non
 * si indicizzano: una domanda può essere intima, e il link va a chi lo riceve. */

import type { Metadata } from "next";
import type { LetturaCondivisa } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { sintesiDelResponso } from "@/lib/sintesi";
import { PaginaCondivisa } from "./condivisa";

/* Il server dell'app parla con l'API dall'interno (`API_INTERNAL_URL`, per esempio
 * il servizio del cluster); i social invece leggono l'immagine dall'indirizzo
 * pubblico dell'API. */
const PUBBLICA = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";
const INTERNA = process.env.API_INTERNAL_URL ?? PUBBLICA;

const SENZA_ANTEPRIMA: Metadata = { title: "TAROTS chat", robots: { index: false, follow: false } };

async function leggi(token: string): Promise<LetturaCondivisa | null> {
  try {
    const r = await fetch(`${INTERNA}/shared/${encodeURIComponent(token)}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(4000),
    });
    return r.ok ? ((await r.json()) as LetturaCondivisa) : null;
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ token: string }> }): Promise<Metadata> {
  const { token } = await params;
  const l = await leggi(token);
  if (!l) return SENZA_ANTEPRIMA;

  const titolo = `«${l.question}»`;
  const descrizione = l.share_text || sintesiDelResponso(l.synthesis, 200) || "TAROTS chat";
  const url = `${SITE_URL}/s/${token}`;
  const immagine = l.immagine
    ? [{ url: `${PUBBLICA}/shared/${encodeURIComponent(token)}/image.webp`, width: 400, height: 300, alt: titolo }]
    : undefined;

  return {
    title: titolo,
    description: descrizione,
    robots: { index: false, follow: false },
    alternates: { canonical: url },
    openGraph: { type: "article", siteName: "TAROTS chat", title: titolo, description: descrizione, url, images: immagine },
    twitter: {
      card: immagine ? "summary_large_image" : "summary",
      title: titolo,
      description: descrizione,
      images: immagine?.map((i) => i.url),
    },
  };
}

export default async function Pagina({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  return <PaginaCondivisa token={token} />;
}
