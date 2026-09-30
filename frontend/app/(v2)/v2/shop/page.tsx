import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Negozio } from "@/v2/pagine/negozio";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.negozio.meta_titolo, t.negozio.meta_descrizione, "/v2/shop");
}

export default function PaginaNegozio() {
  return (
    <Pagina>
      <Sottotitolo sezione="negozio" compatto />
      <Negozio />
    </Pagina>
  );
}
