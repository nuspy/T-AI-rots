import type { Metadata } from "next";
import { Suspense } from "react";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { LetturaV2 } from "@/v2/lettura/lettura";
import { metaV2, testiServer } from "@/v2/lib/meta";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.lettura.meta_titolo, t.lettura.meta_descrizione, "/read");
}

export default function PaginaLeggi() {
  return (
    <Pagina>
      <Sottotitolo sezione="lettura" compatto />
      {/* `useSearchParams` vuole un confine di sospensione. */}
      <Suspense fallback={null}>
        <LetturaV2 />
      </Suspense>
    </Pagina>
  );
}
