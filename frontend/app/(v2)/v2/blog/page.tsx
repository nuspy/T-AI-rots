import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Diario } from "@/v2/pagine/blog";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.blog.meta_titolo, t.blog.meta_descrizione, "/v2/blog");
}

export default function PaginaDiario() {
  return (
    <Pagina>
      <Sottotitolo sezione="blog" compatto />
      <Diario />
    </Pagina>
  );
}
