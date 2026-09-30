import type { Metadata, Viewport } from "next";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { IMMAGINE_PREDEFINITA } from "@/lib/seo";
import { Providers } from "./providers";
import { Cosmo } from "./componenti/cosmo";
import { classiFont } from "./fonts";
import "./globals.css";

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
  /* v8.5: la v1 vive sotto `/old` e non si indicizza (il sito è la v2). Anche il proxy lo dice (`X-Robots-Tag`). */
  robots: { index: false, follow: false, googleBot: { index: false, follow: false } },
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
    <html lang={lingua} className={classiFont}>
      <body>
        <Cosmo />
        <Providers linguaIniziale={lingua}>{children}</Providers>
      </body>
    </html>
  );
}
