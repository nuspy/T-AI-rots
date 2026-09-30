import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Biblioteca } from "@/v2/pagine/carte";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.carte.meta_titolo, t.carte.meta_descrizione, "/v2/cards");
}

export default function PaginaCarte() {
  return (
    <Pagina>
      <Sottotitolo sezione="carte" compatto />
      <Biblioteca />
    </Pagina>
  );
}
