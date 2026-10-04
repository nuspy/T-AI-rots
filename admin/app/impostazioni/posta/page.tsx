"use client";

/* Impostazioni → Posta in uscita (v9, Fase 2c): il server da cui il sito spedisce le email (agli utenti: rinnovi,
 * solleciti, conferme; agli admin: rapporti e avvisi), la prova d'invio e lo stato del DNS (SPF, DKIM, DMARC).
 *
 * La password si scrive e non si rilegge. Se la console è vuota vale la configurazione del server, che al primo avvio
 * si copia qui da sola. */

import { useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import {
  dnsPosta, provaSmtp, salvaSmtp, statoSmtp,
  type EsitoDns, type StatoRecord, type StatoSmtp, type ValoriSmtp,
} from "@/lib/configurazioni";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../../configurazioni.module.css";
import { Presenza } from "../../pagamenti/fornitore";

const ORIGINE: Record<StatoSmtp["origine"], string> = {
  console: "impostata da questa pagina",
  ambiente: "quella del server (ripiego): salvala qui per gestirla dalla console",
  nessuna: "nessuna: email e rapporti non partono",
};

export default function PaginaPosta() {
  const stato = useDati(statoSmtp);
  const [aggiornato, setAggiornato] = useState<StatoSmtp | null>(null);
  const dati = aggiornato ?? stato.dati;

  return (
    <>
      <p className={stili.spiegazione}>
        Il server di posta del sito è <strong>Stalwart</strong>, su mail.tadamoo.com: <strong>solo spedisce</strong>{" "}
        (le email agli utenti e i rapporti agli amministratori). La posta che arriva agli indirizzi @tarots.chat non
        passa da qui: la riceve Namecheap e la inoltra ad a.taini@gmail.com (vedi Account → Namecheap).
      </p>
      {stato.errore && <p className={comuni.errore} role="alert">{stato.errore}</p>}
      {!dati && !stato.errore && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && (
        <>
          <Configurazione dati={dati} onStato={setAggiornato} />
          <Prova dati={dati} />
          <Dns dominio={dati.dominio} />
        </>
      )}
    </>
  );
}

function Configurazione({ dati, onStato }: { dati: StatoSmtp; onStato: (s: StatoSmtp) => void }) {
  const { esegui, inCorso, errore } = useAzione();
  /* Se la console è vuota, il modulo parte dai valori del server (tranne la password, che non esce mai). */
  const base: ValoriSmtp = dati.console.attiva
    ? dati.console
    : {
      host: dati.ambiente.host, porta: dati.ambiente.porta || 465, sicurezza: dati.ambiente.sicurezza,
      utente: dati.ambiente.utente, mittente: dati.ambiente.mittente, nome_mittente: dati.console.nome_mittente,
      dkim_selettore: dati.console.dkim_selettore,
    };
  const [v, setV] = useState<ValoriSmtp>(base);
  const [password, setPassword] = useState("");
  const [salvato, setSalvato] = useState(false);
  const passwordPresente = dati.console.password.impostata || (!dati.console.attiva && dati.ambiente.password.impostata);

  const campo = (nome: keyof ValoriSmtp) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setSalvato(false);
    setV({ ...v, [nome]: nome === "porta" ? Number(e.target.value.replace(/\D/g, "")) || 0 : e.target.value });
  };

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    const r = await esegui((t) => salvaSmtp(t, { ...v, porta: v.porta || 465, password }));
    if (r) {
      onStato(r);
      setPassword("");
      setSalvato(true);
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="posta-titolo">
      <h2 id="posta-titolo" className={comuni.riquadroTitolo}>Il server da cui partono le email</h2>
      <dl className={stili.voci}>
        <div className={stili.voce}>
          <dt>In uso</dt>
          <dd>{dati.in_uso.configurata ? `${dati.in_uso.host}:${dati.in_uso.porta}` : "—"}</dd>
        </div>
        <div className={stili.voce}>
          <dt>Mittente</dt>
          <dd>{dati.in_uso.mittente || "—"}</dd>
        </div>
        <div className={stili.voce}>
          <dt>Configurazione</dt>
          <dd>{ORIGINE[dati.origine]}</dd>
        </div>
      </dl>

      <form onSubmit={salva}>
        <div className={stili.campi}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Server (host)</span>
            <input className={comuni.ingresso} value={v.host} onChange={campo("host")} placeholder="mail.tadamoo.com"
              autoComplete="off" spellCheck={false} />
            <span className={comuni.campoAiuto}>Vuoto: la console smette di decidere e vale il server.</span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Porta</span>
            <input className={comuni.ingresso} inputMode="numeric" value={v.porta || ""} onChange={campo("porta")} />
            <span className={comuni.campoAiuto}>Di solito 465 con SSL, 587 con STARTTLS.</span>
          </label>
        </div>
        <fieldset className={stili.scelte}>
          <legend className={comuni.campoEtichetta}>Sicurezza della connessione</legend>
          <label className={stili.scelta}>
            <input type="radio" name="sicurezza" checked={v.sicurezza === "ssl"} onChange={() => setV({ ...v, sicurezza: "ssl" })} />
            <span>SSL (consigliata)<small>La connessione è cifrata dal primo byte. Porta 465.</small></span>
          </label>
          <label className={stili.scelta}>
            <input type="radio" name="sicurezza" checked={v.sicurezza === "starttls"} onChange={() => setV({ ...v, sicurezza: "starttls" })} />
            <span>STARTTLS<small>Si apre in chiaro e poi passa a cifrata. Porta 587.</small></span>
          </label>
        </fieldset>
        <div className={stili.campi}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Utente</span>
            <input className={comuni.ingresso} value={v.utente} onChange={campo("utente")} autoComplete="off"
              spellCheck={false} placeholder="noreply@tarots.chat" />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Password</span>
            <input className={comuni.ingresso} type="password" value={password} autoComplete="new-password"
              onChange={(e) => { setSalvato(false); setPassword(e.target.value); }}
              placeholder={passwordPresente ? "Impostata: lascia vuoto per non cambiarla" : ""} />
            <span className={comuni.campoAiuto}>
              <Presenza presente={passwordPresente} testo={["impostata", "mancante"]} /> Si salva cifrata e non si rilegge.
              {!dati.console.attiva && dati.ambiente.password.impostata && " Se lasci vuoto, si copia quella del server."}
            </span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Mittente (indirizzo)</span>
            <input className={comuni.ingresso} type="email" value={v.mittente} onChange={campo("mittente")}
              autoComplete="off" spellCheck={false} placeholder="noreply@tarots.chat" />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Nome del mittente</span>
            <input className={comuni.ingresso} value={v.nome_mittente} onChange={campo("nome_mittente")} />
            <span className={comuni.campoAiuto}>Quello che chi riceve vede accanto all&apos;indirizzo.</span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Selettore DKIM (facoltativo)</span>
            <input className={comuni.ingresso} value={v.dkim_selettore} onChange={campo("dkim_selettore")}
              autoComplete="off" spellCheck={false} />
            <span className={comuni.campoAiuto}>
              Il nome della firma DKIM che Stalwart usa (in Stalwart: Domini → tarots.chat → DKIM). Serve solo al
              controllo del DNS qui sotto; vuoto: si provano i nomi più comuni.
            </span>
          </label>
        </div>
        <button type="submit" className={`${comuni.primaria} ${stili.tocco}`} disabled={inCorso}>Salva</button>
      </form>
      <div aria-live="polite">
        {salvato && <p className={comuni.esito}>Posta salvata: da ora valgono questi valori.</p>}
        {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      </div>
    </section>
  );
}

function Prova({ dati }: { dati: StatoSmtp }) {
  const { esegui, inCorso, errore } = useAzione();
  const [a, setA] = useState(dati.email_admin ?? "");
  const [esito, setEsito] = useState(dati.ultima_prova.esito);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    const r = await esegui((t) => provaSmtp(t, a.trim()));
    if (r) setEsito(r);
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="prova-titolo">
      <h2 id="prova-titolo" className={comuni.riquadroTitolo}>Invia un&apos;email di prova</h2>
      <p className={stili.spiegazione}>
        Parte dallo stesso server e con le stesse impostazioni di tutte le altre email: se arriva, arrivano anche le
        altre. Salva prima le modifiche.
      </p>
      <form onSubmit={invia} className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Destinatario</span>
          <input className={comuni.ingresso} type="email" value={a} onChange={(e) => setA(e.target.value)} required />
        </label>
        <button type="submit" className={`${comuni.primaria} ${stili.tocco}`} disabled={inCorso || !a.trim()}>
          {inCorso ? "Invio…" : "Invia la prova"}
        </button>
      </form>
      <div aria-live="polite">
        {esito && (
          <p className={esito.ok ? comuni.esito : comuni.errore}>
            {esito.ok ? "✓ " : "✗ "}{esito.messaggio}
            {dati.ultima_prova.quando && !inCorso && esito === dati.ultima_prova.esito && (
              <span className={comuni.campoAiuto}> ({quandoCompleto(dati.ultima_prova.quando)})</span>
            )}
          </p>
        )}
        {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      </div>
    </section>
  );
}

const SPIEGAZIONI: Record<"spf" | "dkim" | "dmarc", { nome: string; cosa: string }> = {
  spf: {
    nome: "SPF",
    cosa: "Dice quali server possono spedire email a nome del dominio. Senza, le email sembrano falsificate.",
  },
  dkim: {
    nome: "DKIM",
    cosa: "Una firma che il server di posta mette su ogni email, con la chiave pubblica scritta nel DNS: prova che "
      + "l'email non è stata alterata. Il record da copiare lo dà Stalwart (Domini → tarots.chat → record DNS).",
  },
  dmarc: {
    nome: "DMARC",
    cosa: "Dice a Gmail e agli altri cosa fare di un'email che non passa SPF e DKIM, e a chi mandare i resoconti. "
      + "Per cominciare: nome _dmarc, tipo TXT, valore «v=DMARC1; p=none; rua=mailto:dmarc@tarots.chat».",
  },
};

const NOMI_STATO: Record<StatoRecord, string> = { presente: "presente", assente: "manca", errore: "non letto" };

function Dns({ dominio }: { dominio: string }) {
  const [forza, setForza] = useState(0);
  const dns = useDati((t) => dnsPosta(t, forza > 0), [forza]);
  const esito: EsitoDns | null = dns.dati;

  return (
    <section className={comuni.riquadro} aria-labelledby="dns-titolo">
      <h2 id="dns-titolo" className={comuni.riquadroTitolo}>Il DNS di {dominio}: le email arrivano o finiscono nello spam?</h2>
      <p className={stili.spiegazione}>
        Tre righe nel DNS del dominio (da Namecheap → Domain List → Manage → <strong>Advanced DNS</strong>) dicono ai
        servizi di posta se fidarsi delle email del sito. Senza DKIM e DMARC molte finiscono nello spam.
      </p>
      {dns.errore && <p className={comuni.errore}>{dns.errore}</p>}
      {!esito && !dns.errore && <p className={comuni.caricamento}>Lettura del DNS…</p>}
      {esito?.errore && <p className={comuni.errore}>{esito.errore}</p>}
      {esito && !esito.errore && (
        <ul className={dns.inCorso ? comuni.inRicarica : undefined} style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: ".75rem" }}>
          {(["spf", "dkim", "dmarc"] as const).map((k) => {
            const r = esito[k];
            const presente = r.stato === "presente";
            return (
              <li key={k} className={comuni.riquadro} style={{ margin: 0, padding: ".75rem 1rem" }}>
                <strong>{SPIEGAZIONI[k].nome}</strong>{" "}
                <span className={`${comuni.stato} ${presente ? comuni.positivo : comuni.negativo}`}>
                  <span aria-hidden="true">{presente ? "✓ " : "✗ "}</span>{NOMI_STATO[r.stato]}
                </span>
                {k === "dkim" && presente && esito.dkim.selettore && (
                  <span className={comuni.campoAiuto}> · selettore {esito.dkim.selettore}</span>
                )}
                <p className={comuni.campoAiuto} style={{ margin: ".35rem 0 0" }}>{SPIEGAZIONI[k].cosa}</p>
                {r.valore && <p className={comuni.mono} style={{ margin: ".35rem 0 0", overflowWrap: "anywhere", fontSize: ".8125rem" }}>{r.valore}</p>}
              </li>
            );
          })}
        </ul>
      )}
      {esito && esito.mx.length > 0 && (
        <p className={comuni.campoAiuto}>
          Posta in arrivo (MX): <span className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{esito.mx.join(", ")}</span>
        </p>
      )}
      <button type="button" className={`${comuni.secondaria} ${stili.tocco}`} onClick={() => setForza((n) => n + 1)}
        disabled={dns.inCorso}>
        Controlla di nuovo
      </button>
    </section>
  );
}
