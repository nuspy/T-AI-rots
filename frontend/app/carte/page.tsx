/* Le 78 carte, pubbliche. Il server scrive già l'elenco. */

import type { Metadata } from "next";
import type { Carta } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";
import { ElencoCarte } from "./elenco";

export const metadata: Metadata = {
  title: "Le 78 carte del Tarocco di Thoth: significati e attribuzioni",
  description:
    "Arcani maggiori e minori del Tarocco di Thoth di Aleister Crowley, con le attribuzioni (lettera ebraica, elemento, astrologia) e i significati dritti e rovesciati.",
  alternates: { canonical: `${SITE_URL}/carte` },
};

export default async function PaginaCarte() {
  const carte = (await leggiDalServer<Carta[]>("/cards")) ?? [];
  return <ElencoCarte carte={carte} />;
}
