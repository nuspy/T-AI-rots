/* `/.well-known/apple-app-site-association` (senza estensione, come lo cerca Apple): l'app iOS che può aprire i
 * collegamenti di questo sito (Universal Links) e quali percorsi. Il contenuto lo scrive l'API dalla console (App mobili
 * → iOS: Team ID e bundle ID); vedi `lib/collegamenti-app.ts`. */

import { fileCollegamenti } from "@/lib/collegamenti-app";

export const dynamic = "force-dynamic";

export function GET() {
  return fileCollegamenti("apple-app-site-association");
}
