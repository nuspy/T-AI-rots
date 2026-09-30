/* Il 404 per gli indirizzi che non corrispondono a nessuna pagina.
 *
 * Con due siti nella stessa app (il sito in `app/(sito)` e la v2 in `app/(v2)`, ciascuno col proprio layout
 * radice) non c'è un layout comune da cui comporre il 404: questo file lo sostituisce, e per questo dichiara da
 * sé `<html>`, font e stile. È la stessa pagina «non trovata» del sito. Gli indirizzi sotto `/v2` sconosciuti non
 * arrivano qui: li raccoglie la v2 (`app/(v2)/v2/[...resto]`) col proprio vestito. */

import type { Metadata } from "next";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { Cosmo } from "./(sito)/componenti/cosmo";
import { classiFont } from "./(sito)/fonts";
import NonTrovata from "./(sito)/not-found";
import { Providers } from "./(sito)/providers";
import "./(sito)/globals.css";

export const metadata: Metadata = {
  title: `404 | ${NOME_MARCHIO}`,
};

export default async function GlobalNotFound() {
  const lingua = await linguaPagina();
  return (
    <html lang={lingua} className={classiFont}>
      <body>
        <Cosmo />
        <Providers linguaIniziale={lingua}>
          <NonTrovata />
        </Providers>
      </body>
    </html>
  );
}
