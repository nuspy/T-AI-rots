"use client";

import NextLink from "next/link";
import type { ComponentProps } from "react";
import { useLingua } from "@/v2/lib/lingua";
import { indirizzoV2 } from "@/v2/lib/percorsi";

/* Il collegamento della v2: come `next/link`, ma conserva il prefisso `/it` quando la pagina è stata aperta in
 * italiano da indirizzo. */
export default function LinkV2({ href, ...resto }: ComponentProps<typeof NextLink>) {
  const { prefissoIt } = useLingua();
  const destinazione = typeof href === "string" ? indirizzoV2(href, prefissoIt) : href;
  return <NextLink href={destinazione} {...resto} />;
}
