/* I metadati delle pagine della v2, scritti dal server nella lingua dell'indirizzo (inglese, o italiano sotto
 * `/it/v2`). Anteprima non indicizzata: niente canonical verso il sito, niente hreflang. */

import type { Metadata } from "next";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { dizionarioPronto, type Dizionario } from "@/v2/i18n";

export async function testiServer(): Promise<Dizionario> {
  return dizionarioPronto(await linguaPagina())!;
}

export function metaV2(titolo: string, descrizione: string, percorso: string, assoluto = false): Metadata {
  return {
    title: assoluto ? { absolute: titolo } : titolo,
    description: descrizione,
    alternates: { canonical: `${SITE_URL}${percorso}` },
    openGraph: {
      type: "website",
      title: titolo,
      description: descrizione,
      url: `${SITE_URL}${percorso}`,
      images: [{ url: `${SITE_URL}/og/tarots-chat.png`, width: 1200, height: 630 }],
    },
  };
}
