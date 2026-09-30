import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Profilo } from "@/v2/pagine/profilo";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.profilo.meta_titolo, t.profilo.meta_descrizione, "/profile");
}

export default function PaginaProfilo() {
  return (
    <Pagina>
      <Sottotitolo sezione="profilo" compatto />
      <Profilo />
    </Pagina>
  );
}
