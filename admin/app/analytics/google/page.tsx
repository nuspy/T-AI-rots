"use client";

/* Google (v8.6): le statistiche del contatore di Google (GA4) lette con la Data API, accanto a quelle di lanterna.
 *
 * GA4 conta solo chi ha accettato i cookie, quindi i suoi numeri sono più bassi di quelli di «Traffico» (che misura
 * tutti, senza cookie): servono per il confronto con l'ecosistema Google (Search Console, Ads), non per sostituire le
 * altre schede. Se manca qualcosa (service account, accesso, ID della proprietà), la pagina lo dice e apre la
 * procedura guidata. */

import { useCallback, useState } from "react";
import { statisticheGoogle } from "@/lib/google";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { ConfiguraGoogle } from "../../configura-google";
import { Barre, Colonne, Tessera, percento } from "../../grafici";
import grafici from "../../grafici.module.css";
import stili from "../../integrazioni.module.css";
import statistiche from "../../statistiche.module.css";
import { FiltriPeriodo, etichettaPeriodo, formatta, serie, usePeriodo, useSegni } from "../comuni";

export default function Google() {
  const { giorni, da, a, imposta } = usePeriodo();
  const segni = useSegni(da, a);
  const esito = useDati(useCallback((t: string) => statisticheGoogle(t, giorni), [giorni]));
  const [configura, setConfigura] = useState(false);

  const d = esito.dati;
  const t = d?.totali;
  const p = d?.precedente ?? null;
  const pronto = d?.pronto === true;
  const mostraConfigura = configura || (d !== null && !pronto);
  const prec = (k: string) => (p ? (p[k] ?? null) : null);

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Google</h1>
          <p className={comuni.sottotitolo}>
            Le statistiche del contatore di Google (GA4). Conta solo chi accetta i cookie: per questo i numeri sono più
            bassi di quelli di «Traffico», che misura tutti senza cookie.
          </p>
        </div>
        <button className={`${comuni.secondaria} ${stili.tocco}`} onClick={() => setConfigura((v) => !v)}
          aria-expanded={mostraConfigura} aria-controls="configura-google">
          {configura ? "Chiudi Configura" : "Configura"}
        </button>
      </div>
      <FiltriPeriodo giorni={giorni} imposta={imposta} />

      {esito.errore && <p className={comuni.errore} role="alert">{esito.errore}</p>}
      {!d && esito.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {d && !pronto && (
        <div className={comuni.avviso} role="status">
          {d.errore ? (
            <><strong>GA4 non risponde come dovrebbe.</strong> {d.errore}</>
          ) : (
            <><strong>Mancano {d.mancano?.join(" e ")}.</strong> Segui i passi qui sotto: carica il service account, aggiungi
              la sua email in GA4 e scrivi l&apos;ID della proprietà.</>
          )}
        </div>
      )}

      {mostraConfigura && (
        <section id="configura-google" className={comuni.riquadro} aria-labelledby="titolo-configura-google">
          <h2 id="titolo-configura-google" className={comuni.riquadroTitolo}>Configura Google</h2>
          <p className={comuni.riquadroNota}>
            Lo stesso service account serve a Search Console (pagina SEO) e a queste statistiche. L&apos;ID di misurazione
            accende il contatore sul sito, solo per chi accetta i cookie.
          </p>
          <ConfiguraGoogle onCambio={esito.ricarica} />
        </section>
      )}

      {d && pronto && t && (
        <div className={esito.inCorso ? comuni.inRicarica : undefined}>
          <div className={grafici.tessere}>
            <Tessera etichetta="Utenti attivi" valore={t.activeUsers ?? null} precedente={prec("activeUsers")} />
            <Tessera etichetta="Nuovi utenti" valore={t.newUsers ?? null} precedente={prec("newUsers")} />
            <Tessera etichetta="Sessioni" valore={t.sessions ?? null} precedente={prec("sessions")} />
            <Tessera etichetta="Visualizzazioni" valore={t.screenPageViews ?? null} precedente={prec("screenPageViews")} />
            <Tessera etichetta="Sessioni con interazione" valore={t.engagementRate ?? null} precedente={prec("engagementRate")}
              formato={(n) => percento(n, 1)} nota="definizione di GA4: 10 s, una conversione o due pagine" />
            <Tessera etichetta="Durata media della sessione" valore={t.averageSessionDuration ?? null}
              precedente={prec("averageSessionDuration")} formato={(n) => formatta(n, "secondi")} />
          </div>

          <Colonne segni={segni}
            titolo="Utenti attivi al giorno (GA4)"
            descrizione={`${etichettaPeriodo(giorni)}, giorni nel fuso della proprietà GA4.`}
            unita="utenti"
            punti={serie((d.giorni ?? []).map((g) => ({ periodo: g.giorno, utenti: g.utenti })), "utenti", da, a)}
          />

          <div className={statistiche.coppie}>
            <Barre titolo="Pagine più viste" unita="visualizzazioni"
              barre={(d.pagine ?? []).map((x) => ({ chiave: x.pagina, etichetta: x.pagina, valore: x.visualizzazioni }))}
              colonneTabella={[{ titolo: "utenti", valori: (d.pagine ?? []).map((x) => formatta(x.utenti)) }]} />
            <Barre titolo="Sorgenti / mezzo" descrizione="Da dove arriva la sessione, secondo Google." unita="sessioni"
              barre={(d.sorgenti ?? []).map((x) => ({ chiave: x.sorgente, etichetta: x.sorgente, valore: x.sessioni }))}
              colonneTabella={[{ titolo: "utenti", valori: (d.sorgenti ?? []).map((x) => formatta(x.utenti)) }]} />
            <Barre titolo="Canali" descrizione="Il raggruppamento predefinito di GA4." unita="sessioni"
              barre={(d.canali ?? []).map((x) => ({ chiave: x.canale, etichetta: x.canale, valore: x.sessioni }))} />
          </div>
          <p className={comuni.campoAiuto}>
            Proprietà GA4 <span className={comuni.mono}>{d.proprieta}</span>
            {d.misurazione && <> · contatore <span className={comuni.mono}>{d.misurazione}</span></>} · dati dalla Data API,
            ricaricati al più ogni dieci minuti.
          </p>
        </div>
      )}
    </>
  );
}
