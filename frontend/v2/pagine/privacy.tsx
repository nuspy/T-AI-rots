"use client";

/* Metodo e privacy nella v2: l'informativa completa (GDPR, Fase 1, artt. 13-14) — titolare e contatti, cosa si usa e
 * con quale base giuridica, chi altro tratta i dati e dove, quanto si conserva, i diritti e come esercitarli (anche da
 * soli: download dei dati e cancellazione dell'account), il reclamo al Garante, l'età minima, i dati particolari —
 * con le scelte del banner (statistiche, Google Analytics, pubblicità), che si cambiano qui quando si vuole: revocare
 * le statistiche fa dimenticare l'identificativo anche al server. Le scelte che riguardano un account (testi, dati
 * particolari, promozioni) stanno nel profilo.
 *
 * I dati del titolare (nome, indirizzo, codice fiscale, email per la privacy, DPO, hosting) e l'elenco dei fornitori
 * dell'AI vengono dalla console (v9, Fase 2c: `GET /privacy/titolare`, letto anche dal server per la prima pagina): i
 * {segnaposto} dei testi si riempiono qui, e un campo vuoto mostra una frase neutra, mai un segnaposto.
 *
 * Dal 10/10/2026 il testo dell'informativa è solo in inglese (`en.privacy`), qualunque sia la lingua del sito, con
 * `lang="en"`: dove il browser sa tradurre lo traduce sul dispositivo, come gli articoli del blog (`AvvisoTraduzione`,
 * e la nota che vale l'originale inglese). Restano nella lingua del sito, e fuori dalla traduzione (`data-no-trad`),
 * le parti che si usano: le caselle dei consensi, i pulsanti e i collegamenti al profilo. Paesi e fornitori si
 * scrivono in inglese, perché il traduttore traduce la frase intera. */

import { useRef, useState } from "react";
import type { TipoConsenso } from "@/lib/api";
import { AvvisoTraduzione } from "@/v2/componenti/avviso-traduzione";
import LinkV2 from "@/v2/componenti/link";
import { cambiaSceltaAnnunciGoogle, usePubblicita } from "@/v2/componenti/pubblicita";
import { en } from "@/v2/i18n/en";
import { P } from "@/v2/lib/api-percorsi";
import { useConsensi } from "@/v2/lib/consensi";
import { useLingua } from "@/v2/lib/lingua";
import { useLinguaTraduzione } from "@/v2/lib/lingua-traduzione";
import { R } from "@/v2/lib/percorsi";
import { usePubblico } from "@/v2/lib/usa";
import { useTraduzione } from "@/v2/lib/usa-traduzione";

/** Ciò che l'API dice del titolare (`/privacy/titolare`): un campo vuoto è `null`. */
export interface TitolarePubblico {
  nome: string | null;
  indirizzo: string | null;
  codice_fiscale: string | null;
  email_privacy: string | null;
  dpo: { nominato: boolean; contatto: string | null };
  hosting: string | null;
  fornitori_ai: { nome: string; paese: string | null; proprio: boolean }[];
}

/** Un testo con i suoi {segnaposto} al loro posto. */
function riempi(testo: string, valori: Record<string, string>): string {
  return testo.replace(/\{(\w+)\}/g, (tutto, nome: string) => valori[nome] ?? tutto);
}

/** «NVIDIA (Stati Uniti), DeepSeek (Cina), LM Studio (su un nostro server, nessun terzo)», nella lingua della pagina. */
function elencoFornitori(fornitori: TitolarePubblico["fornitori_ai"], lingua: string, proprio: string, vuoto: string): string {
  if (!fornitori.length) return vuoto;
  let paesi: Intl.DisplayNames | null = null;
  try {
    paesi = new Intl.DisplayNames([lingua], { type: "region" });
  } catch {
    paesi = null;
  }
  return fornitori.map((f) => {
    const dove = f.proprio ? proprio : f.paese ? (paesi?.of(f.paese) ?? f.paese) : "";
    return dove ? `${f.nome} (${dove})` : f.nome;
  }).join(", ");
}

/** «Hivelocity, London, GB» → «Hivelocity, London, Regno Unito»: il codice ISO del paese in fondo (v9, Fase 4) si scrive
 * nella lingua della pagina; fornitore e città restano come in console. Un testo senza codice resta com'è. */
export function hostingInLingua(hosting: string, lingua: string): string {
  const m = /^(.*?),\s*([A-Z]{2})\s*$/.exec(hosting.trim());
  if (!m) return hosting;
  try {
    const paese = new Intl.DisplayNames([lingua], { type: "region" }).of(m[2]);
    return paese && paese !== m[2] ? `${m[1]}, ${paese}` : hosting;
  } catch {
    return hosting;
  }
}

export function Privacy() {
  const { t, lingua } = useLingua();
  /* `k`: il testo dell'informativa, sempre inglese; `u`: le parti che si usano, nella lingua del sito. */
  const k = en.privacy;
  const u = t.privacy;
  const c = t.comune;
  const titolare = usePubblico<TitolarePubblico>(P.titolare()).dati;
  const valori = {
    hosting: titolare?.hosting ? hostingInLingua(titolare.hosting, "en") : k.hosting_vuoto,
    fornitori_ai: titolare ? elencoFornitori(titolare.fornitori_ai, "en", k.fornitori_ai_proprio, k.fornitori_ai_vuoto) : "…",
  };
  const corpo = useRef<HTMLDivElement>(null);
  const linguaTraduzione = useLinguaTraduzione().lingua;
  const traduzione = useTraduzione([corpo], linguaTraduzione, { sorgente: "en", chiave: "privacy" });
  const consensi = useConsensi();
  const pubblicita = usePubblicita();
  const [salvando, setSalvando] = useState(false);
  const [errore, setErrore] = useState(false);
  const dati = consensi.dati;
  const annunci = pubblicita.consenso !== undefined ? pubblicita.consenso : dati?.pubblicita ?? null;
  const scelte: { tipo: TipoConsenso; titolo: string; testo: string; valore: string | null }[] = [
    { tipo: "statistiche", titolo: c.consenso_statistiche, testo: c.consenso_statistiche_testo, valore: dati?.statistiche ?? null },
    { tipo: "google_analytics", titolo: c.consenso_google, testo: c.consenso_google_testo, valore: dati?.google_analytics ?? null },
    /* Dove decide il CMP di Google (TCF) la scelta sugli annunci si cambia lì (riquadro «Pubblicità» più sotto). */
    ...((pubblicita.attiva || annunci !== null) && pubblicita.tcf.applica !== true
      ? [{ tipo: "pubblicita" as const, titolo: c.consenso_pubblicita, testo: c.consenso_pubblicita_testo, valore: annunci }] : []),
  ];
  const cambia = async (tipo: TipoConsenso, acceso: boolean) => {
    setSalvando(true);
    setErrore(false);
    try {
      await consensi.scegli({ [tipo]: acceso ? "accettato" : "rifiutato" });
    } catch {
      setErrore(true);
    } finally {
      setSalvando(false);
    }
  };

  return (
    <section className="band band-tight">
      <AvvisoTraduzione stato={traduzione} />
      <div ref={corpo} lang="en" className="profile-grid">
        <p className="small muted privacy-originale">{en.termini.originale}</p>
        <section className="panel wide" aria-labelledby="pv-titolare">
          <h2 id="pv-titolare">{k.custode_titolo}</h2>
          {titolare ? (
            <>
              <p className="small">
                {titolare.nome ? riempi(k.custode_testo, { titolare: titolare.nome }) : k.custode_testo_senza_nome}
              </p>
              <p className="small">
                {titolare.indirizzo ? riempi(k.custode_indirizzo, { indirizzo: titolare.indirizzo }) : k.custode_indirizzo_vuoto}
              </p>
              {titolare.codice_fiscale && <p className="small">{riempi(k.custode_codice, { codice: titolare.codice_fiscale })}</p>}
              <p className="small">
                {titolare.email_privacy ? (
                  <>
                    {riempi(k.custode_email, { email: "" })}
                    <a className="inline" href={`mailto:${titolare.email_privacy}`} translate="no">{titolare.email_privacy}</a>
                  </>
                ) : k.custode_email_vuoto}
              </p>
              <p className="small">
                {titolare.dpo.nominato && titolare.dpo.contatto
                  ? riempi(k.custode_dpo, { dpo: titolare.dpo.contatto })
                  : k.custode_dpo_no}
              </p>
            </>
          ) : (
            <p className="small muted" aria-busy="true">{k.custode_testo_senza_nome}</p>
          )}
        </section>

        {/* Le scelte si fanno qui: riquadro nella lingua del sito, che il traduttore non tocca. */}
        <section className="panel wide" aria-labelledby="pv-scelte" lang={lingua} data-no-trad>
          <h2 id="pv-scelte">{u.scelte_titolo}</h2>
          <p className="small">{u.scelte_testo}</p>
          <ul className="list-plain consensi-elenco">
            {scelte.map((s) => (
              <li key={s.tipo}>
                <label className="check">
                  <input type="checkbox" checked={s.valore === "accettato"} disabled={!dati || salvando}
                    onChange={(e) => cambia(s.tipo, e.target.checked)} />
                  <span><b>{s.titolo}</b><small>{s.testo}</small></span>
                </label>
              </li>
            ))}
          </ul>
          {errore && <p className="error" role="alert">{c.err_operazione}</p>}
          <p className="small">{u.scelte_account} <LinkV2 className="inline" href={`${R.profilo}#privacy`}>{u.scelte_account_cta}</LinkV2>.</p>
        </section>

        <section className="panel wide" aria-labelledby="pv-finalita">
          <h2 id="pv-finalita">{k.finalita_titolo}</h2>
          <p className="small">{k.finalita_intro}</p>
          <dl className="privacy-finalita">
            {k.finalita.map((v) => (
              <div key={v.cosa}>
                <dt>{v.cosa}</dt>
                <dd className="small">{v.perche} <span className="muted">{v.base}</span></dd>
              </div>
            ))}
          </dl>
        </section>

        <section className="panel" aria-labelledby="pv-letture">
          <h2 id="pv-letture">{k.letture_titolo}</h2>
          <p className="small">{k.letture_testo}</p>
          <p className="small">{k.letture_accesso}</p>
          <LinkV2 className="button button-quiet button-small" href={R.storia} lang={lingua} data-no-trad>{u.letture_cta}</LinkV2>
        </section>
        <section className="panel" aria-labelledby="pv-ai">
          <h2 id="pv-ai">{k.ai_titolo}</h2>
          <p className="small">{k.ai_testo}</p>
        </section>

        <section className="panel wide" aria-labelledby="pv-art9">
          <h2 id="pv-art9">{k.art9_titolo}</h2>
          <p className="small">{k.art9_testo}</p>
          <p className="small">{k.art9_crisi}</p>
        </section>

        <section className="panel wide" aria-labelledby="pv-social">
          <h2 id="pv-social">{k.social_titolo}</h2>
          <p className="small">{k.social_account}</p>
          <p className="small">{k.social_cosa}</p>
          <p className="small">{k.social_perche}</p>
          <p className="small">{k.social_posizione}</p>
          <p className="small">{k.social_controllo}</p>
          <LinkV2 className="button button-quiet button-small" href={`${R.profilo}#dati`} lang={lingua} data-no-trad>{u.social_cta}</LinkV2>
        </section>

        <section className="panel wide" aria-labelledby="pv-stat">
          <h2 id="pv-stat">{k.stat_titolo}</h2>
          <p className="small">{k.stat_anonime}</p>
          <p className="small">{k.stat_account}</p>
          <p className="small">{k.stat_esteso}</p>
          <p className="small">{k.stat_google}</p>
          <p className="small">{k.stat_conservazione}</p>
          <p className="small">{k.stat_geo} <a className="inline" href="https://db-ip.com" rel="noopener" target="_blank" translate="no">IP Geolocation by DB-IP</a> (CC BY 4.0)</p>
        </section>

        {(pubblicita.attiva || annunci !== null) && (
          <section className="panel wide" aria-labelledby="pv-pubblicita">
            <h2 id="pv-pubblicita">{k.pubblicita_titolo}</h2>
            <p className="small">{k.pubblicita_testo}</p>
            {pubblicita.tcf.applica === true && (
              <>
                <p className="small">{k.pubblicita_tcf}</p>
                <button type="button" className="button button-quiet" onClick={cambiaSceltaAnnunciGoogle} lang={lingua} data-no-trad>
                  {u.pubblicita_tcf_cambia}
                </button>
              </>
            )}
          </section>
        )}

        <section className="panel wide" aria-labelledby="pv-responsabili">
          <h2 id="pv-responsabili">{k.responsabili_titolo}</h2>
          <p className="small">{k.responsabili_intro}</p>
          <ul className="small privacy-elenco">
            {k.responsabili.map((r) => <li key={r.chi}><b>{r.chi}</b> — {riempi(r.cosa, valori)}</li>)}
          </ul>
          <p className="small">{k.trasferimenti}</p>
        </section>

        <section className="panel wide" aria-labelledby="pv-conservazione">
          <h2 id="pv-conservazione">{k.conservazione_titolo}</h2>
          <ul className="small privacy-elenco">
            {k.conservazione.map((v) => <li key={v}>{v}</li>)}
          </ul>
        </section>

        <section className="panel wide" aria-labelledby="pv-diritti">
          <h2 id="pv-diritti">{k.diritti_titolo}</h2>
          <p className="small">{k.diritti_testo}</p>
          <p className="small">{k.diritti_come}</p>
          <div className="button-row" lang={lingua} data-no-trad>
            <LinkV2 className="button button-quiet button-small" href={`${R.profilo}#privacy`}>{u.diritti_cta_dati}</LinkV2>
            <LinkV2 className="button button-quiet button-small" href={R.elimina}>{u.diritti_cta_elimina}</LinkV2>
          </div>
          <h3>{k.garante_titolo}</h3>
          <p className="small">{k.garante_testo}</p>
        </section>

        <section className="panel wide" aria-labelledby="pv-eta">
          <h2 id="pv-eta">{k.eta_titolo}</h2>
          <p className="small">{k.eta_testo}</p>
        </section>

        <p className="small privacy-versione">
          <LinkV2 className="inline" href={R.termini}>{en.termini.meta_titolo}</LinkV2>
          <span className="muted"> · {k.versione}</span>
        </p>
      </div>
    </section>
  );
}
