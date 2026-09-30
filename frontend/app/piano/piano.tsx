"use client";

/* Crediti, pacchetti e abbonamenti. Da Personalities, con i pacchetti.
 *
 * **Il ritorno dal pagamento non si fida dell'indirizzo.** Chi torna con
 * `?checkout=…` potrebbe averlo scritto a mano: lo stato vero si chiede al
 * server, che lo cambia solo quando arriva l'evento firmato del fornitore.
 * Se il pagamento era partito da una lettura, si torna alla lettura.
 */

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  abbonaGratis, anteprimaCoupon, apriPagamento, disdici, elencaPiani, euro, leggiConto, leggiMovimenti,
  motivoCodice, statoPagamento, type AnteprimaCoupon, type Conto, type Piano,
} from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { indirizzo } from "@/lib/percorsi";
import { useAzione, useCarica, useToken } from "@/lib/usa";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";
import { SezioneCodici } from "./codici";

/* `pianiIniziali`: i piani letti dal server, perché la pagina esca già con i prezzi scritti nell'HTML — chi cerca
 * «tarot reading price» non aspetta JavaScript. Il client poi li rilegge e li aggiorna. */
export function PaginaPiano({ pianiIniziali = null }: { pianiIniziali?: Piano[] | null }) {
  const { t } = useLingua();
  return (
    <Involucro titolo={t.piano_titolo} sottotitolo={t.piano_sottotitolo}>
      <Suspense fallback={null}>
        <Contenuto iniziali={pianiIniziali} />
      </Suspense>
    </Involucro>
  );
}

function Contenuto({ iniziali }: { iniziali: Piano[] | null }) {
  const { t, locale } = useLingua();
  const conto = useCarica(leggiConto);
  const piani = useCarica(useCallback(() => elencaPiani(), []), [], { pubblico: true });
  const movimenti = useCarica(leggiMovimenti);
  const ritorno = useRitornoDalPagamento(() => {
    conto.ricarica();
    movimenti.ricarica();
  });

  const ricarica = () => {
    conto.ricarica();
    movimenti.ricarica();
  };

  const elencoPiani = piani.dati ?? iniziali ?? [];
  const pacchetti = elencoPiani.filter((p) => p.tipo === "pacchetto");
  const abbonamenti = elencoPiani.filter((p) => p.tipo === "abbonamento");
  /* Il codice sconto applicato ai prezzi (dopo averlo provato), e l'offerta a pagamento su cui provarlo. */
  const [codice, setCodice] = useState<string | null>(null);
  const provaSu = elencoPiani.find((p) => p.prezzo_mensile > 0)?.slug ?? null;

  return (
    <>
      {ritorno && <p className={ritorno.buono ? stili.avvisoBuono : stili.avviso} role="status">{ritorno.messaggio}</p>}
      {conto.errore && <p className={stili.errore}>{conto.errore}</p>}
      {conto.dati && <Attuale conto={conto.dati} suCambio={ricarica} />}

      <SezioneCodici applicato={codice} applica={setCodice} provaSu={provaSu} suRiscatto={ricarica} />

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>{t.pacchetti}</h2>
        <div className={stili.griglia}>
          {pacchetti.map((p) => <Offerta key={p.slug} piano={p} conto={conto.dati} suCambio={ricarica} codice={codice} />)}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>{t.abbonamenti}</h2>
        <div className={stili.griglia}>
          {abbonamenti.map((p) => <Offerta key={p.slug} piano={p} conto={conto.dati} suCambio={ricarica} codice={codice} />)}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>{t.movimenti_recenti}</h2>
        {movimenti.dati && movimenti.dati.movimenti.length === 0 && (
          <div className={stili.vuoto}>{t.nessun_movimento}</div>
        )}
        <ul className={stili.elenco}>
          {movimenti.dati?.movimenti.map((m, i) => (
            <li key={i} className={`pannello ${stili.riga}`}>
              <div className={stili.rigaCorpo}>
                <p className={stili.rigaTitolo}>{(t.motivi as Record<string, string>)[m.reason] ?? m.reason}</p>
                <p className={stili.rigaDettagli}>
                  {new Date(m.quando).toLocaleString(locale)}{m.note ? ` · ${m.note}` : ""}
                </p>
              </div>
              <span className={m.delta >= 0 ? stili.positivo : stili.negativo}>{m.delta > 0 ? "+" : ""}{m.delta}</span>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}

function Attuale({ conto, suCambio }: { conto: Conto; suCambio: () => void }) {
  const { t, locale } = useLingua();
  const { esegui, inCorso, errore } = useAzione();
  const a = conto.abbonamento;
  const quota = conto.uso?.letture_al_giorno;
  const pagato = a && a.piano !== "free";
  return (
    <section className={`pannello ${stili.attuale} ${stili.sezione}`}>
      <div>
        <span className={stili.etichetta}>{t.il_tuo_saldo}</span>
        <div className={stili.saldo}>
          <span className={stili.saldoNumero}>{conto.saldo}</span>
          <span className={stili.nota}>{conto.saldo === 1 ? t.credito : t.crediti}</span>
        </div>
      </div>
      <div>
        <span className={stili.etichetta}>{t.abbonamento}</span>
        <div className={stili.nome}>{a?.nome ?? t.gratuito}</div>
        {pagato && (
          <p className={stili.nota}>
            {a.disdetto_il
              ? t.disdetto_fino(new Date(a.periodo_fine).toLocaleDateString(locale))
              : t.si_rinnova(new Date(a.periodo_fine).toLocaleDateString(locale))}
          </p>
        )}
        {quota && quota.limite ? (
          <div className={stili.misura}>
            {t.letture_di_oggi}: {quota.usati} / {quota.limite}
            <div className={stili.barra}><span style={{ width: `${Math.min(100, (quota.usati / quota.limite) * 100)}%` }} /></div>
          </div>
        ) : null}
        {pagato && !a.disdetto_il && (
          <button className="bottone-secondario" disabled={inCorso} style={{ marginTop: 10 }}
            onClick={async () => { await esegui((tok) => disdici(tok)); suCambio(); }}>
            {t.disdici}
          </button>
        )}
        {errore && <p className={stili.errore}>{errore}</p>}
      </div>
    </section>
  );
}

type EsitoAnteprima = { ok: AnteprimaCoupon } | { motivo: string } | null;

function Offerta({
  piano, conto, suCambio, codice,
}: { piano: Piano; conto: Conto | null; suCambio: () => void; codice: string | null }) {
  const { t, locale, lingua } = useLingua();
  const { esegui, inCorso, errore } = useAzione();
  const parametri = useSearchParams();
  const attuale = conto?.abbonamento?.piano === piano.slug;
  const pacchetto = piano.tipo === "pacchetto";
  const gratuito = piano.prezzo_mensile === 0;
  const evidente = piano.slug === "pacchetto-15" || piano.slug === "mensile-base";

  /* Quanto costa con il codice applicato: lo dice il server (le regole sono sue), offerta per offerta. */
  const anteprima = useCarica<EsitoAnteprima>(
    useCallback(async (tok) => {
      if (!codice || gratuito) return null;
      try {
        return { ok: await anteprimaCoupon(tok, codice, piano.slug) };
      } catch (e) {
        return { motivo: motivoCodice(e) ?? "coupon_sconosciuto" };
      }
    }, [codice, piano.slug, gratuito]),
    [codice, piano.slug],
  );
  const scontato = anteprima.dati && "ok" in anteprima.dati ? anteprima.dati.ok : null;
  const nonValeQui = anteprima.dati && "motivo" in anteprima.dati && codice !== null;

  const compra = async () => {
    if (gratuito) {
      await esegui((tok) => abbonaGratis(tok, piano.slug));
      suCambio();
      return;
    }
    /* Si torna sempre a questa pagina, nella lingua di chi ha pagato (`/pricing` o `/it/piano`): il vecchio `/piano`
     * senza prefisso porterebbe all'italiano. */
    const ritorno = parametri.get("ritorno");
    const qui = indirizzo(lingua, "/piano");
    const r = await esegui((tok) =>
      apriPagamento(
        tok, piano.slug, false, ritorno && ritorno.startsWith("/") ? `${qui}?dopo=${encodeURIComponent(ritorno)}` : qui,
        scontato ? codice ?? undefined : undefined,
      ),
    );
    if (r?.url) window.location.assign(r.url);
  };

  return (
    <div className={`pannello ${stili.scheda} ${evidente ? stili.schedaEvidente : ""}`}>
      <span className={stili.nome}>{piano.nome}</span>
      <span className={stili.prezzo}>
        {gratuito ? t.gratis : scontato ? (
          <>
            <s className={stili.nota}>{euro(piano.prezzo_mensile, piano.valuta, locale)}</s>{" "}
            {scontato.gratis ? t.gratis : euro(scontato.importo, piano.valuta, locale)}
          </>
        ) : euro(piano.prezzo_mensile, piano.valuta, locale)}
        {!pacchetto && !gratuito && <span className={stili.nota}> {t.al_mese}</span>}
      </span>
      {scontato && <p className={stili.nota} role="status">{scontato.gratis ? t.codice_gratis : t.codice_prezzo_scontato}</p>}
      {nonValeQui && <p className={stili.nota}>{t.codice_non_per_questa}</p>}
      <p className={stili.nota}>{piano.descrizione}</p>
      {pacchetto ? (
        <p className={stili.nota}>{t.crediti_a_lettura(piano.crediti_per_periodo, euro(Math.round(piano.prezzo_mensile / piano.crediti_per_periodo), piano.valuta, locale))}</p>
      ) : (
        <p className={stili.nota}>{piano.limiti.letture_al_giorno ? t.letture_al_giorno(piano.limiti.letture_al_giorno) : t.carta_giorno_gratuita}</p>
      )}
      <button className={evidente ? "bottone" : "bottone-secondario"} disabled={inCorso || (attuale && !pacchetto)} onClick={compra}
        data-an="piano_scelto" data-an-piano={piano.slug}>
        {attuale && !pacchetto ? t.il_tuo_piano : pacchetto ? t.acquista : gratuito ? t.scegli : t.abbonati}
      </button>
      {errore && <p className={stili.errore}>{errore}</p>}
    </div>
  );
}

function useRitornoDalPagamento(suPagato: () => void) {
  const { t } = useLingua();
  const parametri = useSearchParams();
  const router = useRouter();
  const token = useToken();
  const checkout = parametri.get("checkout");
  const dopo = parametri.get("dopo");
  const [esito, setEsito] = useState<{ buono: boolean; messaggio: string } | null>(null);

  useEffect(() => {
    if (!checkout) return;
    let annullato = false;
    statoPagamento(token, checkout)
      .then((s) => {
        if (annullato) return;
        const buono = s.stato === "pagato";
        setEsito({
          buono,
          messaggio: buono
            ? s.tipo === "pacchetto"
              ? t.pagamento_pacchetto(s.nome)
              : t.pagamento_piano(s.nome)
            : t.pagamento_non_completato,
        });
        if (buono) {
          suPagato();
          if (dopo && dopo.startsWith("/")) setTimeout(() => router.push(dopo), 1400);
        }
      })
      .catch(() => { if (!annullato) setEsito({ buono: false, messaggio: t.pagamento_non_verificato }); });
    return () => { annullato = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [checkout, token]);

  return esito;
}
