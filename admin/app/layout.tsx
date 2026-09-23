import type { Metadata, Viewport } from "next";
import { Cinzel, IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";
import { Providers } from "./providers";
import { Guscio } from "./guscio";
import "./globals.css";

/* Tre facce, ciascuna col suo compito.
 *
 * Cinzel porta l'identità — è il lapidario del prodotto — ma solo nei titoli
 * e nel marchio: in maiuscolo romano una tabella non si legge. Il corpo è
 * Plex Sans, perché qui si leggono etichette, nomi e importi. Plex Mono porta
 * i numeri e gli identificativi, che vanno allineati in colonna e copiati.
 *
 * Le variabili stanno su `<html>` e non su `<body>`: i token di
 * `globals.css` sono dichiarati su `:root` e le leggono da lì — messe più in
 * basso, a `:root` risulterebbero indefinite e i caratteri ricadrebbero sui
 * sostituti. */
const display = Cinzel({
  weight: ["500", "600"],
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const interfaccia = IBM_Plex_Sans({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-interfaccia",
  display: "swap",
});

const apparato = IBM_Plex_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-apparato",
  display: "swap",
});

export const metadata: Metadata = {
  title: "T-AI-rots · Console",
  description: "Amministrazione di utenti, pagamenti, catalogo e modelli.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#0d0a1a",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="it"
      className={`${display.variable} ${interfaccia.variable} ${apparato.variable}`}
    >
      <body>
        <Providers>
          <Guscio>{children}</Guscio>
        </Providers>
      </body>
    </html>
  );
}
