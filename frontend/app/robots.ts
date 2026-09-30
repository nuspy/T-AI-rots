/* Cosa possono leggere i motori di ricerca (e i crawler delle intelligenze artificiali che fanno da motori di
 * risposta). Le pagine personali (lettura, storia, profilo, carrello, condivise) sono fuori; così la v1 sotto `/old`
 * (anche `noindex`), le ricerche del blog (`?q=`) e il ritorno del pagamento (`?ritorno=`). I vecchi indirizzi
 * (`/leggi`, `/s/…`, `/v2/…`) non sono fra i divieti: rispondono con un reindirizzamento permanente, e chi lo segue
 * deve poterlo vedere. */

import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/condivisione";

const PERSONALI = ["/read", "/my-story", "/profile", "/cart", "/shared/"];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: [...PERSONALI, ...PERSONALI.map((p) => `/it${p}`), "/old", "/admin", "/*?q=", "/*?ritorno="],
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
