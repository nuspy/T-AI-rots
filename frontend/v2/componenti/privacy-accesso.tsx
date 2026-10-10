"use client";

/* Ciò che il sito chiede appena si entra (GDPR, Fase 1), in un dialogo:
 *
 * - **l'età minima**: «ho almeno N anni», con N per il paese (14 in Italia e Spagna, 15 in Francia, 16 altrove;
 *   `backend/tarot_core/tarot/eta_minima.py`). Senza conferma niente letture né chat: il dialogo si può chiudere
 *   («Non ora»), e si ripresenta alla prossima lettura (`DialogoEta`, usato anche da `lettura.tsx`);
 * - **la cancellazione in corso**: chi ha chiesto di cancellare l'account e rientra nei 30 giorni lo trova chiuso;
 *   qui può riaprirlo («Annulla la cancellazione») o uscire.
 *
 * Una sola chiamata a ogni sessione (`GET /me/privacy`): un 200 dice l'età, un 409 `account_in_cancellazione` la
 * cancellazione in corso. */

import { useEffect, useId, useState } from "react";
import { f } from "@/v2/i18n";
import {
  annullaCancellazione, confermaEta, inCancellazione, leggiPrivacy, type StatoCancellazione, type StatoEta,
} from "@/lib/privacy";
import { useSessione } from "@/lib/sessione";
import { useLingua } from "@/v2/lib/lingua";
import { etaConfermata, ricordaEta } from "@/v2/lib/ricordi-lettura";
import { R } from "@/v2/lib/percorsi";
import LinkV2 from "./link";
import { Modale } from "./modale";

/** «Ho almeno N anni». `onConferma` riceve gli anni confermati: chi chiama li manda al server (con o senza account). */
export function DialogoEta({
  anni, aperta, insufficiente = false, onConferma, onChiudi,
}: {
  anni: number;
  aperta: boolean;
  /** La data di nascita dice meno anni del minimo: niente da confermare, solo da spiegare. */
  insufficiente?: boolean;
  onConferma: (anni: number) => Promise<void> | void;
  onChiudi: () => void;
}) {
  const { t } = useLingua();
  const k = t.comune;
  const id = useId();
  const [spuntata, setSpuntata] = useState(false);
  const [inCorso, setInCorso] = useState(false);
  return (
    <Modale aperta={aperta} titolo={insufficiente ? k.eta_titolo_no : k.eta_titolo} onChiudi={onChiudi}>
      {insufficiente ? (
        <>
          <p>{f(k.eta_insufficiente, { anni })}</p>
          <div className="button-row">
            <LinkV2 className="button button-quiet" href={`${R.profilo}#carte`} onClick={onChiudi}>{k.eta_correggi}</LinkV2>
          </div>
        </>
      ) : (
        <>
          <p>{f(k.eta_testo, { anni })}</p>
          <label className="check" htmlFor={`${id}-c`}>
            <input id={`${id}-c`} type="checkbox" checked={spuntata} onChange={(e) => setSpuntata(e.target.checked)} />
            <span>{f(k.eta_dichiaro, { anni })}</span>
          </label>
          {/* Prima della prima lettura: accanto all'informativa, i termini di servizio (che la lettura fa accettare). */}
          <p className="small muted">
            {k.eta_perche} <LinkV2 className="inline" href={`${R.privacy}#pv-eta`}>{k.cookie_leggi}</LinkV2>
            {" · "}<LinkV2 className="inline" href={R.termini}>{k.piede_termini}</LinkV2>
          </p>
          <div className="button-row">
            <button type="button" className="button" disabled={!spuntata || inCorso} onClick={async () => {
              setInCorso(true);
              try { await onConferma(anni); } finally { setInCorso(false); }
            }}>{k.eta_conferma}</button>
            <button type="button" className="button button-quiet" onClick={onChiudi}>{k.eta_non_ora}</button>
          </div>
        </>
      )}
    </Modale>
  );
}

export function PrivacyAccesso() {
  const { t, locale } = useLingua();
  const k = t.comune;
  const sessione = useSessione();
  const [eta, setEta] = useState<StatoEta | null>(null);
  const [cancellazione, setCancellazione] = useState<StatoCancellazione | null>(null);
  const [chiuso, setChiuso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);
  const [inCorso, setInCorso] = useState(false);

  useEffect(() => {
    if (!sessione.autenticata) return;
    let attivo = true;
    leggiPrivacy(sessione.token)
      .then(async (p) => {
        if (!attivo) return;
        setCancellazione(null);
        /* L'età già confermata su questo dispositivo (cookie, `ricordi-lettura.ts`) va nel profilo da sola: il dialogo
         * non si ripresenta a chi ha già detto di sì, anche prima di entrare con l'account. */
        const giaConfermata = etaConfermata();
        if (p.eta.da_confermare && giaConfermata !== null && giaConfermata >= p.eta.anni) {
          try {
            const ora = await confermaEta(sessione.token, giaConfermata);
            if (attivo) setEta(ora);
            return;
          } catch {
            /* si chiede col dialogo */
          }
        }
        if (attivo) setEta(p.eta);
      })
      .catch((e: unknown) => { if (attivo) setCancellazione(inCancellazione(e)); });
    return () => { attivo = false; };
  }, [sessione.autenticata, sessione.token]);

  if (!sessione.autenticata) return null;

  if (cancellazione) {
    const quando = cancellazione.definitiva_il
      ? new Date(cancellazione.definitiva_il).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" })
      : "";
    return (
      <Modale aperta titolo={k.cancellazione_titolo} onChiudi={sessione.esci}>
        <p>{f(k.cancellazione_testo, { data: quando })}</p>
        <div className="button-row">
          <button type="button" className="button" disabled={inCorso} onClick={async () => {
            setInCorso(true);
            setErrore(null);
            try {
              await annullaCancellazione(sessione.token);
              window.location.reload();
            } catch {
              setErrore(k.err_operazione);
            } finally {
              setInCorso(false);
            }
          }}>{k.cancellazione_annulla}</button>
          <button type="button" className="button button-quiet" onClick={sessione.esci}>{k.cancellazione_esci}</button>
        </div>
        {errore && <p className="error" role="alert">{errore}</p>}
      </Modale>
    );
  }

  if (!eta || chiuso || (!eta.da_confermare && !eta.sotto_eta)) return null;
  return (
    <DialogoEta anni={eta.anni} aperta insufficiente={eta.sotto_eta} onChiudi={() => setChiuso(true)}
      onConferma={async (anni) => {
        ricordaEta(anni);
        try {
          setEta(await confermaEta(sessione.token, anni));
        } catch {
          setChiuso(true);
        }
      }} />
  );
}
