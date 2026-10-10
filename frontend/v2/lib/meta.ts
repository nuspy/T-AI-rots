/* I metadati delle pagine della v2 (dalla v8.5 il sito), scritti dal server nella lingua dell'indirizzo: inglese alla
 * radice, italiano sotto `/it`. Canonical e `hreflang` fra le due versioni, anteprima per i social, e `noindex` per le
 * pagine personali (lettura, storia, profilo, carrello, condivise). */

import type { Metadata } from "next";
import { indicizzabile, type LinguaPubblica } from "@/lib/indirizzi";
import { linguaPagina } from "@/lib/lingua-server";
import { alternative, anteprima, soloInglese, titoloPagina, urlPubblico } from "@/lib/seo";
import { dizionarioPronto, type Dizionario } from "@/v2/i18n";

export async function testiServer(): Promise<Dizionario> {
  return dizionarioPronto(await linguaPagina())!;
}

export const NOINDEX: Metadata["robots"] = { index: false, follow: false, googleBot: { index: false, follow: false } };

/**
 * Titolo, descrizione, canonical e anteprima di una pagina. `interno` è l'indirizzo interno (`/cards`, `/daily-card`):
 * se la pagina esiste uguale nelle due lingue basta quello; se lo slug cambia con la lingua si passa `interni`.
 * `assoluto`: il titolo porta già il marchio (la home), senza il modello del layout.
 * `soloEn`: il contenuto è sempre in inglese, qualunque sia la lingua dell'indirizzo (termini di servizio,
 * informativa privacy, 10/10/2026): niente `hreflang` e in italiano il canonical va all'inglese (`soloInglese`).
 */
export async function metaV2(
  titolo: string,
  descrizione: string,
  interno: string,
  { assoluto = false, interni, immagine, tipo, soloEn = false }: {
    assoluto?: boolean;
    interni?: Partial<Record<LinguaPubblica, string>>;
    immagine?: { url: string; width?: number; height?: number; alt?: string };
    tipo?: "website" | "article";
    soloEn?: boolean;
  } = {},
): Promise<Metadata> {
  const lingua = await linguaPagina();
  const pagine = interni ?? { en: interno, it: interno };
  const pubblica = indicizzabile(interno);
  return {
    title: assoluto ? { absolute: titolo } : titoloPagina(titolo),
    description: descrizione,
    alternates: !pubblica ? { canonical: urlPubblico(lingua, interno) }
      : soloEn ? soloInglese(lingua, interno) : alternative(lingua, pagine),
    ...(pubblica ? {} : { robots: NOINDEX }),
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, pagine[lingua] ?? interno), tipo, immagine }),
  };
}
