"use client";

/* I prezzi nella v2 (specifica v2, §4-5): il cuore del modello — letture, pacchetti, abbonamenti — presentato come
 * continuità, dopo il valore, non come un cancello. I piani, i prezzi e i diritti vengono dall'API (niente cifre
 * inventate). Il ritorno dal pagamento si verifica sul server; se il pagamento era partito da una lettura, si torna
 * alla lettura. */

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTraccia } from "lanterna-osservatore/react";
import {
  abbonaGratis, apriPagamento, euro, impostazioniPubbliche, leggiMovimenti, motivoCodice, riscattaCodice, statoPagamento, type Conto, type Piano,
} from "@/lib/api";
import { BandaCoupon, RigheCoupon, etichettaSconto, type EsitoCoupon } from "@/v2/componenti/coupon-prezzi";
import {
  anteprimaCouponPubblica, normalizzaCodice, useCouponAttivo, voceCoupon, type AnteprimaCouponPubblica,
} from "@/v2/lib/coupon";
import { apriAbbonamento, motivoErrore } from "@/lib/abbonamenti";
import { useSessione } from "@/lib/sessione";
import { CambioPiano } from "@/v2/componenti/cambio-piano";
import { useImpostazioniProva } from "@/v2/lib/prova";
import { f, plurale } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { ConPubblicita } from "@/v2/componenti/pubblicita";
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
  /* Il codice del link (`?coupon=`) o della sessione, e i suoi conti su tutte le offerte (anche senza account). */
  const [codice, setCodice] = useCouponAttivo();
  const coupon = useCarica<EsitoCoupon | null>(async (tok) => {
    if (!codice) return null;
    try { return { ok: await anteprimaCouponPubblica(tok, codice) }; } catch (e) { return { motivo: motivoCodice(e) ?? "coupon_sconosciuto" }; }
  }, [codice], { pubblico: true });
  const anteprima = coupon.dati && "ok" in coupon.dati ? coupon.dati.ok : null;
  const ricarica = () => { conto.ricarica(); movimenti.ricarica(); };
  const esito = useRitorno(() => { ricarica(); setCodice(null); });

  const elenco = piani.dati ?? [];
  const pacchetti = elenco.filter((p) => p.tipo === "pacchetto");
  const abbonamenti = elenco.filter((p) => p.tipo === "abbonamento" && p.prezzo_mensile > 0);
  const provaSu = elenco.find((p) => p.prezzo_mensile > 0)?.slug ?? null;

  return (
    <>
      {esito && <section className="band band-tight" style={{ paddingBottom: 0 }}><p className={esito.buono ? "success" : "error"} role="status">{esito.testo}</p></section>}
      {conto.dati && <section className="band band-tight" style={{ paddingBottom: 0 }}><Attuale conto={conto.dati} /></section>}
      {codice && coupon.dati && (
        <section className="band band-tight" style={{ paddingBottom: 0 }} aria-live="polite">
          <BandaCoupon codice={codice} esito={coupon.dati} valuta={elenco[0]?.valuta} onTogli={() => setCodice(null)} />
        </section>
      )}

      {/* Gli spazi pubblicitari (spenti per default) fra i blocchi: pacchetti, abbonamenti, conto; la fine prima della
          nota di fiducia che chiude la pagina. */}
      <ConPubblicita>
        <section key="pacchetti" className="band band-tight" aria-labelledby="titolo-pacchetti">
          <div className="pricing-grid">
            <article className="plan">
              <h2>{k.gratis_titolo}</h2>
              <p className="price">{k.gratis_prezzo}</p>
              <p>{k.gratis_testo}</p>
              <ul>{k.gratis_voci.map((v) => <li key={v}>{f(v, { n: omaggi.dati?.crediti_iscrizione ?? 3 })}</li>)}</ul>
              <LinkV2 className="button button-quiet" href={`${R.leggi}?source=pricing`}>{k.gratis_cta}</LinkV2>
            </article>
            {pacchetti.map((p, i) => <Offerta key={p.slug} piano={p} conto={conto.dati} codice={codice} anteprima={anteprima} evidente={i === Math.floor(pacchetti.length / 2)} suCambio={ricarica} />)}
          </div>
          <h2 id="titolo-pacchetti" className="sr-only">{k.pacchetti}</h2>
          <p className="small muted" style={{ marginTop: "1rem" }}>{k.pacchetti_testo}</p>
        </section>

        {abbonamenti.length > 0 && (
          <section key="abbonamenti" className="band band-tight" aria-labelledby="titolo-abbonamenti">
            <h2 id="titolo-abbonamenti" className="section-title">{k.abbonamenti}</h2>
            <p className="section-intro">{k.abbonamenti_testo}</p>
            <Abbonamenti piani={abbonamenti} conto={conto.dati} codice={codice} anteprima={anteprima} />
          </section>
        )}
        {piani.errore && <section key="errore" className="band band-tight"><p className="error">{piani.errore}</p></section>}

        {sessione.autenticata && (
          <section key="conto" className="band band-tight">
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
      </ConPubblicita>
      <section className="band band-tight"><p className="notice">{k.fiducia}</p></section>
    </>
  );
}

function Attuale({ conto }: { conto: Conto }) {
  const { t, locale } = useLingua();
  const k = t.prezzi;
  const a = conto.abbonamento;
  const quota = conto.uso?.letture_al_giorno;
  const pagato = a && a.piano !== "free";
  return (
    <div className="stat-row">
      <div><span>{k.saldo}</span><b>{conto.saldo}</b><span>{plurale(conto.saldo, k.crediti)}</span></div>
      <div>
        <span>{k.piano}</span><b style={{ fontSize: "1.3rem" }}>{a?.nome ?? k.gratuito}</b>
        {pagato && <span>{a.disdetto_il ? f(k.disdetto, { data: new Date(a.periodo_fine).toLocaleDateString(locale) }) : f(k.rinnovo, { data: new Date(a.periodo_fine).toLocaleDateString(locale) })}</span>}
        {/* Il rinnovo automatico si spegne dal profilo, con la conferma formale (v9, Fase 2b). */}
        {pagato && (
          <div><LinkV2 className="button button-quiet button-small" style={{ marginTop: ".5rem" }} href={`${R.profilo}#abbonamento`}>
            {t.abbonamento.rinnovo_titolo}</LinkV2></div>
        )}
      </div>
      <div>
        <span>{k.oggi}</span>
        <b>{quota && quota.limite ? `${quota.usati} / ${quota.limite}` : "—"}</b>
        {quota && quota.limite ? <div className="stat-bar"><span style={{ width: `${Math.min(100, (quota.usati / quota.limite) * 100)}%` }} /></div> : null}
      </div>
    </div>
  );
}

function Offerta({ piano, conto, codice, anteprima, evidente, suCambio }: {
  piano: Piano; conto: Conto | null; codice: string | null; anteprima: AnteprimaCouponPubblica | null; evidente: boolean;
  suCambio: () => void;
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
  /* Fase 2d: il prezzo col codice viene dall'anteprima di tutte le offerte (`/coupon/anteprima`). */
  const voce = codice && !gratuito ? voceCoupon(anteprima, piano.slug, false, false) : null;
  const scontato = voce?.applicato && voce.importo !== undefined
    ? { importo: voce.importo, gratis: voce.importo === 0 } : null;

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
          <><s className="prezzo-barrato">{euro(piano.prezzo_mensile, piano.valuta, locale)}</s> {scontato.gratis ? k.gratuito : euro(scontato.importo, piano.valuta, locale)}</>
        ) : euro(piano.prezzo_mensile, piano.valuta, locale)}
        {!pacchetto && !gratuito && <small> {k.al_mese}</small>}
      </p>
      {scontato?.gratis && <p role="status">{k.gratis_codice}</p>}
      <RigheCoupon voce={voce} valuta={piano.valuta} />
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

/* Gli abbonamenti (v9, Fase 2b): mensile o annuale, col rinnovo automatico (acceso per default, −20%) o senza
 * (listino, un periodo). Il prezzo grande è quello che si paga davvero; il listino barrato e lo sconto si vedono
 * accanto. La prova gratuita ha la sua banda per chi può ancora usarla. Chi è già abbonato cambia piano col
 * conguaglio (`CambioPiano`), non ne apre un secondo. */
function Abbonamenti({ piani, conto, codice, anteprima }: {
  piani: Piano[]; conto: Conto | null; codice: string | null; anteprima: AnteprimaCouponPubblica | null;
}) {
  const { t, locale, prefissoIt } = useLingua();
  const k = t.abbonamento;
  const kp = t.prezzi;
  const sessione = useSessione();
  const parametri = useSearchParams();
  const traccia = useTraccia();
  const impostazioni = useImpostazioniProva();
  const { esegui, inCorso, errore } = useAzione();
  const [annuale, setAnnuale] = useState(false);
  const [rinnovo, setRinnovo] = useState(true);
  const [cambio, setCambio] = useState<Piano | null>(null);
  const [motivo, setMotivo] = useState<string | null>(null);
  const sconto = impostazioni?.sconto_rinnovo ?? 20;
  const attuale = conto?.abbonamento && conto.abbonamento.piano !== "free" ? conto.abbonamento : null;
  const provaPossibile = (impostazioni?.prova_disponibile ?? false) && (!sessione.autenticata || (conto?.prova?.idonea ?? false));
  const conAnnuale = piani.some((p) => p.prezzo_annuale > 0);

  const abbonati = async (piano: Piano) => {
    traccia("subscription_started", { piano: piano.slug, annuale, rinnovo });
    if (!sessione.autenticata) { sessione.entra(indirizzoV2(`${R.prezzi}${window.location.search}`, prefissoIt)); return; }
    if (attuale) { setCambio(piano); return; }
    setMotivo(null);
    const ritorno = parametri.get("ritorno");
    const qui = indirizzoV2(R.prezzi, prefissoIt);
    const r = await esegui(async (tok) => {
      try {
        return await apriAbbonamento(tok, piano.slug, annuale, rinnovo, dentroV2(ritorno) ? `${qui}?dopo=${encodeURIComponent(ritorno!)}` : qui, codice ?? undefined);
      } catch (e) {
        setMotivo(motivoErrore(e));
        throw e;
      }
    });
    if (r?.url) window.location.assign(r.url);
  };

  return (
    <>
      {provaPossibile && impostazioni && (
        <div className="prova-banda">
          <div>
            <p className="prova-banda-titolo">{f(k.prova_banda_titolo, { giorni: impostazioni.giorni_prova })}</p>
            <p className="small">{f(k.prova_banda_testo, { sconto: impostazioni.sconto_prova })}</p>
          </div>
          <LinkV2 className="button button-brass button-small" href={R.prova} data-an="prezzi_prova">{k.prova_banda_cta}</LinkV2>
        </div>
      )}

      <div className="abbonamenti-comandi">
        {conAnnuale && (
          <div className="chips" role="radiogroup" aria-label={k.scegli_periodo}>
            <button type="button" role="radio" aria-checked={!annuale} className={`chip${!annuale ? " active" : ""}`} onClick={() => setAnnuale(false)}>{k.periodo_mensile}</button>
            <button type="button" role="radio" aria-checked={annuale} className={`chip${annuale ? " active" : ""}`} onClick={() => setAnnuale(true)}>{k.periodo_annuale}</button>
          </div>
        )}
        {!attuale && (
          <label className="interruttore">
            <input type="checkbox" role="switch" checked={rinnovo} onChange={(e) => setRinnovo(e.target.checked)} />
            <span><b>{k.rinnovo_prezzi}</b> <small className="muted">{f(k.rinnovo_prezzi_testo, { sconto })}</small></span>
          </label>
        )}
      </div>

      <div className="pricing-grid">
        {piani.map((p) => {
          const voce = annuale ? p.prezzi?.annuale : p.prezzi?.mensile;
          const listino = annuale ? p.prezzo_annuale : p.prezzo_mensile;
          if (annuale && listino <= 0) return null;
          const conSconto = voce?.con_rinnovo ?? listino;
          // Fase 2d: col codice il prezzo è quello dell'anteprima (rinnovo e coupon secondo il cumulo). Non vale per
          // chi è già abbonato: un cambio di piano ha il suo conguaglio, senza codice.
          const conCodice = codice && !attuale ? voceCoupon(anteprima, p.slug, annuale, rinnovo) : null;
          const mostrato = conCodice?.applicato && conCodice.importo !== undefined
            ? conCodice.importo : rinnovo || attuale ? conSconto : listino;
          const suo = attuale?.piano === p.slug && !!attuale.annuale === annuale;
          // Ritocco della Fase 4: quando vince lo sconto del codice, il bollino del rinnovo (−20%) non vale su questo
          // prezzo e confondeva; al suo posto il bollino del codice.
          const vinceCodice = !!conCodice?.applicato && conCodice.vince === "coupon" && !!anteprima;
          return (
            <article key={p.slug} className="plan plan-abbonamento">
              {vinceCodice && anteprima
                ? <p className="badge-offer">{f(kp.coupon.badge, { sconto: etichettaSconto(anteprima.coupon, p.valuta, locale) })}</p>
                : rinnovo && conSconto < listino && <p className="badge-offer">{f(k.badge_rinnovo, { sconto })}</p>}
              <h3>{p.nome}</h3>
              <p className="price">
                {mostrato < listino && <><s className="prezzo-barrato">{euro(listino, p.valuta, locale)}</s>{" "}</>}
                {euro(mostrato, p.valuta, locale)}
                <small> {annuale ? k.al_anno : kp.al_mese}</small>
              </p>
              <RigheCoupon voce={conCodice} valuta={p.valuta} perPeriodo={` ${annuale ? k.al_anno : kp.al_mese}`} />
              <p className="small">{rinnovo ? k.con_rinnovo : f(k.senza_rinnovo, { prezzo: euro(listino, p.valuta, locale) })}</p>
              {p.descrizione && <p>{p.descrizione}</p>}
              <ul>
                {p.limiti.letture_al_giorno ? <li>{f(kp.al_giorno, { n: p.limiti.letture_al_giorno })}</li> : <li>{kp.giorno_gratis}</li>}
              </ul>
              <button type="button" className="button button-brass" disabled={inCorso || suo} onClick={() => abbonati(p)}
                data-an="piano_scelto" data-an-piano={p.slug}>
                {suo ? kp.il_tuo : attuale ? k.passa : kp.abbonati}
              </button>
            </article>
          );
        })}
      </div>
      {motivo === "fattura_aperta" && (
        <p className="notice">{k.sospeso_testo} <LinkV2 className="inline" href={`${R.profilo}#abbonamento`}>{k.sistema}</LinkV2></p>
      )}
      {errore && motivo !== "fattura_aperta" && <p className="error" role="alert">{errore}</p>}
      {cambio && (
        <CambioPiano piano={cambio} annuale={annuale} scontoRinnovo={sconto} onChiudi={() => setCambio(null)} />
      )}
    </>
  );
}

const normalizza = normalizzaCodice;

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
          // Fase 2d: le regole del codice (e della persona) sull'anteprima di tutte le offerte; quelle della singola
          // offerta si vedono poi offerta per offerta.
          try { await anteprimaCouponPubblica(token, c); applica(c); }
          catch (err) { setErroreSconto(messaggio(err)); }
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
      <form style={{ marginTop: ".5rem" }} onSubmit={async (e) => {
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
