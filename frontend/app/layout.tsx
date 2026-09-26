import type { Metadata, Viewport } from "next";
import { Cinzel, Cormorant_Garamond, IBM_Plex_Sans } from "next/font/google";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { IMMAGINE_PREDEFINITA } from "@/lib/seo";
import { Providers } from "./providers";
import { Cosmo } from "./componenti/cosmo";
import "./globals.css";

/* Tre voci tipografiche: Cinzel per i titoli, lapidaria come un'iscrizione;
 * Cormorant per la voce dell'oracolo; IBM Plex Sans per l'interfaccia, che
 * deve restare leggibile anche quando tutto il resto è atmosfera. */
/* `latin-ext` per ő, ű, ł, ș, ă…: senza, l'ungherese, il polacco e il rumeno
 * ripiegherebbero sul carattere di sistema a metà parola. Il cirillico (russo,
 * ucraino) c'è in Cormorant e in IBM Plex, non in Cinzel: nei titoli ripiega
 * sul serif di sistema. Cinese, hindi, coreano e arabo usano il carattere di
 * sistema (vedi `globals.css`). */
const titoli = Cinzel({ subsets: ["latin", "latin-ext"], variable: "--font-titoli", weight: ["400", "600", "700"] });
const oracolo = Cormorant_Garamond({
  subsets: ["latin", "latin-ext", "cyrillic"],
  variable: "--font-oracolo",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});
const interfaccia = IBM_Plex_Sans({ subsets: ["latin", "latin-ext", "cyrillic"], variable: "--font-ui", weight: ["400", "500", "600"] });

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  applicationName: NOME_MARCHIO,
  title: { default: `${NOME_MARCHIO}: Thoth tarot readings, guided by AI`, template: `%s | ${NOME_MARCHIO}` },
  description:
    "Online tarot reading with the Thoth Tarot and AI: a short interview, cards revealed one by one, and an interpretation rooted in Golden Dawn tradition.",
  authors: [{ name: NOME_MARCHIO, url: SITE_URL }],
  creator: NOME_MARCHIO,
  publisher: NOME_MARCHIO,
  category: "spirituality",
  formatDetection: { telephone: false, email: false, address: false },
  /* Tutto si indicizza di norma; le pagine private (`/leggi`, `/letture`, `/profilo`, `/s/…`) lo escludono da sé. */
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1, "max-video-preview": -1 },
  },
  openGraph: { type: "website", siteName: NOME_MARCHIO, images: [IMMAGINE_PREDEFINITA] },
  twitter: { card: "summary_large_image", images: [IMMAGINE_PREDEFINITA.url] },
};

export const viewport: Viewport = {
  themeColor: "#07050f",
  colorScheme: "dark",
};

/* `<html lang>` e la lingua di partenza dell'interfaccia vengono dall'indirizzo (`/it/…` è italiano, il resto
 * è inglese), letta dal proxy: così l'HTML scritto dal server è già nella lingua giusta. */
export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const lingua = await linguaPagina();
  return (
    <html lang={lingua} className={`${titoli.variable} ${oracolo.variable} ${interfaccia.variable}`}>
      <body>
        <Cosmo />
        <Providers linguaIniziale={lingua}>{children}</Providers>
      </body>
    </html>
  );
}
