import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Prezzi } from "@/v2/pagine/prezzi";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.prezzi.meta_titolo, t.prezzi.meta_descrizione, "/v2/pricing");
}

export default function PaginaPrezzi() {
  return (
    <Pagina>
      <Sottotitolo sezione="prezzi" compatto />
      <Prezzi />
    </Pagina>
  );
}
