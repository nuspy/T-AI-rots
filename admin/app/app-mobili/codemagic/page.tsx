"use client";

/* App mobili → Codemagic: chi costruisce le app (AAB per Google Play, IPA per TestFlight e l'App Store). Qui solo
 * appunti e collegamenti: la chiave API di App Store Connect per la firma e il keystore di upload Android si caricano
 * in Codemagic, non qui. */

import { useState } from "react";
import { salvaCodemagic, type ParametriCodemagic } from "@/lib/app-mobili";
import comuni from "../../comuni.module.css";
import stili from "../app-mobili.module.css";
import { Campo, Caricamento, Casella, Esterno, Messaggi, useAppMobili } from "../comuni";

export default function Codemagic() {
  const { dati, erroreCaricamento, azione, inCorso, errore, esito } = useAppMobili();
  const [bozza, setBozza] = useState<ParametriCodemagic | null>(null);

  if (!dati) return <Caricamento errore={erroreCaricamento} />;

  const c = dati.codemagic;
  const p = bozza ?? c.parametri;
  const cambia = (parziale: Partial<ParametriCodemagic>) => setBozza({ ...p, ...parziale });

  return (
    <>
      <Messaggi errore={errore} esito={esito} />

      <section className={comuni.riquadro} aria-labelledby="titolo-passi">
        <h2 id="titolo-passi" className={comuni.riquadroTitolo}>Come si prepara</h2>
        <ol className={stili.passi}>
          <li>Crea l&apos;account da <Esterno href="https://codemagic.io/signup">Codemagic</Esterno> e collega il repository dell&apos;app.</li>
          <li>
            In Codemagic → Team settings → Integrations → Developer Portal carica la chiave API di App Store Connect
            (ruolo «App Manager»): serve a firmare l&apos;IPA e a mandarla su TestFlight. È un&apos;altra chiave rispetto
            alla .p8 della App Store Server API.
          </li>
          <li>
            In Code signing identities carica il keystore di upload Android, e tienine una copia fuori dal repository:
            perso il keystore, l&apos;app non si aggiorna più senza passare dal supporto di Google.
          </li>
          <li>La configurazione delle build sta in <span className={comuni.mono}>mobile/codemagic.yaml</span> (Fase 10).</li>
        </ol>
        <p style={{ margin: 0 }}><Esterno blocco href={c.link_console}>Apri Codemagic</Esterno></p>
      </section>

      <form
        className={comuni.riquadro}
        aria-labelledby="titolo-appunti"
        onSubmit={async (e) => {
          e.preventDefault();
          if (bozza && await azione((t) => salvaCodemagic(t, bozza), "Appunti di Codemagic salvati.")) setBozza(null);
        }}
      >
        <h2 id="titolo-appunti" className={comuni.riquadroTitolo}>Appunti</h2>
        <div className={comuni.riga}>
          <Campo etichetta="Team" valore={p.team} cambia={(v) => cambia({ team: v })} />
          <Campo etichetta="ID dell'app in Codemagic" valore={p.app_id} cambia={(v) => cambia({ app_id: v })} mono
            aiuto="La parte finale dell'indirizzo della pagina dell'app." />
          <Campo etichetta="Email dell'account" tipo="email" modo="email" valore={p.email_account}
            cambia={(v) => cambia({ email_account: v })} />
        </div>
        <Casella etichetta="Chiave API di App Store Connect caricata in Codemagic" valore={p.chiave_asc_caricata}
          cambia={(v) => cambia({ chiave_asc_caricata: v })} />
        <div className={comuni.riga}>
          <Campo etichetta="Key ID di quella chiave" valore={p.chiave_asc_key_id} massimo={10} mono
            cambia={(v) => cambia({ chiave_asc_key_id: v.toUpperCase() })}
            aiuto="Solo per riconoscerla: la chiave resta in Codemagic." />
        </div>
        <Casella etichetta="Keystore di upload Android caricato in Codemagic (e copiato fuori dal repo)"
          valore={p.keystore_caricato} cambia={(v) => cambia({ keystore_caricato: v })} />
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Note</span>
          <textarea className={comuni.area} style={{ minHeight: "4rem", fontFamily: "inherit" }} value={p.note}
            onChange={(e) => cambia({ note: e.target.value })} />
        </label>
        <div className={stili.azioni}>
          <button type="submit" className={comuni.primaria} disabled={inCorso || !bozza}>
            {inCorso ? "Salvataggio…" : "Salva gli appunti"}
          </button>
          {bozza && (
            <button type="button" className={comuni.secondaria} onClick={() => setBozza(null)} disabled={inCorso}>
              Annulla le modifiche
            </button>
          )}
        </div>
      </form>
    </>
  );
}
