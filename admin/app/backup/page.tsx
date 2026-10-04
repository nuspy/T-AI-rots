"use client";

/* Backup del database sul NAS (v8.3). Ogni notte alle 2:30 un CronJob salva il database intero (app, Keycloak,
 * immagini) sul NAS via SFTP e tiene le ultime copie. Qui: dove va, la prova del collegamento (con la chiave del NAS
 * da accettare una volta), «Esegui ora», le copie presenti sul NAS, lo storico, e il ripristino di una copia — con
 * una copia di sicurezza fatta prima, e la conferma scritta. La credenziale del NAS (chiave SSH o password) si carica
 * qui (v9, Fase 2c), cifrata, e non si rilegge. */

import { useEffect, useState } from "react";
import {
  copieBackup, eseguiBackup, provaBackup, ripristinaBackup, salvaCredenzialeBackup, salvaImpostazioniBackup,
  statoBackup, statoRipristino,
  type CopiaBackup, type CredenzialeBackup, type EsitoProva, type EsecuzioneBackup, type StatoRipristino,
} from "@/lib/backup";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";

const TIPI: Record<EsecuzioneBackup["tipo"], string> = {
  backup: "backup", sicurezza: "copia di sicurezza", ripristino: "ripristino", prova: "prova",
};
const ESITI: Record<EsecuzioneBackup["esito"], [string, string]> = {
  in_corso: ["in corso", comuni.neutro], ok: ["riuscito", comuni.positivo], errore: ["errore", comuni.negativo],
  saltato: ["saltato", comuni.neutro],
};

function dimensione(byte: number | null): string {
  if (byte == null) return "—";
  if (byte < 1024 * 1024) return `${Math.round(byte / 1024)} KB`;
  return `${(byte / 1024 / 1024).toFixed(1)} MB`;
}

export default function Backup() {
  const stato = useDati(statoBackup);
  const { esegui, inCorso, errore } = useAzione();
  const [prova, setProva] = useState<EsitoProva | null>(null);
  const [avviato, setAvviato] = useState(false);
  const [modulo, setModulo] = useState<{
    attivo: boolean; host: string; porta: string; utente: string; cartella: string; conserva: string;
  } | null>(null);

  const imp = stato.dati?.impostazioni;
  const valori = modulo ?? (imp ? {
    attivo: imp.attivo, host: imp.host, porta: String(imp.porta), utente: imp.utente, cartella: imp.cartella,
    conserva: String(imp.conserva),
  } : null);
  const inCorsoQualcosa = (stato.dati?.esecuzioni ?? []).some((e) => e.esito === "in_corso");

  /* Mentre un backup lavora, lo storico si rilegge da solo. */
  useEffect(() => {
    if (!inCorsoQualcosa && !avviato) return;
    const t = setInterval(() => stato.ricarica(), 3000);
    return () => clearInterval(t);
  }, [inCorsoQualcosa, avviato, stato]);

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valori) return;
    const r = await esegui((t) => salvaImpostazioniBackup(t, {
      attivo: valori.attivo, host: valori.host.trim(), porta: Number(valori.porta) || 22, utente: valori.utente.trim(),
      cartella: valori.cartella.trim(), conserva: Number(valori.conserva) || 7,
    }));
    if (r) { setModulo(null); stato.ricarica(); }
  };

  const fai = async (fidati: boolean) => {
    const r = await esegui((t) => provaBackup(t, fidati));
    if (r) { setProva(r); stato.ricarica(); }
  };

  const oraBackup = async () => {
    if (await esegui((t) => eseguiBackup(t))) { setAvviato(true); stato.ricarica(); setTimeout(() => setAvviato(false), 60000); }
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Backup</h1>
          <p className={comuni.sottotitolo}>
            Ogni notte alle 2:30 il database intero (letture, utenti e accessi di Keycloak, immagini) va sul NAS, e si
            tengono le ultime copie. Le più vecchie si cancellano solo dopo un caricamento riuscito.
          </p>
        </div>
        <button className={comuni.primaria} onClick={oraBackup} disabled={inCorso || inCorsoQualcosa || !imp?.impronta_host}>
          {inCorsoQualcosa || avviato ? "Backup in corso…" : "Esegui ora"}
        </button>
      </div>

      {(stato.errore || errore) && <p className={comuni.errore} role="alert">{errore ?? stato.errore}</p>}
      {!stato.dati && stato.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {stato.dati && valori && (
        <>
          <section className={comuni.riquadro} aria-labelledby="titolo-destinazione">
            <h2 id="titolo-destinazione" className={comuni.riquadroTitolo}>Destinazione</h2>
            <form onSubmit={salva} className={comuni.riga} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Host</span>
                <input className={comuni.ingresso} value={valori.host} placeholder="100.84.254.116"
                  onChange={(e) => setModulo({ ...valori, host: e.target.value })} />
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Porta</span>
                <input className={comuni.ingresso} inputMode="numeric" value={valori.porta}
                  onChange={(e) => setModulo({ ...valori, porta: e.target.value })} />
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Utente</span>
                <input className={comuni.ingresso} value={valori.utente} autoComplete="off" placeholder="nuspy"
                  onChange={(e) => setModulo({ ...valori, utente: e.target.value })} />
                <span className={comuni.campoAiuto}>
                  L&apos;utente del NAS per cui è installata la chiave SSH (qui: nuspy). root di solito non la accetta.
                </span>
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Cartella</span>
                <input className={comuni.ingresso} value={valori.cartella} placeholder="/Volume1/backup/tarots"
                  onChange={(e) => setModulo({ ...valori, cartella: e.target.value })} />
                <span className={comuni.campoAiuto}>
                  Si crea da sola alla prima prova, se manca. Le maiuscole contano: /Volume1/backup/tarots non è
                  /Volume1/Backup/Tarots.
                </span>
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Copie da tenere</span>
                <input className={comuni.ingresso} inputMode="numeric" value={valori.conserva}
                  onChange={(e) => setModulo({ ...valori, conserva: e.target.value })} />
              </label>
              <label className={comuni.campo} style={{ flexDirection: "row", alignItems: "center", gap: ".5rem" }}>
                <input type="checkbox" checked={valori.attivo} onChange={(e) => setModulo({ ...valori, attivo: e.target.checked })} />
                <span>Backup notturno acceso</span>
              </label>
              <button className={comuni.primaria} type="submit" disabled={inCorso || !modulo}>Salva</button>
            </form>
            <p className={comuni.campoAiuto} style={{ marginTop: "1rem" }}>
              Chiave del NAS accettata:{" "}
              {imp?.impronta_host
                ? <span className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{imp.impronta_host}</span>
                : <b>nessuna — fai la prova e accettala, altrimenti il backup non parte</b>}
            </p>
            <div className={comuni.riga} style={{ flexWrap: "wrap", marginTop: ".75rem" }}>
              <button className={comuni.secondaria} onClick={() => fai(false)} disabled={inCorso || !!modulo}>Prova il collegamento</button>
              {prova?.riuscita && !prova.accettata && (
                <button className={comuni.primaria} onClick={() => fai(true)} disabled={inCorso}>Fidati di questa chiave</button>
              )}
            </div>
            {modulo && <p className={comuni.campoAiuto}>Salva le modifiche prima della prova.</p>}
            {prova && (
              prova.riuscita ? (
                <p className={comuni.esito}>
                  Collegamento riuscito in {prova.millisecondi} ms: cartella pronta, scrittura e cancellazione di un file di
                  prova riuscite, {prova.copie} copie presenti. Chiave del NAS:{" "}
                  <span className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{prova.impronta}</span>
                  {prova.accettata ? " (accettata)." : " — confrontala con quella del NAS prima di accettarla."}
                </p>
              ) : <p className={comuni.errore}>{prova.dettaglio}</p>
            )}
          </section>

          <Credenziale credenziale={stato.dati.credenziale} onCambiata={() => stato.ricarica()} />

          <Copie abilitato={!!imp?.impronta_host} onRipristino={() => stato.ricarica()} />

          <h2 className={comuni.riquadroTitolo} style={{ marginTop: "1.5rem" }}>Storico</h2>
          {stato.dati.esecuzioni.length === 0 ? (
            <div className={comuni.vuoto}>Nessuna esecuzione ancora.</div>
          ) : (
            <ul className={stato.inCorso ? comuni.inRicarica : undefined}
              style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: ".6rem" }}>
              {stato.dati.esecuzioni.map((e) => (
                <li key={e.id} className={comuni.riquadro} style={{ padding: ".75rem 1rem" }}>
                  <strong>{e.avviata_il ? quandoCompleto(e.avviata_il) : "—"}</strong>{" "}
                  <span className={comuni.stato}>{TIPI[e.tipo]}</span>{" "}
                  <span className={`${comuni.stato} ${ESITI[e.esito][1]}`}>{ESITI[e.esito][0]}</span>{" "}
                  <span className={comuni.stato}>{e.manuale ? "dalla console" : "notturno"}</span>
                  {e.file && <div className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{e.file} · {dimensione(e.byte)}{e.durata_secondi != null ? ` · ${e.durata_secondi} s` : ""}</div>}
                  {e.eliminati.length > 0 && <div className={comuni.campoAiuto}>Cancellate: {e.eliminati.join(", ")}</div>}
                  {e.dettaglio && <div style={{ overflowWrap: "anywhere" }}>{e.dettaglio}</div>}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </>
  );
}

/* La credenziale per entrare nel NAS (v9, Fase 2c): la chiave SSH privata (dal file o incollata) o la password
 * dell'utente del NAS. Si salva cifrata con la chiave master che sta solo sul server, e non si rilegge: della chiave
 * si mostrano soltanto tipo e impronta. */
function Credenziale({ credenziale, onCambiata }: { credenziale: CredenzialeBackup; onCambiata: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [chiave, setChiave] = useState("");
  const [password, setPassword] = useState("");
  const [nomeFile, setNomeFile] = useState<string | null>(null);
  const [salvata, setSalvata] = useState(false);

  const leggiFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 20_000) {
      setNomeFile(`${file.name}: troppo grande per essere una chiave SSH`);
      return;
    }
    setNomeFile(file.name);
    setChiave(await file.text());
    setSalvata(false);
  };

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    const r = await esegui((t) => salvaCredenzialeBackup(t, { chiave_ssh: chiave, password }));
    if (r) {
      setChiave("");
      setPassword("");
      setNomeFile(null);
      setSalvata(true);
      onCambiata();
    }
  };

  const togli = async () => {
    if (!window.confirm("Togliere dalla console chiave e password del NAS? Il backup userà il Secret del server, se c'è.")) return;
    if (await esegui((t) => salvaCredenzialeBackup(t, { togli: true }))) onCambiata();
  };

  const origine = credenziale.origine === "console" ? "caricata da questa pagina"
    : credenziale.origine === "server" ? "dal Secret del server (ripiego)" : null;

  return (
    <section className={comuni.riquadro} aria-labelledby="titolo-credenziale" style={{ marginTop: "1.5rem" }}>
      <h2 id="titolo-credenziale" className={comuni.riquadroTitolo}>Credenziale del NAS</h2>
      <p className={comuni.riquadroNota}>
        Per entrare nel NAS serve una <b>chiave SSH privata</b> (un file di testo che comincia con «-----BEGIN OPENSSH
        PRIVATE KEY-----», la cui metà pubblica è installata sul NAS per l&apos;utente qui sopra) oppure la password di
        quell&apos;utente. Si salva cifrata: il backup che va sul NAS contiene solo testo illeggibile, non la chiave.
      </p>
      <p>
        {credenziale.configurata ? (
          <span className={`${comuni.stato} ${comuni.positivo}`}><span aria-hidden="true">✓ </span>impostata</span>
        ) : (
          <span className={`${comuni.stato} ${comuni.negativo}`}><span aria-hidden="true">○ </span>mancante: il backup non parte</span>
        )}
        {origine && <span className={comuni.campoAiuto}> · {origine}</span>}
        {credenziale.chiave_tipo && (
          <span className={comuni.campoAiuto} style={{ display: "block", overflowWrap: "anywhere" }}>
            Chiave {credenziale.chiave_tipo}, impronta <span className={comuni.mono}>{credenziale.chiave_impronta}</span>
            {credenziale.password ? " · c'è anche una password" : ""}
          </span>
        )}
      </p>
      <form onSubmit={salva}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Chiave SSH privata: scegli il file…</span>
          <input type="file" onChange={leggiFile} style={{ minHeight: 44 }} />
          {nomeFile && <span className={comuni.campoAiuto}>{nomeFile}</span>}
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>…oppure incollala qui</span>
          <textarea className={comuni.area} value={chiave} spellCheck={false} autoComplete="off"
            onChange={(e) => { setChiave(e.target.value); setSalvata(false); }}
            placeholder={"-----BEGIN OPENSSH PRIVATE KEY-----\n…\n-----END OPENSSH PRIVATE KEY-----"} />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Oppure la password dell&apos;utente del NAS</span>
          <input className={comuni.ingresso} type="password" value={password} autoComplete="new-password"
            onChange={(e) => { setPassword(e.target.value); setSalvata(false); }} />
        </label>
        <div className={comuni.riga} style={{ alignItems: "center" }}>
          <button type="submit" className={comuni.primaria} style={{ minHeight: 44 }}
            disabled={inCorso || (!chiave.trim() && !password)}>
            Salva la credenziale
          </button>
          {credenziale.origine === "console" && (
            <button type="button" className={comuni.secondaria} style={{ minHeight: 44 }} onClick={togli} disabled={inCorso}>
              Togli la credenziale
            </button>
          )}
        </div>
      </form>
      <div aria-live="polite">
        {salvata && <p className={comuni.esito}>Credenziale salvata (cifrata). Ora «Prova il collegamento».</p>}
        {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      </div>
    </section>
  );
}

function Copie({ abilitato, onRipristino }: { abilitato: boolean; onRipristino: () => void }) {
  const [aperte, setAperte] = useState(false);
  const copie = useDati(async (t) => (aperte ? copieBackup(t) : { copie: [] as CopiaBackup[] }), [aperte]);
  const { esegui, inCorso, errore } = useAzione();
  const [scelta, setScelta] = useState<string | null>(null);
  const [conferma, setConferma] = useState("");
  /* Subito dopo l'avvio il server potrebbe non dire ancora «in corso»: si segue per qualche secondo comunque. */
  const [seguendo, setSeguendo] = useState(false);
  const stato = useDati(statoRipristino);

  const lavora = seguendo || !!stato.dati?.in_corso;
  useEffect(() => {
    if (!lavora) return;
    const t = setInterval(() => { stato.ricarica(); onRipristino(); }, 2000);
    return () => clearInterval(t);
  }, [lavora, stato, onRipristino]);

  const ripristina = async () => {
    if (!scelta) return;
    if (await esegui((t) => ripristinaBackup(t, scelta, conferma))) {
      setSeguendo(true);
      setTimeout(() => setSeguendo(false), 6000);
      setConferma("");
      stato.ricarica();
    }
  };
  const mostra: StatoRipristino | null = stato.dati?.file ? stato.dati : null;

  return (
    <section className={comuni.riquadro} aria-labelledby="titolo-copie" style={{ marginTop: "1.5rem" }}>
      <h2 id="titolo-copie" className={comuni.riquadroTitolo}>Copie sul NAS e ripristino</h2>
      {!aperte ? (
        <button className={comuni.secondaria} onClick={() => setAperte(true)} disabled={!abilitato}>Mostra le copie sul NAS</button>
      ) : (
        <>
          {copie.errore && <p className={comuni.errore}>{copie.errore}</p>}
          {copie.inCorso && !copie.dati?.copie.length && <p className={comuni.caricamento}>Lettura del NAS…</p>}
          {copie.dati && copie.dati.copie.length === 0 && !copie.inCorso && <div className={comuni.vuoto}>Nessuna copia sul NAS.</div>}
          <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: ".4rem" }}>
            {copie.dati?.copie.map((c) => (
              <li key={c.nome}>
                <label style={{ display: "flex", gap: ".6rem", alignItems: "center", flexWrap: "wrap", minHeight: 44 }}>
                  <input type="radio" name="copia" checked={scelta === c.nome} onChange={() => setScelta(c.nome)} />
                  <span className={comuni.mono}>{c.nome}</span>
                  <span>{dimensione(c.byte)} · {quandoCompleto(c.data)}</span>
                  {c.sicurezza && <span className={comuni.stato}>copia di sicurezza</span>}
                  {!c.con_sha256 && <span className={`${comuni.stato} ${comuni.negativo}`}>senza sha256</span>}
                </label>
              </li>
            ))}
          </ul>
          {scelta && (
            <div style={{ marginTop: "1rem" }}>
              <p className={comuni.errore}>
                Il ripristino sostituisce <b>tutto</b> il database — letture, utenti, accessi, ordini, blog — con la copia{" "}
                <span className={comuni.mono}>{scelta}</span>. Prima si fa da solo una copia di sicurezza di com&apos;è
                adesso. Dopo, API e Keycloak vanno riavviati.
              </p>
              <div className={comuni.riga} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Scrivi «tarots» per confermare</span>
                  <input className={comuni.ingresso} value={conferma} autoComplete="off" onChange={(e) => setConferma(e.target.value)} />
                </label>
                <button className={comuni.distruttiva} onClick={ripristina} disabled={inCorso || lavora || conferma.trim() !== "tarots"}>
                  Ripristina questa copia
                </button>
              </div>
              {errore && <p className={comuni.errore}>{errore}</p>}
            </div>
          )}
          <button className={comuni.secondaria} style={{ marginTop: "1rem" }} onClick={() => copie.ricarica()} disabled={copie.inCorso}>Rileggi il NAS</button>
        </>
      )}
      {mostra && (mostra.in_corso || mostra.esito) && (
        <div role="status" style={{ marginTop: "1rem" }}>
          <p className={mostra.esito === "errore" ? comuni.errore : comuni.esito}>
            {mostra.in_corso ? `Ripristino in corso: ${mostra.fase}…` : mostra.esito === "ok"
              ? `Ripristino riuscito (${mostra.dettaglio}). Ora riavvia API e Keycloak: kubectl -n tarots rollout restart deploy/tarots-api deploy/tarots-keycloak`
              : `Ripristino non riuscito: ${mostra.dettaglio}. Il database non è cambiato.`}
          </p>
          {mostra.passi.length > 0 && (
            <ul className={comuni.mono} style={{ margin: 0, paddingLeft: "1.25rem" }}>
              {mostra.passi.map((p) => <li key={p}>{p}</li>)}
            </ul>
          )}
        </div>
      )}
    </section>
  );
}
