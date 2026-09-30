import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Esplora } from "@/v2/pagine/blog";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.blog.esplora_meta_titolo, t.blog.esplora_meta_descrizione, "/v2/explore");
}

export default function PaginaEsplora() {
  return (
    <Pagina>
      <Esplora />
    </Pagina>
  );
}
