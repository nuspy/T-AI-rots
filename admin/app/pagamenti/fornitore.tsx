"use client";

import Link from "next/link";
import { statoStripe, type StatoStripe } from "@/lib/configurazioni";
import { useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "../configurazioni.module.css";

/* Chi incassa, in cima ai pagamenti (v9). Solo il riassunto: si configura nel sotto-tab «Stripe» (Fase 2c), dove
 * stanno le chiavi, la prova e il webhook. Mai i valori delle chiavi: solo se ci sono. */

export const NOMI_FORNITORE: Record<string, string> = {
  stripe: "Stripe",
  mock: "Simulato",
  disattivato: "Nessuno",
};

export function Fornitore() {
  const { dati, errore } = useDati(statoStripe);

  if (errore) return <p className={comuni.errore}>{errore}</p>;
  if (!dati) return null;
  return (
    <>
      <AvvisoFornitore dati={dati} />
      <section className={comuni.riquadro} aria-labelledby="fornitore-titolo">
        <h2 id="fornitore-titolo" className={comuni.riquadroTitolo}>
          Chi incassa
        </h2>
        <dl className={stili.voci}>
          <div className={stili.voce}>
            <dt>Fornitore attivo</dt>
            <dd>
              <strong>{NOMI_FORNITORE[dati.provider] ?? dati.provider}</strong>
            </dd>
          </div>
          <div className={stili.voce}>
            <dt>Chiave segreta Stripe</dt>
            <dd>
              <Presenza presente={dati.chiave_segreta.impostata} />
              {dati.modalita && (
                <span className={comuni.campoAiuto}> · {dati.modalita === "live" ? "reale" : "di prova"}</span>
              )}
            </dd>
          </div>
          <div className={stili.voce}>
            <dt>Webhook</dt>
            <dd>
              <Presenza presente={dati.segreto_webhook.impostata} />
            </dd>
          </div>
        </dl>
        <Link href="/pagamenti/stripe" className={`${comuni.secondaria} ${stili.vai}`}>
          Configura Stripe
        </Link>
      </section>
      {/* Gli incassi della pubblicità hanno la loro pagina in Pubblicità → Google Ads → Pagamenti: da qui solo il
       * rimando, così chi cerca «i pagamenti di Google Ads» fra i pagamenti li trova. */}
      <section className={comuni.riquadro} aria-labelledby="google-ads-titolo">
        <h2 id="google-ads-titolo" className={comuni.riquadroTitolo}>
          Incassi della pubblicità (Google Ads)
        </h2>
        <p className={comuni.campoAiuto}>
          Il profilo pagamenti di AdSense (beneficiario, metodo, soglia, dati fiscali, PIN): sono i soldi che Google
          versa al sito per i banner. Si annota in Pubblicità → Google Ads → Pagamenti.
        </p>
        <Link href="/pubblicita/google/pagamenti" className={`${comuni.secondaria} ${stili.vai}`}>
          Configura Google Ads
        </Link>
      </section>
    </>
  );
}

export function AvvisoFornitore({ dati }: { dati: StatoStripe }) {
  if (dati.provider === "mock") {
    return (
      <p className={comuni.avviso}>
        <strong>Pagamenti simulati.</strong> Il fornitore attivo è quello di prova: nessuna carta viene addebitata, e
        «pagato» significa che qualcuno ha premuto il pulsante di conferma nella cassa finta. Gli incassi mostrati non
        sono denaro reale.
      </p>
    );
  }
  if (dati.provider === "disattivato") {
    return (
      <p className={comuni.avviso}>
        <strong>Pagamenti spenti.</strong> Nessun fornitore attivo: i piani a pagamento rispondono «non ancora
        disponibili» e gli ordini restano in attesa.
      </p>
    );
  }
  if (dati.provider === "stripe" && (!dati.chiave_segreta.impostata || !dati.segreto_webhook.impostata)) {
    return (
      <p className={comuni.errore} role="alert">
        <strong>Stripe incompleto.</strong> Manca{" "}
        {!dati.chiave_segreta.impostata ? "la chiave segreta" : "il webhook (premi «Registra il webhook»)"}: i
        pagamenti non si aprono o non vengono confermati.
      </p>
    );
  }
  if (dati.provider === "stripe" && dati.modalita === "test") {
    return (
      <p className={comuni.avviso}>
        <strong>Stripe in modalità di prova.</strong> Le chiavi sono quelle di test: nessun incasso è denaro reale.
      </p>
    );
  }
  return null;
}

/* Presente o assente: il colore accompagna la parola, non la sostituisce. */
export function Presenza({ presente, testo }: { presente: boolean; testo?: [string, string] }) {
  const [si, no] = testo ?? ["presente", "assente"];
  return (
    <span className={`${comuni.stato} ${presente ? comuni.positivo : comuni.negativo}`}>
      <span aria-hidden="true">{presente ? "✓ " : "○ "}</span>
      {presente ? si : no}
    </span>
  );
}
