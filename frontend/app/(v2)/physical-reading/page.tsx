import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { LetturaFisica } from "@/v2/lettura/fisica";
import { metaV2, testiServer } from "@/v2/lib/meta";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.fisica.meta_titolo, t.fisica.meta_descrizione, "/physical-reading");
}

export default function PaginaFisica() {
  return (
    <Pagina>
      <Sottotitolo sezione="fisica" compatto />
      <LetturaFisica />
    </Pagina>
  );
}
