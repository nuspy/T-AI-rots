"use client";

/* «L'account che c'era con la tua email era tuo?» (v8.6). Quando si entra con un social su un account la cui email
 * non era mai stata verificata, Keycloak (passo `tarots-unione-sicura`) collega il social, ma prima gli toglie i vecchi
 * accessi: chiunque poteva averlo creato scrivendo l'email di un altro. Il token porta la nota (claim `tarots_unione`)
 * e il server la tiene finché la persona non risponde: è suo (resta com'è) o non è suo (si separa, e lei riparte con
 * un account nuovo). Nella stessa finestra può scegliere una password, anche quella di prima.
 *
 * La domanda si apre solo se il token ha la nota: senza, nessuna chiamata. «Più tardi» la nasconde fino alla
 * prossima visita (la domanda resta aperta sul server). */

import { useEffect, useState } from "react";
import { ErroreApi, rispondiUnione, unioneDaConfermare, type UnioneDaConfermare } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { useLingua } from "@/v2/lib/lingua";
import { Modale } from "./modale";

const RISOLTA = "tarots.unione.risolta";
const RIMANDATA = "tarots.unione.rimandata";

/* I nomi dei social come li conosce la persona (gli alias di Keycloak, `auth/provider_sociali.py`). */
const NOMI_SOCIAL: Record<string, string> = {
  google: "Google", facebook: "Facebook", apple: "Apple", github: "GitHub", linkedin: "LinkedIn",
  microsoft: "Microsoft", twitter: "X",
};

function notaDelToken(token: string): string | null {
  try {
    const corpo = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const dati = JSON.parse(atob(corpo.padEnd(Math.ceil(corpo.length / 4) * 4, "=")));
    const nota = dati?.tarots_unione;
    return typeof nota === "string" && nota.includes("|") ? nota.split("|")[0] : null;
  } catch {
    return null;
  }
}

function leggi(memoria: Storage | undefined, chiave: string): string | null {
  try {
    return memoria?.getItem(chiave) ?? null;
  } catch {
    return null;
  }
}

function scrivi(memoria: Storage | undefined, chiave: string, valore: string): void {
  try {
    memoria?.setItem(chiave, valore);
  } catch {
    /* memoria bloccata: la domanda si ripresenterà, e il server sa già se ha risposta */
  }
}

export function ConfermaUnione() {
  const { token, autenticata } = useSessione();
  const [unione, setUnione] = useState<UnioneDaConfermare | null>(null);

  useEffect(() => {
    if (!autenticata || !token) return;
    const id = notaDelToken(token);
    if (!id || leggi(window.localStorage, RISOLTA) === id || leggi(window.sessionStorage, RIMANDATA) === id) return;
    let attivo = true;
    unioneDaConfermare(token)
      .then(({ unione: u }) => {
        if (!attivo) return;
        if (u) setUnione(u);
        else scrivi(window.localStorage, RISOLTA, id);
      })
      .catch(() => {
        /* riproverà al prossimo caricamento */
      });
    return () => {
      attivo = false;
    };
  }, [autenticata, token]);

  if (!unione) return null;
  return <DialogoUnione unione={unione} token={token} onChiusa={() => setUnione(null)} />;
}

/* La finestra, data la domanda. */
export function DialogoUnione({
  unione, token, onChiusa,
}: { unione: UnioneDaConfermare; token: string | null; onChiusa: () => void }) {
  const { t, locale } = useLingua();
  const k = t.profilo;
  const [scelta, setScelta] = useState<"mia" | "non_mia" | null>(null);
  const [password, setPassword] = useState("");
  const [mostra, setMostra] = useState(false);
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);

  const data = (iso: string | null) =>
    iso ? new Intl.DateTimeFormat(locale, { day: "numeric", month: "long", year: "numeric" }).format(new Date(iso)) : null;
  const creato = data(unione.creato_il ?? unione.contenuto.iscritto_il);
  const credenziali: Record<string, string> = { password: k.unione_cred_password, otp: k.unione_cred_otp };
  const tolti = [
    ...unione.credenziali.map((c) => credenziali[c] ?? k.unione_cred_chiave),
    ...unione.social.map((s) => NOMI_SOCIAL[s] ?? s),
  ];
  const c = unione.contenuto;
  const erroriPassword: Record<string, string> = {
    invalidPasswordMinLengthMessage: k.unione_pw_corta,
    invalidPasswordNotUsernameMessage: k.unione_pw_nome,
    invalidPasswordNotEmailMessage: k.unione_pw_email,
    invalidPasswordHistoryMessage: k.unione_pw_storia,
  };

  const rimanda = () => {
    scrivi(window.sessionStorage, RIMANDATA, unione.id);
    onChiusa();
  };

  const conferma = async () => {
    if (!scelta) return;
    setInCorso(true);
    setErrore(null);
    try {
      const esito = await rispondiUnione(token, scelta, password || undefined);
      scrivi(window.localStorage, RISOLTA, unione.id);
      onChiusa();
      /* Un account nuovo: profilo, crediti e storia della pagina sono ancora quelli dell'altro. */
      if (esito.nuovo_account) window.location.reload();
    } catch (e) {
      const chiave = e instanceof ErroreApi && e.stato === 422
        ? (e.dettaglio as { password?: string } | undefined)?.password
        : undefined;
      setErrore(chiave ? erroriPassword[chiave] ?? k.unione_pw_altro : k.unione_errore);
    } finally {
      setInCorso(false);
    }
  };

  return (
    <Modale aperta titolo={k.unione_titolo} onChiudi={rimanda}>
      <div className="unione">
        <p>{k.unione_esisteva}{creato ? ` ${k.unione_creato.replace("{data}", creato)}` : ""}</p>
        {tolti.length > 0 && <p>{k.unione_tolti.replace("{tolti}", tolti.join(", "))}</p>}
        <p className="unione-contenuto">
          {c.vuoto
            ? k.unione_vuoto
            : `${k.unione_contiene} ${k.unione_letture} ${c.letture} · ${k.unione_memorie} ${c.memorie} · ${k.unione_crediti} ${c.crediti} · ${k.unione_acquisti} ${c.ordini + c.acquisti}`}
        </p>

        <fieldset className="unione-scelta">
          <legend>{k.unione_domanda}</legend>
          <label className="check">
            <input type="radio" name="unione" checked={scelta === "mia"} onChange={() => setScelta("mia")} />
            <span>{k.unione_mia}</span>
          </label>
          <label className="check">
            <input type="radio" name="unione" checked={scelta === "non_mia"} onChange={() => setScelta("non_mia")} />
            <span>
              {k.unione_non_mia}
              {scelta === "non_mia" && <small>{c.vuoto ? k.unione_non_mia_vuoto : k.unione_non_mia_pieno}</small>}
            </span>
          </label>
        </fieldset>

        <label className="field">
          <span>{k.unione_password_titolo}</span>
          <span className="unione-password">
            <input type={mostra ? "text" : "password"} value={password} autoComplete="new-password" maxLength={128}
              onChange={(e) => setPassword(e.target.value)} />
            <button type="button" className="button button-quiet button-small" onClick={() => setMostra(!mostra)}
              aria-pressed={mostra}>
              {mostra ? k.unione_nascondi : k.unione_mostra}
            </button>
          </span>
          <small>{k.unione_password_aiuto}</small>
        </label>

        {errore && <p className="error" role="alert">{errore}</p>}
        <div className="button-row">
          <button type="button" className="button" disabled={!scelta || inCorso} onClick={conferma}>
            {k.unione_conferma}
          </button>
          <button type="button" className="button button-quiet" onClick={rimanda}>{k.unione_dopo}</button>
        </div>
      </div>
    </Modale>
  );
}
