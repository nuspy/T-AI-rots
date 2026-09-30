"use client";

/* La pagina privacy (v7, Fase G): il custode del trattamento dati, e il consenso — separato da
 * quello cookie — alla condivisione dei dati con i partner. Pubblica: chi non ha un account deve
 * poterla leggere prima di decidere se registrarsi. */

import { useState } from "react";
import { leggiConsenso, registraConsenso } from "@/lib/api";
import { dimenticaAnalytics, impostaConsensoAnalytics } from "@/lib/analytics";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";

export default function PaginaPrivacy() {
  const { t } = useLingua();
  const sessione = useSessione();
  const consenso = useCarica(leggiConsenso, [], { pubblico: true });
  const [inCorso, setInCorso] = useState(false);
  const [locale, setLocale] = useState<"accettato" | "rifiutato" | null>(null);

  const attuale = locale ?? consenso.dati?.condivisione_dati_partner ?? null;
  /* Il consenso dei cookie (il livello esteso degli analytics) si cambia qui quando si vuole: revocarlo
   * deve essere facile quanto darlo, e fa dimenticare l'identificativo del browser anche al server. */
  const [cookieLocale, setCookieLocale] = useState<"accettato" | "rifiutato" | null>(null);
  const cookie = cookieLocale ?? consenso.dati?.cookie ?? null;
  const scegliCookie = async (valore: "accettato" | "rifiutato") => {
    setInCorso(true);
    try {
      await registraConsenso(sessione.token, "cookie", valore);
      if (valore === "rifiutato" && cookie === "accettato") dimenticaAnalytics();
      else impostaConsensoAnalytics(valore);
      setCookieLocale(valore);
    } finally {
      setInCorso(false);
    }
  };

  const scegli = async (valore: "accettato" | "rifiutato") => {
    setInCorso(true);
    try {
      // Come nel banner cookie: funziona per chi è loggato e per chi non lo è ancora, quindi si
      // chiama l'API direttamente invece di `useAzione` (che richiede sessione autenticata).
      await registraConsenso(sessione.token, "condivisione_dati_partner", valore);
      setLocale(valore);
    } finally {
      setInCorso(false);
    }
  };

  return (
    <Involucro titolo={t.privacy_titolo} pubblica>
      <section className={`pannello ${stili.scheda} ${stili.sezione}`}>
        <h2 className={stili.sezioneTitolo}>{t.privacy_custode_titolo}</h2>
        <p className={stili.nota}>{t.privacy_custode_testo}</p>
      </section>

      <section className={`pannello ${stili.scheda} ${stili.sezione}`} aria-labelledby="privacy-partner">
        <h2 id="privacy-partner" className={stili.sezioneTitolo}>{t.privacy_partner_titolo}</h2>
        <p className={stili.nota}>{t.privacy_partner_testo}</p>
        <div className={stili.linea}>
          <button
            type="button"
            className={attuale === "accettato" ? "bottone" : "bottone-secondario"}
            disabled={inCorso}
            onClick={() => scegli("accettato")}
          >
            {t.privacy_partner_accetta}
          </button>
          <button
            type="button"
            className={attuale === "rifiutato" ? "bottone" : "bottone-secondario"}
            disabled={inCorso}
            onClick={() => scegli("rifiutato")}
          >
            {t.privacy_partner_rifiuta}
          </button>
        </div>
        {attuale && (
          <p className={stili.nota}>
            {attuale === "accettato" ? t.privacy_partner_stato_accettato : t.privacy_partner_stato_rifiutato}
          </p>
        )}
      </section>

      {/* Gli analytics (v8, libreria `lanterna`): cosa si misura, su quale base, per quanto. */}
      <section className={`pannello ${stili.scheda} ${stili.sezione}`} aria-labelledby="privacy-statistiche">
        <h2 id="privacy-statistiche" className={stili.sezioneTitolo}>{t.privacy_statistiche_titolo}</h2>
        <p className={stili.nota}>{t.privacy_statistiche_anonime}</p>
        <p className={stili.nota}>{t.privacy_statistiche_account}</p>
        <p className={stili.nota}>{t.privacy_statistiche_esteso}</p>
        <p className={stili.nota}>{t.privacy_statistiche_conservazione}</p>
        <div className={stili.linea} role="group" aria-label={t.privacy_cookie_titolo}>
          <button type="button" className={cookie === "accettato" ? "bottone" : "bottone-secondario"} disabled={inCorso}
            aria-pressed={cookie === "accettato"} onClick={() => scegliCookie("accettato")}>
            {t.privacy_cookie_accetta}
          </button>
          <button type="button" className={cookie === "rifiutato" ? "bottone" : "bottone-secondario"} disabled={inCorso}
            aria-pressed={cookie === "rifiutato"} onClick={() => scegliCookie("rifiutato")}>
            {t.privacy_cookie_rifiuta}
          </button>
        </div>
        {cookie && (
          <p className={stili.nota} role="status">
            {cookie === "accettato" ? t.privacy_cookie_stato_accettato : t.privacy_cookie_stato_rifiutato}
          </p>
        )}
        <p className={stili.nota}>
          {t.privacy_statistiche_geo}{" "}
          <a href="https://db-ip.com" rel="noopener" target="_blank">IP Geolocation by DB-IP</a> (CC BY 4.0)
        </p>
      </section>
    </Involucro>
  );
}
