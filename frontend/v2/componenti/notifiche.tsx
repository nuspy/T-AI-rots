"use client";

/* Le notifiche nel sito (v9, Fase 5): tre pezzi.
 *
 * - `FusoAutomatico`: una volta per sessione, il fuso del browser (`Intl`) va sul profilo. Decide il giorno della carta
 *   del giorno e l'ora dei promemoria; nessuno deve sceglierlo a mano.
 * - `InvitoNotifiche`: dopo aver girato la carta del giorno, una domanda cortese («vuoi che te la ricordiamo ogni
 *   mattina?»). Solo con un sì il browser chiede il permesso: mai al caricamento. Un «non ora» lo fa tacere per un mese.
 * - `NotificheProfilo`: la sezione «Notifiche» del profilo — acceso/spento in questo browser, carta del giorno e la
 *   sua ora, promemoria, offerte (lo stesso consenso «Promozioni» della privacy), ore di silenzio. */

import { useEffect, useState } from "react";
import { useSessione } from "@/lib/sessione";
import { f, plurale } from "@/v2/i18n";
import { useConsensi } from "@/v2/lib/consensi";
import { useLingua } from "@/v2/lib/lingua";
import {
  attiva, disattiva, disponibilita, fusoDelBrowser, invitoChiuso, invitoDaMostrare, iscrizioneAttuale, leggiPreferenze,
  permesso, salvaFuso, salvaPreferenze, type Disponibilita, type EsitoAttivazione, type ModificaPreferenze,
} from "@/v2/lib/notifiche";
import { useAzione, useCarica } from "@/v2/lib/usa";

const CHIAVE_FUSO = "tarots.fuso";

export function FusoAutomatico() {
  const { autenticata, token } = useSessione();
  useEffect(() => {
    if (!autenticata) return;
    const fuso = fusoDelBrowser();
    if (!fuso) return;
    try {
      if (window.sessionStorage.getItem(CHIAVE_FUSO) === fuso) return;
    } catch {
      /* memoria bloccata: si salva comunque, è idempotente */
    }
    salvaFuso(token, fuso)
      .then(() => {
        try {
          window.sessionStorage.setItem(CHIAVE_FUSO, fuso);
        } catch {
          /* niente */
        }
      })
      .catch(() => undefined);
  }, [autenticata, token]);
  return null;
}

/** Lo stato delle notifiche in questo browser, letto dopo il montaggio (sul server non esiste). */
function useStatoBrowser() {
  const [stato, setStato] = useState<{ disponibile: Disponibilita; iscritto: boolean; negato: boolean } | null>(null);
  const aggiorna = () => {
    const disponibile = disponibilita();
    iscrizioneAttuale()
      .then((i) => setStato({ disponibile, iscritto: Boolean(i), negato: permesso() === "denied" }))
      .catch(() => setStato({ disponibile, iscritto: false, negato: permesso() === "denied" }));
  };
  useEffect(aggiorna, []);
  return { stato, aggiorna };
}

function messaggioEsito(esito: EsitoAttivazione | null, k: { negato: string; errore: string; non_supportato: string }) {
  if (esito === "negato") return k.negato;
  if (esito === "errore") return k.errore;
  if (esito === "non_supportato") return k.non_supportato;
  return null;
}

export function InvitoNotifiche() {
  const { t, lingua } = useLingua();
  const k = t.notifiche;
  const { token } = useSessione();
  const { stato } = useStatoBrowser();
  const [visibile, setVisibile] = useState(true);
  const [inCorso, setInCorso] = useState(false);
  const [esito, setEsito] = useState<EsitoAttivazione | null>(null);

  if (!stato || !visibile) return null;
  if (esito === "attive") return <p className="success invito-notifiche" role="status">{k.invito_fatto}</p>;
  if (stato.iscritto || stato.negato || stato.disponibile === "no" || !invitoDaMostrare()) return null;

  const chiudi = () => { invitoChiuso(); setVisibile(false); };

  return (
    <aside className="invito-notifiche" aria-labelledby="invito-notifiche-t">
      <p id="invito-notifiche-t" className="invito-notifiche-titolo">{k.invito_titolo}</p>
      {stato.disponibile === "ios_home" ? (
        <>
          <p className="small">{k.ios_testo}</p>
          <div className="button-row">
            <button type="button" className="button button-quiet button-small" onClick={chiudi}>{k.invito_no}</button>
          </div>
        </>
      ) : (
        <>
          <p className="small">{k.invito_testo}</p>
          <div className="button-row">
            <button type="button" className="button button-small" disabled={inCorso} onClick={async () => {
              setInCorso(true);
              const r = await attiva(token, lingua);
              setInCorso(false);
              setEsito(r);
              if (r === "negato") invitoChiuso();
            }}>{inCorso ? k.attivazione : k.invito_si}</button>
            <button type="button" className="button button-quiet button-small" onClick={chiudi}>{k.invito_no}</button>
          </div>
          {messaggioEsito(esito, k) && <p className="error small" role="alert">{messaggioEsito(esito, k)}</p>}
        </>
      )}
    </aside>
  );
}

export function NotificheProfilo() {
  const { t, lingua } = useLingua();
  const k = t.notifiche;
  const { token } = useSessione();
  const consensi = useConsensi();
  const preferenze = useCarica(leggiPreferenze);
  const { stato, aggiorna } = useStatoBrowser();
  const { esegui, inCorso, errore } = useAzione();
  const [esito, setEsito] = useState<EsitoAttivazione | null>(null);
  const [salvato, setSalvato] = useState(false);
  const [lavoro, setLavoro] = useState(false);
  const p = preferenze.dati;

  useEffect(() => {
    if (!salvato) return;
    const id = window.setTimeout(() => setSalvato(false), 3000);
    return () => window.clearTimeout(id);
  }, [salvato]);

  const salva = async (corpo: ModificaPreferenze) => {
    const r = await esegui((tok) => salvaPreferenze(tok, corpo));
    if (r) { preferenze.ricarica(); setSalvato(true); }
  };

  const altri = (p?.dispositivi ?? []).filter((d) => d.attivo && d.canale === "fcm").length;

  return (
    <section className="panel wide notifiche-profilo" id="notifiche" aria-labelledby="notifiche-t">
      <h2 id="notifiche-t">{k.titolo}</h2>
      <p className="small">{k.intro}</p>

      {stato && stato.disponibile === "si" && (
        <>
          <p className="small" role="status"><b>{stato.iscritto ? k.stato_attive : k.stato_spente}</b></p>
          <div className="button-row">
            {stato.iscritto ? (
              <button type="button" className="button button-quiet button-small" disabled={lavoro} onClick={async () => {
                setLavoro(true);
                await disattiva(token).catch(() => undefined);
                setLavoro(false);
                setEsito(null);
                aggiorna();
                preferenze.ricarica();
              }}>{k.disattiva}</button>
            ) : (
              <button type="button" className="button button-small" disabled={lavoro || stato.negato} onClick={async () => {
                setLavoro(true);
                const r = await attiva(token, lingua);
                setLavoro(false);
                setEsito(r);
                aggiorna();
                preferenze.ricarica();
              }}>{lavoro ? k.attivazione : k.attiva}</button>
            )}
          </div>
          {(stato.negato || messaggioEsito(esito, k)) && (
            <p className="error small" role="alert">{stato.negato ? k.negato : messaggioEsito(esito, k)}</p>
          )}
        </>
      )}
      {stato && stato.disponibile === "ios_home" && (
        <div className="notice">
          <b>{k.ios_titolo}</b>
          <p className="small" style={{ margin: ".3rem 0 0" }}>{k.ios_testo}</p>
        </div>
      )}
      {stato && stato.disponibile === "no" && <p className="small muted">{k.non_supportato}</p>}
      {altri > 0 && <p className="small muted">{plurale(altri, k.altri)}</p>}

      {p && (
        <div className="notifiche-scelte">
          <label className="check">
            <input type="checkbox" checked={p.carta_giorno} disabled={inCorso} onChange={(e) => salva({ carta_giorno: e.target.checked })} />
            <span><b>{k.carta}</b><small>{k.carta_testo}</small></span>
          </label>
          {p.carta_giorno && (
            <label className="field notifiche-ora">
              <span>{k.ora}</span>
              <input type="time" value={p.ora_carta} disabled={inCorso} onChange={(e) => e.target.value && salva({ ora_carta: e.target.value })} />
            </label>
          )}
          <label className="check">
            <input type="checkbox" checked={p.promemoria} disabled={inCorso} onChange={(e) => salva({ promemoria: e.target.checked })} />
            <span><b>{k.promemoria}</b><small>{k.promemoria_testo}</small></span>
          </label>
          <label className="check">
            <input type="checkbox" checked={consensi.dati?.marketing === "accettato"} disabled={!consensi.dati || inCorso}
              onChange={async (e) => {
                await consensi.scegli({ marketing: e.target.checked ? "accettato" : "rifiutato" }).catch(() => undefined);
              }} />
            <span><b>{k.promozioni}</b><small>{f(k.promozioni_testo, { n: p.tetto_promozioni_settimana })}</small></span>
          </label>
          <label className="check">
            <input type="checkbox" checked={p.silenzio} disabled={inCorso} onChange={(e) => salva({ silenzio: e.target.checked })} />
            <span><b>{k.silenzio}</b><small>{k.silenzio_testo}</small></span>
          </label>
          {p.silenzio && (
            <div className="form-grid notifiche-silenzio">
              <label className="field">
                <span>{k.dalle}</span>
                <input type="time" value={p.silenzio_dal} disabled={inCorso}
                  onChange={(e) => e.target.value && salva({ silenzio: true, silenzio_dal: e.target.value })} />
              </label>
              <label className="field">
                <span>{k.alle}</span>
                <input type="time" value={p.silenzio_al} disabled={inCorso}
                  onChange={(e) => e.target.value && salva({ silenzio: true, silenzio_al: e.target.value })} />
              </label>
            </div>
          )}
          {p.fuso_orario && <p className="small muted">{f(k.fuso, { fuso: p.fuso_orario.replace(/_/g, " ") })}</p>}
        </div>
      )}
      {preferenze.errore && <p className="error small" role="alert">{preferenze.errore}</p>}
      {errore && <p className="error small" role="alert">{errore}</p>}
      <p className="small" role="status" aria-live="polite">{salvato ? k.salvato : ""}</p>
    </section>
  );
}
