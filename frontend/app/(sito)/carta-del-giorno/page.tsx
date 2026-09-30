/* La carta del giorno, pubblica: la carta di oggi per tutti, scritta dal server e con un contenuto nuovo ogni giorno.
 * È la porta d'ingresso di chi cerca «tarot card of the day». */

import type { Metadata } from "next";
import type { CartaOggi } from "@/lib/api";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { alternative, anteprima, briciole, grafo, titoloPagina, urlPubblico } from "@/lib/seo";
import { GIORNO } from "@/lib/seo-testi";
import { leggiDalServer } from "@/lib/server-api";
import { JsonLd } from "../componenti/json-ld";
import { PaginaGiorno } from "./giorno";

export async function generateMetadata(): Promise<Metadata> {
  const lingua = await linguaPagina();
  const titolo = GIORNO.title(lingua);
  const descrizione = GIORNO.description(lingua);
  return {
    title: titoloPagina(titolo),
    description: descrizione,
    alternates: alternative(lingua, { en: "/carta-del-giorno", it: "/carta-del-giorno" }),
    ...anteprima(lingua, { titolo, descrizione, url: urlPubblico(lingua, "/carta-del-giorno") }),
  };
}

export default async function Pagina() {
  const lingua = await linguaPagina();
  /* Un minuto di memoria basta: la carta cambia una volta al giorno. */
  const oggi = await leggiDalServer<CartaOggi>(`/daily-card/today?lang=${lingua}`, { secondi: 60 });
  const url = urlPubblico(lingua, "/carta-del-giorno");
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
    <>
      <JsonLd dati={dati} />
      <PaginaGiorno oggi={oggi} lingua={lingua} />
    </>
  );
}
