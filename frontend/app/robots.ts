/* Cosa possono leggere i motori di ricerca (e i crawler delle intelligenze artificiali che fanno da motori di
 * risposta). Le pagine dell'account e delle letture sono personali: fuori. Le pagine condivise (`/s/`) sono
 * `noindex` già dall'intestazione. Restano fuori anche le ricerche del blog (`?q=`) e il parametro di ritorno del
 * pagamento (`?ritorno=`): sono infinite e non aggiungono nulla. Il vecchio `/piano` non c'è fra i divieti: risponde
 * con un reindirizzamento permanente, e chi lo segue deve poterlo vedere. */

import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/condivisione";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      /* La v2 (`/v2`, `/it/v2`) è un'anteprima non indicizzata: fuori, finché non si decide se sostituisce il sito. */
      disallow: ["/leggi", "/letture", "/profilo", "/s/", "/admin", "/v2", "/it/v2", "/*?q=", "/*?ritorno="],
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
