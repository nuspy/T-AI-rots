import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* `standalone`: la build porta con sé soltanto i moduli che usa davvero, e
   * l'immagine di produzione non deve installare node_modules da capo. */
  output: "standalone",
  /* Il sito v2 (`public/v2/`) è HTML statico: senza queste righe solo `/v2/…/index.html` esplicito
   * risponde, e `/v2` o `/v2/read` danno 404. `fallback` scatta solo quando nessun file statico
   * corrisponde, quindi `app.js`, `styles.css` e gli `index.html` espliciti si servono come prima. */
  async rewrites() {
    return {
      beforeFiles: [],
      afterFiles: [],
      fallback: [
        { source: "/v2", destination: "/v2/index.html" },
        { source: "/v2/:path*", destination: "/v2/:path*/index.html" },
      ],
    };
  },
};

export default nextConfig;
