"use client";

/* Il cambio di piano (v9, Fase 2b). Un upgrade parte subito e si paga col conguaglio, in tre righe che chiunque può
 * rifare a mano: il valore residuo dell'abbonamento (sottratto), il nuovo abbonamento (con lo sconto del rinnovo
 * automatico, se scelto), il totale. Stripe addebita esattamente il totale mostrato. Un downgrade si programma per la
 * fine del periodo già pagato. Gli abbonamenti degli store non passano di qui: lì decide lo store. */

import { useEffect, useState } from "react";
import { euro, type Piano } from "@/lib/api";
import { anteprimaCambio, cambiaPiano, type Conguaglio } from "@/lib/abbonamenti";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import { Modale } from "@/v2/componenti/modale";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";

export function CambioPiano({
  piano, annuale, scontoRinnovo, onChiudi, onFatto,
}: {
  piano: Piano | null;
  annuale: boolean;
  scontoRinnovo: number;
  onChiudi: () => void;
  onFatto?: () => void;
}) {
  const { t, locale, lingua, prefissoIt } = useLingua();
  const k = t.abbonamento;
  const { token } = useSessione();
  const [rinnovo, setRinnovo] = useState(true);
  const [conto, setConto] = useState<Conguaglio | null>(null);
  const [errore, setErrore] = useState<string | null>(null);
  const [inCorso, setInCorso] = useState(false);
  const [fatto, setFatto] = useState<string | null>(null);

  useEffect(() => {
    if (!piano) return;
    let annullato = false;
    anteprimaCambio(token, piano.slug, annuale, rinnovo, lingua)
      .then((c) => { if (!annullato) { setConto(c); setErrore(null); } })
      .catch((e: unknown) => { if (!annullato) { setConto(null); setErrore(e instanceof Error ? e.message : t.comune.err_richiesta); } });
    return () => { annullato = true; };
  }, [piano, annuale, rinnovo, token, lingua, t.comune.err_richiesta]);

  if (!piano) return null;
  const soldi = (c: number) => euro(c, conto?.valuta ?? piano.valuta, locale);
  const data = (iso: string) => new Date(iso).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" });

  const conferma = async () => {
    if (!conto) return;
    setInCorso(true);
    setErrore(null);
    try {
      const r = await cambiaPiano(token, piano.slug, annuale, rinnovo, indirizzoV2(R.prezzi, prefissoIt), lingua);
      if (r.tipo === "upgrade" && r.url) { window.location.assign(r.url); return; }
      setFatto(f(k.cambio_programmato, { data: data(r.conguaglio.decorre) }));
      onFatto?.();
    } catch (e) {
      setErrore(e instanceof Error ? e.message : t.comune.err_richiesta);
    } finally {
      setInCorso(false);
    }
  };

  return (
    <Modale aperta titolo={f(k.cambio_titolo, { piano: piano.nome })} onChiudi={onChiudi}>
      {conto?.tipo === "upgrade" && (
        <>
          <dl className="conguaglio" aria-live="polite">
            <div className="conguaglio-riga">
              <dt>{k.cambio_residuo}<small>{f(k.cambio_residuo_nota, { rimasti: conto.giorni_rimasti, totale: conto.giorni_periodo, pagato: soldi(conto.pagato) })}</small></dt>
              <dd>−{soldi(conto.residuo)}</dd>
            </div>
            <div className="conguaglio-riga">
              <dt>{conto.rinnovo ? k.cambio_nuovo_rinnovo : k.cambio_nuovo}
                {conto.rinnovo && <small>{f(k.cambio_nuovo_nota, { listino: soldi(conto.listino), sconto: scontoRinnovo })}</small>}
              </dt>
              <dd>{soldi(conto.nuovo)}</dd>
            </div>
            <div className="conguaglio-riga conguaglio-totale">
              <dt>{k.cambio_totale}</dt>
              <dd>{soldi(conto.totale)}</dd>
            </div>
          </dl>
          <p className="small muted">{conto.totale === 0 ? k.cambio_zero : k.cambio_subito}</p>
        </>
      )}
      {conto?.tipo === "downgrade" && (
        <p>{f(k.cambio_downgrade, { data: data(conto.decorre), importo: soldi(conto.totale) })}</p>
      )}
      {conto && (
        <label className="interruttore">
          <input type="checkbox" role="switch" checked={rinnovo} onChange={(e) => setRinnovo(e.target.checked)} />
          <span>{f(k.cambio_rinnovo, { sconto: scontoRinnovo })}</span>
        </label>
      )}
      {fatto && <p className="success" role="status">{fatto}</p>}
      {errore && <p className="error" role="alert">{errore}</p>}
      <div className="button-row">
        {!fatto && conto && (
          <button type="button" className="button button-brass" disabled={inCorso} onClick={conferma} data-an="cambio_conferma">
            {conto.tipo === "upgrade" ? f(k.cambio_paga, { importo: soldi(conto.totale) }) : k.cambio_programma}
          </button>
        )}
        <button type="button" className="button button-quiet" onClick={onChiudi}>{t.comune.chiudi}</button>
      </div>
    </Modale>
  );
}
