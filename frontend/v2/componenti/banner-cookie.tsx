"use client";

/* Il banner dei consensi della v2 (GDPR, Fase 1): categorie separate, ciascuna spenta finché non la si accende.
 *
 * - `statistiche`: l'identificativo casuale del browser per le statistiche del sito (lanterna);
 * - `google_analytics`: Google Analytics 4 con i suoi cookie;
 * - `pubblicita`: gli annunci di Google AdSense, solo se la console ha acceso gli spazi pubblicitari.
 *
 * Tre comandi con lo stesso peso: «accetta tutto», «rifiuta tutto» e «scegli», che apre le categorie una per una.
 * Le altre scelte (testi per le statistiche, dati particolari, promozioni) non stanno qui: riguardano un account e
 * si fanno nel profilo («Privacy e consensi»).
 *
 * Il banner ricompare a chi non ha ancora scelto su una delle categorie, a chi aveva accettato Google Analytics su un
 * testo che non lo nominava (`daRinnovare`), e a chi non ha ancora scelto sugli annunci quando gli spazi si accendono.
 * Sul telefono è un foglio in basso a tutta larghezza, sopra la barra dell'oracolo e la safe area. */

import { useId, useState } from "react";
import type { TipoConsenso, ValoreConsenso } from "@/lib/api";
import { useConsensi } from "@/v2/lib/consensi";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useStatoGoogle } from "./contatore-google";
import LinkV2 from "./link";
import { usePubblicita } from "./pubblicita";

type Categoria = "statistiche" | "google_analytics" | "pubblicita";

export function BannerCookieV2() {
  const { t } = useLingua();
  const k = t.comune;
  const consensi = useConsensi();
  const google = useStatoGoogle();
  const pubblicita = usePubblicita();
  const id = useId();
  const [inCorso, setInCorso] = useState(false);
  const [nascosto, setNascosto] = useState(false);
  const [aperto, setAperto] = useState(false);
  const [errore, setErrore] = useState(false);
  const [scelte, setScelte] = useState<Partial<Record<Categoria, boolean>>>({});

  const dati = consensi.dati;
  if (!dati || nascosto) return null;
  const sceltaAnnunci = pubblicita.consenso !== undefined ? pubblicita.consenso : dati.pubblicita;
  const daRinnovareGa = dati.google_analytics === "accettato" && google.misurazione !== null && google.daRinnovare;
  const chiedeAnnunci = pubblicita.attiva && sceltaAnnunci === null;
  const chiede = dati.statistiche === null || dati.google_analytics === null || daRinnovareGa || chiedeAnnunci;
  if (!chiede) return null;

  const categorie: Categoria[] = ["statistiche", "google_analytics", ...(pubblicita.attiva ? ["pubblicita" as const] : [])];
  const etichette: Record<Categoria, { titolo: string; testo: string }> = {
    statistiche: { titolo: k.consenso_statistiche, testo: k.consenso_statistiche_testo },
    google_analytics: { titolo: k.consenso_google, testo: k.consenso_google_testo },
    pubblicita: { titolo: k.consenso_pubblicita, testo: k.consenso_pubblicita_testo },
  };
  /* Nel pannello «scegli» ogni casella parte da ciò che la persona ha già scelto, spenta se non ha mai scelto. */
  const acceso = (c: Categoria) => scelte[c] ?? (c === "pubblicita" ? sceltaAnnunci : dati[c]) === "accettato";

  const registra = async (valori: Record<Categoria, ValoreConsenso>) => {
    setInCorso(true);
    setErrore(false);
    try {
      const invio: Partial<Record<TipoConsenso, ValoreConsenso>> = {};
      for (const c of categorie) invio[c] = valori[c];
      await consensi.scegli(invio);
      setNascosto(true);
    } catch {
      /* la scelta non è arrivata: il banner resta, si può riprovare */
      setErrore(true);
    } finally {
      setInCorso(false);
    }
  };
  const tutte = (v: ValoreConsenso) =>
    registra({ statistiche: v, google_analytics: v, pubblicita: v });
  const salvaScelte = () =>
    registra({
      statistiche: acceso("statistiche") ? "accettato" : "rifiutato",
      google_analytics: acceso("google_analytics") ? "accettato" : "rifiutato",
      pubblicita: acceso("pubblicita") ? "accettato" : "rifiutato",
    });

  return (
    <section className="cookie cookie-categorie" role="dialog" aria-labelledby={`${id}-t`} aria-describedby={`${id}-d`}>
      <h2 id={`${id}-t`}>{k.cookie_titolo}</h2>
      <p id={`${id}-d`}>
        {k.consenso_banner_testo} <LinkV2 className="inline" href={R.privacy}>{k.cookie_leggi}</LinkV2>.
      </p>
      {aperto && (
        <fieldset className="cookie-scelte">
          <legend className="sr-only">{k.consenso_scegli}</legend>
          {categorie.map((c) => (
            <label key={c} className="check cookie-voce">
              <input type="checkbox" checked={acceso(c)} disabled={inCorso}
                onChange={(e) => setScelte((s) => ({ ...s, [c]: e.target.checked }))} />
              <span><b>{etichette[c].titolo}</b><small>{etichette[c].testo}</small></span>
            </label>
          ))}
          <p className="small muted">{k.consenso_tecnici}</p>
        </fieldset>
      )}
      <div className="button-row cookie-comandi">
        {aperto ? (
          <button type="button" className="button button-small" disabled={inCorso} onClick={salvaScelte}>{k.consenso_salva}</button>
        ) : (
          <>
            <button type="button" className="button button-small" disabled={inCorso} onClick={() => tutte("accettato")}>{k.consenso_accetta_tutto}</button>
            <button type="button" className="button button-small" disabled={inCorso} onClick={() => tutte("rifiutato")}>{k.consenso_rifiuta_tutto}</button>
            <button type="button" className="button button-quiet button-small" disabled={inCorso} aria-expanded={aperto}
              onClick={() => setAperto(true)}>{k.consenso_scegli}</button>
          </>
        )}
      </div>
      {errore && <p className="error small" role="alert">{k.err_operazione}</p>}
    </section>
  );
}
