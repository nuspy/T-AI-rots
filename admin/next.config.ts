import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Sotto un percorso dello stesso dominio (`/admin` in produzione, dove il
   * DNS ha un solo nome). Vale alla build e finisce nel JavaScript del browser:
   * per cambiarlo si ricostruisce. Vuoto: la console sta alla radice. */
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || undefined,
  /* `standalone`: la build porta con sé soltanto i moduli che usa davvero, e
   * l'immagine di produzione non deve installare node_modules da capo. */
  output: "standalone",
  /* In sviluppo, le prove dal cellulare sulla rete di casa: Next accetta le richieste delle sue risorse solo dalle
   * origini elencate. Senza effetto sulla build di produzione. */
  allowedDevOrigins: ["192.168.*.*", "10.*.*.*", "100.*.*.*"],
};

export default nextConfig;
