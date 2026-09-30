"use client";

/* Metodo e privacy nella v2: gli stessi contenuti e le stesse scelte della pagina privacy del sito (titolare,
 * condivisione con i partner, statistiche e cookie — la scelta si può cambiare quando si vuole, e revocarla fa
 * dimenticare l'identificativo anche al server), con in più che cosa ricorda il lettore e come si usa l'AI. */

import { useState } from "react";
import { leggiConsenso, registraConsenso } from "@/lib/api";
import { dimenticaAnalytics, impostaConsensoAnalytics } from "@/lib/analytics";
import { useSessione } from "@/lib/sessione";
import LinkV2 from "@/v2/componenti/link";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";

type Valore = "accettato" | "rifiutato";

export function Privacy() {
  const { t } = useLingua();
  const k = t.privacy;
  const sessione = useSessione();
  const consenso = useCarica(leggiConsenso, [], { pubblico: true });
  const [inCorso, setInCorso] = useState(false);
  const [partnerLocale, setPartnerLocale] = useState<Valore | null>(null);
  const [cookieLocale, setCookieLocale] = useState<Valore | null>(null);
  const partner = partnerLocale ?? consenso.dati?.condivisione_dati_partner ?? null;
  const cookie = cookieLocale ?? consenso.dati?.cookie ?? null;

  const scegliPartner = async (v: Valore) => {
    setInCorso(true);
    try { await registraConsenso(sessione.token, "condivisione_dati_partner", v); setPartnerLocale(v); } finally { setInCorso(false); }
  };
  const scegliCookie = async (v: Valore) => {
    setInCorso(true);
    try {
      await registraConsenso(sessione.token, "cookie", v);
      if (v === "rifiutato" && cookie === "accettato") dimenticaAnalytics(); else impostaConsensoAnalytics(v);
      setCookieLocale(v);
    } finally { setInCorso(false); }
  };
  const scelta = (valore: Valore | null, onSi: () => void, onNo: () => void, si: string, no: string, etichetta: string) => (
    <div className="button-row" role="group" aria-label={etichetta}>
      <button type="button" className={`button button-small ${valore === "accettato" ? "" : "button-quiet"}`} aria-pressed={valore === "accettato"} disabled={inCorso} onClick={onSi}>{si}</button>
      <button type="button" className={`button button-small ${valore === "rifiutato" ? "" : "button-quiet"}`} aria-pressed={valore === "rifiutato"} disabled={inCorso} onClick={onNo}>{no}</button>
    </div>
  );

  return (
    <section className="band band-tight">
      <div className="profile-grid">
        <section className="panel" aria-labelledby="pv-letture">
          <h2 id="pv-letture">{k.letture_titolo}</h2>
          <p className="small">{k.letture_testo}</p>
          <LinkV2 className="button button-quiet button-small" href={R.storia}>{k.letture_cta}</LinkV2>
        </section>
        <section className="panel" aria-labelledby="pv-ai">
          <h2 id="pv-ai">{k.ai_titolo}</h2>
          <p className="small">{k.ai_testo}</p>
        </section>
        <section className="panel" aria-labelledby="pv-titolare">
          <h2 id="pv-titolare">{k.custode_titolo}</h2>
          <p className="small">{k.custode_testo}</p>
        </section>
        <section className="panel" aria-labelledby="pv-partner">
          <h2 id="pv-partner">{k.partner_titolo}</h2>
          <p className="small">{k.partner_testo}</p>
          {scelta(partner, () => scegliPartner("accettato"), () => scegliPartner("rifiutato"), k.partner_si, k.partner_no, k.partner_titolo)}
          {partner && <p className="small" role="status">{partner === "accettato" ? k.partner_stato_si : k.partner_stato_no}</p>}
        </section>
        <section className="panel wide" aria-labelledby="pv-stat">
          <h2 id="pv-stat">{k.stat_titolo}</h2>
          <p className="small">{k.stat_anonime}</p>
          <p className="small">{k.stat_account}</p>
          <p className="small">{k.stat_esteso}</p>
          <p className="small">{k.stat_conservazione}</p>
          <h3>{k.cookie_titolo}</h3>
          {scelta(cookie, () => scegliCookie("accettato"), () => scegliCookie("rifiutato"), k.cookie_si, k.cookie_no, k.cookie_titolo)}
          {cookie && <p className="small" role="status">{cookie === "accettato" ? k.cookie_stato_si : k.cookie_stato_no}</p>}
          <p className="small">{k.stat_geo} <a className="inline" href="https://db-ip.com" rel="noopener" target="_blank">IP Geolocation by DB-IP</a> (CC BY 4.0)</p>
        </section>
      </div>
    </section>
  );
}
