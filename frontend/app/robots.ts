/* Cosa possono leggere i motori di ricerca. Le pagine dell'account e delle letture sono
 * personali: fuori. Le pagine condivise (`/s/`) sono `noindex` già dall'intestazione. */

import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/condivisione";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/leggi", "/letture", "/profilo", "/piano", "/s/", "/admin"] },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
