import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Mazzi } from "@/v2/pagine/mazzi";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.mazzi.meta_titolo, t.mazzi.meta_descrizione, "/v2/decks");
}

export default function PaginaMazzi() {
  return (
    <Pagina>
      <Sottotitolo sezione="mazzi" compatto />
      <Mazzi />
    </Pagina>
  );
}
