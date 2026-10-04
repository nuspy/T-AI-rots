"use client";

/* Social (v8.6): Reddit. A ogni articolo pubblicato (anche in blocco o programmato) parte un post a galleria con la
 * copertina e le immagini del testo, il titolo e il link all'articolo; se le immagini non si possono caricare, un post
 * link. Un post per articolo, mai due; fra un post e l'altro almeno l'intervallo scelto. Qui: l'account (app Reddit
 * di tipo «script»), la prova senza pubblicare, i post fatti con il loro link, «Riprova» per gli errori. */

import { useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import {
  articoliSenzaReddit, configuraReddit, giroReddit, portaSuReddit, provaReddit, riprovaPostReddit, statoReddit,
  type ConfigReddit, type ModificaReddit, type StatoPostReddit,
} from "@/lib/reddit";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "../integrazioni.module.css";

const LINGUE: [string, string][] = [["en", "Inglese"], ["it", "Italiano"], ["hu", "Ungherese"], ["ru", "Russo"], ["uk", "Ucraino"], ["es", "Spagnolo"]];

const STATI: Record<StatoPostReddit, [string, string]> = {
  in_coda: ["in coda", comuni.neutro],
  in_corso: ["in corso", comuni.neutro],
  pubblicato: ["pubblicato", comuni.positivo],
  errore: ["errore", comuni.negativo],
  saltato: ["saltato", comuni.neutro],
};

interface Modulo {
  client_id: string;
  client_secret: string;
  utente: string;
  password: string;
  subreddit: string;
  flair_id: string;
  lingue: string[];
  intervallo_minuti: string;
  attivo: boolean;
}

const daConfig = (c: ConfigReddit): Modulo => ({
  client_id: c.client_id ?? "",
  client_secret: "",
  utente: c.utente ?? "",
  password: "",
  subreddit: c.subreddit ? (c.subreddit.startsWith("u_") ? `u/${c.subreddit.slice(2)}` : c.subreddit) : "",
  flair_id: c.flair_id ?? "",
  lingue: c.lingue,
  intervallo_minuti: String(c.intervallo_minuti),
  attivo: c.attivo,
});

function Esito({ titolo, ok, messaggio }: { titolo: string; ok: boolean; messaggio: string }) {
  return (
    <li className={stili.esito}>
      <span className={`${stili.esitoSegno} ${ok ? comuni.positivo : comuni.negativo}`} aria-hidden="true">{ok ? "✓" : "✗"}</span>
      <span><strong>{titolo}</strong>{" "}
        <span className={`${comuni.stato} ${ok ? comuni.positivo : comuni.negativo}`}>{ok ? "a posto" : "da sistemare"}</span></span>
      <span className={stili.esitoTesto}>{messaggio}</span>
    </li>
  );
}

export default function Social() {
  const stato = useDati(statoReddit);
  const articoli = useDati(articoliSenzaReddit);
  const { esegui, inCorso, errore } = useAzione();
  const [modulo, setModulo] = useState<Modulo | null>(null);
  const [scelto, setScelto] = useState("");
  const [avviso, setAvviso] = useState<string | null>(null);

  const c = stato.dati?.config;
  const valori = modulo ?? (c ? daConfig(c) : null);
  const cambia = (parziale: Partial<Modulo>) => valori && setModulo({ ...valori, ...parziale });
  const flair = c?.esito_prova.destinazione?.flair ?? [];

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valori || !c) return;
    const dati: ModificaReddit = {
      client_id: valori.client_id.trim(), utente: valori.utente.trim(), subreddit: valori.subreddit.trim(),
      flair_id: valori.flair_id.trim(), lingue: valori.lingue, attivo: valori.attivo,
      intervallo_minuti: Math.max(0, Number(valori.intervallo_minuti) || 0),
    };
    /* I segreti si mandano solo se scritti: vuoti, restano quelli di prima. */
    if (valori.client_secret) dati.client_secret = valori.client_secret;
    if (valori.password) dati.password = valori.password;
    const r = await esegui((t) => configuraReddit(t, dati));
    if (r) { setModulo(null); stato.ricarica(); setAvviso("Configurazione salvata."); }
  };

  const prova = async () => {
    const r = await esegui(provaReddit);
    if (r) { stato.ricarica(); setAvviso(null); }
  };

  const riprova = async (id: string) => {
    if (await esegui((t) => riprovaPostReddit(t, id))) {
      setAvviso("Rimesso in coda: parte adesso, se è passato l'intervallo dal post precedente.");
      setTimeout(() => stato.ricarica(), 2500);
      stato.ricarica();
    }
  };

  const porta = async () => {
    if (!scelto) return;
    if (await esegui((t) => portaSuReddit(t, scelto))) {
      setScelto("");
      setAvviso("Articolo in coda per Reddit.");
      articoli.ricarica();
      setTimeout(() => stato.ricarica(), 2500);
      stato.ricarica();
    }
  };

  const giro = async () => {
    if (await esegui(giroReddit)) {
      setAvviso("Giro della coda avviato.");
      setTimeout(() => stato.ricarica(), 3000);
    }
  };

  const prove = c?.esito_prova;

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Social</h1>
          <p className={comuni.sottotitolo}>
            Reddit: a ogni articolo del blog pubblicato (anche in blocco o programmato) parte un post con titolo,
            copertina e immagini del testo e il link all&apos;articolo. Un post per articolo, mai due, e uno alla volta.
          </p>
        </div>
        {c?.attivo && (
          <button className={`${comuni.secondaria} ${stili.tocco}`} onClick={giro} disabled={inCorso}>Pubblica la coda ora</button>
        )}
      </div>

      {(stato.errore || errore) && <p className={comuni.errore} role="alert">{errore ?? stato.errore}</p>}
      {avviso && !errore && <p className={comuni.esito} role="status">{avviso}</p>}
      {!stato.dati && stato.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {c && valori && (
        <section className={comuni.riquadro} aria-labelledby="titolo-account">
          <h2 id="titolo-account" className={comuni.riquadroTitolo}>
            Account Reddit{" "}
            <span className={`${comuni.stato} ${c.attivo ? comuni.positivo : comuni.neutro}`}>
              {c.attivo ? `acceso${c.attivo_dal ? ` dal ${quandoCompleto(c.attivo_dal)}` : ""}` : "spento"}
            </span>
          </h2>
          <details style={{ margin: "0 0 1rem" }}>
            <summary style={{ minHeight: 44, display: "flex", alignItems: "center", cursor: "pointer" }}>
              Come si crea l&apos;app Reddit
            </summary>
            <div className={stili.passoTesto}>
              <ol>
                <li>Entra su Reddit con l&apos;account che pubblicherà (meglio uno dedicato, es. u/tarotschat, senza verifica in
                  due passaggi: le app «script» non la supportano).</li>
                <li>Apri <a className={comuni.collegamento} href="https://www.reddit.com/prefs/apps" target="_blank" rel="noreferrer">reddit.com/prefs/apps</a>{" "}
                  → «create another app…» → tipo <b>script</b>, nome «TAROTS blog», redirect uri{" "}
                  <span className={comuni.mono}>http://localhost:8080</span> (non si usa).</li>
                <li>Il <b>client id</b> è la stringa sotto il nome dell&apos;app; il <b>secret</b> è accanto a «secret».</li>
                <li>Reddit può chiedere di registrarsi come sviluppatore, accettare i termini dell&apos;API (Responsible
                  Builder Policy) o richiedere l&apos;approvazione dell&apos;accesso prima di dare client id e secret: se la
                  pagina lo chiede, fai la richiesta indicando l&apos;uso (pubblicare gli articoli del proprio blog, pochi post
                  al giorno).</li>
                <li>Destinazione: il nome di un subreddit (es. <span className={comuni.mono}>tarotschat</span>) o il tuo profilo
                  (<span className={comuni.mono}>u/nomeutente</span>). Poi «Salva» e «Prova»: non pubblica nulla.</li>
              </ol>
            </div>
          </details>

          <form onSubmit={salva}>
            <div className={comuni.riga}>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Client id</span>
                <input className={comuni.ingresso} value={valori.client_id} autoComplete="off" spellCheck={false}
                  onChange={(e) => cambia({ client_id: e.target.value })} />
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Secret</span>
                <input className={comuni.ingresso} type="password" value={valori.client_secret} autoComplete="new-password"
                  placeholder={c.client_secret_impostato ? `impostato (${c.client_secret_fine ?? "…"})` : ""}
                  onChange={(e) => cambia({ client_secret: e.target.value })} />
                <span className={comuni.campoAiuto}>Vuoto: resta quello salvato. Si salva cifrato e non si rilegge.</span>
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Utente Reddit</span>
                <input className={comuni.ingresso} value={valori.utente} autoComplete="off" spellCheck={false} placeholder="tarotschat"
                  onChange={(e) => cambia({ utente: e.target.value })} />
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Password</span>
                <input className={comuni.ingresso} type="password" value={valori.password} autoComplete="new-password"
                  placeholder={c.password_impostata ? "impostata" : ""} onChange={(e) => cambia({ password: e.target.value })} />
                <span className={comuni.campoAiuto}>Vuoto: resta quella salvata.</span>
              </label>
            </div>
            <div className={comuni.riga}>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Dove pubblicare</span>
                <input className={comuni.ingresso} value={valori.subreddit} autoComplete="off" spellCheck={false}
                  placeholder="tarotschat oppure u/nomeutente" onChange={(e) => cambia({ subreddit: e.target.value })} />
                <span className={comuni.campoAiuto}>Un subreddit (senza r/) o il profilo u/utente.</span>
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Flair</span>
                {flair.length > 0 ? (
                  <select className={comuni.selezione} value={valori.flair_id} onChange={(e) => cambia({ flair_id: e.target.value })}>
                    <option value="">Nessuno</option>
                    {flair.map((f) => <option key={f.id} value={f.id}>{f.testo || f.id}</option>)}
                  </select>
                ) : (
                  <input className={comuni.ingresso} value={valori.flair_id} autoComplete="off" spellCheck={false}
                    placeholder="facoltativo" onChange={(e) => cambia({ flair_id: e.target.value })} />
                )}
                <span className={comuni.campoAiuto}>Solo se il subreddit lo chiede. «Prova» elenca quelli disponibili.</span>
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Minuti fra un post e l&apos;altro</span>
                <input className={comuni.ingresso} inputMode="numeric" value={valori.intervallo_minuti}
                  onChange={(e) => cambia({ intervallo_minuti: e.target.value })} />
                <span className={comuni.campoAiuto}>60 di partenza: dieci articoli insieme diventano dieci post in dieci ore.</span>
              </label>
            </div>
            <fieldset className={comuni.campo} style={{ border: 0, padding: 0, margin: "0 0 0.9rem" }}>
              <legend className={comuni.campoEtichetta}>Articoli da portare su Reddit</legend>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0 1rem" }}>
                {LINGUE.map(([codice, nome]) => (
                  <label key={codice} className={stili.interruttore}>
                    <input type="checkbox" checked={valori.lingue.includes(codice)}
                      onChange={(e) => cambia({
                        lingue: e.target.checked ? [...valori.lingue, codice] : valori.lingue.filter((x) => x !== codice),
                      })} />
                    {nome}
                  </label>
                ))}
              </div>
              <span className={comuni.campoAiuto}>Di solito solo l&apos;inglese: le traduzioni dello stesso articolo sarebbero doppioni.</span>
            </fieldset>
            <label className={stili.interruttore}>
              <input type="checkbox" checked={valori.attivo} onChange={(e) => cambia({ attivo: e.target.checked })} />
              Pubblica su Reddit gli articoli che escono da ora in poi
            </label>
            {c.mancano.length > 0 && (
              <p className={comuni.campoAiuto}>Per accenderla mancano: {c.mancano.join(", ")}.</p>
            )}
            <div className={comuni.riga} style={{ marginTop: "0.75rem" }}>
              <button type="submit" className={`${comuni.primaria} ${stili.tocco}`} disabled={inCorso || !modulo}>Salva</button>
              <button type="button" className={`${comuni.secondaria} ${stili.tocco}`} onClick={prova} disabled={inCorso || !!modulo}>
                {inCorso ? "Prova in corso…" : "Prova"}
              </button>
            </div>
            {modulo && <p className={comuni.campoAiuto}>Salva prima di provare.</p>}
          </form>

          {prove && (prove.accesso || prove.destinazione) && (
            <ul className={stili.esiti} aria-live="polite">
              {prove.accesso && <Esito titolo="Accesso" ok={prove.accesso.ok} messaggio={prove.accesso.messaggio} />}
              {prove.destinazione && <Esito titolo="Destinazione" ok={prove.destinazione.ok} messaggio={prove.destinazione.messaggio} />}
            </ul>
          )}
          {c.ultima_prova_il && <p className={comuni.campoAiuto} style={{ marginTop: "0.5rem" }}>Ultima prova: {quandoCompleto(c.ultima_prova_il)}</p>}
          <p className={comuni.campoAiuto} style={{ marginTop: "0.5rem" }}>
            User-Agent: <span className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{c.user_agent}</span>
          </p>
        </section>
      )}

      {stato.dati && (
        <section className={comuni.riquadro} aria-labelledby="titolo-post">
          <h2 id="titolo-post" className={comuni.riquadroTitolo}>Post su Reddit</h2>
          {stato.dati.post.length === 0 ? (
            <div className={comuni.vuoto}>
              Nessun post ancora. Partono da soli con i prossimi articoli pubblicati, quando Reddit è acceso.
            </div>
          ) : (
            <ul className={`${stili.schede} ${stato.inCorso ? comuni.inRicarica : ""}`}>
              {stato.dati.post.map((p) => {
                const [parola, classe] = STATI[p.stato];
                return (
                  <li key={p.id} className={stili.scheda}>
                    <span className={stili.schedaTitolo}>
                      {p.articolo ? (
                        <a className={comuni.collegamento} href={p.articolo.url} target="_blank" rel="noreferrer">{p.articolo.titolo}</a>
                      ) : "Articolo cancellato"}
                    </span>
                    <span className={stili.schedaRiga}>
                      <span className={`${comuni.stato} ${classe}`}>{parola}</span>
                      {p.tipo && <span>{p.tipo === "galleria" ? "galleria" : "link"}</span>}
                      {p.subreddit && <span className={comuni.mono}>{p.subreddit.startsWith("u_") ? `u/${p.subreddit.slice(2)}` : `r/${p.subreddit}`}</span>}
                      {p.pubblicato_il && <span>{quandoCompleto(p.pubblicato_il)}</span>}
                      {p.tentativi > 1 && <span>{p.tentativi} tentativi</span>}
                      {p.riprova_dopo && p.stato === "in_coda" && <span>riprova dopo {quandoCompleto(p.riprova_dopo)}</span>}
                    </span>
                    {p.url && (
                      <a className={comuni.collegamento} href={p.url} target="_blank" rel="noreferrer" style={{ overflowWrap: "anywhere" }}>
                        {p.url}
                      </a>
                    )}
                    {p.errore && <span className={p.stato === "errore" ? comuni.negativo : stili.esitoTesto}>{p.errore}</span>}
                    {(p.stato === "errore" || p.stato === "saltato") && (
                      <div>
                        <button className={`${comuni.secondaria} ${stili.tocco}`} onClick={() => riprova(p.id)} disabled={inCorso}>
                          Riprova
                        </button>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      )}

      {c && (
        <section className={comuni.riquadro} aria-labelledby="titolo-porta">
          <h2 id="titolo-porta" className={comuni.riquadroTitolo}>Porta su Reddit un articolo già uscito</h2>
          <p className={comuni.riquadroNota}>
            All&apos;accensione si parte dagli articoli nuovi: l&apos;archivio non si riversa su Reddit da solo. Qui se ne
            sceglie uno alla volta, con giudizio.
          </p>
          <div className={comuni.riga}>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Articolo</span>
              <select className={comuni.selezione} value={scelto} onChange={(e) => setScelto(e.target.value)}>
                <option value="">Scegli…</option>
                {(articoli.dati ?? []).map((x) => (
                  <option key={x.id} value={x.id}>{x.titolo} ({x.lang})</option>
                ))}
              </select>
            </label>
            <button className={`${comuni.primaria} ${stili.tocco}`} onClick={porta} disabled={inCorso || !scelto}>Porta su Reddit</button>
          </div>
        </section>
      )}
    </>
  );
}
