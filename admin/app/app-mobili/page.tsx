"use client";

/* App mobili → Android: l'account sviluppatore di Google Play, l'app, la Play Developer API (il JSON del service
 * account, cifrato), le notifiche in tempo reale (RTDN) e gli appunti del profilo pagamenti. «Verifica» legge i
 * prodotti in-app dalla Play Developer API: sola lettura, gratis. */

import { useState } from "react";
import {
  NOMI_TEST_CHIUSO, NOMI_TIPO_ACCOUNT, salvaAndroid, verificaStore,
  type ParametriAndroid, type StatoTestChiuso, type TipoAccount,
} from "@/lib/app-mobili";
import comuni from "../comuni.module.css";
import stili from "./app-mobili.module.css";
import {
  AppuntiPagamenti, Campo, Caricamento, CaricaSegreto, Casella, Copia, Esterno, EsitoUltimaVerifica, Messaggi,
  Scelta, UltimaNotificaStore, useAppMobili,
} from "./comuni";
import { AccessoApp } from "./accesso-app";

export default function Android() {
  const { dati, erroreCaricamento, azione, inCorso, errore, esito } = useAppMobili();
  const [bozza, setBozza] = useState<ParametriAndroid | null>(null);
  /* Il testo delle impronte com'è scritto (righe vuote comprese), finché non si salva. */
  const [testoImpronte, setTestoImpronte] = useState<string | null>(null);

  if (!dati) return <Caricamento errore={erroreCaricamento} />;

  const a = dati.android;
  const p = bozza ?? a.parametri;
  const cambia = (parziale: Partial<ParametriAndroid>) => setBozza({ ...p, ...parziale });
  const sa = a.segreti.service_account;

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bozza) return;
    if (await azione((t) => salvaAndroid(t, { parametri: bozza }), "Impostazioni Android salvate.")) {
      setBozza(null);
      setTestoImpronte(null);
    }
  };

  return (
    <>
      <Messaggi errore={errore} esito={esito} />

      <form onSubmit={salva}>
        <section className={comuni.riquadro} aria-labelledby="titolo-account">
          <h2 id="titolo-account" className={comuni.riquadroTitolo}>Account sviluppatore Google Play</h2>
          <p className={comuni.riquadroNota}>
            Si apre una volta (25 $) da <Esterno href="https://play.google.com/console/signup">Play Console</Esterno>.
            Un account <strong>personale</strong> nuovo, prima di andare in produzione, deve fare un{" "}
            <strong>test chiuso con almeno 12 tester per 14 giorni</strong> di fila; un account di{" "}
            <strong>organizzazione</strong> (serve il numero D-U-N-S) no.
          </p>
          <div className={comuni.riga}>
            <Campo etichetta="ID account sviluppatore" valore={p.id_sviluppatore} cambia={(v) => cambia({ id_sviluppatore: v })}
              modo="numeric" mono aiuto="Il numero nell'indirizzo di Play Console: …/developers/<numero>/…" />
            <Campo etichetta="Email dell'account" tipo="email" modo="email" valore={p.email_account}
              cambia={(v) => cambia({ email_account: v })} />
          </div>
          <div className={comuni.riga}>
            <Scelta<TipoAccount> etichetta="Tipo di account" valore={p.tipo_account} nomi={NOMI_TIPO_ACCOUNT}
              cambia={(v) => cambia({ tipo_account: v })} />
            <Scelta<StatoTestChiuso> etichetta="Test chiuso (12 tester × 14 giorni)" valore={p.test_chiuso}
              nomi={NOMI_TEST_CHIUSO} cambia={(v) => cambia({ test_chiuso: v })} />
            <Campo etichetta="Test chiuso iniziato il" tipo="date" valore={p.test_chiuso_dal ?? ""}
              cambia={(v) => cambia({ test_chiuso_dal: v || null })} />
          </div>
          <p style={{ margin: 0 }}><Esterno blocco href={a.link_console}>Apri Play Console</Esterno></p>
        </section>

        <section className={comuni.riquadro} aria-labelledby="titolo-app">
          <h2 id="titolo-app" className={comuni.riquadroTitolo}>L&apos;app</h2>
          <div className={comuni.riga}>
            <Campo etichetta="Package name" valore={p.package_name} cambia={(v) => cambia({ package_name: v })} mono
              aiuto="Proposta: chat.tarots.app. Non si cambia più dopo la prima pubblicazione." />
          </div>
          <div className={comuni.riga}>
            <Campo etichetta="Versione minima" valore={p.versione_minima} cambia={(v) => cambia({ versione_minima: v })}
              segnaposto="1.0.0" mono aiuto="Sotto questa versione l'app chiede di aggiornare e non va avanti." />
            <Campo etichetta="Ultima versione pubblicata" valore={p.versione_ultima}
              cambia={(v) => cambia({ versione_ultima: v })} segnaposto="1.0.0" mono
              aiuto="Sotto questa, l'app propone l'aggiornamento senza imporlo." />
          </div>
          <Casella etichetta="Commissione ridotta al 15%" valore={p.commissione_ridotta}
            cambia={(v) => cambia({ commissione_ridotta: v })}
            aiuto="Google applica il 15% sul primo milione di dollari l'anno (gli abbonamenti sono sempre al 15%): va chiesto in Play Console creando il gruppo di account." />
          {a.link_store && <p style={{ margin: 0 }}><Esterno blocco href={a.link_store}>Scheda su Google Play</Esterno></p>}
        </section>

        <section className={comuni.riquadro} aria-labelledby="titolo-collegamenti">
          <h2 id="titolo-collegamenti" className={comuni.riquadroTitolo}>Collegamenti del sito nell&apos;app (App Links)</h2>
          <p className={comuni.riquadroNota}>
            Con le impronte dei certificati che firmano l&apos;app, un collegamento a tarots.chat (una carta, la carta del
            giorno, il ritorno da un pagamento) si apre direttamente nell&apos;app, senza chiedere «apri con».
            Il sito le pubblica da solo in <span className={comuni.mono}>/.well-known/assetlinks.json</span>. Copiale da
            Play Console → l&apos;app → Test e rilascio → Configurazione → <strong>Integrità dell&apos;app</strong> → Firma
            dell&apos;app: servono la <strong>chiave di firma dell&apos;app</strong> e la <strong>chiave di caricamento</strong>{" "}
            (riga «Impronta del certificato SHA-256»). Una per riga; per provare un APK di debug aggiungi anche quella di
            debug.
          </p>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Impronte SHA-256 dei certificati</span>
            <textarea className={`${comuni.area} ${comuni.mono}`} style={{ minHeight: "5rem" }} spellCheck={false}
              value={testoImpronte ?? (p.impronte_sha256 ?? []).join("\n")}
              placeholder="14:6D:E9:83:C5:73:06:50:D8:EE:B9:95:2F:34:FC:64:16:A0:83:42:E6:1D:BE:A8:8A:04:96:B2:3F:CF:44:E5"
              onChange={(e) => {
                setTestoImpronte(e.target.value);
                cambia({ impronte_sha256: e.target.value.split(/[\s,;]+/).map((x) => x.trim()).filter(Boolean) });
              }} />
          </label>
          <p style={{ margin: 0 }}>
            <Esterno blocco href="https://developers.google.com/digital-asset-links/tools/generator">
              Controlla il collegamento con lo strumento di Google
            </Esterno>
          </p>
        </section>

        <section className={comuni.riquadro} aria-labelledby="titolo-rtdn">
          <h2 id="titolo-rtdn" className={comuni.riquadroTitolo}>Notifiche in tempo reale (RTDN)</h2>
          <p className={comuni.riquadroNota}>
            Google avvisa il sito di rinnovi, rimborsi e cancellazioni tramite Pub/Sub. Crea un topic in Google Cloud,
            dai a <span className={comuni.mono}>google-play-developer-notifications@system.gserviceaccount.com</span> il
            ruolo «Publisher» sul topic, crea una sottoscrizione <strong>push</strong> autenticata verso questo indirizzo
            e indica il topic in Play Console → Monetizzazione → Impostazioni di monetizzazione. Il sito accetta solo
            i messaggi firmati da Google con l&apos;audience e l&apos;email del service account del push scritte qui sotto.
          </p>
          <Copia valore={a.url_rtdn} etichetta="Indirizzo RTDN" />
          <UltimaNotificaStore notifica={a.ultima_notifica} />
          <Campo etichetta="Topic Pub/Sub" valore={p.pubsub_topic} cambia={(v) => cambia({ pubsub_topic: v })} mono
            segnaposto="projects/<progetto>/topics/play-rtdn" />
          <div className={comuni.riga}>
            <Campo etichetta="Audience del push autenticato" valore={p.rtdn_audience}
              cambia={(v) => cambia({ rtdn_audience: v })} mono
              aiuto="Quella scritta nella sottoscrizione (se vuota, Google usa l'indirizzo di push)." />
            <Campo etichetta="Service account del push" valore={p.rtdn_email} modo="email"
              cambia={(v) => cambia({ rtdn_email: v })} mono
              aiuto="L'email con cui Pub/Sub firma il token: il sito accetterà solo quella." />
          </div>
        </section>

        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Note</span>
          <textarea className={comuni.area} style={{ minHeight: "4rem", fontFamily: "inherit" }} value={p.note}
            onChange={(e) => cambia({ note: e.target.value })} />
        </label>

        <div className={stili.azioni}>
          <button type="submit" className={comuni.primaria} disabled={inCorso || !bozza}>
            {inCorso ? "Salvataggio…" : "Salva le impostazioni Android"}
          </button>
          {bozza && (
            <button type="button" className={comuni.secondaria} onClick={() => { setBozza(null); setTestoImpronte(null); }} disabled={inCorso}>
              Annulla le modifiche
            </button>
          )}
        </div>
      </form>

      <section className={comuni.riquadro} aria-labelledby="titolo-api">
        <h2 id="titolo-api" className={comuni.riquadroTitolo}>Play Developer API (verifica degli acquisti)</h2>
        <ol className={stili.passi}>
          <li>
            In <Esterno href="https://console.cloud.google.com/iam-admin/serviceaccounts">Google Cloud → Service account</Esterno>{" "}
            crea un service account (anche nello stesso progetto di Search Console) e una chiave JSON.
          </li>
          <li>Abilita l&apos;API «Google Play Android Developer API» nel progetto.</li>
          <li>
            In Play Console → Utenti e autorizzazioni invita l&apos;email del service account con accesso all&apos;app:
            «Visualizza dati finanziari» e «Gestisci ordini e abbonamenti».
          </li>
          <li>Carica qui il file JSON, poi «Verifica».</li>
        </ol>
        <CaricaSegreto
          etichetta="il JSON del service account"
          accetta=".json,application/json"
          presente={sa.presente}
          inCorso={inCorso}
          descrizione={sa.presente ? (
            <>
              <span className={comuni.mono}>{sa.client_email}</span> · progetto {sa.project_id} · chiave …{sa.chiave_fine}
            </>
          ) : "Senza, il sito non può verificare gli acquisti fatti su Google Play."}
          carica={(testo) => void azione((t) => salvaAndroid(t, { service_account_json: testo }), "Service account caricato.")}
          togli={() => {
            if (window.confirm("Togliere il service account? Gli acquisti Google Play non si potranno più verificare.")) {
              void azione((t) => salvaAndroid(t, { service_account_json: "" }), "Service account tolto.");
            }
          }}
        />
        <EsitoUltimaVerifica esito={a.esito_verifica} quando={a.verificato_il} />
        <div className={stili.azioni}>
          <button type="button" className={comuni.secondaria} disabled={inCorso}
            onClick={() => void azione((t) => verificaStore(t, "android"), "Verifica completata.")}>
            {inCorso ? "Verifica…" : "Verifica"}
          </button>
        </div>
      </section>

      <AccessoApp piattaforma="android" />

      <AppuntiPagamenti
        pagamenti={a.pagamenti}
        store="Play Console → Configurazione → Profilo pagamenti"
        aiutoProfilo="12 cifre a gruppi di 4 (1234-5678-9012)."
        inCorso={inCorso}
        salva={(pag) => azione((t) => salvaAndroid(t, { pagamenti: pag }), "Appunti dei pagamenti salvati.")}
      />
    </>
  );
}
