import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { PaginaCarrello } from "@/v2/pagine/negozio";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.negozio.carrello_meta_titolo, t.negozio.carrello_meta_descrizione, "/cart");
}

export default function PaginaCarrelloV2() {
  return (
    <Pagina>
      <PaginaCarrello />
    </Pagina>
  );
}
