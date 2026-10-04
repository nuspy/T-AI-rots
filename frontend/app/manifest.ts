/* Il manifest del sito (v9, Fase 5): `/manifest.webmanifest`.
 *
 * Serve soprattutto a iPhone e iPad: Safari su iOS (dalla 16.4) riceve le notifiche Web Push **solo** dal sito
 * aggiunto alla schermata Home («Condividi» → «Aggiungi alla schermata Home»), che si apre poi come un'app a sé
 * (`display: standalone`). Senza manifest quell'icona aprirebbe una scheda di Safari, e il permesso alle notifiche
 * non si potrebbe nemmeno chiedere. Il profilo («Notifiche») lo spiega a chi usa Safari su iOS.
 *
 * Nessuna promessa di funzionare offline: il service worker (`public/sw.js`) fa solo le notifiche. */

import type { MetadataRoute } from "next";
import { NOME_MARCHIO } from "@/lib/marchio";

export default function manifest(): MetadataRoute.Manifest {
  return {
    id: "/",
    name: NOME_MARCHIO,
    short_name: NOME_MARCHIO,
    description: "A living Tarot ritual with guided interpretation and a reader who remembers your story.",
    start_url: "/",
    scope: "/",
    display: "standalone",
    background_color: "#f6f1e7",
    theme_color: "#201026",
    icons: [
      { src: "/icon.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/apple-icon.png", sizes: "180x180", type: "image/png" },
    ],
  };
}
