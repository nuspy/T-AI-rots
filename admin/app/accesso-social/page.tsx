"use client";

import { useState } from "react";
import Link from "next/link";
import {
  accessoSociale, accountDoppi, applicaUnione, rinnovaSegretoApple, salvaProvider, salvaSegretoApple, segretoApple,
  type AccessoSociale, type ProviderSociale, type SegretoApple,
} from "@/lib/accesso-social";
import { giorno } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./accesso-social.module.css";

/* «Accesso con i social»: per ogni provider (Google, Facebook, Microsoft, Apple, GitHub, LinkedIn, X) lo si accende
 * o spegne e si inseriscono client id e segreto. Il backend li applica a Keycloak (identity provider) e il pulsante
 * compare — o sparisce — subito nella pagina di accesso, senza ricostruire niente.
 *
 * Il segreto non torna mai indietro: la pagina sa solo se c'è. Un campo segreto lasciato vuoto tiene quello che
 * Keycloak ha già. Ogni scheda mostra l'indirizzo di ritorno da registrare presso il provider, con il pulsante per
 * copiarlo, e una guida breve (aperta a richiesta: su un telefono otto guide aperte sono un muro).
 *
 * In cima, l'account unico: stessa email = stesso account, comunque si entri. Il pannello dice se il flusso che
 * unisce gli account c'è ed è assegnato, e lo applica con un clic; in fondo, gli account doppi nati prima (da unire
 * a mano: deploy/k8s/LEGGIMI.md, «Account doppi»). */

export default function AccessoSocial() {
  const { dati, errore, inCorso, ricarica } = useDati(accessoSociale);

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Accesso con i social</h1>
          <p className={comuni.sottotitolo}>
            I pulsanti «Continua con…» della pagina di accesso. Un provider acceso compare subito, uno spento sparisce.
            I segreti vanno solo a Keycloak: qui non si salvano e non si rileggono.
          </p>
        </div>
      </div>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {inCorso && !dati && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && !dati.keycloak_raggiungibile && (
        <p className={comuni.errore}>
          Keycloak non risponde, lo stato dei provider non si può leggere: {dati.errore}
        </p>
      )}
      {dati && dati.keycloak_raggiungibile && <Unione stato={dati} ricarica={ricarica} />}
      {dati && (
        <div className={stili.elenco}>
          {dati.provider.map((p) => (
            <SchedaProvider
              key={p.alias}
              provider={p}
              modificabile={dati.keycloak_raggiungibile}
              ricarica={ricarica}
            />
          ))}
        </div>
      )}
      <Doppioni />
    </>
  );
}

/* Il flusso che unisce gli account: presente e assegnato a tutti i provider con l'email garantita? */
function Unione({ stato, ricarica }: { stato: AccessoSociale; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [esito, setEsito] = useState<string | null>(null);
  const daSistemare = stato.provider.filter((p) => p.presente && p.unione_possibile && !p.unione_automatica);
  const applica = async () => {
    setEsito(null);
    const r = await esegui((t) => applicaUnione(t));
    if (r) {
      setEsito(r.provider_aggiornati.length
        ? `Fatto: ${r.provider_aggiornati.join(", ")} ora uniscono gli account.`
        : "Era già tutto a posto.");
      ricarica();
    }
  };
  return (
    <section className={stili.unione} aria-labelledby="unione-titolo">
      <h2 id="unione-titolo" className={stili.nome}>Un account per persona</h2>
      <p className={stili.nota}>
        Chi entra con Google, Facebook, Apple, GitHub o LinkedIn e ha già un account con la stessa email (con la password
        o con un altro social) ritrova il suo, senza domande. X e Microsoft non garantiscono l&apos;email: chiedono di
        confermare rientrando con la password o con un social già collegato.
      </p>
      <p className={stili.nota} role="status">
        {stato.unione.completa
          ? "Attiva su tutti i provider presenti."
          : !stato.unione.flusso_presente
            ? "Non ancora attiva: il flusso di Keycloak non c'è."
            : `Da applicare a: ${daSistemare.map((p) => p.nome).join(", ")}.`}
      </p>
      {!stato.unione.completa && (
        <button type="button" className={stili.salva} onClick={applica} disabled={inCorso}>
          {inCorso ? "Applicazione…" : "Applica l'unione degli account"}
        </button>
      )}
      <div aria-live="polite">
        {errore && <p className={comuni.errore}>{errore}</p>}
        {esito && !errore && <p className={comuni.esito}>{esito}</p>}
      </div>
    </section>
  );
}

/* Gli account dell'app con la stessa email nati prima dell'unione automatica: si uniscono a mano (LEGGIMI). */
function Doppioni() {
  const { dati, errore } = useDati(accountDoppi);
  return (
    <section className={stili.unione} aria-labelledby="doppi-titolo" style={{ marginTop: "1.5rem" }}>
      <h2 id="doppi-titolo" className={stili.nome}>Account con la stessa email</h2>
      <p className={stili.nota}>
        Nati prima dell&apos;unione automatica, o da X e Microsoft. Non si fondono da soli: due account sono due storie
        (letture, crediti, acquisti). La procedura è in deploy/k8s/LEGGIMI.md, «Account doppi».
      </p>
      {errore && <p className={comuni.errore}>{errore}</p>}
      {dati && dati.gruppi.length === 0 && <p className={comuni.vuoto}>Nessun account doppio.</p>}
      {dati && dati.gruppi.map((g) => (
        <div key={g.email} className={stili.doppio}>
          <h3 className={stili.doppioEmail}>{g.email}</h3>
          <ul className={stili.doppioElenco}>
            {g.utenti.map((u) => (
              <li key={u.id}>
                <Link href={`/utenti/${u.id}`} className={stili.collegamento}>#{u.id} {u.display_name ?? ""}</Link>
                <span className={stili.nota}>
                  {" "}· {u.letture} letture · dal {giorno(u.creato)}{u.attivo ? "" : " · disattivato"}
                  {" "}· <span className={comuni.mono}>{u.keycloak_sub.slice(0, 8)}…</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}

function statoDi(p: ProviderSociale): { testo: string; classe: string } {
  if (!p.disponibile) return { testo: "Non disponibile", classe: stili.statoSpento };
  if (p.abilitato) return { testo: "Acceso", classe: stili.statoAcceso };
  if (p.client_id && p.segreto_impostato) return { testo: "Spento", classe: stili.statoSpento };
  return { testo: "Da configurare", classe: stili.statoNuovo };
}

function SchedaProvider({
  provider: p, modificabile, ricarica,
}: { provider: ProviderSociale; modificabile: boolean; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [abilitato, setAbilitato] = useState(p.abilitato);
  const [clientId, setClientId] = useState(p.client_id);
  const [segreto, setSegreto] = useState("");
  const [estesi, setEstesi] = useState(p.dati_estesi);
  const [esito, setEsito] = useState<string | null>(null);
  const [problema, setProblema] = useState<string | null>(null);
  const stato = statoDi(p);
  const idBase = `social-${p.alias}`;

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setEsito(null);
    setProblema(null);
    if (abilitato && !clientId.trim()) return setProblema("Per accenderlo serve il client id.");
    if (abilitato && !segreto.trim() && !p.segreto_impostato) return setProblema("Per accenderlo serve il segreto.");
    const fatto = await esegui((t) =>
      salvaProvider(t, p.alias, {
        abilitato, client_id: clientId.trim(), client_secret: segreto.trim(),
        ...(p.dati_estesi_disponibili ? { dati_estesi: estesi } : {}),
      }),
    );
    if (fatto) {
      setSegreto("");
      setEsito(fatto.abilitato ? "Salvato: il pulsante è nella pagina di accesso." : "Salvato: il provider è spento.");
      if (fatto.avviso) setProblema(fatto.avviso);
      ricarica();
    }
  };

  return (
    <section className={stili.scheda} aria-labelledby={`${idBase}-titolo`}>
      <header className={stili.testa}>
        <h2 id={`${idBase}-titolo`} className={stili.nome}>{p.nome}</h2>
        <span className={`${stili.stato} ${stato.classe}`}>{stato.testo}</span>
      </header>

      {p.nota && <p className={p.disponibile ? stili.nota : stili.notaForte}>{p.nota}</p>}
      {p.disponibile && p.presente && (
        <p className={stili.nota}>
          {p.unione_possibile
            ? (p.unione_automatica ? "Unisce gli account con la stessa email." : "Non unisce ancora gli account: salva o applica l'unione.")
            : "Email non garantita: per collegarsi a un account esistente chiede conferma."}
          {p.legge_profilo && (p.token_conservato ? " Legge i dati del profilo." : " Non legge ancora i dati del profilo: salva per attivarlo.")}
        </p>
      )}

      {p.disponibile && (
        <>
          <Ritorno id={idBase} uri={p.uri_reindirizzamento} />

          <details className={stili.guida}>
            <summary>Come ottenere le credenziali</summary>
            <ol>
              {p.guida.map((passo) => <li key={passo}>{passo}</li>)}
            </ol>
            <a className={stili.collegamento} href={p.console} target="_blank" rel="noopener noreferrer">
              Apri la console di {p.nome} <span aria-hidden="true">↗</span>
            </a>
          </details>

          {p.alias === "apple" ? (
            <ModuloApple acceso={p.abilitato} modificabile={modificabile} ricarica={ricarica} />
          ) : (
          <form onSubmit={invia} className={stili.modulo}>
            <label className={stili.interruttore}>
              <input
                type="checkbox" checked={abilitato} disabled={!modificabile}
                onChange={(e) => setAbilitato(e.target.checked)}
              />
              <span>Acceso nella pagina di accesso</span>
            </label>
            {p.dati_estesi_disponibili && (
              <>
                <label className={stili.interruttore}>
                  <input
                    type="checkbox" checked={estesi} disabled={!modificabile}
                    onChange={(e) => setEstesi(e.target.checked)}
                  />
                  <span>{p.alias === "facebook" ? "Chiedi anche compleanno, sesso e città" : "Chiedi anche data di nascita e sesso"}</span>
                </label>
                <span className={comuni.campoAiuto}>{p.nota_estesi}</span>
              </>
            )}
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Client id</span>
              <input
                className={comuni.ingresso} value={clientId} disabled={!modificabile}
                autoComplete="off" spellCheck={false}
                onChange={(e) => setClientId(e.target.value)}
              />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Segreto</span>
              <input
                className={comuni.ingresso} type="password" value={segreto} disabled={!modificabile}
                autoComplete="new-password" spellCheck={false}
                placeholder={p.segreto_impostato ? "Impostato: lascia vuoto per non cambiarlo" : "Non ancora impostato"}
                onChange={(e) => setSegreto(e.target.value)}
              />
              <span className={comuni.campoAiuto}>
                Va solo a Keycloak. {p.segreto_impostato ? "Scrivine uno nuovo solo per sostituirlo." : ""}
              </span>
            </label>
            <div aria-live="polite">
              {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
              {esito && !problema && !errore && <p className={comuni.esito}>{esito}</p>}
            </div>
            <button className={stili.salva} type="submit" disabled={inCorso || !modificabile}>
              {inCorso ? "Salvataggio…" : "Salva"}
            </button>
          </form>
          )}
        </>
      )}
    </section>
  );
}

/* Apple (v9, Fase 6): niente segreto da incollare. Apple vuole un JWT firmato con la chiave «Sign in with Apple»
 * (.p8) che scade entro sei mesi: lo firma il sito con Team ID, Key ID, Services ID e la chiave caricata qui (cifrata,
 * mai mostrata), lo scrive in Keycloak e lo rinnova ogni mese da solo (CronJob tarots-apple-segreto). Qui si vede
 * quando scade quello in uso. Il Services ID vale per il sito e per le app, che passano da Keycloak nel browser. */
function ModuloApple({
  acceso, modificabile, ricarica,
}: { acceso: boolean; modificabile: boolean; ricarica: () => void }) {
  const { dati: letti, errore: erroreLettura } = useDati(segretoApple);
  const { esegui, inCorso, errore } = useAzione();
  const [campi, setCampi] = useState<{ team_id?: string; key_id?: string; services_id?: string }>({});
  const [chiave, setChiave] = useState<{ nome: string; testo: string } | null>(null);
  const [abilitato, setAbilitato] = useState<boolean | null>(null);
  const [esito, setEsito] = useState<string | null>(null);
  /* La risposta di un salvataggio è già lo stato nuovo: si mostra subito, senza rileggere. */
  const [risposta, setRisposta] = useState<SegretoApple | null>(null);
  /* Cambia a ogni salvataggio: rimonta il campo del file, che altrimenti mostrerebbe ancora il nome caricato. */
  const [giro, setGiro] = useState(0);
  const dati = risposta ?? letti;

  if (erroreLettura) return <p className={comuni.errore}>{erroreLettura}</p>;
  if (!dati) return <p className={comuni.caricamento}>Caricamento…</p>;
  const valore = (c: "team_id" | "key_id" | "services_id") =>
    campi[c] ?? (c === "team_id" ? dati.team_id || dati.team_id_suggerito : dati[c]);
  const s = dati.segreto;

  const dopo = (r: SegretoApple | null, messaggio: string) => {
    if (!r) return;
    setCampi({}); setChiave(null); setAbilitato(null); setGiro((n) => n + 1);
    setEsito(r.applicato?.avviso ? `${messaggio} ${r.applicato.avviso}` : messaggio);
    setRisposta(r); ricarica();
  };

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setEsito(null);
    const corpo = {
      ...Object.fromEntries((["team_id", "key_id", "services_id"] as const).map((c) => [c, valore(c).trim()])),
      ...(chiave ? { chiave_p8: chiave.testo } : {}),
      ...(abilitato !== null ? { abilitato } : {}),
    };
    const r = await esegui((t) => salvaSegretoApple(t, corpo));
    dopo(r, r?.applicato ? `Salvato. Segreto scritto in Keycloak, valido fino al ${giorno(r.applicato.scade_il)}.`
      : "Salvato. Per firmare il segreto mancano ancora dei dati.");
  };

  const leggiFile = async (file: File | undefined) => {
    if (!file) return;
    setChiave({ nome: file.name, testo: await file.text() });
  };

  return (
    <form onSubmit={invia} className={stili.modulo} aria-describedby="apple-segreto-stato">
      <p id="apple-segreto-stato" className={s.scaduto || s.da_rinnovare ? stili.notaForte : stili.nota} role="status">
        {!s.scade_il
          ? "Nessun segreto firmato da qui: compila i campi e carica la chiave."
          : s.scaduto
            ? `Il segreto è scaduto il ${giorno(s.scade_il)}: l'accesso con Apple non funziona. Premi «Rinnova ora».`
            : `Segreto in uso valido fino al ${giorno(s.scade_il)} (${s.giorni_rimasti} giorni). Si rinnova da solo quando ne mancano meno di ${dati.rinnova_entro_giorni}.`}
        {dati.esito.ok === false && ` Ultimo tentativo non riuscito: ${dati.esito.messaggio}`}
      </p>
      <label className={stili.interruttore}>
        <input type="checkbox" checked={abilitato ?? acceso} disabled={!modificabile} onChange={(e) => setAbilitato(e.target.checked)} />
        <span>Acceso nella pagina di accesso e nell&apos;app per iPhone</span>
      </label>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Team ID</span>
        <input className={comuni.ingresso} value={valore("team_id")} maxLength={10} autoComplete="off" spellCheck={false}
          disabled={!modificabile} onChange={(e) => setCampi((c) => ({ ...c, team_id: e.target.value.toUpperCase() }))} />
        <span className={comuni.campoAiuto}>
          10 caratteri: developer.apple.com → Account → Membership.{!dati.team_id && dati.team_id_suggerito ? " Proposto quello di «App mobili → iOS»." : ""}
        </span>
      </label>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Services ID (client id)</span>
        <input className={comuni.ingresso} value={valore("services_id")} maxLength={150} autoComplete="off" spellCheck={false}
          placeholder="chat.tarots.web" disabled={!modificabile}
          onChange={(e) => setCampi((c) => ({ ...c, services_id: e.target.value.trim() }))} />
        <span className={comuni.campoAiuto}>Lo stesso per il sito e per le app (Identifiers → Services IDs).</span>
      </label>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Key ID</span>
        <input className={comuni.ingresso} value={valore("key_id")} maxLength={10} autoComplete="off" spellCheck={false}
          disabled={!modificabile} onChange={(e) => setCampi((c) => ({ ...c, key_id: e.target.value.toUpperCase() }))} />
      </label>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Chiave «Sign in with Apple» (file .p8)</span>
        <input key={giro} className={comuni.ingresso} type="file" accept=".p8,text/plain" disabled={!modificabile}
          onChange={(e) => void leggiFile(e.target.files?.[0])} />
        <span className={comuni.campoAiuto}>
          {chiave ? `Pronta da salvare: ${chiave.nome}.`
            : dati.chiave.illeggibile ? "La chiave salvata non si legge più (chiave master cambiata): ricaricala."
              : dati.chiave.presente ? `Caricata (impronta ${dati.chiave.impronta}). Carica un file solo per sostituirla.`
                : "Non ancora caricata. Si salva cifrata e non si rilegge."}
        </span>
      </label>
      <div aria-live="polite">
        {errore && <p className={comuni.errore}>{errore}</p>}
        {esito && !errore && <p className={comuni.esito}>{esito}</p>}
      </div>
      <div className={stili.ritornoRiga}>
        <button className={stili.salva} type="submit" disabled={inCorso || !modificabile}>
          {inCorso ? "Salvataggio…" : "Salva e firma"}
        </button>
        {dati.completa && (
          <button type="button" className={stili.copia} disabled={inCorso || !modificabile} onClick={async () => {
            setEsito(null);
            const r = await esegui((t) => rinnovaSegretoApple(t));
            dopo(r, r?.applicato ? `Rinnovato: valido fino al ${giorno(r.applicato.scade_il)}.` : "");
          }}>Rinnova ora</button>
        )}
      </div>
    </form>
  );
}

/* L'URI di reindirizzamento, in un campo di sola lettura (si seleziona anche a mano) con il pulsante per copiarlo. */
function Ritorno({ id, uri }: { id: string; uri: string }) {
  const [copiato, setCopiato] = useState<"si" | "no" | null>(null);

  const copia = async () => {
    try {
      await navigator.clipboard.writeText(uri);
      setCopiato("si");
    } catch {
      /* Senza permesso degli appunti (pagina non sicura, browser vecchio): si seleziona il testo, e lo si dice. */
      (document.getElementById(`${id}-uri`) as HTMLInputElement | null)?.select();
      setCopiato("no");
    }
  };

  return (
    <div className={stili.ritorno}>
      <label className={comuni.campoEtichetta} htmlFor={`${id}-uri`}>
        URI di reindirizzamento da registrare presso il provider
      </label>
      <div className={stili.ritornoRiga}>
        <input
          id={`${id}-uri`} className={`${comuni.ingresso} ${stili.uri}`} value={uri} readOnly
          onFocus={(e) => e.currentTarget.select()}
        />
        <button type="button" className={stili.copia} onClick={copia}>
          Copia
        </button>
      </div>
      <span className={comuni.campoAiuto} aria-live="polite">
        {copiato === "si" ? "Copiato negli appunti." : copiato === "no" ? "Selezionato: copialo con Ctrl+C." : ""}
      </span>
    </div>
  );
}
