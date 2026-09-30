import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Privacy } from "@/v2/pagine/privacy";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.privacy.meta_titolo, t.privacy.meta_descrizione, "/privacy");
}

export default function PaginaPrivacy() {
  return (
    <Pagina>
      <Sottotitolo sezione="privacy" compatto />
      <Privacy />
    </Pagina>
  );
}
