"use client";

import NextLink from "next/link";
import type { ComponentProps } from "react";
import { useLingua } from "@/lib/lingua";
import { indirizzo } from "@/lib/percorsi";

/* Il collegamento del sito: come `next/link`, ma sceglie l'indirizzo nella lingua.
 *
 * Nel codice si scrivono gli indirizzi con i nomi delle cartelle (`/carte/maj-17`, `/piano`); qui diventano
 * `/cards/maj-17` in inglese e `/it/carte/maj-17` in italiano (`lib/percorsi.ts`). Gli indirizzi che non sono
 * pubblici, esterni o interni alla pagina (`/leggi`, `https://…`, `#…`) passano invariati. Sul server la lingua
 * è già quella dell'indirizzo, quindi l'HTML esce con i collegamenti giusti. */
export default function Link({ href, ...resto }: ComponentProps<typeof NextLink>) {
  const { lingua } = useLingua();
  const testo = typeof href === "string" ? indirizzo(lingua, href) : href;
  return <NextLink href={testo} {...resto} />;
}
