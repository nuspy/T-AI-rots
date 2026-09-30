import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Giorno } from "@/v2/pagine/giorno";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.giorno.meta_titolo, t.giorno.meta_descrizione, "/v2/daily-card");
}

export default function PaginaGiorno() {
  return (
    <Pagina>
      <Sottotitolo sezione="giorno" compatto />
      <Giorno />
    </Pagina>
  );
}
