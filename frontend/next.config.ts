import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* `standalone`: la build porta con sé soltanto i moduli che usa davvero, e
   * l'immagine di produzione non deve installare node_modules da capo. */
  output: "standalone",
  /* In sviluppo, le prove dal cellulare sulla rete di casa (`tools/run_local.py --rete <IP>`): Next accetta le
   * richieste delle sue risorse solo dalle origini elencate. Senza effetto sulla build di produzione. */
  allowedDevOrigins: ["192.168.*.*", "10.*.*.*", "100.*.*.*"],
  experimental: {
    /* Due siti nella stessa app, ciascuno col proprio layout radice (`app/(sito)` e `app/(v2)`): il 404 degli
     * indirizzi sconosciuti non può passare da un layout comune e sta in `app/global-not-found.tsx`. */
    globalNotFound: true,
  },
};

export default nextConfig;
