"use client";

/* Notifications → Impostazioni: Firebase (per le app), APNs (dentro Firebase, per iPhone e iPad), le chiavi del Web
 * Push (per il sito, generate da sole) e i predefiniti: ora della carta del giorno, ore di silenzio, tetto delle
 * promozioni, velocità d'invio. */

import { useEffect, useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import {
  NOMI_PIATTAFORMA, caricaFirebase, provaFirebase, salvaImpostazioni, statoNotifiche, togliFirebase,
  type Piattaforma, type StatoNotifiche,
} from "@/lib/notifiche";
import { useAzione, useDati } from "@/lib/usa";
import { CaricaSegreto, Esterno, EsitoUltimaVerifica } from "../../app-mobili/comuni";
import comuni from "../../comuni.module.css";
import { Casella } from "../comuni";
import stili from "../notifiche.module.css";

interface Predefiniti {
  ora_carta: string;
  silenzio: boolean;
  silenzio_dal: string;
  silenzio_al: string;
  tetto_promozioni_settimana: number;
  limite_al_minuto: number;
  vapid_contatto: string;
}

function daStato(s: StatoNotifiche): Predefiniti {
  const i = s.impostazioni;
  return {
    ora_carta: i.ora_carta, silenzio: Boolean(i.silenzio_dal && i.silenzio_al), silenzio_dal: i.silenzio_dal ?? "22:00",
    silenzio_al: i.silenzio_al ?? "08:00", tetto_promozioni_settimana: i.tetto_promozioni_settimana,
    limite_al_minuto: i.limite_al_minuto, vapid_contatto: i.vapid_contatto,
  };
}

export default function Impostazioni() {
  const caricato = useDati(statoNotifiche);
  const { esegui, inCorso, errore } = useAzione();
  const [ultimo, setUltimo] = useState<StatoNotifiche | null>(null);
  const [esito, setEsito] = useState<string | null>(null);
  const [bozza, setBozza] = useState<Predefiniti | null>(null);
  const dati = ultimo ?? caricato.dati;

  useEffect(() => {
    if (!esito) return;
    const t = window.setTimeout(() => setEsito(null), 4000);
    return () => window.clearTimeout(t);
  }, [esito]);

  if (caricato.errore) return <p className={comuni.errore} role="alert">{caricato.errore}</p>;
  if (!dati) return <p className={comuni.caricamento}>Caricamento…</p>;

  const azione = async (f: (t: string) => Promise<StatoNotifiche>, messaggio: string) => {
    const r = await esegui(f);
    if (r) { setUltimo(r); setEsito(messaggio); }
    return r;
  };
  const p = bozza ?? daStato(dati);
  const cambia = (parziale: Partial<Predefiniti>) => setBozza({ ...p, ...parziale });
  const fb = dati.firebase;

  return (
    <>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      <p className={comuni.esito} role="status" hidden={!esito}>{esito}</p>

      <section className={comuni.riquadro} aria-labelledby="titolo-dispositivi">
        <h2 id="titolo-dispositivi" className={comuni.riquadroTitolo}>Dispositivi registrati</h2>
        <dl className={stili.numeri}>
          {(Object.keys(dati.dispositivi) as Piattaforma[]).map((k) => (
            <div key={k}><dt>{NOMI_PIATTAFORMA[k]}</dt><dd>{dati.dispositivi[k].attivi} attivi</dd></div>
          ))}
        </dl>
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-firebase">
        <h2 id="titolo-firebase" className={comuni.riquadroTitolo}>
          Firebase (notifiche nelle app)
          <span className={`${comuni.stato} ${fb.presente ? comuni.positivo : comuni.neutro}`}>{fb.presente ? "✓ caricato" : "○ da configurare"}</span>
        </h2>
        <p className={comuni.riquadroNota}>
          <strong>Cos&apos;è, in parole semplici.</strong> Firebase è il servizio gratuito di Google che recapita le notifiche
          ai telefoni. Il sito gli consegna il messaggio, Firebase lo porta all&apos;app Android direttamente e
          all&apos;iPhone passando da Apple. Per farlo, il sito deve presentarsi con un «tesserino»: un file JSON chiamato
          <em> chiave del service account</em>, che si scarica una volta e si carica qui.
        </p>
        <ol className={stili.passi}>
          <li>
            Apri la <Esterno href="https://console.firebase.google.com/">console di Firebase</Esterno> con l&apos;account
            Google dell&apos;attività e crea un progetto (per esempio «TAROTS chat»). Google Analytics è facoltativo.
          </li>
          <li>Nel progetto aggiungi l&apos;app Android e l&apos;app Apple con l&apos;identificativo <span className={comuni.mono}>chat.tarots.app</span>: i due file che Firebase fa scaricare servono all&apos;app.</li>
          <li>Vai in ⚙ Impostazioni progetto → <strong>Account di servizio</strong> → «Genera nuova chiave privata»: si scarica un file .json.</li>
          <li>Caricalo qui sotto e premi «Prova». Il file resta cifrato nel database: da qui non si rilegge più.</li>
        </ol>
        <CaricaSegreto
          etichetta="il JSON del service account"
          accetta=".json,application/json"
          presente={fb.presente}
          inCorso={inCorso}
          descrizione={fb.presente ? (
            <>Progetto <span className={comuni.mono}>{fb.progetto}</span> · <span className={comuni.mono}>{fb.email}</span>
              {fb.caricato_il && <> · caricato {quandoCompleto(fb.caricato_il)}</>}</>
          ) : "Senza, le app non ricevono notifiche (il sito sì, con il Web Push)."}
          carica={(testo) => void azione((t) => caricaFirebase(t, testo), "Service account di Firebase caricato.")}
          togli={() => { if (window.confirm("Togliere il service account? Le app smettono di ricevere notifiche.")) void azione(togliFirebase, "Service account tolto."); }}
        />
        <div className={stili.azioni}>
          <button type="button" className={comuni.secondaria} disabled={inCorso || !fb.presente}
            onClick={() => void azione(provaFirebase, "Prova eseguita.")}>
            {inCorso ? "Prova in corso…" : "Prova"}
          </button>
        </div>
        <p className={comuni.campoAiuto}>La prova chiede a Firebase di controllare un messaggio senza recapitarlo a nessuno.</p>
        <EsitoUltimaVerifica esito={fb.esito} quando={fb.prova_il} />
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-apns">
        <h2 id="titolo-apns" className={comuni.riquadroTitolo}>Apple (iPhone e iPad): la chiave APNs, dentro Firebase</h2>
        <p className={comuni.riquadroNota}>
          Apple accetta notifiche solo da chi ha una sua chiave. Non si carica qui: si carica in Firebase, che la usa per
          noi. Si fa una volta, dopo l&apos;iscrizione all&apos;Apple Developer Program.
        </p>
        <ol className={stili.passi}>
          <li>
            Apri <Esterno href="https://developer.apple.com/account/resources/authkeys/list">Certificates, Identifiers &amp; Profiles → Keys</Esterno>,
            premi «+», dai un nome, spunta «Apple Push Notifications service (APNs)» e scarica il file .p8 (si scarica una
            volta sola: conservalo). Annota il <strong>Key ID</strong> e il <strong>Team ID</strong>.
          </li>
          <li>In Firebase: ⚙ Impostazioni progetto → <strong>Cloud Messaging</strong> → app Apple → «Chiave di autenticazione APNs» → carica il .p8 con Key ID e Team ID.</li>
          <li>Fatto: le notifiche verso iPhone e iPad passano da Firebase, senza altro da fare qui.</li>
        </ol>
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-vapid">
        <h2 id="titolo-vapid" className={comuni.riquadroTitolo}>
          Web Push (notifiche sul sito)
          <span className={`${comuni.stato} ${dati.vapid.presente ? comuni.positivo : comuni.negativo}`}>{dati.vapid.presente ? "✓ automatico" : "✗ chiavi illeggibili"}</span>
        </h2>
        <p className={comuni.riquadroNota}>
          Nessun account da aprire: le chiavi del Web Push (VAPID) le ha generate il sito da solo e le conserva cifrate.
          La parte pubblica la ricevono i browser quando la persona accetta le notifiche. Funziona su Chrome, Edge e
          Firefox (computer e Android) e su Safari; su iPhone e iPad solo dopo aver aggiunto il sito alla schermata Home.
        </p>
        {dati.vapid.pubblica && (
          <>
            <p className={comuni.campoEtichetta} style={{ margin: "0 0 0.3rem" }}>Chiave pubblica</p>
            <p className={stili.chiave}>{dati.vapid.pubblica}</p>
          </>
        )}
        {dati.vapid.creata_il && <p className={comuni.campoAiuto}>Generata {quandoCompleto(dati.vapid.creata_il)}. Non si rigenera: cambiarla scollegherebbe tutti i browser iscritti.</p>}
      </section>

      <form className={comuni.riquadro} aria-labelledby="titolo-predefiniti" onSubmit={async (e) => {
        e.preventDefault();
        if (!bozza) return;
        const corpo: Record<string, unknown> = {
          ora_carta: p.ora_carta, silenzio: p.silenzio, tetto_promozioni_settimana: p.tetto_promozioni_settimana,
          limite_al_minuto: p.limite_al_minuto, vapid_contatto: p.vapid_contatto,
          ...(p.silenzio ? { silenzio_dal: p.silenzio_dal, silenzio_al: p.silenzio_al } : {}),
        };
        if (await azione((t) => salvaImpostazioni(t, corpo), "Impostazioni salvate.")) setBozza(null);
      }}>
        <h2 id="titolo-predefiniti" className={comuni.riquadroTitolo}>Predefiniti</h2>
        <p className={comuni.riquadroNota}>Valgono per chi non ha cambiato le sue preferenze dal profilo. Le ore sono quelle locali di chi riceve.</p>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Ora della carta del giorno</span>
            <input className={comuni.ingresso} type="time" value={p.ora_carta} onChange={(e) => cambia({ ora_carta: e.target.value })} />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Promozioni al massimo a settimana</span>
            <input className={comuni.ingresso} type="number" inputMode="numeric" min={0} max={14} value={p.tetto_promozioni_settimana}
              onChange={(e) => cambia({ tetto_promozioni_settimana: Number(e.target.value) || 0 })} />
            <span className={comuni.campoAiuto}>A persona; 0 = nessuna promozione. La persona può abbassarlo, non alzarlo.</span>
          </label>
        </div>
        <Casella etichetta="Ore di silenzio" valore={p.silenzio} cambia={(v) => cambia({ silenzio: v })}
          aiuto="Niente notifiche di notte: chi è nelle ore di silenzio le riceve dopo." />
        {p.silenzio && (
          <div className={comuni.riga}>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Dalle</span>
              <input className={comuni.ingresso} type="time" value={p.silenzio_dal} onChange={(e) => cambia({ silenzio_dal: e.target.value })} />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Alle</span>
              <input className={comuni.ingresso} type="time" value={p.silenzio_al} onChange={(e) => cambia({ silenzio_al: e.target.value })} />
            </label>
          </div>
        )}
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Notifiche al minuto, al massimo</span>
            <input className={comuni.ingresso} type="number" inputMode="numeric" min={10} max={100000} value={p.limite_al_minuto}
              onChange={(e) => cambia({ limite_al_minuto: Number(e.target.value) || 10 })} />
            <span className={comuni.campoAiuto}>Per non mandare raffiche ai servizi push. 600 va bene finché gli utenti sono qualche migliaio.</span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Contatto per i servizi push</span>
            <input className={comuni.ingresso} value={p.vapid_contatto} onChange={(e) => cambia({ vapid_contatto: e.target.value })}
              spellCheck={false} placeholder="mailto:privacy@tarots.chat" />
            <span className={comuni.campoAiuto}>Lo vedono Google, Mozilla e Apple se qualcosa non va: «mailto:» seguito da un&apos;email.</span>
          </label>
        </div>
        <div className={stili.azioni}>
          <button type="submit" className={comuni.primaria} disabled={inCorso || !bozza}>{inCorso ? "Salvataggio…" : "Salva i predefiniti"}</button>
          {bozza && <button type="button" className={comuni.secondaria} onClick={() => setBozza(null)}>Annulla le modifiche</button>}
        </div>
      </form>
    </>
  );
}
