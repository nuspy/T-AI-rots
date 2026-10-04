"use client";

/* Il banner della prova gratuita (v9, Fase 2b), su ogni pagina, sotto la testata.
 *
 * Chi lo vede: i visitatori senza account e gli utenti senza abbonamento che non hanno ancora usato la prova. Non chi
 * l'ha già usata o è abbonato (`/me/billing` → `prova.idonea`), e non sulla pagina della prova stessa.
 *
 * Dove sta: **nel flusso della pagina**, sotto la testata, mai sopra il contenuto: non copre niente, non si somma alla
 * barra dell'oracolo in fondo né agli spazi pubblicitari, e i margini rispettano le safe area. Le impostazioni
 * arrivano dal layout (server), quindi l'HTML esce già col banner e la pagina non salta quando compare.
 *
 * Si chiude (✕, 44 px) e torna dopo `GIORNI_CHIUSO` giorni (localStorage). Il testo dice il beneficio (le letture
 * comprese, gratis), il gancio (−50% per sempre) e la verità (diventa annuale, si disdice prima e non si paga). */

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { useTraccia } from "lanterna-osservatore/react";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { useConto } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2, senzaPrefisso } from "@/v2/lib/percorsi";
import { GIORNI_CHIUSO, GIORNI_NON_IDONEO, nascostoOra, ricordaNascosto, useImpostazioniProva } from "@/v2/lib/prova";

export function BannerProva() {
  const { t, prefissoIt } = useLingua();
  const k = t.abbonamento;
  const impostazioni = useImpostazioniProva();
  const sessione = useSessione();
  const conto = useConto();
  const percorso = usePathname();
  const traccia = useTraccia();
  const [nascosto, setNascosto] = useState(false);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- il ricordo sta nel browser: si legge dopo il montaggio
    if (nascostoOra()) setNascosto(true);
  }, []);
  const nonIdoneo = sessione.autenticata && conto.dati?.prova !== undefined && !conto.dati.prova.idonea;
  useEffect(() => {
    if (nonIdoneo) ricordaNascosto(GIORNI_NON_IDONEO);
  }, [nonIdoneo]);

  if (!impostazioni?.banner_prova || nascosto || nonIdoneo) return null;
  if (senzaPrefisso(percorso ?? "/").startsWith(R.prova)) return null;

  const valori = { giorni: impostazioni.giorni_prova, sconto: impostazioni.sconto_prova };
  const chiudi = () => {
    ricordaNascosto(GIORNI_CHIUSO);
    setNascosto(true);
    traccia("trial_banner_closed");
  };
  const versoProva = indirizzoV2(R.prova, prefissoIt);

  return (
    <aside className="banner-prova" aria-label={k.banner_etichetta}>
      <div className="banner-prova-testo">
        <p className="banner-prova-etichetta">{k.banner_etichetta}</p>
        <p className="banner-prova-titolo">{f(k.banner_titolo, valori)}</p>
        <p className="banner-prova-nota">{f(k.banner_testo, valori)}</p>
      </div>
      {sessione.autenticata || !sessione.pronta ? (
        <LinkV2 className="button button-brass button-small banner-prova-cta" href={R.prova} data-an="trial_banner_cta">
          {f(k.banner_cta, valori)}
        </LinkV2>
      ) : (
        /* Chi non ha un account passa dalla registrazione e torna alla pagina della prova. */
        <button type="button" className="button button-brass button-small banner-prova-cta" data-an="trial_banner_cta"
          onClick={() => sessione.registratiPoi(versoProva)}>
          {f(k.banner_cta, valori)}
        </button>
      )}
      <button type="button" className="banner-prova-chiudi" aria-label={k.banner_chiudi} title={k.banner_chiudi} onClick={chiudi}>
        <span aria-hidden="true">✕</span>
      </button>
    </aside>
  );
}
