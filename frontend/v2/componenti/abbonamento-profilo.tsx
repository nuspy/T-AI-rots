"use client";

/* La sezione «Abbonamento» del profilo (v9, Fase 2b): stato, periodo pagato, rinnovo automatico con l'interruttore,
 * il prossimo addebito, il downgrade programmato, la prova, e «Sistema il pagamento» quando un rinnovo non è andato.
 *
 * Spegnere il rinnovo apre un dialogo di conferma formale (il server manda poi l'email di conferma); riaccenderlo è
 * un clic, fino alla scadenza. Un abbonamento degli store mostra solo la spiegazione e il link allo store. */

import { useState } from "react";
import { euro } from "@/lib/api";
import {
  annullaCambio, impostaRinnovo, mioAbbonamento, pagamentoDaSistemare, type AbbonamentoDettaglio,
} from "@/lib/abbonamenti";
import { f, plurale } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { Modale } from "@/v2/componenti/modale";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";

export function AbbonamentoProfilo() {
  const { t, locale, lingua } = useLingua();
  const k = t.abbonamento;
  const dati = useCarica((tok) => mioAbbonamento(tok, lingua), [lingua]);
  const { esegui, inCorso, errore } = useAzione();
  const [conferma, setConferma] = useState(false);
  const [esito, setEsito] = useState<string | null>(null);
  const [pagamento, setPagamento] = useState<string | null>(null);

  const a = dati.dati?.abbonamento ?? null;
  const imp = dati.dati?.impostazioni;
  const data = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" }) : "");
  const soldi = (c: number | null, valuta = a?.valuta ?? "EUR") => euro(c ?? 0, valuta, locale);

  const rinnovo = async (attivo: boolean) => {
    setConferma(false);
    const r = await esegui((tok) => impostaRinnovo(tok, attivo, lingua));
    if (r) { setEsito(attivo ? k.acceso_ok : k.spento_ok); dati.ricarica(); }
  };
  const sistema = async () => {
    setPagamento(null);
    const r = await esegui((tok) => pagamentoDaSistemare(tok));
    if (r?.url) window.location.assign(r.url);
    else if (r?.gia_pagata) setPagamento(k.sistema_pagata);
  };

  return (
    <section className="panel abbonamento-profilo wide" id="abbonamento" aria-labelledby="abbonamento-t">
      <h2 id="abbonamento-t">{k.sezione_titolo}</h2>
      {dati.errore && <p className="error">{dati.errore}</p>}
      {dati.dati && (!a || a.gratuito) && (
        <>
          <p className="small">{k.nessuno}</p>
          <div className="button-row">
            {dati.dati.prova.idonea && imp && (
              <LinkV2 className="button button-brass button-small" href={R.prova}>{f(k.prova_cta_profilo, { giorni: imp.giorni_prova })}</LinkV2>
            )}
            <LinkV2 className="button button-quiet button-small" href={R.prezzi}>{k.vedi_piani}</LinkV2>
          </div>
        </>
      )}
      {a && !a.gratuito && imp && (
        <Dettaglio a={a} sconto={a.prova ? imp.sconto_prova : imp.sconto_rinnovo} data={data} soldi={soldi}
          inCorso={inCorso}
          onSpegni={() => setConferma(true)} onAccendi={() => rinnovo(true)} onSistema={sistema}
          onAnnullaCambio={async () => { if (await esegui((tok) => annullaCambio(tok, lingua))) dati.ricarica(); }} />
      )}
      {esito && <p className="success" role="status">{esito}</p>}
      {pagamento && <p className="notice" role="status">{pagamento}</p>}
      {errore && <p className="error" role="alert">{errore}</p>}

      {a && conferma && (
        <Modale aperta titolo={k.conferma_titolo} onChiudi={() => setConferma(false)}>
          <p className="prose">{f(k.conferma_testo, { piano: a.nome, data: data(a.periodo_fine) })}</p>
          <div className="button-row">
            <button type="button" className="button button-danger" disabled={inCorso} onClick={() => rinnovo(false)}
              data-an="rinnovo_spento">{k.conferma_si}</button>
            <button type="button" className="button button-brass" autoFocus onClick={() => setConferma(false)}>{k.conferma_no}</button>
          </div>
        </Modale>
      )}
    </section>
  );
}

function Dettaglio({
  a, sconto, data, soldi, inCorso, onSpegni, onAccendi, onSistema, onAnnullaCambio,
}: {
  a: AbbonamentoDettaglio;
  sconto: number;
  data: (iso: string | null) => string;
  soldi: (c: number | null) => string;
  inCorso: boolean;
  onSpegni: () => void;
  onAccendi: () => void;
  onSistema: () => void;
  onAnnullaCambio: () => void;
}) {
  const { t } = useLingua();
  const k = t.abbonamento;
  const stato = k[`stato_${a.stato}` as const] ?? a.stato;
  const nomeStore = a.provider === "app_store" ? k.store_app_store : k.store_google_play;
  const vivo = a.stato === "attivo" || a.stato === "in_prova" || a.stato === "in_sospeso";

  return (
    <div className="abbonamento-dettaglio">
      <p className="abbonamento-testa">
        <strong>{a.nome}</strong>
        <span className={`stato-abbonamento stato-${a.stato}`}>{stato}</span>
        <span className="muted small">{a.annuale ? k.annuale : k.mensile}</span>
      </p>
      {a.stato === "in_prova"
        ? <p className="small">{f(k.prova_fino, { data: data(a.periodo_fine), importo: soldi(a.prossimo_rinnovo ?? a.listino), sconto })}</p>
        : <p className="small">{f(k.periodo_fino, { data: data(a.periodo_fine) })}</p>}

      {a.store ? (
        /* v9, Fase 4: un abbonamento di Google Play o dell'App Store si gestisce là. Qui lo stato com'è presso lo store
         * (tolleranza, sospensione, rinnovo spento) e il link, senza i nostri interruttori di disdetta o di cambio. */
        <div className={`notice${a.stato === "in_sospeso" || a.stato === "sospeso" ? " notice-pagamento" : ""}`}
          role={a.stato === "in_sospeso" || a.stato === "sospeso" ? "status" : undefined}>
          {a.stato === "in_sospeso" && <p style={{ margin: "0 0 .6rem" }}>{f(k.store_tolleranza, { store: nomeStore })}</p>}
          {a.stato === "sospeso" && <p style={{ margin: "0 0 .6rem" }}>{f(k.store_sospeso, { store: nomeStore })}</p>}
          {vivo && (
            <p style={{ margin: "0 0 .6rem" }}>
              {a.rinnovo_automatico ? f(k.store_rinnovo, { store: nomeStore })
                : f(k.store_disdetto, { store: nomeStore, data: data(a.periodo_fine) })}
            </p>
          )}
          <p className="small" style={{ margin: "0 0 .6rem" }}>{f(k.store_testo, { store: nomeStore })} {f(k.store_nota, { store: nomeStore })}</p>
          {a.gestione_store && (
            <a className="button button-brass button-small" href={a.gestione_store} target="_blank" rel="noopener noreferrer"
              data-an="gestisci_store">
              {f(k.store_gestisci, { store: nomeStore })}
            </a>
          )}
        </div>
      ) : (
        <>
          {(a.stato === "in_sospeso" || a.stato === "sospeso") && (
            <div className="notice notice-pagamento" role="status">
              <p style={{ margin: "0 0 .6rem" }}>
                {a.stato === "in_sospeso" ? f(k.tolleranza, { data: data(a.fine_tolleranza) }) : k.sospeso_testo}
              </p>
              {a.fattura_aperta && (
                <>
                  <button type="button" className="button button-brass button-small" disabled={inCorso} onClick={onSistema}
                    data-an="sistema_pagamento">{k.sistema}</button>
                  <p className="small muted" style={{ margin: ".5rem 0 0" }}>{k.sistema_nota}</p>
                </>
              )}
            </div>
          )}
          {vivo && (
            <div className="rinnovo-automatico">
              <h3>{k.rinnovo_titolo}</h3>
              <label className="interruttore">
                <input type="checkbox" role="switch" checked={a.rinnovo_automatico} disabled={inCorso}
                  onChange={(e) => (e.target.checked ? onAccendi() : onSpegni())} />
                <span>{k.rinnovo_interruttore}</span>
              </label>
              <p className="small">
                {a.rinnovo_automatico
                  ? <>{f(k.rinnovo_acceso, { data: data(a.periodo_fine), importo: soldi(a.prossimo_rinnovo) })}{a.sconto_ricorrente > 0 ? ` ${k.rinnovo_acceso_sconto}` : ""}</>
                  : f(k.rinnovo_spento, { data: data(a.periodo_fine) })}
              </p>
              {a.coupon && (
                <p className="small coupon-nota">
                  {a.coupon.per_sempre ? f(k.coupon_sempre, { codice: a.coupon.codice })
                    : f(plurale(a.coupon.rinnovi_rimasti ?? 0, k.coupon_rinnovi), { codice: a.coupon.codice })}
                </p>
              )}
            </div>
          )}
          {a.piano_successivo && (
            <p className="small">
              {f(k.successivo, { data: data(a.piano_successivo.dal), piano: a.piano_successivo.nome, periodo: a.piano_successivo.annuale ? k.annuale : k.mensile })}{" "}
              <button type="button" className="button button-quiet button-small" disabled={inCorso} onClick={onAnnullaCambio}>{k.annulla_successivo}</button>
            </p>
          )}
          {vivo && <LinkV2 className="button button-quiet button-small" href={R.prezzi}>{k.cambia_piano}</LinkV2>}
        </>
      )}
    </div>
  );
}
