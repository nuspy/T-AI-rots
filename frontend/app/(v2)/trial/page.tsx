/* La prova gratuita (`/trial`, `/it/trial`; v9, Fase 2b): pubblica, perché ci arriva anche chi non ha ancora un
 * account (dal banner, dopo la registrazione). Il server scrive i piani e i numeri della prova nella pagina. */

import type { Metadata } from "next";
import type { Piano } from "@/lib/api";
import { PERCORSO_PUBBLICO_ABBONAMENTI, type ImpostazioniPubblicheAbbonamenti } from "@/lib/abbonamenti";
import { linguaPagina } from "@/lib/lingua-server";
import { leggiDalServer } from "@/lib/server-api";
import { f } from "@/v2/i18n";
import { Pagina } from "@/v2/componenti/pagina";
import { P } from "@/v2/lib/api-percorsi";
import { DatiIniziali } from "@/v2/lib/iniziali";
import { NOINDEX, metaV2, testiServer } from "@/v2/lib/meta";
import { precarica } from "@/v2/lib/precarica";
import { ProvaGratuita } from "@/v2/pagine/prova";

type Parametri = { searchParams: Promise<Record<string, string | string[] | undefined>> };

export async function generateMetadata({ searchParams }: Parametri): Promise<Metadata> {
  const [t, prova] = await Promise.all([
    testiServer(),
    leggiDalServer<ImpostazioniPubblicheAbbonamenti>(PERCORSO_PUBBLICO_ABBONAMENTI, { secondi: 60 }),
  ]);
  const valori = { giorni: prova?.giorni_prova ?? 14, sconto: prova?.sconto_prova ?? 50 };
  const m = await metaV2(f(t.abbonamento.prova_meta_titolo, valori), f(t.abbonamento.prova_meta_descrizione, valori), "/trial");
  return (await searchParams).checkout ? { ...m, robots: NOINDEX } : m;
}

export default async function PaginaProva() {
  const lingua = await linguaPagina();
  const valori = await precarica([P.piani(lingua), PERCORSO_PUBBLICO_ABBONAMENTI]);
  const piani = ((valori[P.piani(lingua)] as Piano[] | undefined) ?? []);
  return (
    <DatiIniziali valori={valori}>
      <Pagina>
        <ProvaGratuita pianiIniziali={piani} />
      </Pagina>
    </DatiIniziali>
  );
}
