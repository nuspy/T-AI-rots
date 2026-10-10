import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { Privacy } from "@/v2/pagine/privacy";

/* Dal 10/10/2026 il testo dell'informativa è solo in inglese (lo traduce il browser): in italiano il canonical va
 * all'inglese, senza `hreflang`. Titolo e descrizione restano nella lingua del sito, come l'apertura della pagina. */
export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.privacy.meta_titolo, t.privacy.meta_descrizione, "/privacy", { soloEn: true });
}

/* L'informativa esce dal server già con i dati del titolare e i fornitori dell'AI (v9, Fase 2c): li legge dall'API,
 * con un minuto di cache, e la pagina nel browser li trova pronti. */
export default async function PaginaPrivacy() {
  const valori = await precarica([P.titolare()]);
  return (
    <DatiIniziali valori={valori}>
      <Pagina>
        <Sottotitolo sezione="privacy" compatto />
        <Privacy />
      </Pagina>
    </DatiIniziali>
  );
}
