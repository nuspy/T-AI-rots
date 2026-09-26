/* I marchi dei canali di condivisione, in SVG: nessuna libreria di icone, nessuna
 * richiesta di rete, e i colori dei marchi (Instagram, Facebook, TikTok, X) come
 * li riconosce chi li usa ogni giorno. Sono decorativi (`aria-hidden`): il pulsante
 * che li contiene porta il nome del canale. */

import type { CanaleCondivisione } from "@/lib/api";

type Canale = Exclude<CanaleCondivisione, "nativo">;

/* Il fondo del pulsante e il colore del marchio. */
export const FONDO_CANALE: Record<Canale, string> = {
  instagram: "linear-gradient(45deg, #f9a13a 0%, #ee2a7b 45%, #6228d7 100%)",
  facebook: "#1877f2",
  tiktok: "#010101",
  x: "#010101",
  email: "#4f5d75",
  link: "linear-gradient(135deg, #8f6c24, #d8b45a)",
};

export function Logo({ canale }: { canale: Canale }) {
  const comune = { width: 28, height: 28, viewBox: "0 0 24 24", "aria-hidden": true, focusable: false } as const;
  switch (canale) {
    case "instagram":
      return (
        <svg {...comune} fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round">
          <rect x="3" y="3" width="18" height="18" rx="5.2" />
          <circle cx="12" cy="12" r="4.1" />
          <circle cx="17.4" cy="6.6" r="1.1" fill="#fff" stroke="none" />
        </svg>
      );
    case "facebook":
      return (
        <svg {...comune} fill="#fff">
          <path d="M13.6 22v-8.2h2.8l.5-3.4h-3.3V8.3c0-1 .4-1.7 1.8-1.7H17V3.5c-.3 0-1.3-.2-2.4-.2-2.6 0-4.3 1.6-4.3 4.4v2.7H7.4v3.4h2.9V22z" />
        </svg>
      );
    case "tiktok":
      return (
        <svg {...comune} fill="#fff">
          <path d="M16.6 2h-3.3v13.4a2.9 2.9 0 1 1-2.9-2.9c.3 0 .6 0 .9.1V9.2a6.2 6.2 0 1 0 5.3 6.2V8.7a7.8 7.8 0 0 0 4.4 1.4V6.8a4.5 4.5 0 0 1-4.4-4.8z" />
        </svg>
      );
    case "x":
      return (
        <svg {...comune} fill="#fff">
          <path d="M18.9 1.15h3.68l-8.04 9.19L24 22.85h-7.4l-5.8-7.58-6.64 7.58H.47l8.6-9.83L0 1.15h7.6l5.24 6.93zm-1.29 19.5h2.04L6.49 3.24H4.3z" />
        </svg>
      );
    case "email":
      return (
        <svg {...comune} fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="5" width="18" height="14" rx="2.4" />
          <path d="M3.6 7.4 12 13.4l8.4-6" />
        </svg>
      );
    case "link":
      return (
        <svg {...comune} fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
      );
  }
}
