"use client";

/* App mobili → iOS: l'Apple Developer Program, l'app (iPhone e iPad), la App Store Server API (chiave .p8 cifrata,
 * Key ID, Issuer ID, ambiente), l'indirizzo delle Server Notifications V2, gli accordi Paid Apps e gli appunti di
 * banca. «Verifica» chiede ad Apple la notifica di prova: gratis, non tocca nessun acquisto. */

import { useState } from "react";
import {
  NOMI_ACCORDI, NOMI_AMBIENTE, NOMI_TIPO_ACCOUNT, salvaIos, verificaStore,
  type Ambiente, type ParametriIos, type StatoAccordi, type TipoAccount,
} from "@/lib/app-mobili";
import comuni from "../../comuni.module.css";
import stili from "../app-mobili.module.css";
import {
  AppuntiPagamenti, Campo, Caricamento, CaricaSegreto, Casella, Copia, Esterno, EsitoUltimaVerifica, Messaggi,
  Scelta, UltimaNotificaStore, useAppMobili,
} from "../comuni";
import { AccessoApp } from "../accesso-app";

export default function Ios() {
  const { dati, erroreCaricamento, azione, inCorso, errore, esito } = useAppMobili();
  const [bozza, setBozza] = useState<ParametriIos | null>(null);

  if (!dati) return <Caricamento errore={erroreCaricamento} />;

  const a = dati.ios;
  const p = bozza ?? a.parametri;
  const cambia = (parziale: Partial<ParametriIos>) => setBozza({ ...p, ...parziale });
  const p8 = a.segreti.chiave_p8;

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bozza) return;
    if (await azione((t) => salvaIos(t, { parametri: bozza }), "Impostazioni iOS salvate.")) setBozza(null);
  };

  return (
    <>
      <Messaggi errore={errore} esito={esito} />

      <form onSubmit={salva}>
        <section className={comuni.riquadro} aria-labelledby="titolo-account">
          <h2 id="titolo-account" className={comuni.riquadroTitolo}>Apple Developer Program</h2>
          <p className={comuni.riquadroNota}>
            L&apos;iscrizione costa 99 $ l&apos;anno e si fa da{" "}
            <Esterno href="https://developer.apple.com/programs/enroll/">developer.apple.com</Esterno>. Come
            organizzazione serve il numero D-U-N-S; come persona l&apos;app esce col proprio nome.
          </p>
          <div className={comuni.riga}>
            <Campo etichetta="Team ID" valore={p.team_id} cambia={(v) => cambia({ team_id: v.toUpperCase() })}
              massimo={10} mono aiuto="10 caratteri: Account → Membership details." />
            <Campo etichetta="Email dell'account" tipo="email" modo="email" valore={p.email_account}
              cambia={(v) => cambia({ email_account: v })} />
            <Scelta<TipoAccount> etichetta="Tipo di account" valore={p.tipo_account} nomi={NOMI_TIPO_ACCOUNT}
              cambia={(v) => cambia({ tipo_account: v })} />
          </div>
          <div className={comuni.riga}>
            <Scelta<StatoAccordi> etichetta="Accordo «Paid Apps»" valore={p.accordi_paid_apps} nomi={NOMI_ACCORDI}
              cambia={(v) => cambia({ accordi_paid_apps: v })}
              aiuto="App Store Connect → Business: senza l'accordo attivo (con banca e moduli fiscali) l'app non vende nulla." />
          </div>
          <Casella etichetta="Iscritto allo App Store Small Business Program" valore={p.small_business}
            cambia={(v) => cambia({ small_business: v })}
            aiuto="Commissione al 15% invece del 30% sotto il milione di dollari l'anno: va chiesto ad Apple." />
        </section>

        <section className={comuni.riquadro} aria-labelledby="titolo-app">
          <h2 id="titolo-app" className={comuni.riquadroTitolo}>L&apos;app (iPhone e iPad)</h2>
          <div className={comuni.riga}>
            <Campo etichetta="Bundle ID" valore={p.bundle_id} cambia={(v) => cambia({ bundle_id: v })} mono
              aiuto="Proposta: chat.tarots.app, lo stesso di Android. Con «Sign in with Apple» e «In-App Purchase»." />
            <Campo etichetta="Apple ID dell'app" valore={p.apple_app_id} cambia={(v) => cambia({ apple_app_id: v })}
              modo="numeric" mono aiuto="App Store Connect → l'app → Informazioni sull'app → Apple ID." />
          </div>
          <div className={comuni.riga}>
            <Campo etichetta="Versione minima" valore={p.versione_minima} cambia={(v) => cambia({ versione_minima: v })}
              segnaposto="1.0.0" mono aiuto="Sotto questa versione l'app chiede di aggiornare e non va avanti." />
            <Campo etichetta="Ultima versione pubblicata" valore={p.versione_ultima}
              cambia={(v) => cambia({ versione_ultima: v })} segnaposto="1.0.0" mono />
          </div>
          <Casella etichetta="Anche su iPad" valore={p.ipad} cambia={(v) => cambia({ ipad: v })}
            aiuto="L'app usa gli stessi breakpoint del sito su iPad, in ogni orientamento." />
          <p style={{ margin: 0 }}><Esterno blocco href={a.link_console}>Apri App Store Connect</Esterno></p>
        </section>

        <section className={comuni.riquadro} aria-labelledby="titolo-chiave">
          <h2 id="titolo-chiave" className={comuni.riquadroTitolo}>App Store Server API</h2>
          <ol className={stili.passi}>
            <li>In App Store Connect → Utenti e accesso → Integrazioni → Acquisti in-app genera una chiave.</li>
            <li>Scarica il file AuthKey_XXXXXXXXXX.p8 (si scarica una volta sola) e annota Key ID e Issuer ID.</li>
            <li>Caricala qui sotto, salva gli ID, poi «Verifica».</li>
          </ol>
          <div className={comuni.riga}>
            <Campo etichetta="Key ID" valore={p.key_id} cambia={(v) => cambia({ key_id: v.toUpperCase() })} massimo={10} mono />
            <Campo etichetta="Issuer ID" valore={p.issuer_id} cambia={(v) => cambia({ issuer_id: v.toLowerCase() })}
              massimo={36} mono segnaposto="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
            <Scelta<Ambiente> etichetta="Ambiente" valore={p.ambiente} nomi={NOMI_AMBIENTE}
              cambia={(v) => cambia({ ambiente: v })} aiuto="Sandbox per TestFlight e le prove; produzione all'uscita." />
          </div>
          <h3 className={comuni.campoEtichetta} style={{ margin: "0.5rem 0 0.25rem" }}>
            Server Notifications V2 (da incollare in App Store Connect → l&apos;app → Informazioni sull&apos;app)
          </h3>
          <Copia valore={a.url_notifiche} etichetta="Indirizzo delle notifiche" />
          <p className={comuni.campoAiuto} style={{ marginTop: "-0.4rem" }}>
            Lo stesso indirizzo per produzione e sandbox, versione 2 delle notifiche.
          </p>
          <UltimaNotificaStore notifica={a.ultima_notifica} />
        </section>

        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Note</span>
          <textarea className={comuni.area} style={{ minHeight: "4rem", fontFamily: "inherit" }} value={p.note}
            onChange={(e) => cambia({ note: e.target.value })} />
        </label>

        <div className={stili.azioni}>
          <button type="submit" className={comuni.primaria} disabled={inCorso || !bozza}>
            {inCorso ? "Salvataggio…" : "Salva le impostazioni iOS"}
          </button>
          {bozza && (
            <button type="button" className={comuni.secondaria} onClick={() => setBozza(null)} disabled={inCorso}>
              Annulla le modifiche
            </button>
          )}
        </div>
      </form>

      <section className={comuni.riquadro} aria-labelledby="titolo-p8">
        <h2 id="titolo-p8" className={comuni.riquadroTitolo}>Chiave .p8 e verifica</h2>
        <CaricaSegreto
          etichetta="la chiave .p8"
          accetta=".p8"
          presente={p8.presente}
          inCorso={inCorso}
          descrizione={p8.presente ? <>impronta <span className={comuni.mono}>{p8.impronta}</span></> : (
            "Senza, il sito non può verificare gli acquisti fatti sull'App Store.")}
          carica={(testo) => void azione((t) => salvaIos(t, { chiave_p8: testo }), "Chiave .p8 caricata.")}
          togli={() => {
            if (window.confirm("Togliere la chiave .p8? Gli acquisti App Store non si potranno più verificare.")) {
              void azione((t) => salvaIos(t, { chiave_p8: "" }), "Chiave .p8 tolta.");
            }
          }}
        />
        <EsitoUltimaVerifica esito={a.esito_verifica} quando={a.verificato_il} />
        <div className={stili.azioni}>
          <button type="button" className={comuni.secondaria} disabled={inCorso}
            onClick={() => void azione((t) => verificaStore(t, "ios"), "Verifica completata.")}>
            {inCorso ? "Verifica…" : "Verifica"}
          </button>
        </div>
      </section>

      <AccessoApp piattaforma="ios" />

      <AppuntiPagamenti
        pagamenti={a.pagamenti}
        store="App Store Connect → Business (accordi, imposte e banche)"
        aiutoProfilo="Facoltativo: un riferimento per riconoscere il profilo."
        inCorso={inCorso}
        salva={(pag) => azione((t) => salvaIos(t, { pagamenti: pag }), "Appunti dei pagamenti salvati.")}
      />
    </>
  );
}
