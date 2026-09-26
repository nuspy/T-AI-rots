/* Il mazzo di TAROTS chat: la pagina di anteprima del prodotto (in preparazione).
 * Il server scrive titolo, descrizione e le carte in vetrina. */

import type { Metadata } from "next";
import type { Carta } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";
import { PaginaMazzo } from "./mazzo";

export const metadata: Metadata = {
  title: "Il mazzo di TAROTS chat: 78 carte con la grafica originale",
  description:
    "Il Tarocco di Thoth con la grafica originale di TAROTS chat: 78 carte illustrate, un dorso dorato e il cofanetto da collezione. In preparazione.",
  alternates: { canonical: `${SITE_URL}/mazzo` },
  openGraph: {
    type: "website",
    siteName: "TAROTS chat",
    title: "Il mazzo di TAROTS chat",
    description: "78 carte illustrate, un dorso dorato, il cofanetto da collezione.",
    url: `${SITE_URL}/mazzo`,
    images: [{ url: `${SITE_URL}/cards/maj-17.webp`, width: 360, height: 640, alt: "La Stella" }],
  },
};

/* Le carte in vetrina: il Matto, il Mago, la Sacerdotessa, la Lussuria, la Stella, il Sole. */
const VETRINA = ["maj-00", "maj-01", "maj-02", "maj-11", "maj-17", "maj-19"];

export default async function Pagina() {
  const tutte = (await leggiDalServer<Carta[]>("/cards")) ?? [];
  const carte = VETRINA.map((id) => tutte.find((c) => c.id === id)).filter((c): c is Carta => !!c);
  return <PaginaMazzo carte={carte} />;
}
