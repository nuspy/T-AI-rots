/* Prezzi e pacchetti (`/pricing`, `/it/piano`): pubblica, anche senza account. Il server legge i piani e li scrive,
 * con i dati strutturati (`Product`/`Offer`). Il ritorno dal pagamento (`?checkout=…`, `?dopo=…`, `?ritorno=…`) è una
 * pagina di servizio: non si indicizza. */

import type { Metadata } from "next";
import type { Piano } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { briciole, grafo, urlPubblico } from "@/lib/seo";
import { PREZZI } from "@/lib/seo-testi";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { NOINDEX, metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { Prezzi } from "@/v2/pagine/prezzi";

type Parametri = { searchParams: Promise<Record<string, string | string[] | undefined>> };

const ritornoDalPagamento = (p: Record<string, unknown>) => Boolean(p.checkout || p.dopo || p.ritorno);

export async function generateMetadata({ searchParams }: Parametri): Promise<Metadata> {
  const lingua = await linguaPagina();
  const m = await metaV2(PREZZI.title(lingua), PREZZI.description(lingua), "/pricing");
  return ritornoDalPagamento(await searchParams) ? { ...m, robots: NOINDEX } : m;
}

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

export default async function PaginaPrezzi() {
  const lingua = await linguaPagina();
  const valori = await precarica([P.piani(lingua), P.impostazioni()]);
  const piani = (valori[P.piani(lingua)] as Piano[] | undefined) ?? [];
  const url = urlPubblico(lingua, "/pricing");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: PREZZI.title(lingua), url }]),
    ...piani.map((p) => ({
      "@type": "Product",
      name: `${NOME_MARCHIO}: ${p.nome}`,
      description: p.descrizione ?? undefined,
      brand: { "@type": "Brand", name: NOME_MARCHIO },
      category: lingua === "it" ? "Letture dei tarocchi" : "Tarot readings",
      offers: offerta(p, url),
    })),
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <Sottotitolo sezione="prezzi" compatto />
        <Prezzi />
      </Pagina>
    </DatiIniziali>
  );
}
