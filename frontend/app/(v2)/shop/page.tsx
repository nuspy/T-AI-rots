import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { Sottotitolo } from "@/v2/componenti/sottotitolo";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { Negozio } from "@/v2/pagine/negozio";
import { linguaPagina } from "@/lib/lingua-server";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { precarica } from "@/v2/lib/precarica";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.negozio.meta_titolo, t.negozio.meta_descrizione, "/shop");
}

export default async function PaginaNegozio() {
  const lingua = await linguaPagina();
  const valori = await precarica([P.mazzi(lingua)]);
  return (
    <DatiIniziali valori={valori}>
    <Pagina>
      <Sottotitolo sezione="negozio" compatto />
      <Negozio />
    </Pagina>
    </DatiIniziali>
  );
}
