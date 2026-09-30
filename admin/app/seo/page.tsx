"use client";

/* Notifica ai motori di ricerca (v8). Ogni notte a mezzanotte (ora italiana) un CronJob annuncia gli
 * articoli del blog pubblicati o modificati dall'ultimo giro: IndexNow (Bing, Yandex…), Search
 * Console (Google: la sitemap da rileggere) e WebSub (il feed RSS). Qui si vede cosa è configurato,
 * cosa è partito, e si può anticipare il giro senza aspettare la notte. */

import { quandoCompleto } from "@/lib/formato";
import { inviaOraAiMotori, notificheMotori, type Canale, type StatoCanale } from "@/lib/seo";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";

const NOMI: Record<Canale, string> = {
  indexnow: "IndexNow (Bing, Yandex…)",
  search_console: "Search Console (Google)",
  websub: "WebSub (feed RSS)",
};

const CANALI: Canale[] = ["indexnow", "search_console", "websub"];

const CLASSE_STATO: Record<StatoCanale, string> = {
  ok: comuni.positivo,
  errore: comuni.negativo,
  saltato: comuni.neutro,
};

const TESTO_STATO: Record<StatoCanale, string> = { ok: "inviato", errore: "errore", saltato: "saltato" };

export default function NotificaMotori() {
  const elenco = useDati(notificheMotori);
  const { esegui, inCorso, errore } = useAzione();

  const inviaOra = async () => {
    if (await esegui((t) => inviaOraAiMotori(t))) elenco.ricarica();
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Motori di ricerca</h1>
          <p className={comuni.sottotitolo}>
            Ogni notte a mezzanotte si annunciano ai motori di ricerca gli articoli del blog pubblicati o modificati
            dall&apos;ultimo invio. Un canale non configurato si salta senza fermare gli altri.
          </p>
        </div>
        <button className={comuni.primaria} onClick={inviaOra} disabled={inCorso}>
          {inCorso ? "Invio in corso…" : "Invia ora"}
        </button>
      </div>

      {(elenco.errore || errore) && (
        <p className={comuni.errore} role="alert">{errore ?? elenco.errore}</p>
      )}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

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
                    {CANALI.map((c) => {
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
                      <summary>{invio.url.length === 1 ? "1 articolo annunciato" : `${invio.url.length} articoli annunciati`}</summary>
                      <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.25rem" }}>
                        {invio.url.map((u) => (
                          <li key={u} className={comuni.mono} style={{ overflowWrap: "anywhere" }}>
                            <a href={u} target="_blank" rel="noreferrer" className={comuni.collegamento}>{u}</a>
                          </li>
                        ))}
                      </ul>
                    </details>
                  ) : (
                    <p style={{ margin: 0 }}>Nessun articolo nuovo o modificato dal giro precedente.</p>
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
