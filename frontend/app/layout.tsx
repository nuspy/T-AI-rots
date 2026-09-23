import type { Metadata, Viewport } from "next";
import { Cinzel, Cormorant_Garamond, IBM_Plex_Sans } from "next/font/google";
import { Providers } from "./providers";
import { Cosmo } from "./componenti/cosmo";
import "./globals.css";

/* Tre voci tipografiche: Cinzel per i titoli, lapidaria come un'iscrizione;
 * Cormorant per la voce dell'oracolo; IBM Plex Sans per l'interfaccia, che
 * deve restare leggibile anche quando tutto il resto è atmosfera. */
const titoli = Cinzel({ subsets: ["latin"], variable: "--font-titoli", weight: ["400", "600", "700"] });
const oracolo = Cormorant_Garamond({
  subsets: ["latin"],
  variable: "--font-oracolo",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});
const interfaccia = IBM_Plex_Sans({ subsets: ["latin"], variable: "--font-ui", weight: ["400", "500", "600"] });

export const metadata: Metadata = {
  title: { default: "T·AI·rots — Tarocchi di Thoth con l'AI", template: "%s · T·AI·rots" },
  description:
    "Letture dei tarocchi di Thoth guidate da un'intelligenza artificiale: intervista, stese tradizionali, carte rivelate una a una e un responso coerente con la dottrina esoterica.",
  openGraph: { type: "website", siteName: "T·AI·rots" },
};

export const viewport: Viewport = {
  themeColor: "#07050f",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it" className={`${titoli.variable} ${oracolo.variable} ${interfaccia.variable}`}>
      <body>
        <Cosmo />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
