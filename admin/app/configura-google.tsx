"use client";

/* «Configura Google» (v8.6): la procedura guidata del service account, usata dalla pagina SEO e dalla scheda Google
 * degli analytics.
 *
 * Quattro passi, ognuno con quello che si fa fuori di qui scritto per intero:
 * 1. caricare il file JSON del service account (si salva cifrato; il file montato sul server resta il ripiego);
 * 2. dargli l'accesso in Search Console e in GA4 (l'email, con il pulsante per copiarla);
 * 3. le proprietà: Search Console (`sc-domain:tarots.chat`), l'ID della proprietà GA4, l'ID di misurazione `G-…`;
 * 4. «Verifica»: ogni passo dice se va, e cosa fare se no. Se l'accesso a Search Console c'è, la sitemap parte. */

import { useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import {
  caricaServiceAccount, impostaGoogle, statoGoogle, togliServiceAccount, verificaGoogle,
  type EsitoPasso, type PassoVerifica, type StatoGoogle,
} from "@/lib/google";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "./comuni.module.css";
import stili from "./integrazioni.module.css";

const NOMI_PASSI: Record<PassoVerifica, string> = {
  credenziali: "Chiave del service account",
  search_console: "Accesso a Search Console",
  sitemap: "Sitemap inviata",
  ga4: "Accesso a GA4 (statistiche)",
  contatore: "Contatore di Google sul sito",
};

function Esito({ nome, esito }: { nome: string; esito: EsitoPasso }) {
  /* Il segno e la parola dicono l'esito: il colore da solo non basta. */
  const [segno, parola, classe] = esito.ok
    ? ["✓", "a posto", comuni.positivo]
    : esito.saltato
      ? ["–", "in attesa", comuni.neutro]
      : ["✗", "da sistemare", comuni.negativo];
  return (
    <li className={stili.esito}>
      <span className={`${stili.esitoSegno} ${classe}`} aria-hidden="true">{segno}</span>
      <span><strong>{nome}</strong> <span className={`${comuni.stato} ${classe}`}>{parola}</span></span>
      <span className={stili.esitoTesto}>{esito.messaggio}</span>
    </li>
  );
}

function Copia({ valore }: { valore: string }) {
  const [copiato, setCopiato] = useState(false);
  const copia = async () => {
    try {
      await navigator.clipboard.writeText(valore);
      setCopiato(true);
      setTimeout(() => setCopiato(false), 2500);
    } catch {
      /* senza appunti (pagina non sicura): il valore resta selezionabile a mano */
    }
  };
  return (
    <div className={stili.copia}>
      <span className={stili.copiaValore}>{valore}</span>
      <button type="button" className={`${comuni.secondaria} ${stili.tocco}`} onClick={copia}>
        {copiato ? "Copiata" : "Copia"}
      </button>
      <span className={stili.soloLettori} role="status">{copiato ? "Email copiata negli appunti" : ""}</span>
    </div>
  );
}

export function RiepilogoGoogle({ stato }: { stato: StatoGoogle }) {
  const c = stato.credenziali;
  return (
    <p className={comuni.riquadroNota} style={{ marginBottom: "0.75rem" }}>
      {c.presenti ? (
        <>
          Service account <span className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{c.client_email}</span>{" "}
          ({c.origine === "console" ? "caricato dalla console" : "dal file montato sul server"}) · proprietà{" "}
          <span className={comuni.mono}>{stato.sc_proprieta}</span>
          {stato.ga4_proprieta_id && <> · GA4 <span className={comuni.mono}>{stato.ga4_proprieta_id}</span></>}
          {stato.ga4_misurazione_id && <> · contatore <span className={comuni.mono}>{stato.ga4_misurazione_id}</span></>}
          {stato.verificato_il && <> · ultima verifica {quandoCompleto(stato.verificato_il)}</>}
        </>
      ) : (
        <>Nessun service account: Search Console e le statistiche di GA4 sono spenti. «Configura Google» guida i passi.</>
      )}
    </p>
  );
}

export function ConfiguraGoogle({ onCambio }: { onCambio?: () => void }) {
  const stato = useDati(statoGoogle);
  const { esegui, inCorso, errore } = useAzione();
  const [modulo, setModulo] = useState<{ sc: string; ga4: string; misurazione: string } | null>(null);
  const [file, setFile] = useState<string | null>(null);

  const s = stato.dati;
  const valori = modulo ?? (s ? { sc: s.sc_proprieta_personalizzata ? s.sc_proprieta : "", ga4: s.ga4_proprieta_id ?? "",
    misurazione: s.ga4_misurazione_id ?? "" } : null);

  const dopo = (r: StatoGoogle | null) => {
    if (!r) return;
    stato.ricarica();
    onCambio?.();
  };

  const leggiFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const scelto = e.target.files?.[0];
    if (!scelto) return;
    setFile(scelto.name);
    const testo = await scelto.text();
    dopo(await esegui((t) => caricaServiceAccount(t, testo)));
    e.target.value = "";
  };

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valori) return;
    const r = await esegui((t) => impostaGoogle(t, {
      sc_proprieta: valori.sc.trim(), ga4_proprieta_id: valori.ga4.trim(), ga4_misurazione_id: valori.misurazione.trim(),
    }));
    if (r) setModulo(null);
    dopo(r);
  };

  const togli = async () => {
    if (!window.confirm("Togliere il service account caricato? Se c'è il file montato sul server, si torna a quello.")) return;
    dopo(await esegui(togliServiceAccount));
  };

  const progetto = s?.credenziali.project_id || "";
  const email = s?.credenziali.client_email;

  return (
    <div>
      {(stato.errore || errore) && <p className={comuni.errore} role="alert">{errore ?? stato.errore}</p>}
      {!s && stato.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {s && valori && (
        <ol className={stili.passi}>
          <li className={stili.passo}>
            <h3 className={stili.passoTitolo}>Il service account e la sua chiave</h3>
            <div className={stili.passoTesto}>
              In <a className={comuni.collegamento} href="https://console.cloud.google.com/iam-admin/serviceaccounts" target="_blank" rel="noreferrer">Google Cloud → IAM → Service account</a>{" "}
              scegli (o crea) il progetto e:
              <ol>
                <li>«Crea service account», un nome qualunque (es. tarots-seo), nessun ruolo nel progetto;</li>
                <li>apri il service account → «Chiavi» → «Aggiungi chiave» → «Crea nuova chiave» → JSON: si scarica un file;</li>
                <li>abilita nel progetto le due API:{" "}
                  <a className={comuni.collegamento} target="_blank" rel="noreferrer"
                    href={`https://console.cloud.google.com/apis/library/searchconsole.googleapis.com${progetto ? `?project=${progetto}` : ""}`}>Google Search Console API</a>{" "}
                  e{" "}
                  <a className={comuni.collegamento} target="_blank" rel="noreferrer"
                    href={`https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com${progetto ? `?project=${progetto}` : ""}`}>Google Analytics Data API</a>;</li>
                <li>carica qui il file JSON. Si salva cifrato e non si rilegge più: la console mostra solo l&apos;email.</li>
              </ol>
            </div>
            <div className={comuni.riga} style={{ alignItems: "center" }}>
              <label className={comuni.campo} style={{ marginBottom: 0 }}>
                <span className={comuni.campoEtichetta}>File JSON del service account</span>
                <input type="file" accept=".json,application/json" className={stili.file} onChange={leggiFile} disabled={inCorso} />
                {file && inCorso && <span className={comuni.campoAiuto}>Caricamento di {file}…</span>}
              </label>
              {s.credenziali.origine === "console" && (
                <button type="button" className={`${comuni.distruttiva} ${stili.tocco}`} onClick={togli} disabled={inCorso}>
                  Togli
                </button>
              )}
            </div>
            {s.credenziali.presenti && (
              <p className={comuni.campoAiuto} style={{ marginTop: "0.5rem" }}>
                {s.credenziali.origine === "console" ? "Caricato" : "Dal file montato sul server"}: progetto{" "}
                <span className={comuni.mono}>{s.credenziali.project_id || "—"}</span>, chiave …
                <span className={comuni.mono}>{s.credenziali.chiave_fine}</span>
              </p>
            )}
          </li>

          <li className={stili.passo}>
            <h3 className={stili.passoTitolo}>L&apos;accesso in Search Console e in GA4</h3>
            {email ? (
              <>
                <p className={stili.passoTesto}>Questa è l&apos;email del service account: aggiungila come utente nei due servizi.</p>
                <Copia valore={email} />
                <div className={stili.passoTesto}>
                  <ol>
                    <li>
                      <a className={comuni.collegamento} target="_blank" rel="noreferrer"
                        href={`https://search.google.com/search-console/users?resource_id=${encodeURIComponent(s.sc_proprieta)}`}>
                        Search Console → Impostazioni → Utenti e autorizzazioni</a>{" "}
                      (proprietà <span className={comuni.mono}>{s.sc_proprieta}</span>) → «Aggiungi utente», incolla l&apos;email,
                      autorizzazione «Completo»;
                    </li>
                    <li>
                      <a className={comuni.collegamento} target="_blank" rel="noreferrer" href="https://analytics.google.com/analytics/web/">
                        Google Analytics</a>{" "}
                      → Amministrazione → Gestione accessi alla proprietà → «+» → Aggiungi utenti, incolla l&apos;email, ruolo
                      «Visualizzatore» (niente notifica via email: il service account non la legge).
                    </li>
                  </ol>
                </div>
              </>
            ) : (
              <p className={stili.passoTesto}>Prima carica il file del passo 1: qui comparirà l&apos;email da aggiungere.</p>
            )}
          </li>

          <li className={stili.passo}>
            <h3 className={stili.passoTitolo}>Le proprietà</h3>
            <form onSubmit={salva}>
              <div className={comuni.riga}>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Proprietà Search Console</span>
                  <input className={comuni.ingresso} value={valori.sc} placeholder={s.sc_proprieta_personalizzata ? "" : s.sc_proprieta}
                    autoComplete="off" spellCheck={false} onChange={(e) => setModulo({ ...valori, sc: e.target.value })} />
                  <span className={comuni.campoAiuto}>Vuoto: {s.sc_proprieta_personalizzata ? "il valore predefinito" : s.sc_proprieta}. Con il prefisso URL: https://tarots.chat/</span>
                </label>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>ID proprietà GA4</span>
                  <input className={comuni.ingresso} value={valori.ga4} inputMode="numeric" placeholder="123456789" autoComplete="off"
                    onChange={(e) => setModulo({ ...valori, ga4: e.target.value })} />
                  <span className={comuni.campoAiuto}>Amministrazione → Dettagli proprietà: un numero. Serve alle statistiche.</span>
                </label>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>ID di misurazione</span>
                  <input className={comuni.ingresso} value={valori.misurazione} placeholder="G-XXXXXXXXXX" autoComplete="off" spellCheck={false}
                    onChange={(e) => setModulo({ ...valori, misurazione: e.target.value })} />
                  <span className={comuni.campoAiuto}>
                    Amministrazione → Stream di dati → il flusso web. Il sito carica il contatore solo a chi accetta i cookie.
                  </span>
                </label>
              </div>
              <button type="submit" className={`${comuni.primaria} ${stili.tocco}`} disabled={inCorso || !modulo}>Salva</button>
            </form>
          </li>

          <li className={stili.passo}>
            <h3 className={stili.passoTitolo}>Verifica</h3>
            <p className={stili.passoTesto}>
              Prova la chiave, l&apos;accesso a Search Console e a GA4. Se Search Console risponde, la sitemap{" "}
              <span className={comuni.mono}>{s.sitemap}</span> parte subito. Dopo aver aggiunto l&apos;email possono servire
              alcuni minuti.
            </p>
            <button type="button" className={`${comuni.primaria} ${stili.tocco}`} disabled={inCorso || !!modulo}
              onClick={async () => dopo(await esegui(verificaGoogle))}>
              {inCorso ? "Verifica in corso…" : "Verifica"}
            </button>
            {modulo && <p className={comuni.campoAiuto}>Salva prima le proprietà.</p>}
            {Object.keys(s.esito_verifica).length > 0 && (
              <ul className={stili.esiti} aria-live="polite">
                {(Object.keys(NOMI_PASSI) as PassoVerifica[]).map((p) => {
                  const esito = s.esito_verifica[p];
                  return esito ? <Esito key={p} nome={NOMI_PASSI[p]} esito={esito} /> : null;
                })}
              </ul>
            )}
            {s.verificato_il && <p className={comuni.campoAiuto} style={{ marginTop: "0.5rem" }}>Ultima verifica: {quandoCompleto(s.verificato_il)}</p>}
          </li>
        </ol>
      )}
    </div>
  );
}
