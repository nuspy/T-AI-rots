import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Voto } from "@/v2/pagine/voto";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.mazzi.voto_meta_titolo, t.mazzi.voto_meta_descrizione, "/vote");
}

export default function PaginaVoto() {
  return (
    <Pagina>
      <Voto />
    </Pagina>
  );
}
