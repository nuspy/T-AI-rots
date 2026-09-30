import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { ElencoStese } from "@/v2/pagine/stese";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.stese.meta_titolo, t.stese.meta_descrizione, "/v2/spreads");
}

export default function PaginaStese() {
  return (
    <Pagina>
      <Sottotitolo sezione="stese" compatto />
      <ElencoStese />
    </Pagina>
  );
}
