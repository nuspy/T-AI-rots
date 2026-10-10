import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { en } from "@/v2/i18n/en";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { metaV2 } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { Termini } from "@/v2/pagine/termini";

/* I termini di servizio (10/10/2026): solo in inglese in ogni lingua, anche titolo e descrizione; `/it/terms` è la
 * stessa pagina con l'interfaccia italiana, e il canonical va all'inglese. */
export async function generateMetadata(): Promise<Metadata> {
  return metaV2(en.termini.meta_titolo, en.termini.meta_descrizione, "/terms", { soloEn: true });
}

/* Come l'informativa: i dati del titolare (nome, indirizzo, codice, contatto) arrivano già dal server. */
export default async function PaginaTermini() {
  const valori = await precarica([P.titolare()]);
  return (
    <DatiIniziali valori={valori}>
      <Pagina>
        <Termini />
      </Pagina>
    </DatiIniziali>
  );
}
