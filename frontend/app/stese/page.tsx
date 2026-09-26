/* Le stese, pubbliche: gli schemi con cui si dispongono le carte, senza account.
 * Il server scrive già l'elenco (chi cerca «croce celtica» non aspetta JavaScript). */

import type { Metadata } from "next";
import type { Stesa } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { leggiDalServer } from "@/lib/server-api";
import { ElencoStese } from "./elenco";

export const metadata: Metadata = {
  title: "Le stese dei tarocchi: croce celtica, ruota astrologica, compatibilità e coppia",
  description:
    "Gli schemi con cui si dispongono i tarocchi, con il significato di ogni posizione: le stese classiche e quelle per la compatibilità con un partner e per la relazione di coppia.",
  alternates: { canonical: `${SITE_URL}/stese` },
};

export default async function PaginaStese() {
  const stese = (await leggiDalServer<Stesa[]>("/spreads")) ?? [];
  return <ElencoStese stese={stese} />;
}
