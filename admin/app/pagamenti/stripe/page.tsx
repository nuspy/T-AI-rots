"use client";

/* Pagamenti → Stripe (v9, Fase 2c): tutto ciò che serve a incassare con Stripe, dalla console.
 *
 * 1. le chiavi (segreta e pubblicabile) e la modalità, con «Prova la chiave»;
 * 2. il webhook, registrato su Stripe con un clic (indirizzo ed eventi li sa la console);
 * 3. il fornitore attivo (nessuno, simulato solo fuori produzione, Stripe).
 *
 * Le chiavi si scrivono e non si rileggono: la pagina dice solo se ci sono e da dove vengono. */

import { useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import {
  provaStripe, registraWebhook, salvaStripe, statoStripe,
  type EsitoProva, type FornitorePagamento, type StatoStripe,
} from "@/lib/configurazioni";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { AvvisoFornitore, NOMI_FORNITORE, Presenza } from "../fornitore";
import stili from "../../configurazioni.module.css";

const ORIGINE: Record<string, string> = { console: "dalla console", ambiente: "dal server (ripiego)" };

export default function PaginaStripe() {
  const stato = useDati(statoStripe);
  const [aggiornato, setAggiornato] = useState<StatoStripe | null>(null);
  const dati = aggiornato ?? stato.dati;

  return (
    <>
      {stato.errore && <p className={comuni.errore} role="alert">{stato.errore}</p>}
      {!dati && !stato.errore && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && (
        <>
          <AvvisoFornitore dati={dati} />
          <Chiavi dati={dati} onStato={setAggiornato} />
          <Webhook dati={dati} onStato={setAggiornato} />
          <Attivo dati={dati} onStato={setAggiornato} />
        </>
      )}
    </>
  );
}

function Chiavi({ dati, onStato }: { dati: StatoStripe; onStato: (s: StatoStripe) => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [modalita, setModalita] = useState<"test" | "live">(dati.modalita ?? "test");
  const [segreta, setSegreta] = useState("");
  const [pubblicabile, setPubblicabile] = useState("");
  const [salvato, setSalvato] = useState(false);
  const [prova, setProva] = useState<EsitoProva | null>(dati.ultima_prova.esito);

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    setSalvato(false);
    const r = await esegui((t) => salvaStripe(t, {
      modalita, chiave_segreta: segreta.trim(), chiave_pubblicabile: pubblicabile.trim(),
    }));
    if (r) {
      onStato(r);
      setSegreta("");
      setPubblicabile("");
      setSalvato(true);
      setProva(null);
    }
  };

  const prova_ = async () => {
    const r = await esegui((t) => provaStripe(t));
    if (r) {
      setProva(r.esito);
      onStato(r.stato);
    }
  };

  const togli = async () => {
    if (!window.confirm("Togliere chiave segreta e segreto del webhook dalla console? Se il server ne ha di suoi, "
      + "torneranno a valere quelli.")) return;
    const r = await esegui((t) => salvaStripe(t, { togli_chiavi: true }));
    if (r) onStato(r);
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="chiavi-titolo">
      <h2 id="chiavi-titolo" className={comuni.riquadroTitolo}>1. Le chiavi di Stripe</h2>
      <p className={stili.spiegazione}>
        Le trovi in Stripe → <strong>Sviluppatori → Chiavi API</strong>. La <strong>chiave segreta</strong> (comincia
        con <code>sk_</code>, o <code>rk_</code> se è una chiave limitata) permette al sito di aprire i pagamenti sul
        tuo conto Stripe: è come una password, si salva cifrata e da qui non si rilegge più. La{" "}
        <strong>chiave pubblicabile</strong> (<code>pk_</code>) non è un segreto: identifica il tuo account nelle pagine
        di pagamento. Stripe ha due <strong>modalità</strong>: «prova», con carte finte e nessun incasso vero, e
        «reale».
      </p>

      <dl className={stili.voci}>
        <div className={stili.voce}>
          <dt>Chiave segreta</dt>
          <dd>
            <Presenza presente={dati.chiave_segreta.impostata} testo={["impostata", "mancante"]} />
            {dati.chiave_segreta.origine && (
              <span className={comuni.campoAiuto}> · {ORIGINE[dati.chiave_segreta.origine]}</span>
            )}
          </dd>
        </div>
        <div className={stili.voce}>
          <dt>Modalità</dt>
          <dd>{dati.modalita === "live" ? "reale" : dati.modalita === "test" ? "di prova" : "—"}</dd>
        </div>
        <div className={stili.voce}>
          <dt>Chiave pubblicabile</dt>
          <dd className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{dati.chiave_pubblicabile ?? "—"}</dd>
        </div>
      </dl>

      <form onSubmit={salva}>
        <fieldset className={stili.scelte}>
          <legend className={comuni.campoEtichetta}>Modalità delle chiavi che incolli</legend>
          <label className={stili.scelta}>
            <input type="radio" name="modalita" checked={modalita === "test"} onChange={() => setModalita("test")} />
            <span>Prova<small>Chiavi sk_test_ e pk_test_: carte finte, nessun addebito.</small></span>
          </label>
          <label className={stili.scelta}>
            <input type="radio" name="modalita" checked={modalita === "live"} onChange={() => setModalita("live")} />
            <span>Reale<small>Chiavi sk_live_ e pk_live_: si incassa davvero.</small></span>
          </label>
        </fieldset>
        <div className={stili.campi}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Chiave segreta</span>
            <input className={comuni.ingresso} type="password" autoComplete="off" spellCheck={false}
              value={segreta} onChange={(e) => setSegreta(e.target.value)}
              placeholder={dati.chiave_segreta.impostata ? "Impostata: lascia vuoto per non cambiarla" : "sk_test_…"} />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Chiave pubblicabile</span>
            <input className={comuni.ingresso} autoComplete="off" spellCheck={false}
              value={pubblicabile} onChange={(e) => setPubblicabile(e.target.value)}
              placeholder={dati.chiave_pubblicabile ? "Lascia vuoto per non cambiarla" : "pk_test_…"} />
          </label>
        </div>
        <div className={stili.azioni}>
          <button type="submit" className={`${comuni.primaria} ${stili.tocco}`} disabled={inCorso}>
            Salva le chiavi
          </button>
          <button type="button" className={`${comuni.secondaria} ${stili.tocco}`} onClick={prova_}
            disabled={inCorso || !dati.chiave_segreta.impostata}>
            Prova la chiave
          </button>
          {dati.chiave_segreta.origine === "console" && (
            <button type="button" className={`${comuni.secondaria} ${stili.tocco}`} onClick={togli} disabled={inCorso}>
              Togli le chiavi
            </button>
          )}
        </div>
      </form>
      <p className={comuni.campoAiuto}>«Prova la chiave» legge soltanto i dati del tuo account Stripe: nessun addebito.</p>
      <div aria-live="polite">
        {salvato && <p className={comuni.esito}>Chiavi salvate (cifrate).</p>}
        {prova && (
          <p className={prova.ok ? comuni.esito : comuni.errore}>
            {prova.ok ? "✓ " : "✗ "}{prova.messaggio}
            {dati.ultima_prova.quando && <span className={comuni.campoAiuto}> ({quandoCompleto(dati.ultima_prova.quando)})</span>}
          </p>
        )}
        {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      </div>
    </section>
  );
}

function Webhook({ dati, onStato }: { dati: StatoStripe; onStato: (s: StatoStripe) => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [esito, setEsito] = useState<string | null>(null);
  const AZIONI = { creato: "creato", aggiornato: "aggiornato", sostituito: "sostituito (Stripe non rivela il segreto di un endpoint esistente)" };

  const registra = async () => {
    setEsito(null);
    const r = await esegui((t) => registraWebhook(t));
    if (r) {
      onStato(r.stato);
      setEsito(`Webhook ${AZIONI[r.azione]}: ${r.eventi.length} eventi abilitati.`);
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="webhook-titolo">
      <h2 id="webhook-titolo" className={comuni.riquadroTitolo}>2. Il webhook</h2>
      <p className={stili.spiegazione}>
        Il <strong>webhook</strong> è il modo in cui Stripe avvisa il sito che un pagamento è andato a buon fine (o è
        fallito, o è stato rimborsato): Stripe chiama un indirizzo del sito e firma ogni avviso con un segreto che
        conoscono solo Stripe e il sito. Senza webhook i pagamenti partono ma non vengono mai confermati. Il pulsante
        registra l&apos;indirizzo su Stripe con tutti gli eventi che il sito gestisce, e salva cifrato il segreto che
        Stripe restituisce. Se c&apos;è già, lo aggiorna invece di crearne un altro.
      </p>
      <dl className={stili.voci}>
        <div className={stili.voce}>
          <dt>Indirizzo</dt>
          <dd className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{dati.webhook.url_atteso}</dd>
        </div>
        <div className={stili.voce}>
          <dt>Segreto del webhook</dt>
          <dd>
            <Presenza presente={dati.segreto_webhook.impostata} testo={["impostato", "mancante"]} />
            {dati.segreto_webhook.origine && (
              <span className={comuni.campoAiuto}> · {ORIGINE[dati.segreto_webhook.origine]}</span>
            )}
          </dd>
        </div>
        <div className={stili.voce}>
          <dt>Registrato</dt>
          <dd>
            {dati.webhook.registrato_il ? quandoCompleto(dati.webhook.registrato_il) : "non da questa console"}
            {dati.webhook.id && <span className={`${comuni.campoAiuto} ${comuni.mono}`}> · {dati.webhook.id}</span>}
          </dd>
        </div>
      </dl>
      <div className={stili.azioni}>
        <button type="button" className={`${comuni.primaria} ${stili.tocco}`} onClick={registra}
          disabled={inCorso || !dati.chiave_segreta.impostata}>
          {inCorso ? "Registrazione…" : dati.webhook.id ? "Aggiorna il webhook" : "Registra il webhook"}
        </button>
      </div>
      {!dati.chiave_segreta.impostata && <p className={comuni.campoAiuto}>Serve prima la chiave segreta.</p>}
      <details className={stili.eventi}>
        <summary>Eventi abilitati ({dati.eventi.length})</summary>
        <ul>{dati.eventi.map((e) => <li key={e}>{e}</li>)}</ul>
      </details>
      <div aria-live="polite">
        {esito && <p className={comuni.esito}>{esito}</p>}
        {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      </div>
    </section>
  );
}

function Attivo({ dati, onStato }: { dati: StatoStripe; onStato: (s: StatoStripe) => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [scelta, setScelta] = useState<FornitorePagamento | "server">(dati.provider_console ?? "server");
  const voci: { valore: FornitorePagamento | "server"; titolo: string; testo: string; nascosta?: boolean }[] = [
    { valore: "disattivato", titolo: "Nessuno", testo: "I piani a pagamento rispondono «non ancora disponibili»." },
    {
      valore: "mock", titolo: "Simulato", nascosta: dati.produzione,
      testo: "Una cassa finta per le prove: nessun addebito. In produzione non si può scegliere.",
    },
    { valore: "stripe", titolo: "Stripe", testo: "Si incassa con Stripe, con le chiavi qui sopra." },
    {
      valore: "server", titolo: `Quello del server (${NOMI_FORNITORE[dati.provider_ambiente] ?? dati.provider_ambiente})`,
      testo: "Decide l'impostazione del server, come prima della console.",
    },
  ];

  const salva = async () => {
    const r = await esegui((t) => salvaStripe(t, { provider: scelta === "server" ? null : scelta }));
    if (r) onStato(r);
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="attivo-titolo">
      <h2 id="attivo-titolo" className={comuni.riquadroTitolo}>3. Il fornitore attivo</h2>
      <p className={stili.spiegazione}>
        Chi incassa adesso: <strong>{NOMI_FORNITORE[dati.provider] ?? dati.provider}</strong> (
        {dati.origine_provider === "console" ? "scelto dalla console" : "deciso dal server"}). Accendi Stripe dopo aver
        provato la chiave e registrato il webhook.
      </p>
      <fieldset className={stili.scelte}>
        <legend className={comuni.campoEtichetta}>Fornitore di pagamento</legend>
        {voci.filter((v) => !v.nascosta).map((v) => (
          <label key={v.valore} className={stili.scelta}>
            <input type="radio" name="fornitore" checked={scelta === v.valore} onChange={() => setScelta(v.valore)} />
            <span>{v.titolo}<small>{v.testo}</small></span>
          </label>
        ))}
      </fieldset>
      <button type="button" className={`${comuni.primaria} ${stili.tocco}`} onClick={salva}
        disabled={inCorso || scelta === (dati.provider_console ?? "server")}>
        Salva il fornitore
      </button>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
    </section>
  );
}
