import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Storia } from "@/v2/pagine/storia";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.storia.meta_titolo, t.storia.meta_descrizione, "/my-story");
}

export default function PaginaStoria() {
  return (
    <Pagina>
      <Sottotitolo sezione="storia" compatto />
      <Storia />
    </Pagina>
  );
}
