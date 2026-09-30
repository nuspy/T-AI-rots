import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Home } from "@/v2/pagine/home";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.home.meta_titolo, t.home.meta_descrizione, "/v2", true);
}

export default function PaginaHome() {
  return (
    <Pagina>
      <Home />
    </Pagina>
  );
}
