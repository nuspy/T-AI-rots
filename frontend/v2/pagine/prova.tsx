"use client";

/* La pagina della prova gratuita (v9, Fase 2b): tutto quello che serve sapere prima di cominciare, detto in chiaro —
 * quando si paga (alla fine, non prima), quanto (l'annuale del livello scelto col −50% per sempre), come si disdice
 * (dal profilo, e durante la prova non si paga nulla), il promemoria due giorni prima. Il «−50% per sempre» è il
 * vantaggio grande, e lo si dice grande. Si sceglie il livello, si registra il metodo di pagamento con Stripe.
 *
 * Chi non ha un account passa dalla registrazione e torna qui; chi ha già usato la prova (o è abbonato) lo legge
 * subito, con il collegamento ai prezzi. Il ritorno dal pagamento (`?checkout=`) dice com'è andata. */

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTraccia } from "lanterna-osservatore/react";
import { euro, motivoCodice, statoPagamento, type Piano } from "@/lib/api";
import { iniziaProva } from "@/lib/abbonamenti";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { useConto, usePiani } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useImpostazioniProva } from "@/v2/lib/prova";
import { anteprimaCouponPubblica, useCouponAttivo, voceCoupon } from "@/v2/lib/coupon";
import { useAzione, useCarica } from "@/v2/lib/usa";

export function ProvaGratuita({ pianiIniziali }: { pianiIniziali: Piano[] }) {
  return <Suspense fallback={null}><Contenuto pianiIniziali={pianiIniziali} /></Suspense>;
}

function Contenuto({ pianiIniziali }: { pianiIniziali: Piano[] }) {
  const { t, locale, prefissoIt } = useLingua();
  const k = t.abbonamento;
  const sessione = useSessione();
  const impostazioni = useImpostazioniProva();
  const piani = usePiani();
  const conto = useConto();
  const traccia = useTraccia();
  const { esegui, inCorso, errore } = useAzione();
  const esito = useRitornoProva();
  const elenco = (piani.dati ?? pianiIniziali).filter((p) => p.tipo === "abbonamento" && p.prezzo_annuale > 0);
  const [scelto, setScelto] = useState<string | null>(null);
  const piano = elenco.find((p) => p.slug === scelto) ?? elenco[elenco.length - 1] ?? null;

  const giorni = impostazioni?.giorni_prova ?? 14;
  const sconto = impostazioni?.sconto_prova ?? 50;
  const valori = { giorni, sconto, giorni_promemoria: impostazioni?.giorni_promemoria_prova ?? 2 };
  const idonea = !sessione.autenticata || (conto.dati?.prova?.idonea ?? true);
  const disponibile = impostazioni?.prova_disponibile ?? true;
  const qui = indirizzoV2(R.prova, prefissoIt);
  /* Fase 2d: il codice del link (o della sessione) vale anche sulla prova: sulla conversione, secondo il cumulo. */
  const [codice] = useCouponAttivo();
  const coupon = useCarica(async (tok) => {
    if (!codice) return null;
    try { return { ok: await anteprimaCouponPubblica(tok, codice) }; } catch (e) { return { motivo: motivoCodice(e) ?? "coupon_sconosciuto" }; }
  }, [codice], { pubblico: true });
  const anteprima = coupon.dati && "ok" in coupon.dati ? coupon.dati.ok : null;
  const motivoCoupon = coupon.dati && "motivo" in coupon.dati ? coupon.dati.motivo : null;
  const voce = piano ? voceCoupon(anteprima, piano.slug, true, false, true) : null;

  const inizia = async () => {
    if (!piano) return;
    traccia("trial_started", { piano: piano.slug });
    const r = await esegui((tok) => iniziaProva(tok, piano.slug, qui, voce?.applicato ? codice ?? undefined : undefined));
    if (r?.url) window.location.assign(r.url);
  };

  return (
    <>
      <section className="band band-tight prova-testa">
        <p className="eyebrow">{k.prova_eyebrow}</p>
        <h1 className="section-title">{f(k.prova_titolo, valori)}</h1>
        <p className="section-intro">{f(k.prova_intro, valori)}</p>
        {esito && <p className={esito.buono ? "success" : "error"} role="status">{esito.testo}</p>}
      </section>

      <section className="band band-tight prova-corpo" aria-labelledby="prova-vantaggio">
        <div className="prova-vantaggio">
          <p className="prova-vantaggio-numero" aria-hidden="true">−{sconto}%</p>
          <div>
            <h2 id="prova-vantaggio">{f(k.prova_vantaggio_titolo, valori)}</h2>
            <p>{f(k.prova_vantaggio_testo, valori)}</p>
          </div>
        </div>

        <div className="prova-griglia">
          <div className="panel">
            <h2>{k.prova_come_titolo}</h2>
            <ol className="prova-passi">
              <li>{f(k.prova_passo_oggi, { zero: euro(0, piano?.valuta ?? "EUR", locale) })}</li>
              <li>{f(k.prova_passo_promemoria, valori)}</li>
              <li>{f(k.prova_passo_fine, valori)}</li>
              <li>{k.prova_passo_disdici}</li>
            </ol>
            <p className="small muted">{k.prova_onesta}</p>
          </div>

          <div className="panel">
            <h2>{k.prova_scegli}</h2>
            {elenco.length > 0 && (
              <div className="prova-livelli" role="radiogroup" aria-label={k.prova_scegli}>
                {elenco.map((p) => {
                  const dopo = p.prezzi?.prova_annuale ?? Math.round(p.prezzo_annuale * (100 - sconto) / 100);
                  const attivo = piano?.slug === p.slug;
                  return (
                    <button key={p.slug} type="button" role="radio" aria-checked={attivo}
                      className={`prova-livello${attivo ? " attivo" : ""}`} onClick={() => setScelto(p.slug)}>
                      <span className="prova-livello-nome">{p.nome}</span>
                      <span className="prova-livello-prezzi">
                        <s aria-label={k.prova_listino}>{euro(p.prezzo_annuale, p.valuta, locale)}</s>{" "}
                        <b>{euro(dopo, p.valuta, locale)}</b> <small>{k.al_anno}</small>
                      </span>
                      <span className="prova-livello-nota">{k.prova_dopo}</span>
                    </button>
                  );
                })}
              </div>
            )}

            {!disponibile ? (
              <p className="notice">{k.prova_non_disponibile}</p>
            ) : !sessione.pronta ? null : !sessione.autenticata ? (
              <div className="prova-azione">
                <p className="small">{k.prova_entra_testo}</p>
                <button type="button" className="button button-brass" onClick={() => sessione.registratiPoi(qui)}
                  data-an="trial_registrati">{k.prova_entra}</button>
              </div>
            ) : !idonea ? (
              <div className="prova-azione">
                <p className="notice">{k.prova_non_idonea}</p>
                <LinkV2 className="button button-quiet" href={R.prezzi}>{k.prova_vai_prezzi}</LinkV2>
              </div>
            ) : (
              <div className="prova-azione">
                <button type="button" className="button button-brass" disabled={inCorso || !piano} onClick={inizia}
                  data-an="trial_inizia">{piano ? f(k.prova_cta, { piano: piano.nome }) : k.prova_eyebrow}</button>
              </div>
            )}
            {codice && motivoCoupon && (
              <p className="small coupon-nota" role="status">
                {codice}: {t.prezzi.errori_codice[motivoCoupon] ?? t.prezzi.non_vale}
              </p>
            )}
            {codice && voce && piano && (
              <p className="small coupon-nota" role="status">
                {voce.motivo ? t.prezzi.errori_codice[voce.motivo] ?? t.prezzi.non_vale
                  : voce.applicato ? f(t.prezzi.coupon.nella_prova, {
                    codice, prezzo: euro((voce.listino ?? 0) - (voce.sconto_ricorrente ?? 0), piano.valuta, locale),
                    listino: euro((voce.listino ?? 0) - (voce.sconto_base ?? 0), piano.valuta, locale),
                  }) : f(t.prezzi.coupon.nella_prova_no, { codice })}
              </p>
            )}
            {errore && <p className="error" role="alert">{errore}</p>}
          </div>
        </div>
      </section>
    </>
  );
}

function useRitornoProva() {
  const { t } = useLingua();
  const k = t.abbonamento;
  const parametri = useSearchParams();
  const { token, autenticata } = useSessione();
  const checkout = parametri.get("checkout");
  const [esito, setEsito] = useState<{ buono: boolean; testo: string } | null>(null);
  useEffect(() => {
    if (!checkout || !autenticata) return;
    let annullato = false;
    statoPagamento(token, checkout)
      .then((s) => {
        if (annullato) return;
        if (s.esito) setEsito({ buono: false, testo: k.prova_rifiutata });
        else if (s.stato === "pagato") setEsito({ buono: true, testo: k.prova_attivata });
        else setEsito({ buono: false, testo: t.prezzi.non_completato });
      })
      .catch(() => { if (!annullato) setEsito({ buono: false, testo: t.prezzi.non_verificato }); });
    return () => { annullato = true; };
  }, [checkout, token, autenticata, k.prova_rifiutata, k.prova_attivata, t.prezzi.non_completato, t.prezzi.non_verificato]);
  return esito;
}
