"use client";

/* «Privacy e consensi» nel profilo (GDPR, Fase 1): ogni consenso, revocabile come si è dato (una casella), il
 * download dei propri dati, la cancellazione della chat e dell'account.
 *
 * Le categorie: statistiche del sito, Google Analytics, pubblicità (solo se gli spazi sono accesi o se ne era già
 * stata fatta una scelta), testi per statistiche e spunti del blog, dati particolari (art. 9), promozioni. Spegnere i
 * dati particolari toglie subito la casella «persona trans» e i ricordi sulla salute (lo fa il server, e lo dice la
 * frase sotto la casella). */

import { useState } from "react";
import type { TipoConsenso } from "@/lib/api";
import { cancellaChat, leggiPrivacy, scaricaEsportazione, type Categoria } from "@/lib/privacy";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { Modale } from "@/v2/componenti/modale";
import { usePubblicita } from "@/v2/componenti/pubblicita";
import { useConsensi } from "@/v2/lib/consensi";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";

export function PrivacyProfilo({ onCambio }: { onCambio?: () => void }) {
  const { t, locale } = useLingua();
  const k = t.profilo;
  const consensi = useConsensi();
  const pubblicita = usePubblicita();
  const stato = useCarica(leggiPrivacy);
  const { esegui, inCorso, errore } = useAzione();
  const [salvando, setSalvando] = useState<TipoConsenso | null>(null);
  const [erroreScelta, setErroreScelta] = useState(false);
  const [esportazione, setEsportazione] = useState<string | null>(null);
  const [chatConferma, setChatConferma] = useState(false);
  const [chatCancellata, setChatCancellata] = useState(false);

  const voci: { tipo: Categoria; titolo: string; testo: string }[] = [
    { tipo: "statistiche", titolo: k.cons_statistiche, testo: k.cons_statistiche_testo },
    { tipo: "google_analytics", titolo: k.cons_google, testo: k.cons_google_testo },
    /* Dove decide il CMP di Google (TCF) la scelta sugli annunci si cambia dalla pagina privacy, nel suo messaggio. */
    ...((pubblicita.attiva || consensi.dati?.pubblicita) && pubblicita.tcf.applica !== true
      ? [{ tipo: "pubblicita" as const, titolo: k.cons_pubblicita, testo: k.cons_pubblicita_testo }] : []),
    { tipo: "testi_statistiche", titolo: k.cons_testi, testo: k.cons_testi_testo },
    { tipo: "dati_particolari", titolo: k.cons_art9, testo: k.cons_art9_testo },
    { tipo: "marketing", titolo: k.cons_marketing, testo: k.cons_marketing_testo },
  ];
  const data = (iso: string | null | undefined) =>
    iso ? new Date(iso).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" }) : "";

  const cambia = async (tipo: Categoria, acceso: boolean) => {
    setSalvando(tipo);
    setErroreScelta(false);
    try {
      await consensi.scegli({ [tipo]: acceso ? "accettato" : "rifiutato" });
      stato.ricarica();
      if (tipo === "dati_particolari" && !acceso) onCambio?.();
    } catch {
      setErroreScelta(true);
    } finally {
      setSalvando(null);
    }
  };

  return (
    <section className="panel wide privacy-profilo" id="privacy" aria-labelledby="privacy-t">
      <h2 id="privacy-t">{k.privacy_titolo}</h2>
      <p className="small">{k.privacy_testo} <LinkV2 className="inline" href={R.privacy}>{k.stat_privacy}</LinkV2></p>

      <ul className="list-plain consensi-elenco">
        {voci.map((v) => {
          const valore = consensi.dati?.[v.tipo] ?? null;
          return (
            <li key={v.tipo}>
              <label className="check">
                <input type="checkbox" checked={valore === "accettato"} disabled={!consensi.dati || salvando !== null}
                  onChange={(e) => cambia(v.tipo, e.target.checked)} />
                <span>
                  <b>{v.titolo}</b>
                  <small className="consenso-stato">
                    {valore === "accettato" ? k.cons_attivo : valore === "rifiutato" ? k.cons_spento : k.cons_mai}
                    {stato.dati?.consensi[v.tipo]?.il ? ` · ${data(stato.dati.consensi[v.tipo]?.il)}` : ""}
                  </small>
                  <small>{v.testo}</small>
                </span>
              </label>
            </li>
          );
        })}
      </ul>
      {erroreScelta && <p className="error" role="alert">{t.comune.err_operazione}</p>}

      <h3>{k.esporta_titolo}</h3>
      <p className="small">{k.esporta_testo}</p>
      <button type="button" className="button button-small" disabled={inCorso} onClick={async () => {
        setEsportazione(null);
        const r = await esegui((tok) => scaricaEsportazione(tok));
        if (!r) return;
        if (r.ok) { setEsportazione(k.esporta_fatto); stato.ricarica(); }
        else setEsportazione(f(k.esporta_attendi, { data: data(r.prossimaDal) }));
      }}>{k.esporta_cta}</button>
      {esportazione && <p className="small" role="status">{esportazione}</p>}
      {stato.dati?.esportazione.ultima_il && !esportazione && (
        <p className="small muted">{f(k.esporta_ultima, { data: data(stato.dati.esportazione.ultima_il) })}</p>
      )}

      <h3>{k.chat_titolo}</h3>
      <p className="small">{k.chat_testo}</p>
      <button type="button" className="button button-quiet button-small" disabled={inCorso} onClick={() => setChatConferma(true)}>{k.chat_cancella}</button>
      {chatCancellata && <p className="success small" role="status">{k.chat_cancellata}</p>}

      <h3>{k.elimina_titolo}</h3>
      <p className="small">{f(k.elimina_breve, { giorni: stato.dati?.cancellazione.giorni_ripensamento ?? 30 })}</p>
      <LinkV2 className="button button-danger button-small" href={R.elimina}>{k.elimina_cta}</LinkV2>
      {errore && <p className="error" role="alert">{errore}</p>}

      <Modale aperta={chatConferma} titolo={k.chat_cancella} onChiudi={() => setChatConferma(false)}>
        <p>{k.chat_conferma}</p>
        <div className="button-row">
          <button type="button" className="button button-danger" disabled={inCorso} onClick={async () => {
            setChatConferma(false);
            const r = await esegui(async (tok) => { await cancellaChat(tok); return true; });
            if (r) setChatCancellata(true);
          }}>{k.chat_cancella}</button>
          <button type="button" className="button button-quiet" onClick={() => setChatConferma(false)}>{t.comune.annulla}</button>
        </div>
      </Modale>
    </section>
  );
}
