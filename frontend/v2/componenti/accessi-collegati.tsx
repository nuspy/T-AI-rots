"use client";

/* «Modi di accesso» nel profilo (v9, Fase 6): i social collegati all'account, «Collega il tuo Apple ID» e «Collega
 * Google», e il codice che arriva dall'app.
 *
 * Perché serve. Nell'app si entra solo con Apple (iPhone) o solo con Google (Android). Con la stessa email l'account
 * è già lo stesso (Keycloak li unisce); con «Nascondi la mia email» di Apple no: nell'app nascerebbe un account
 * nuovo. Collegando prima Apple da qui, l'app trova subito questo account. Se l'account nuovo nell'app c'è già, l'app
 * mostra un codice: scritto qui, l'accesso dell'app (e ciò che c'era) passa a questo account.
 *
 * Il collegamento è quello «avviato dal client» di Keycloak (vedi `backend/tarot_core/tarot/collega_identita.py`): il
 * suo indirizzo contiene un'impronta dell'id della sessione, che deve essere quella del browser. Per questo, al clic,
 * si ripassa prima da Keycloak (istantaneo se la sessione c'è ancora, la pagina d'accesso se è scaduta) tornando qui con il
 * ritorno `?collega=apple`; al ritorno si chiede l'indirizzo e si parte. Keycloak riporta qui con `?collegato=apple`
 * (e `link_error` se non è riuscito). */

import { useEffect, useRef, useState } from "react";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import {
  PARAMETRO_COLLEGA, PARAMETRO_COLLEGATO, eCollegabile, leggiCollegamenti, motivoErrore, urlCollegamento, usaCodice,
  type SocialCollegabile,
} from "@/v2/lib/collega";
import { useLingua } from "@/v2/lib/lingua";
import { useCarica } from "@/v2/lib/usa";

const NOMI: Record<string, string> = { apple: "Apple", google: "Google" };

/** Toglie dall'indirizzo i parametri del collegamento, senza ricaricare la pagina. */
function pulisciIndirizzo(): void {
  const url = new URL(window.location.href);
  for (const p of [PARAMETRO_COLLEGA, PARAMETRO_COLLEGATO, "link_error", "nonce"]) url.searchParams.delete(p);
  window.history.replaceState(window.history.state, document.title, `${url.pathname}${url.search}${url.hash}`);
}

/** Cosa dice l'indirizzo all'apertura: si parte verso Keycloak (`?collega=`), o si torna da lui (`?collegato=`). */
function leggiIndirizzo(): { parti: SocialCollegabile | null; tornato: SocialCollegabile | null; errore: string | null } {
  if (typeof window === "undefined") return { parti: null, tornato: null, errore: null };
  const q = new URLSearchParams(window.location.search);
  const parti = q.get(PARAMETRO_COLLEGA);
  const tornato = q.get(PARAMETRO_COLLEGATO);
  return { parti: eCollegabile(parti) ? parti : null, tornato: eCollegabile(tornato) ? tornato : null, errore: q.get("link_error") };
}

export function AccessiCollegati({ onSpostato }: { onSpostato?: () => void }) {
  const { t } = useLingua();
  const k = t.profilo;
  const sessione = useSessione();
  const stato = useCarica(leggiCollegamenti);
  /* Letto una volta, al montaggio: la sezione esiste solo nel browser, dopo l'accesso. */
  const [indirizzo] = useState(leggiIndirizzo);
  const [messaggio, setMessaggio] = useState<{ testo: string; buono: boolean } | null>(() => {
    if (!indirizzo.tornato) return null;
    if (indirizzo.errore) {
      return { testo: indirizzo.errore === "not_logged_in" ? k.acc_errore_sessione : k.acc_errore, buono: false };
    }
    return { testo: f(k.acc_fatto, { provider: NOMI[indirizzo.tornato] }), buono: true };
  });
  const [inCorso, setInCorso] = useState(indirizzo.parti !== null);
  const [codice, setCodice] = useState("");
  const avviato = useRef(false);

  /* Una volta sola: si toglie il segno dall'indirizzo e, se si parte, si chiede l'indirizzo del collegamento. */
  useEffect(() => {
    if (!sessione.autenticata || !sessione.token || avviato.current) return;
    if (!indirizzo.parti && !indirizzo.tornato) return;
    avviato.current = true;
    pulisciIndirizzo();
    const provider = indirizzo.parti;
    if (!provider) return;
    const ritorno = new URL(window.location.href);
    ritorno.searchParams.set(PARAMETRO_COLLEGATO, provider);
    ritorno.hash = "";
    urlCollegamento(sessione.token, provider, ritorno.toString())
      .then(({ url }) => { window.location.assign(url); })
      .catch(() => { setInCorso(false); setMessaggio({ testo: k.acc_errore, buono: false }); });
  }, [sessione.autenticata, sessione.token, indirizzo, k]);

  const collega = (provider: SocialCollegabile) => {
    setMessaggio(null);
    setInCorso(true);
    const qui = new URL(window.location.href);
    qui.searchParams.set(PARAMETRO_COLLEGA, provider);
    sessione.entraQui(`${qui.pathname}${qui.search}`);
  };

  const usa = async () => {
    setMessaggio(null);
    setInCorso(true);
    try {
      const r = await usaCodice(sessione.token, codice);
      setCodice("");
      setMessaggio({ testo: f(k.acc_codice_fatto, { provider: r.provider.map((p) => NOMI[p] ?? p).join(", ") }), buono: true });
      stato.ricarica();
      onSpostato?.();
    } catch (e) {
      const { motivo, provider } = motivoErrore(e);
      const testi = k.acc_codice_errori as Record<string, string>;
      setMessaggio({
        testo: f(testi[motivo] ?? testi.generico, { provider: (provider ?? []).map((p) => NOMI[p] ?? p).join(", ") }),
        buono: false,
      });
    } finally {
      setInCorso(false);
    }
  };

  const dati = stato.dati;
  const pulito = codice.replace(/[^A-Za-z0-9]/g, "");
  return (
    <section className="panel" id="accessi" aria-labelledby="accessi-t">
      <h2 id="accessi-t">{k.acc_titolo}</h2>
      <p className="small">{k.acc_testo}</p>
      {dati && !dati.raggiungibile && <p className="small muted">{k.acc_non_raggiungibile}</p>}
      {dati?.raggiungibile && (
        <p role="status">
          <b>{k.acc_collegati}</b>{" "}
          {dati.collegati.length
            ? dati.collegati.map((p) => `✓ ${NOMI[p] ?? p}`).join(" · ")
            : <span className="muted">{k.acc_nessuno}</span>}
        </p>
      )}
      {dati?.raggiungibile && dati.collegabili.length > 0 && (
        <div className="button-row">
          {dati.collegabili.map((p) => (
            <button key={p} type="button" className="button button-small" disabled={inCorso} onClick={() => collega(p)}>
              {p === "apple" ? k.acc_collega_apple : k.acc_collega_google}
            </button>
          ))}
        </div>
      )}

      <h3 style={{ marginTop: ".8rem" }}>{k.acc_codice_titolo}</h3>
      <p className="small">{k.acc_codice_testo}</p>
      <form className="button-row" style={{ alignItems: "end" }} onSubmit={(e) => { e.preventDefault(); if (pulito.length === 8) void usa(); }}>
        <label className="field" style={{ margin: 0, flex: "1 1 10rem" }}><span>{k.acc_codice_campo}</span>
          <input value={codice} maxLength={12} autoComplete="one-time-code" autoCapitalize="characters" spellCheck={false}
            inputMode="text" placeholder="ABCD-EFGH" style={{ letterSpacing: ".12em", textTransform: "uppercase" }}
            onChange={(e) => setCodice(e.target.value.toUpperCase())} /></label>
        <button type="submit" className="button button-small" disabled={inCorso || pulito.length !== 8}>{k.acc_codice_usa}</button>
      </form>
      {messaggio && <p className={messaggio.buono ? "success" : "error"} role={messaggio.buono ? "status" : "alert"}>{messaggio.testo}</p>}
    </section>
  );
}
