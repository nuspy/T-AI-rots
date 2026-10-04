"use client";

/* Notifica ai motori di ricerca (v8). Ogni notte a mezzanotte (ora italiana) un CronJob annuncia gli
 * articoli del blog pubblicati o modificati dall'ultimo giro, le pagine della sitemap mai annunciate (home,
 * carte, stese…) e la carta del giorno: IndexNow (Bing, Yandex…), Search Console (Google: la sitemap da
 * rileggere) e WebSub (il feed RSS). Qui si vede cosa è configurato, cosa è partito, si può anticipare il giro
 * e, dopo un cambiamento dei contenuti, annunciare tutte le pagine. */

import { useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import { inviaOraAiMotori, notificheMotori, type Canale, type StatoCanale, type VoceEsito } from "@/lib/seo";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import { ConfiguraGoogle } from "../configura-google";
import stili from "../integrazioni.module.css";

const NOMI: Record<VoceEsito, string> = {
  indexnow: "IndexNow (Bing, Yandex…)",
  search_console: "Search Console (Google)",
  websub: "WebSub (feed RSS)",
  sitemap: "Sitemap del sito",
};

const CANALI: Canale[] = ["indexnow", "search_console", "websub"];
const VOCI_ESITO: VoceEsito[] = ["sitemap", ...CANALI];

const CLASSE_STATO: Record<StatoCanale, string> = {
  ok: comuni.positivo,
  errore: comuni.negativo,
  saltato: comuni.neutro,
};

const TESTO_STATO: Record<StatoCanale, string> = { ok: "inviato", errore: "errore", saltato: "saltato" };

export default function NotificaMotori() {
  const elenco = useDati(notificheMotori);
  const { esegui, inCorso, errore } = useAzione();
  /* v8.6: la procedura guidata di Google (service account, accesso, verifica), aperta da «Configura Google». */
  const [google, setGoogle] = useState(false);

  const inviaOra = async (tutte = false) => {
    if (await esegui((t) => inviaOraAiMotori(t, tutte))) elenco.ricarica();
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Motori di ricerca</h1>
          <p className={comuni.sottotitolo}>
            Ogni notte a mezzanotte si annunciano ai motori di ricerca gli articoli del blog pubblicati o modificati
            dall&apos;ultimo invio, le pagine del sito mai annunciate (home, carte, stese, anche in una lingua nuova) e
            la carta del giorno. Un canale non configurato si salta senza fermare gli altri. Dopo aver cambiato i
            testi di carte, stese o home, «Annuncia tutte le pagine» le ripropone tutte.
          </p>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          <button className={comuni.primaria} onClick={() => inviaOra()} disabled={inCorso}>
            {inCorso ? "Invio in corso…" : "Invia ora"}
          </button>
          <button className={comuni.secondaria} onClick={() => inviaOra(true)} disabled={inCorso}>
            Annuncia tutte le pagine
          </button>
          <button className={`${comuni.secondaria} ${stili.tocco}`} onClick={() => setGoogle((v) => !v)} aria-expanded={google}
            aria-controls="configura-google">
            {google ? "Chiudi Configura Google" : "Configura Google"}
          </button>
        </div>
      </div>

      {(elenco.errore || errore) && (
        <p className={comuni.errore} role="alert">{errore ?? elenco.errore}</p>
      )}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {google && (
        <section id="configura-google" className={comuni.riquadro} aria-labelledby="titolo-google">
          <h2 id="titolo-google" className={comuni.riquadroTitolo}>Configura Google</h2>
          <p className={comuni.riquadroNota}>
            Un service account di Google legge Search Console (l&apos;invio della sitemap) e GA4 (le statistiche nella
            scheda Analytics → Google). Quattro passi; «Verifica» dice quale manca e come sistemarlo.
          </p>
          <ConfiguraGoogle onCambio={elenco.ricarica} />
          <button className={`${comuni.secondaria} ${stili.tocco}`} style={{ marginTop: "1rem" }} onClick={() => setGoogle(false)}>
            Chiudi
          </button>
        </section>
      )}

      {elenco.dati && (
        <>
          <section className={comuni.riquadro} aria-labelledby="titolo-canali">
            <h2 id="titolo-canali" className={comuni.riquadroTitolo}>Canali</h2>
            <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "0.75rem" }}>
              {CANALI.map((c) => {
                const conf = elenco.dati!.canali[c];
                return (
                  <li key={c}>
                    <strong>{NOMI[c]}</strong>{" "}
                    <span className={`${comuni.stato} ${conf.configurato ? comuni.positivo : comuni.neutro}`}>
                      {conf.configurato ? "configurato" : "non configurato"}
                    </span>
                    <br />
                    <span className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{conf.dettaglio}</span>
                    {c === "search_console" && !conf.configurato && !google && (
                      <>
                        <br />
                        <button className={`${comuni.primaria} ${stili.tocco}`} style={{ marginTop: "0.5rem" }}
                          onClick={() => setGoogle(true)}>
                          Configura Google
                        </button>
                      </>
                    )}
                  </li>
                );
              })}
            </ul>
          </section>

          <h2 className={comuni.riquadroTitolo} style={{ marginTop: "1.5rem" }}>Invii</h2>
          {elenco.dati.invii.length === 0 ? (
            <div className={comuni.vuoto}>
              Nessun invio ancora. Il primo parte stanotte a mezzanotte, oppure subito con «Invia ora».
            </div>
          ) : (
            <ul className={elenco.inCorso ? comuni.inRicarica : undefined}
              style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "0.75rem" }}>
              {elenco.dati.invii.map((invio) => (
                <li key={invio.id} className={comuni.riquadro}>
                  <p style={{ margin: "0 0 0.5rem" }}>
                    <strong>{invio.avviata_il ? quandoCompleto(invio.avviata_il) : "—"}</strong>{" "}
                    <span className={`${comuni.stato} ${invio.riuscita ? comuni.positivo : comuni.negativo}`}>
                      {invio.riuscita ? "riuscito" : "con errori"}
                    </span>{" "}
                    <span className={comuni.stato}>{invio.manuale ? "manuale" : "notturno"}</span>
                  </p>
                  <ul style={{ listStyle: "none", margin: "0 0 0.5rem", padding: 0, display: "grid", gap: "0.25rem" }}>
                    {VOCI_ESITO.map((c) => {
                      const esito = invio.esiti[c];
                      if (!esito) return null;
                      return (
                        <li key={c}>
                          {NOMI[c]}: <span className={`${comuni.stato} ${CLASSE_STATO[esito.stato]}`}>{TESTO_STATO[esito.stato]}</span>{" "}
                          <span style={{ overflowWrap: "anywhere" }}>{esito.dettaglio}</span>
                        </li>
                      );
                    })}
                  </ul>
                  {invio.url.length > 0 ? (
                    <details>
                      <summary>{invio.url.length === 1 ? "1 pagina annunciata" : `${invio.url.length} pagine annunciate`}</summary>
                      <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.25rem" }}>
                        {invio.url.map((u) => (
                          <li key={u} className={comuni.mono} style={{ overflowWrap: "anywhere" }}>
                            <a href={u} target="_blank" rel="noreferrer" className={comuni.collegamento}>{u}</a>
                          </li>
                        ))}
                      </ul>
                    </details>
                  ) : (
                    <p style={{ margin: 0 }}>Nessuna pagina nuova o modificata dal giro precedente.</p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </>
  );
}
