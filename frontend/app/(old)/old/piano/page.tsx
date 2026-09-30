/* Prezzi e pacchetti (il «negozio» delle letture). Pagina pubblica e indicizzabile: il server legge i piani e li scrive
 * nell'HTML, con i dati strutturati (`Product`/`Offer`) che i motori di ricerca mostrano come prezzo.
 *
 * Il ritorno dal pagamento (`?checkout=…`, `?dopo=…`, `?ritorno=…`) è una pagina di servizio, non un contenuto: non si
 * indicizza. */

import type { Metadata } from "next";
import type { Piano } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { PREZZI } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "@/lib/json-ld";
import { PaginaPiano } from "./piano";

type Parametri = { searchParams: Promise<Record<string, string | string[] | undefined>> };

const ritornoDalPagamento = (p: Record<string, unknown>) => Boolean(p.checkout || p.dopo || p.ritorno);

export async function generateMetadata({ searchParams }: Parametri): Promise<Metadata> {
  const lingua = await linguaPagina();
  const titolo = PREZZI.title(lingua);
  const descrizione = PREZZI.description(lingua);
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    alternates: alternative(lingua, { en: "/piano", it: "/piano" }),
    ...(ritornoDalPagamento(await searchParams) ? { robots: { index: false, follow: false } } : {}),
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, "/piano") }),
  };
}

/* Un piano come offerta: importi in euro (arrivano in centesimi). Il gratuito ha prezzo 0. */
function offerta(p: Piano, url: string) {
  const importo = (centesimi: number) => (centesimi / 100).toFixed(2);
  const abbonamento = p.tipo === "abbonamento" && p.prezzo_mensile > 0;
  return {
    "@type": "Offer",
    name: p.nome,
    price: importo(p.prezzo_mensile),
    priceCurrency: p.valuta.toUpperCase(),
    availability: "https://schema.org/InStock",
    url,
    ...(abbonamento
      ? { priceSpecification: { "@type": "UnitPriceSpecification", price: importo(p.prezzo_mensile), priceCurrency: p.valuta.toUpperCase(), billingDuration: 1, unitCode: "MON" } }
      : {}),
  };
}

export default async function Pagina() {
  const lingua = await linguaPagina();
  const piani = await leggiDalServer<Piano[]>("/plans", { secondi: 60 });
  const url = urlPubblico(lingua, "/piano");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: PREZZI.title(lingua), url }]),
    ...(piani ?? []).map((p) => ({
      "@type": "Product",
      name: `${NOME_MARCHIO}: ${p.nome}`,
      description: p.descrizione ?? undefined,
      brand: { "@type": "Brand", name: NOME_MARCHIO },
      category: lingua === "it" ? "Letture dei tarocchi" : "Tarot readings",
      offers: offerta(p, url),
    })),
  );
  return (
    <>
      <JsonLd dati={dati} />
      <PaginaPiano pianiIniziali={piani} />
    </>
  );
}
