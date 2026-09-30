"use client";

/* Il banner dei cookie della v2: stessa scelta del sito (una sola, per browser e account), stesse etichette
 * «It's fine» / «Please no» — un requisito letterale dell'operatore, non tradotto, come nel sito. */

import { useState } from "react";
import { leggiConsenso, registraConsenso } from "@/lib/api";
import { impostaConsensoAnalytics } from "@/lib/analytics";
import { useSessione } from "@/lib/sessione";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";
import LinkV2 from "./link";

export function BannerCookieV2() {
  const { t } = useLingua();
  const sessione = useSessione();
  const consenso = useCarica(leggiConsenso, [], { pubblico: true });
  const [inCorso, setInCorso] = useState(false);
  const [nascosto, setNascosto] = useState(false);

  if (!consenso.dati || consenso.dati.cookie !== null || nascosto) return null;

  const scegli = async (valore: "accettato" | "rifiutato") => {
    setInCorso(true);
    try {
      await registraConsenso(sessione.token, "cookie", valore);
      impostaConsensoAnalytics(valore);
      setNascosto(true);
    } catch {
      /* la scelta non è arrivata: il banner resta, si può riprovare */
    } finally {
      setInCorso(false);
    }
  };

  return (
    <section className="cookie" role="dialog" aria-labelledby="cookie-titolo">
      <h2 id="cookie-titolo">{t.comune.cookie_titolo}</h2>
      <p>
        {t.comune.cookie_testo} <LinkV2 className="inline" href={R.privacy}>{t.comune.cookie_leggi}</LinkV2>.
      </p>
      <div className="button-row">
        <button type="button" className="button button-small" disabled={inCorso} onClick={() => scegli("accettato")}>
          {t.comune.cookie_si}
        </button>
        <button type="button" className="button button-quiet button-small" disabled={inCorso} onClick={() => scegli("rifiutato")}>
          {t.comune.cookie_no}
        </button>
      </div>
    </section>
  );
}
