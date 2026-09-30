"use client";

/* I prezzi nella v2 (specifica v2, §4-5): il cuore del modello — letture, pacchetti, abbonamenti — presentato come
 * continuità, dopo il valore, non come un cancello. I piani, i prezzi e i diritti vengono dall'API (niente cifre
 * inventate). Il ritorno dal pagamento si verifica sul server; se il pagamento era partito da una lettura, si torna
 * alla lettura. */

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTraccia } from "lanterna-osservatore/react";
import {
  abbonaGratis, anteprimaCoupon, apriPagamento, disdici, euro, impostazioniPubbliche, leggiMovimenti, motivoCodice, riscattaCodice, statoPagamento, type AnteprimaCoupon, type Conto, type Piano,
} from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { f, plurale } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";
import { P, useConto, usePiani } from "@/v2/lib/dati";

export function Prezzi() {
  return <Suspense fallback={null}><Contenuto /></Suspense>;
}

/* Un ritorno accettato solo dentro la v2. */
const dentroV2 = (r: string | null) => !!r && r.startsWith("/") && !r.startsWith("//") && !/^\/old(\/|\?|$)/.test(r);

function Contenuto() {
  const { t, locale } = useLingua();
  const k = t.prezzi;
  const sessione = useSessione();
  const piani = usePiani();
  const omaggi = useCarica(impostazioniPubbliche, [], { pubblico: true, iniziale: P.impostazioni() });
  const conto = useConto();
  const movimenti = useCarica(leggiMovimenti);
  const [codice, setCodice] = useState<string | null>(null);
  const ricarica = () => { conto.ricarica(); movimenti.ricarica(); };
  const esito = useRitorno(ricarica);

  const elenco = piani.dati ?? [];
  const pacchetti = elenco.filter((p) => p.tipo === "pacchetto");
  const abbonamenti = elenco.filter((p) => p.tipo === "abbonamento" && p.prezzo_mensile > 0);
  const provaSu = elenco.find((p) => p.prezzo_mensile > 0)?.slug ?? null;

  return (
    <>
      {esito && <section className="band band-tight" style={{ paddingBottom: 0 }}><p className={esito.buono ? "success" : "error"} role="status">{esito.testo}</p></section>}
      {conto.dati && <section className="band band-tight" style={{ paddingBottom: 0 }}><Attuale conto={conto.dati} suCambio={ricarica} /></section>}

      <section className="band band-tight" aria-labelledby="titolo-pacchetti">
        <div className="pricing-grid">
          <article className="plan">
            <h2>{k.gratis_titolo}</h2>
            <p className="price">{k.gratis_prezzo}</p>
            <p>{k.gratis_testo}</p>
            <ul>{k.gratis_voci.map((v) => <li key={v}>{f(v, { n: omaggi.dati?.crediti_iscrizione ?? 3 })}</li>)}</ul>
            <LinkV2 className="button button-quiet" href={`${R.leggi}?source=pricing`}>{k.gratis_cta}</LinkV2>
          </article>
          {pacchetti.map((p, i) => <Offerta key={p.slug} piano={p} conto={conto.dati} codice={codice} evidente={i === Math.floor(pacchetti.length / 2)} suCambio={ricarica} />)}
        </div>
        <h2 id="titolo-pacchetti" className="sr-only">{k.pacchetti}</h2>
        <p className="small muted" style={{ marginTop: "1rem" }}>{k.pacchetti_testo}</p>
      </section>

      {abbonamenti.length > 0 && (
        <section className="band band-tight" aria-labelledby="titolo-abbonamenti">
          <h2 id="titolo-abbonamenti" className="section-title">{k.abbonamenti}</h2>
          <p className="section-intro">{k.abbonamenti_testo}</p>
          <div className="pricing-grid">
            {abbonamenti.map((p) => <Offerta key={p.slug} piano={p} conto={conto.dati} codice={codice} evidente={false} suCambio={ricarica} />)}
          </div>
        </section>
      )}
      {piani.errore && <section className="band band-tight"><p className="error">{piani.errore}</p></section>}

      {sessione.autenticata && (
        <section className="band band-tight">
          <div className="story-grid">
            <Codici applicato={codice} applica={setCodice} provaSu={provaSu} suRiscatto={ricarica} />
            <div className="panel">
              <h2>{k.movimenti}</h2>
              {movimenti.dati && movimenti.dati.movimenti.length === 0 && <p className="muted small">{k.nessun_movimento}</p>}
              <ul className="list-plain">
                {movimenti.dati?.movimenti.map((m, i) => (
                  <li key={i} className="button-row" style={{ justifyContent: "space-between", padding: ".5rem 0", borderBottom: "1px solid var(--line)" }}>
                    <span>{k.motivi[m.reason] ?? m.reason}<br /><small className="muted">{new Date(m.quando).toLocaleString(locale)}{m.note ? ` · ${m.note}` : ""}</small></span>
                    <b style={{ color: m.delta >= 0 ? "var(--verdigris)" : "var(--danger)" }}>{m.delta > 0 ? "+" : ""}{m.delta}</b>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}
      <section className="band band-tight"><p className="notice">{k.fiducia}</p></section>
    </>
  );
}

function Attuale({ conto, suCambio }: { conto: Conto; suCambio: () => void }) {
  const { t, locale } = useLingua();
  const k = t.prezzi;
  const { esegui, inCorso, errore } = useAzione();
  const a = conto.abbonamento;
  const quota = conto.uso?.letture_al_giorno;
  const pagato = a && a.piano !== "free";
  return (
    <div className="stat-row">
      <div><span>{k.saldo}</span><b>{conto.saldo}</b><span>{plurale(conto.saldo, k.crediti)}</span></div>
      <div>
        <span>{k.piano}</span><b style={{ fontSize: "1.3rem" }}>{a?.nome ?? k.gratuito}</b>
        {pagato && <span>{a.disdetto_il ? f(k.disdetto, { data: new Date(a.periodo_fine).toLocaleDateString(locale) }) : f(k.rinnovo, { data: new Date(a.periodo_fine).toLocaleDateString(locale) })}</span>}
        {pagato && !a.disdetto_il && (
          <div><button type="button" className="button button-quiet button-small" style={{ marginTop: ".5rem" }} disabled={inCorso}
            onClick={async () => { await esegui((tok) => disdici(tok)); suCambio(); }}>{k.disdici}</button></div>
        )}
        {errore && <p className="error">{errore}</p>}
      </div>
      <div>
        <span>{k.oggi}</span>
        <b>{quota && quota.limite ? `${quota.usati} / ${quota.limite}` : "—"}</b>
        {quota && quota.limite ? <div className="stat-bar"><span style={{ width: `${Math.min(100, (quota.usati / quota.limite) * 100)}%` }} /></div> : null}
      </div>
    </div>
  );
}

type EsitoAnteprima = { ok: AnteprimaCoupon } | { motivo: string } | null;

function Offerta({ piano, conto, codice, evidente, suCambio }: {
  piano: Piano; conto: Conto | null; codice: string | null; evidente: boolean; suCambio: () => void;
}) {
  const { t, locale, prefissoIt } = useLingua();
  const k = t.prezzi;
  const sessione = useSessione();
  const parametri = useSearchParams();
  const traccia = useTraccia();
  const { esegui, inCorso, errore } = useAzione();
  const attuale = conto?.abbonamento?.piano === piano.slug;
  const pacchetto = piano.tipo === "pacchetto";
  const gratuito = piano.prezzo_mensile === 0;
  const anteprima = useCarica<EsitoAnteprima>(async (tok) => {
    if (!codice || gratuito) return null;
    try { return { ok: await anteprimaCoupon(tok, codice, piano.slug) }; } catch (e) { return { motivo: motivoCodice(e) ?? "coupon_sconosciuto" }; }
  }, [codice, piano.slug]);
  const scontato = anteprima.dati && "ok" in anteprima.dati ? anteprima.dati.ok : null;
  const nonVale = anteprima.dati && "motivo" in anteprima.dati && codice !== null;

  const compra = async () => {
    traccia(pacchetto ? "package_selected" : "subscription_started", { piano: piano.slug });
    if (!sessione.autenticata) { sessione.entra(indirizzoV2(`${R.prezzi}${window.location.search}`, prefissoIt)); return; }
    if (gratuito) { await esegui((tok) => abbonaGratis(tok, piano.slug)); suCambio(); return; }
    const ritorno = parametri.get("ritorno");
    const qui = indirizzoV2(R.prezzi, prefissoIt);
    const r = await esegui((tok) => apriPagamento(
      tok, piano.slug, false, dentroV2(ritorno) ? `${qui}?dopo=${encodeURIComponent(ritorno!)}` : qui, scontato ? codice ?? undefined : undefined,
    ));
    if (r?.url) window.location.assign(r.url);
  };

  return (
    <article className={`plan ${evidente ? "featured" : ""}`}>
      <h3>{piano.nome}</h3>
      <p className="price">
        {gratuito ? k.gratuito : scontato ? (
          <><s style={{ fontSize: "1.2rem" }}>{euro(piano.prezzo_mensile, piano.valuta, locale)}</s> {scontato.gratis ? k.gratuito : euro(scontato.importo, piano.valuta, locale)}</>
        ) : euro(piano.prezzo_mensile, piano.valuta, locale)}
        {!pacchetto && !gratuito && <small> {k.al_mese}</small>}
      </p>
      {scontato && <p role="status">{scontato.gratis ? k.gratis_codice : k.scontato}</p>}
      {nonVale && <p>{k.non_vale}</p>}
      {piano.descrizione && <p>{piano.descrizione}</p>}
      <ul>
        <li>{pacchetto
          ? f(k.per_lettura, { n: piano.crediti_per_periodo, prezzo: euro(Math.round(piano.prezzo_mensile / Math.max(1, piano.crediti_per_periodo)), piano.valuta, locale) })
          : piano.limiti.letture_al_giorno ? f(k.al_giorno, { n: piano.limiti.letture_al_giorno }) : k.giorno_gratis}</li>
      </ul>
      <button type="button" className={`button ${evidente ? "button-brass" : "button-quiet"}`} disabled={inCorso || (attuale && !pacchetto)} onClick={compra}
        data-an="piano_scelto" data-an-piano={piano.slug}>
        {attuale && !pacchetto ? k.il_tuo : pacchetto ? k.acquista : gratuito ? k.scegli : k.abbonati}
      </button>
      {errore && <p className="error">{errore}</p>}
    </article>
  );
}

const PER_OFFERTA = new Set(["coupon_non_per_questo_piano", "coupon_azzera_abbonamento"]);
const normalizza = (s: string) => s.replace(/\s+/g, "").toUpperCase();

function Codici({ applicato, applica, provaSu, suRiscatto }: {
  applicato: string | null; applica: (c: string | null) => void; provaSu: string | null; suRiscatto: () => void;
}) {
  const { t } = useLingua();
  const k = t.prezzi;
  const { token } = useSessione();
  const [sconto, setSconto] = useState("");
  const [erroreSconto, setErroreSconto] = useState<string | null>(null);
  const [regalo, setRegalo] = useState("");
  const [esitoRegalo, setEsitoRegalo] = useState<{ buono: boolean; testo: string } | null>(null);
  const [inCorso, setInCorso] = useState(false);
  const messaggio = (e: unknown) => k.errori_codice[motivoCodice(e) ?? ""] ?? t.comune.err_richiesta;

  return (
    <div className="panel">
      <h2>{k.codici}</h2>
      {applicato ? (
        <p className="success" role="status">
          {f(k.applicato, { codice: applicato })}{" "}
          <button type="button" className="button button-quiet button-small" onClick={() => { applica(null); setSconto(""); }}>{k.togli}</button>
        </p>
      ) : (
        <form onSubmit={async (e) => {
          e.preventDefault();
          const c = normalizza(sconto);
          if (!c || !provaSu) return;
          setErroreSconto(null); setInCorso(true);
          try { await anteprimaCoupon(token, c, provaSu); applica(c); }
          catch (err) { const m = motivoCodice(err); if (m && PER_OFFERTA.has(m)) applica(c); else setErroreSconto(messaggio(err)); }
          finally { setInCorso(false); }
        }}>
          <label className="field"><span>{k.codice_sconto}</span>
            <input value={sconto} onChange={(e) => setSconto(e.target.value)} autoCapitalize="characters" autoComplete="off" spellCheck={false} maxLength={60} />
            <small>{k.codice_sconto_aiuto}</small>
          </label>
          <button type="submit" className="button button-quiet button-small" disabled={inCorso || !sconto.trim() || !provaSu}>{k.applica}</button>
          {erroreSconto && <p className="error" role="alert">{erroreSconto}</p>}
        </form>
      )}
      <form style={{ marginTop: "1.4rem" }} onSubmit={async (e) => {
        e.preventDefault();
        const c = normalizza(regalo);
        if (!c) return;
        setEsitoRegalo(null); setInCorso(true);
        try { const r = await riscattaCodice(token, c); setEsitoRegalo({ buono: true, testo: plurale(r.crediti, k.riscattato) }); setRegalo(""); suRiscatto(); }
        catch (err) { setEsitoRegalo({ buono: false, testo: messaggio(err) }); }
        finally { setInCorso(false); }
      }}>
        <label className="field"><span>{k.codice_regalo}</span>
          <input value={regalo} onChange={(e) => setRegalo(e.target.value)} autoCapitalize="characters" autoComplete="off" spellCheck={false} maxLength={60} />
          <small>{k.codice_regalo_aiuto}</small>
        </label>
        <button type="submit" className="button button-quiet button-small" disabled={inCorso || !regalo.trim()}>{k.riscatta}</button>
        {esitoRegalo && <p className={esitoRegalo.buono ? "success" : "error"} role={esitoRegalo.buono ? "status" : "alert"}>{esitoRegalo.testo}</p>}
      </form>
    </div>
  );
}

function useRitorno(suPagato: () => void) {
  const { t, prefissoIt } = useLingua();
  const k = t.prezzi;
  const parametri = useSearchParams();
  const router = useRouter();
  const { token, autenticata } = useSessione();
  const traccia = useTraccia();
  const checkout = parametri.get("checkout");
  const dopo = parametri.get("dopo");
  const [esito, setEsito] = useState<{ buono: boolean; testo: string } | null>(null);
  useEffect(() => {
    if (!checkout || !autenticata) return;
    let annullato = false;
    statoPagamento(token, checkout)
      .then((s) => {
        if (annullato) return;
        const buono = s.stato === "pagato";
        setEsito({ buono, testo: buono ? f(s.tipo === "pacchetto" ? k.pagato_pacchetto : k.pagato_piano, { nome: s.nome }) + (dentroV2(dopo) ? ` ${k.torno}` : "") : k.non_completato });
        if (buono) {
          traccia("purchase_completed", { tipo: s.tipo });
          suPagato();
          if (dentroV2(dopo)) setTimeout(() => router.push(indirizzoV2(dopo!.replace(/^\/it/, ""), prefissoIt)), 1400);
        }
      })
      .catch(() => { if (!annullato) setEsito({ buono: false, testo: k.non_verificato }); });
    return () => { annullato = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [checkout, token, autenticata]);
  return esito;
}
