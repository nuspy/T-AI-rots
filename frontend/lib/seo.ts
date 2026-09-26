/* Ciò che serve a ogni pagina pubblica per farsi trovare: indirizzi assoluti, lingue alternative, dati strutturati.
 *
 * Tutto in inglese per primo (`lingua`: `en` è la versione canonica), con l'italiano come alternativa collegata
 * da `hreflang`. Nessun testo qui: i testi stanno in `seo-testi.ts`. */

import type { Metadata } from "next";
import { SITE_URL } from "./condivisione";
import { NOME_MARCHIO } from "./marchio";
import { indirizzo, type LinguaPubblica } from "./percorsi";

/** L'immagine di anteprima di tutte le pagine che non ne hanno una loro (1200 × 630, generata da `tools/prepara_logo.py`). */
export const IMMAGINE_PREDEFINITA = {
  url: `${SITE_URL}/og/tarots-chat.png`,
  width: 1200,
  height: 630,
  alt: `${NOME_MARCHIO}: Thoth tarot readings, guided by AI`,
} as const;

/** L'indirizzo assoluto di una pagina interna, nella lingua: `urlPubblico("en", "/carte/the-star")` → `https://…/cards/the-star`. */
export const urlPubblico = (lingua: LinguaPubblica, interno: string): string => `${SITE_URL}${indirizzo(lingua, interno)}`;

/**
 * Canonical e lingue alternative di una pagina. `interni` porta l'indirizzo interno in ciascuna lingua in cui la
 * pagina esiste (gli slug possono cambiare: `/carte/the-star`, `/carte/la-stella`). La versione canonica è sempre
 * quella della lingua corrente; `x-default`, per chi non ha una lingua fra le due, è l'inglese.
 */
export function alternative(
  corrente: LinguaPubblica,
  interni: Partial<Record<LinguaPubblica, string>>,
): NonNullable<Metadata["alternates"]> {
  const url: Partial<Record<LinguaPubblica, string>> = {};
  for (const l of ["en", "it"] as const) {
    const i = interni[l];
    if (i) url[l] = urlPubblico(l, i);
  }
  const lingue: Record<string, string> = {};
  if (url.en) {
    lingue.en = url.en;
    lingue["x-default"] = url.en;
  }
  if (url.it) lingue.it = url.it;
  return { canonical: url[corrente] ?? url.en ?? url.it, languages: lingue };
}

/** Le informazioni di apertura per i social (Open Graph) e per X: un solo posto, per non dimenticarne pezzi. */
export function anteprima(
  lingua: LinguaPubblica,
  { titolo, descrizione, url, tipo = "website", immagine }: {
    titolo: string;
    descrizione: string;
    url: string;
    tipo?: "website" | "article";
    immagine?: { url: string; width?: number; height?: number; alt?: string };
  },
): Pick<Metadata, "openGraph" | "twitter"> {
  const img = immagine ?? IMMAGINE_PREDEFINITA;
  return {
    openGraph: {
      type: tipo, siteName: NOME_MARCHIO, title: titolo, description: descrizione, url,
      locale: lingua === "it" ? "it_IT" : "en_US",
      alternateLocale: lingua === "it" ? ["en_US"] : ["it_IT"],
      images: [img],
    },
    twitter: { card: "summary_large_image", title: titolo, description: descrizione, images: [img.url] },
  };
}

/**
 * Il titolo di una pagina: il marchio lo aggiunge il modello del layout («… | TAROTS chat»), ma un titolo che con
 * quell'aggiunta supera i 65 caratteri si taglierebbe nei risultati di ricerca, e allora si dà «assoluto», senza marchio.
 */
export function titoloPagina(titolo: string): NonNullable<Metadata["title"]> {
  return titolo.length + NOME_MARCHIO.length + 3 > 65 ? { absolute: titolo } : titolo;
}

/** Un testo troncato a fine parola, per le descrizioni (160 caratteri è il limite di una riga di risultato). */
export function breve(testo: string, massimo = 160): string {
  const pulito = testo.replace(/\s+/g, " ").trim();
  if (pulito.length <= massimo) return pulito;
  const taglio = pulito.slice(0, massimo);
  const spazio = taglio.lastIndexOf(" ");
  return `${taglio.slice(0, spazio > massimo * 0.6 ? spazio : massimo).trimEnd().replace(/[,;:.–-]+$/, "")}…`;
}

/* ---- dati strutturati (JSON-LD) ------------------------------------------------------------------------------- */

type Dati = Record<string, unknown>;

export const organizzazione = (): Dati => ({
  "@type": "Organization",
  "@id": `${SITE_URL}/#organization`,
  name: NOME_MARCHIO,
  url: SITE_URL,
  logo: { "@type": "ImageObject", url: `${SITE_URL}/marchio/logo-512.webp` },
});

export const sito = (lingua: LinguaPubblica): Dati => ({
  "@type": "WebSite",
  "@id": `${SITE_URL}/#website`,
  url: SITE_URL,
  name: NOME_MARCHIO,
  inLanguage: lingua === "it" ? "it-IT" : "en",
  publisher: { "@id": `${SITE_URL}/#organization` },
});

/** L'applicazione: quello che si fa qui (una lettura), per chi cerca «AI tarot reading». */
export const applicazione = (lingua: LinguaPubblica, descrizione: string): Dati => ({
  "@type": "WebApplication",
  name: NOME_MARCHIO,
  url: SITE_URL,
  description: descrizione,
  applicationCategory: "LifestyleApplication",
  operatingSystem: "Any",
  inLanguage: lingua === "it" ? "it-IT" : "en",
  publisher: { "@id": `${SITE_URL}/#organization` },
  offers: { "@type": "Offer", price: "0", priceCurrency: "EUR", description: lingua === "it" ? "La carta del giorno è gratuita" : "The card of the day is free" },
});

export const briciole = (voci: { nome: string; url: string }[]): Dati => ({
  "@type": "BreadcrumbList",
  itemListElement: voci.map((v, i) => ({ "@type": "ListItem", position: i + 1, name: v.nome, item: v.url })),
});

export const domande = (voci: { d: string; r: string }[]): Dati => ({
  "@type": "FAQPage",
  mainEntity: voci.map((v) => ({
    "@type": "Question",
    name: v.d,
    acceptedAnswer: { "@type": "Answer", text: v.r },
  })),
});

export const comeSiFa = (
  { nome, descrizione, url, passi, immagine, lingua }: {
    nome: string; descrizione: string; url: string; passi: { nome: string; testo: string }[]; immagine?: string;
    lingua: LinguaPubblica;
  },
): Dati => ({
  "@type": "HowTo",
  name: nome,
  description: descrizione,
  url,
  inLanguage: lingua === "it" ? "it-IT" : "en",
  ...(immagine ? { image: immagine } : {}),
  step: passi.map((p, i) => ({ "@type": "HowToStep", position: i + 1, name: p.nome, text: p.testo })),
});

export const elenco = (voci: { nome: string; url: string; immagine?: string }[]): Dati => ({
  "@type": "ItemList",
  numberOfItems: voci.length,
  itemListElement: voci.map((v, i) => ({
    "@type": "ListItem", position: i + 1, url: v.url, name: v.nome, ...(v.immagine ? { image: v.immagine } : {}),
  })),
});

/** Più oggetti in un solo `<script>`: il formato `@graph`. */
export const grafo = (...oggetti: Dati[]): Dati => ({ "@context": "https://schema.org", "@graph": oggetti });
