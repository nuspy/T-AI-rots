"use client";

/* Advertisements → Google Ads → Pagamenti: il profilo pagamenti di AdSense come **appunti** di chi amministra
 * (beneficiario, indirizzo, metodo, banca, soglia, informazioni fiscali, PIN, ultimo pagamento). Il profilo vero sta in
 * AdSense: niente di questo serve a pagare o a incassare, e il sito non lo riceve. Del conto si tengono solo le ultime
 * 4 cifre: il backend rifiuta un IBAN o un numero di carta interi, anche nelle note. */

import { useEffect, useState } from "react";
import {
  NOMI_METODO, NOMI_MODULO, NOMI_STATO_FISCALE, NOMI_STATO_PIN, NOMI_TIPO_PROFILO, PAGAMENTI_VUOTI, salvaPagamentiGoogle,
  statoPubblicita,
  type MetodoPagamento, type ModuloFiscale, type PagamentiGoogle, type StatoFiscale, type StatoPin,
  type StatoPubblicita, type TipoProfilo,
} from "@/lib/pubblicita";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../../comuni.module.css";
import stili from "../../pubblicita.module.css";

const chiavi = <T extends string>(o: Record<T, string>) => Object.keys(o) as T[];

export default function PagamentiGoogleAds() {
  const stato = useDati(statoPubblicita);
  const { esegui, inCorso, errore } = useAzione();
  const [ultimo, setUltimo] = useState<StatoPubblicita | null>(null);
  const [bozza, setBozza] = useState<PagamentiGoogle | null>(null);
  const [esito, setEsito] = useState<string | null>(null);
  const dati = ultimo ?? stato.dati;

  useEffect(() => {
    if (!esito) return;
    const t = window.setTimeout(() => setEsito(null), 4000);
    return () => window.clearTimeout(t);
  }, [esito]);

  if (!dati) {
    return stato.errore ? <p className={comuni.errore} role="alert">{stato.errore}</p> : <p className={comuni.caricamento}>Caricamento…</p>;
  }

  const p = bozza ?? { ...PAGAMENTI_VUOTI, ...dati.fornitori.google.pagamenti };
  const cambia = (parziale: Partial<PagamentiGoogle>) => setBozza({ ...p, ...parziale });
  const ultime4Valide = p.conto_ultime4 === "" || /^[0-9A-Za-z]{4}$/.test(p.conto_ultime4);

  const salva = async () => {
    const nuovo = await esegui((t) => salvaPagamentiGoogle(t, p));
    if (nuovo) {
      setUltimo(nuovo);
      setBozza(null);
      setEsito("Dettagli dei pagamenti salvati.");
    }
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); if (ultime4Valide) void salva(); }}>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {esito && <p className={comuni.esito} role="status">{esito}</p>}

      <p className={comuni.avviso}>
        <strong>Solo appunti.</strong> Il profilo pagamenti vero si gestisce in AdSense → Pagamenti: qui se ne tiene un
        promemoria, che non serve a pagare né a incassare e non arriva al sito. Ogni modifica resta nel registro.
      </p>

      <section className={comuni.riquadro} aria-labelledby="titolo-profilo">
        <h2 id="titolo-profilo" className={comuni.riquadroTitolo}>Profilo pagamenti</h2>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>ID profilo pagamenti</span>
            <input className={comuni.ingresso} value={p.id_profilo} onChange={(e) => cambia({ id_profilo: e.target.value })}
              placeholder="1234-5678-9012" inputMode="numeric" autoComplete="off" />
            <span className={comuni.campoAiuto}>AdSense → Pagamenti → Impostazioni: 12 cifre.</span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Tipo di profilo</span>
            <select className={comuni.selezione} value={p.tipo_profilo} onChange={(e) => cambia({ tipo_profilo: e.target.value as TipoProfilo })}>
              {chiavi(NOMI_TIPO_PROFILO).map((k) => <option key={k} value={k}>{NOMI_TIPO_PROFILO[k]}</option>)}
            </select>
          </label>
        </div>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Beneficiario</span>
          <input className={comuni.ingresso} value={p.beneficiario} onChange={(e) => cambia({ beneficiario: e.target.value })} autoComplete="off" />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Indirizzo postale</span>
          <textarea className={comuni.area} style={{ minHeight: "5rem", fontFamily: "inherit" }} value={p.indirizzo}
            onChange={(e) => cambia({ indirizzo: e.target.value })} autoComplete="off" />
          <span className={comuni.campoAiuto}>Quello del profilo: è dove arriva la lettera col PIN di verifica.</span>
        </label>
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-metodo">
        <h2 id="titolo-metodo" className={comuni.riquadroTitolo}>Metodo di pagamento</h2>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Metodo</span>
            <select className={comuni.selezione} value={p.metodo} onChange={(e) => cambia({ metodo: e.target.value as MetodoPagamento })}>
              {chiavi(NOMI_METODO).map((k) => <option key={k} value={k}>{NOMI_METODO[k]}</option>)}
            </select>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Banca</span>
            <input className={comuni.ingresso} value={p.banca} onChange={(e) => cambia({ banca: e.target.value })} autoComplete="off" />
          </label>
        </div>
        <label className={comuni.campo} style={{ maxWidth: "16rem" }}>
          <span className={comuni.campoEtichetta}>Conto: ultime 4 cifre</span>
          <input
            className={comuni.ingresso}
            value={p.conto_ultime4}
            onChange={(e) => cambia({ conto_ultime4: e.target.value.replace(/[\s-]/g, "").slice(0, 4) })}
            maxLength={4}
            placeholder="1234"
            autoComplete="off"
            aria-invalid={!ultime4Valide}
            aria-describedby="aiuto-ultime4"
          />
          <span id="aiuto-ultime4" className={comuni.campoAiuto}>
            Solo le ultime 4, per riconoscere il conto. L&apos;IBAN intero, i numeri di carta e il codice SWIFT/BIC non si
            salvano qui: chi legge questa pagina o il registro non deve poter ricostruire il conto, che resta solo in
            AdSense e in banca.
          </span>
        </label>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Soglia di pagamento</span>
            <input className={comuni.ingresso} type="number" min={0} step="1" inputMode="decimal" value={p.soglia ?? ""}
              onChange={(e) => cambia({ soglia: e.target.value === "" ? null : Number(e.target.value) })} />
            <span className={comuni.campoAiuto}>AdSense paga quando il saldo la supera (di solito 70 € o 100 $).</span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Valuta</span>
            <input className={comuni.ingresso} value={p.valuta} maxLength={3} placeholder="EUR" autoComplete="off"
              onChange={(e) => cambia({ valuta: e.target.value.toUpperCase() })} />
          </label>
        </div>
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-verifiche">
        <h2 id="titolo-verifiche" className={comuni.riquadroTitolo}>Fisco, PIN, ultimo pagamento</h2>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Informazioni fiscali</span>
            <select className={comuni.selezione} value={p.stato_fiscale} onChange={(e) => cambia({ stato_fiscale: e.target.value as StatoFiscale })}>
              {chiavi(NOMI_STATO_FISCALE).map((k) => <option key={k} value={k}>{NOMI_STATO_FISCALE[k]}</option>)}
            </select>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Modulo</span>
            <select className={comuni.selezione} value={p.modulo_fiscale} onChange={(e) => cambia({ modulo_fiscale: e.target.value as ModuloFiscale })}>
              {chiavi(NOMI_MODULO).map((k) => <option key={k} value={k}>{NOMI_MODULO[k]}</option>)}
            </select>
            <span className={comuni.campoAiuto}>Fuori dagli USA: W-8BEN (persona) o W-8BEN-E (azienda), in AdSense → Pagamenti.</span>
          </label>
        </div>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Verifica dell&apos;indirizzo (PIN)</span>
            <select className={comuni.selezione} value={p.stato_pin} onChange={(e) => cambia({ stato_pin: e.target.value as StatoPin })}>
              {chiavi(NOMI_STATO_PIN).map((k) => <option key={k} value={k}>{NOMI_STATO_PIN[k]}</option>)}
            </select>
            <span className={comuni.campoAiuto}>Google spedisce il PIN per posta quando il saldo arriva a circa 10 €.</span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Ultimo pagamento</span>
            <input className={comuni.ingresso} type="date" value={p.ultimo_pagamento ?? ""}
              onChange={(e) => cambia({ ultimo_pagamento: e.target.value || null })} />
          </label>
        </div>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Note</span>
          <textarea className={comuni.area} style={{ minHeight: "6rem", fontFamily: "inherit" }} value={p.note}
            onChange={(e) => cambia({ note: e.target.value })} />
          <span className={comuni.campoAiuto}>Niente IBAN o numeri di carta, nemmeno qui: il salvataggio li rifiuta.</span>
        </label>
      </section>

      <div className={stili.azioni} style={{ marginBottom: "1.25rem" }}>
        <button type="submit" className={comuni.primaria} disabled={inCorso || bozza === null || !ultime4Valide}>
          {inCorso ? "Salvataggio…" : "Salva i dettagli dei pagamenti"}
        </button>
        {bozza !== null && (
          <button type="button" className={comuni.secondaria} disabled={inCorso} onClick={() => setBozza(null)}>
            Annulla le modifiche
          </button>
        )}
      </div>
    </form>
  );
}
