import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { metaV2, testiServer } from "@/v2/lib/meta";
import { EliminaAccount } from "@/v2/pagine/elimina-account";

/* La cancellazione dell'account (GDPR, Fase 1): pubblica, come la vuole Google Play («un link che l'utente può aprire
 * per chiedere la cancellazione dell'account e dei dati»), anche senza essere entrati. */
export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return metaV2(t.profilo.elimina_meta_titolo, t.profilo.elimina_meta_descrizione, "/account/elimina");
}

export default function PaginaEliminaAccount() {
  return (
    <Pagina>
      <EliminaAccount />
    </Pagina>
  );
}
