/* La carta del giorno, pubblica (`/card-of-the-day`, `/it/carta-del-giorno`): la carta di oggi per tutti, scritta dal
 * server. È la porta d'ingresso di chi cerca «tarot card of the day». */

import type { Metadata } from "next";
import type { CartaOggi } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { JsonLd } from "@/lib/json-ld";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { briciole, grafo, urlPubblico } from "@/lib/seo";
import { GIORNO } from "@/lib/seo-testi";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { Giorno } from "@/v2/pagine/giorno";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  return metaV2(GIORNO.title(lingua), GIORNO.description(lingua), "/daily-card");
}

export default async function PaginaGiorno() {
  const lingua = await linguaPagina();
  /* Un minuto di memoria basta: la carta cambia una volta al giorno. */
  const valori = await precarica([P.oggi(lingua), P.nove()], 60);
  const oggi = valori[P.oggi(lingua)] as CartaOggi | undefined;
  const url = urlPubblico(lingua, "/daily-card");
  const dati = grafo(
    briciole([{ nome: NOME_MARCHIO, url: SITE_URL }, { nome: GIORNO.h1(lingua), url }]),
    {
      "@type": "WebPage",
      name: GIORNO.title(lingua),
      description: GIORNO.description(lingua),
      url,
      inLanguage: lingua === "it" ? "it-IT" : "en",
      ...(oggi ? { dateModified: oggi.giorno, image: `${SITE_URL}/cards/${oggi.carta.id}.webp` } : {}),
    },
  );
  return (
    <DatiIniziali valori={valori}>
      <JsonLd dati={dati} />
      <Pagina>
        <Sottotitolo sezione="giorno" compatto />
        <Giorno />
      </Pagina>
    </DatiIniziali>
  );
}
