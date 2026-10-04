"use client";

/* Impostazioni → Dati del titolare (v9, Fase 2c): chi è il titolare del trattamento dei dati, come lo si contatta,
 * dove stanno i server. L'informativa privacy del sito li mostra da sola in tutte le lingue; l'elenco dei fornitori
 * di intelligenza artificiale non si scrive qui: lo prende dai fornitori attivi in «Modelli».
 *
 * Perché in Impostazioni e non in «Conservazione dati»: quella pagina cancella dati vecchi, questa dice chi risponde
 * dei dati — un'impostazione del sito intero, che si tocca una volta. */

import Link from "next/link";
import { useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import { leggiTitolare, salvaTitolare, type Titolare } from "@/lib/configurazioni";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../../configurazioni.module.css";

const NOMI_PAESI = typeof Intl !== "undefined" && "DisplayNames" in Intl
  ? new Intl.DisplayNames(["it"], { type: "region" })
  : null;

function paese(codice: string | null): string {
  if (!codice) return "";
  return NOMI_PAESI?.of(codice) ?? codice;
}

export default function PaginaTitolare() {
  const stato = useDati(leggiTitolare);
  return (
    <>
      <p className={stili.spiegazione}>
        Il <strong>titolare del trattamento</strong> è chi decide perché e come si usano i dati delle persone che usano
        il sito, e ne risponde. La legge (GDPR) vuole che l&apos;informativa privacy dica chi è e come contattarlo: la
        pagina Privacy del sito prende questi dati da qui, in tutte le lingue. I campi lasciati vuoti non compaiono.
      </p>
      {stato.errore && <p className={comuni.errore} role="alert">{stato.errore}</p>}
      {!stato.dati && !stato.errore && <p className={comuni.caricamento}>Caricamento…</p>}
      {stato.dati && <Modulo iniziale={stato.dati} />}
    </>
  );
}

function Modulo({ iniziale }: { iniziale: Titolare }) {
  const { esegui, inCorso, errore } = useAzione();
  const [v, setV] = useState<Titolare>(iniziale);
  const [salvato, setSalvato] = useState<Titolare | null>(null);
  const fornitori = (salvato ?? iniziale).fornitori_ai ?? [];

  const campo = (nome: keyof Titolare) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setSalvato(null);
    setV({ ...v, [nome]: e.target.value });
  };

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    const r = await esegui((t) => salvaTitolare(t, v));
    if (r) {
      setSalvato(r);
      setV(r);
    }
  };

  return (
    <>
      <form onSubmit={salva} className={comuni.riquadro} aria-labelledby="titolare-titolo">
        <h2 id="titolare-titolo" className={comuni.riquadroTitolo}>Chi è il titolare</h2>
        <div className={stili.campi}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Nome e cognome, o ragione sociale</span>
            <input className={comuni.ingresso} value={v.nome} onChange={campo("nome")} autoComplete="name" />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Partita IVA o codice fiscale (facoltativo)</span>
            <input className={comuni.ingresso} value={v.codice_fiscale} onChange={campo("codice_fiscale")} autoComplete="off" />
          </label>
        </div>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Indirizzo postale</span>
          <input className={comuni.ingresso} value={v.indirizzo} onChange={campo("indirizzo")} autoComplete="street-address"
            placeholder="Via, numero, CAP, città, paese" />
          <span className={comuni.campoAiuto}>Dove una persona può scrivere per lettera. Compare nell&apos;informativa.</span>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Email per la privacy</span>
          <input className={comuni.ingresso} type="email" value={v.email_privacy} onChange={campo("email_privacy")}
            placeholder={iniziale.predefiniti?.email_privacy} />
          <span className={comuni.campoAiuto}>
            Dove le persone chiedono di vedere, correggere o cancellare i loro dati. La posta in arrivo a @tarots.chat
            la inoltra Namecheap ad a.taini@gmail.com.
          </span>
        </label>

        <fieldset className={stili.scelte}>
          <legend className={comuni.campoEtichetta}>Responsabile della protezione dei dati (DPO)</legend>
          <p className={comuni.campoAiuto} style={{ margin: 0 }}>
            Una persona che controlla come si trattano i dati. La legge lo chiede solo in certi casi (per esempio
            trattamenti di dati sensibili su larga scala): decidilo con il consulente.
          </p>
          <label className={stili.scelta}>
            <input type="radio" name="dpo" checked={!v.dpo_nominato} onChange={() => setV({ ...v, dpo_nominato: false })} />
            <span>Non nominato</span>
          </label>
          <label className={stili.scelta}>
            <input type="radio" name="dpo" checked={v.dpo_nominato} onChange={() => setV({ ...v, dpo_nominato: true })} />
            <span>Nominato<small>Scrivi sotto come contattarlo.</small></span>
          </label>
        </fieldset>
        {v.dpo_nominato && (
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Contatto del DPO</span>
            <input className={comuni.ingresso} value={v.dpo_contatto} onChange={campo("dpo_contatto")}
              placeholder="Nome, email" />
          </label>
        )}
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Fornitore dell&apos;hosting</span>
          <input className={comuni.ingresso} value={v.hosting} onChange={campo("hosting")}
            placeholder={iniziale.predefiniti?.hosting} />
          <span className={comuni.campoAiuto}>
            Chi ospita il server e il database, e dove: fornitore, città e in fondo il codice del paese di due lettere
            (GB, IT, DE…), come «Hivelocity, London, GB». Il sito scrive il paese nella lingua di chi legge.
          </span>
        </label>

        <button type="submit" className={`${comuni.primaria} ${stili.tocco}`} disabled={inCorso}>Salva</button>
        <div aria-live="polite">
          {salvato && (
            <p className={comuni.esito}>
              Salvato{salvato.aggiornato_il ? ` (${quandoCompleto(salvato.aggiornato_il)})` : ""}: la pagina Privacy del
              sito li mostra entro un minuto.
            </p>
          )}
          {errore && <p className={comuni.errore} role="alert">{errore}</p>}
        </div>
      </form>

      <section className={comuni.riquadro} aria-labelledby="ai-titolo">
        <h2 id="ai-titolo" className={comuni.riquadroTitolo}>Fornitori di intelligenza artificiale nell&apos;informativa</h2>
        <p className={stili.spiegazione}>
          L&apos;informativa elenca da sola i fornitori attivi in <Link href="/modelli">Modelli</Link>, con il paese in
          cui trattano i testi: se ne cambi uno, l&apos;informativa cambia con lui.
        </p>
        {fornitori.length === 0 ? (
          <p className={comuni.campoAiuto}>Nessun fornitore attivo.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: "1.25rem", lineHeight: 1.7 }}>
            {fornitori.map((f) => (
              <li key={f.nome}>
                {f.nome}
                {f.proprio ? " — su un nostro server, nessun terzo" : f.paese ? ` — ${paese(f.paese)}` : " — paese non indicato"}
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
