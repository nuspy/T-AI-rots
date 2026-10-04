/* `/.well-known/assetlinks.json`: le app Android che possono aprire i collegamenti di questo sito (Android App Links).
 * Il contenuto lo scrive l'API dalla console (App mobili → Android: package e impronte dei certificati di firma);
 * vedi `lib/collegamenti-app.ts`. */

import { fileCollegamenti } from "@/lib/collegamenti-app";

export const dynamic = "force-dynamic";

export function GET() {
  return fileCollegamenti("assetlinks.json");
}
