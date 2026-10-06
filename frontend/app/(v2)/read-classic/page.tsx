import type { Metadata } from "next";
import { Suspense } from "react";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { LetturaV2 } from "@/v2/lettura/lettura";
import { metaV2, testiServer } from "@/v2/lib/meta";

/* v9.5: la lettura classica (conversazione e console del rito) nella prova 90/10. Ci si arriva solo da `/read`, che
 * sceglie la variante (`proxy.ts`): nessun link del sito punta qui direttamente. */
export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.lettura.meta_titolo, t.lettura.meta_descrizione, "/read");
}

export default function PaginaLetturaClassica() {
  return (
    <Pagina>
      <Sottotitolo sezione="lettura" compatto />
      <Suspense fallback={null}>
        <LetturaV2 variante="classica" />
      </Suspense>
    </Pagina>
  );
}
