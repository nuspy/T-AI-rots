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
  abbonaGratis, apriPagamento, disdici, elencaPiani, euro, leggiConto, leggiMovimenti,
  statoPagamento, type Conto, type Piano,
} from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useAzione, useCarica, useToken } from "@/lib/usa";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";

const MOTIVI: Record<string, string> = {
  accredito_piano: "Crediti del piano",
  acquisto: "Pacchetto acquistato",
  consumo: "Lettura",
  rimborso: "Rimborso",
  rettifica: "Correzione",
  scadenza: "Scadenza",
  omaggio: "Omaggio",
};

export default function PaginaPiano() {
  const { lingua } = useLingua();
  return (
    <Involucro
      titolo={lingua === "en" ? "Credits and plans" : "Crediti e abbonamenti"}
      sottotitolo={lingua === "en"
        ? "Each reading uses one credit, or one of your subscription's daily readings. Payments are simulated in this version."
        : "Ogni lettura usa un credito, oppure una delle letture giornaliere del tuo abbonamento. In questa versione i pagamenti sono simulati."}
    >
      <Suspense fallback={null}>
        <Contenuto />
      </Suspense>
    </Involucro>
  );
}

function Contenuto() {
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

  const pacchetti = (piani.dati ?? []).filter((p) => p.tipo === "pacchetto");
  const abbonamenti = (piani.dati ?? []).filter((p) => p.tipo === "abbonamento");

  return (
    <>
      {ritorno && <p className={ritorno.buono ? stili.avvisoBuono : stili.avviso} role="status">{ritorno.messaggio}</p>}
      {conto.errore && <p className={stili.errore}>{conto.errore}</p>}
      {conto.dati && <Attuale conto={conto.dati} suCambio={ricarica} />}

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>Pacchetti di letture</h2>
        <div className={stili.griglia}>
          {pacchetti.map((p) => <Offerta key={p.slug} piano={p} conto={conto.dati} suCambio={ricarica} />)}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>Abbonamenti</h2>
        <div className={stili.griglia}>
          {abbonamenti.map((p) => <Offerta key={p.slug} piano={p} conto={conto.dati} suCambio={ricarica} />)}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>Movimenti recenti</h2>
        {movimenti.dati && movimenti.dati.movimenti.length === 0 && (
          <div className={stili.vuoto}>Nessun movimento ancora.</div>
        )}
        <ul className={stili.elenco}>
          {movimenti.dati?.movimenti.map((m, i) => (
            <li key={i} className={`pannello ${stili.riga}`}>
              <div className={stili.rigaCorpo}>
                <p className={stili.rigaTitolo}>{MOTIVI[m.reason] ?? m.reason}</p>
                <p className={stili.rigaDettagli}>
                  {new Date(m.quando).toLocaleString("it-IT")}{m.note ? ` · ${m.note}` : ""}
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
  const { esegui, inCorso, errore } = useAzione();
  const a = conto.abbonamento;
  const quota = conto.uso?.letture_al_giorno;
  const pagato = a && a.piano !== "free";
  return (
    <section className={`pannello ${stili.attuale} ${stili.sezione}`}>
      <div>
        <span className={stili.etichetta}>Il tuo saldo</span>
        <div className={stili.saldo}>
          <span className={stili.saldoNumero}>{conto.saldo}</span>
          <span className={stili.nota}>{conto.saldo === 1 ? "credito" : "crediti"}</span>
        </div>
      </div>
      <div>
        <span className={stili.etichetta}>Abbonamento</span>
        <div className={stili.nome}>{a?.nome ?? "Gratuito"}</div>
        {pagato && (
          <p className={stili.nota}>
            {a.disdetto_il
              ? `Disdetto: resta attivo fino al ${new Date(a.periodo_fine).toLocaleDateString("it-IT")}.`
              : `Si rinnova il ${new Date(a.periodo_fine).toLocaleDateString("it-IT")}.`}
          </p>
        )}
        {quota && quota.limite ? (
          <div className={stili.misura}>
            Letture di oggi: {quota.usati} / {quota.limite}
            <div className={stili.barra}><span style={{ width: `${Math.min(100, (quota.usati / quota.limite) * 100)}%` }} /></div>
          </div>
        ) : null}
        {pagato && !a.disdetto_il && (
          <button className="bottone-secondario" disabled={inCorso} style={{ marginTop: 10 }}
            onClick={async () => { await esegui((t) => disdici(t)); suCambio(); }}>
            Disdici
          </button>
        )}
        {errore && <p className={stili.errore}>{errore}</p>}
      </div>
    </section>
  );
}

function Offerta({ piano, conto, suCambio }: { piano: Piano; conto: Conto | null; suCambio: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const parametri = useSearchParams();
  const attuale = conto?.abbonamento?.piano === piano.slug;
  const pacchetto = piano.tipo === "pacchetto";
  const gratuito = piano.prezzo_mensile === 0;
  const evidente = piano.slug === "pacchetto-15" || piano.slug === "mensile-base";

  const compra = async () => {
    if (gratuito) {
      await esegui((t) => abbonaGratis(t, piano.slug));
      suCambio();
      return;
    }
    const ritorno = parametri.get("ritorno");
    const r = await esegui((t) =>
      apriPagamento(t, piano.slug, false, ritorno && ritorno.startsWith("/") ? `/piano?dopo=${encodeURIComponent(ritorno)}` : undefined),
    );
    if (r?.url) window.location.assign(r.url);
  };

  return (
    <div className={`pannello ${stili.scheda} ${evidente ? stili.schedaEvidente : ""}`}>
      <span className={stili.nome}>{piano.nome}</span>
      <span className={stili.prezzo}>
        {gratuito ? "Gratis" : euro(piano.prezzo_mensile, piano.valuta)}
        {!pacchetto && !gratuito && <span className={stili.nota}> / mese</span>}
      </span>
      <p className={stili.nota}>{piano.descrizione}</p>
      {pacchetto ? (
        <p className={stili.nota}>{piano.crediti_per_periodo} crediti · {euro(Math.round(piano.prezzo_mensile / piano.crediti_per_periodo), piano.valuta)} a lettura</p>
      ) : (
        <p className={stili.nota}>{piano.limiti.letture_al_giorno ? `${piano.limiti.letture_al_giorno} letture al giorno` : "Carta del giorno gratuita"}</p>
      )}
      <button className={evidente ? "bottone" : "bottone-secondario"} disabled={inCorso || (attuale && !pacchetto)} onClick={compra}>
        {attuale && !pacchetto ? "Il tuo piano" : pacchetto ? "Acquista" : gratuito ? "Scegli" : "Abbonati"}
      </button>
      {errore && <p className={stili.errore}>{errore}</p>}
    </div>
  );
}

function useRitornoDalPagamento(suPagato: () => void) {
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
              ? `Pagamento riuscito: i crediti di «${s.nome}» sono sul tuo saldo.`
              : `Pagamento riuscito: il piano «${s.nome}» è attivo.`
            : "Il pagamento non è stato completato.",
        });
        if (buono) {
          suPagato();
          if (dopo && dopo.startsWith("/")) setTimeout(() => router.push(dopo), 1400);
        }
      })
      .catch(() => { if (!annullato) setEsito({ buono: false, messaggio: "Non è stato possibile verificare il pagamento." }); });
    return () => { annullato = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [checkout, token]);

  return esito;
}
