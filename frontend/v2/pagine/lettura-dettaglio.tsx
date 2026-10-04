"use client";

/* Una lettura conclusa, dentro la mia storia: la domanda, il tavolo, il quadro, l'interpretazione, e il ritorno
 * sulla lettura («si è avverato?»), che il lettore terrà presente nelle prossime. */

import { ProviderMazzoAttivo } from "@/lib/mazzo-attivo";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Markdown } from "@/lib/markdown";
import { annotaLettura, cancellaLettura, leggiLettura, type Compatibilita, type PersoneLettura } from "@/lib/api";
import { comeLingua } from "@/lib/i18n/lingue";
import { nomeCarta, nomeStesa } from "@/lib/i18n/nomi";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { Modale } from "@/v2/componenti/modale";
import { CarteDaStampare, NotaStampa, PulsanteStampa } from "@/v2/componenti/stampa";
import { PannelloCondivisione, urlCondivisioneV2 } from "@/v2/lettura/condivisione";
import { Tavolo, type Posata } from "@/v2/lettura/tavolo";
import stili from "@/v2/lettura/lettura.module.css";
import { LinguaNomi, useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";

function Persone({ persone, compat }: { persone: PersoneLettura; compat: Compatibilita | null }) {
  const { t, locale, lingua } = useLingua();
  const s = t.storia;
  const segno = (c?: string) => (c ? s.segni[c] ?? c : "");
  const cuspide = (x?: { cuspide: boolean; vicino: string | null }) => (x?.cuspide && x.vicino ? f(s.cuspide, { segno: segno(x.vicino) }) : "");
  const riga = (genere: string | null, altro: string | null, trans: boolean, nascita: string, sg: string, cu: string) => [
    genere ? `${genere === "altro" && altro ? altro : s.generi[genere] ?? genere}${trans ? `, ${s.persona_trans}` : ""}` : "",
    new Date(nascita).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" }),
    sg + (cu ? ` (${cu})` : ""),
  ].filter(Boolean).join(" · ");
  const p = persone.partner;
  return (
    <div className="panel">
      <h3>{s.le_persone}</h3>
      <p className="small"><strong>{s.tu}</strong> — {riga(persone.tu.genere, persone.tu.genere_altro, persone.tu.trans, persone.tu.nascita, segno(compat?.segni.tu.codice), cuspide(compat?.segni.tu))}</p>
      <p className="small"><strong>{[p.nome, p.cognome].filter(Boolean).join(" ")}</strong> — {riga(p.genere, p.genere_altro, p.trans, p.nascita, segno(compat?.segni.partner.codice), cuspide(compat?.segni.partner))}</p>
      {compat && (
        <>
          <h3 style={{ marginTop: "1rem" }}>{s.compat_titolo}</h3>
          <p className="small">{s.aspetto}: <strong>{s.aspetti[compat.aspetto] ?? compat.aspetto}</strong> · {s.armonia}: <strong>{s.armonie[compat.armonia] ?? compat.armonia}</strong></p>
          <p className="small">{s.elementi}: {s.nomi_elementi[compat.segni.tu.elemento] ?? compat.segni.tu.elemento} / {s.nomi_elementi[compat.segni.partner.elemento] ?? compat.segni.partner.elemento} · {s.relazioni_elementi[compat.relazione_elementi] ?? compat.relazione_elementi}</p>
          <p className="small">{s.carta_coppia}: {nomeCarta(compat.carta_coppia, lingua)}</p>
          <p className="small muted">{s.compat_avviso}</p>
        </>
      )}
    </div>
  );
}

export function DettaglioLettura({ id }: { id: string }) {
  const { t, lingua, locale, prefissoIt } = useLingua();
  const s = t.storia;
  const l = t.lettura;
  const sessione = useSessione();
  const router = useRouter();
  const lettura = useCarica((tok) => leggiLettura(tok, id), [id]);
  const { esegui } = useAzione();
  const [condividendo, setCondividendo] = useState(false);
  const [cancellando, setCancellando] = useState(false);
  const [annotato, setAnnotato] = useState(false);

  if (sessione.pronta && !sessione.autenticata) {
    return (
      <section className="band band-tight">
        <p>{s.fuori_testo}</p>
        <button type="button" className="button" onClick={() => sessione.entra(indirizzoV2(R.lettura(id), prefissoIt))}>{s.fuori_entra}</button>
      </section>
    );
  }
  if (lettura.errore) return <section className="band band-tight"><p className="error">{lettura.errore}</p></section>;
  const lt = lettura.dati;
  if (!lt) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;

  const ll = comeLingua(lt.lang) ?? lingua;
  const posate: Posata[] = lt.cards.map((c) => ({
    posizione: c.posizione, slot: null, calcolata: c.calcolata, rivelata: c.rivelata, carta: c.carta,
    rovescio: c.rovescio, interpretazione: c.interpretazione, dignita: lt.dignita?.[String(c.posizione)] ?? null,
  }));
  const annota = async (esito: string) => {
    await esegui((tok) => annotaLettura(tok, id, esito));
    setAnnotato(true);
    lettura.ricarica();
  };

  return (
    <ProviderMazzoAttivo slug={lt.mazzo ?? null}>
    <LinguaNomi valore={ll}>
      <section className="band band-tight">
        <LinkV2 className="button button-quiet button-small" href={R.storia}>← {s.indietro}</LinkV2>
        <div className={stili.scena} style={{ marginTop: ".5rem" }}>
          <small>{nomeStesa(lt.stesa_dati, ll)} · {f(s.dettaglio_quando, { data: new Date(lt.created_at).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" }) })}</small>
          <q dir="auto">{lt.question}</q>
        </div>
        <div className="read-layout">
          <section className="read-panel dark" aria-label={nomeStesa(lt.stesa_dati, ll)}>
            <Tavolo stesa={lt.stesa_dati} posate={posate} prossima={null} rivelazioneInCorso={false} evidenzia={null}
              nomePartner={lt.persone?.partner.nome} manuale={lt.manuale} />
          </section>
          <section className="read-panel">
            <p className="eyebrow">{s.esito}</p>
            <p className="small">{s.esito_testo}</p>
            <div className="button-row" role="group" aria-label={s.esito}>
              {(["si", "in_parte", "no"] as const).map((e) => (
                <button key={e} type="button" className={`button button-small ${lt.feedback === e ? "" : "button-quiet"}`}
                  aria-pressed={lt.feedback === e} onClick={() => annota(e)}>{s.esiti[e]}</button>
              ))}
            </div>
            {annotato && <p className="success" role="status">{s.esito_salvato}</p>}
            <div className="button-row" style={{ marginTop: ".5rem" }}>
              {lt.status === "completata" && (
                <button type="button" className="button button-small" onClick={() => setCondividendo(true)} data-an="share_started">{s.condividi}</button>
              )}
              <LinkV2 className="button button-quiet button-small" data-an="followup_started"
                href={`${R.leggi}?question=${encodeURIComponent(lt.question)}&source=story`}>{s.riprendi_tema}</LinkV2>
              {lt.status === "completata" && <PulsanteStampa etichetta={s.stampa_pdf} piccolo />}
              <button type="button" className="button button-danger button-small" onClick={() => setCancellando(true)}>{s.cancella}</button>
            </div>
            {lt.share_token && (
              <p className="small" style={{ overflowWrap: "anywhere" }}>
                {s.link_attivo}: <a className="inline" href={R.condivisa(lt.share_token)}>{urlCondivisioneV2(lt.share_token)}</a>
              </p>
            )}
            {lt.context_summary && (
              <>
                <p className="eyebrow" style={{ marginTop: ".5rem" }}>{s.il_quadro}</p>
                <p dir="auto" style={{ fontFamily: "var(--serif)" }}>{lt.context_summary}</p>
              </>
            )}
          </section>
        </div>
        {lt.persone && <div style={{ marginTop: ".5rem" }}><Persone persone={lt.persone} compat={lt.compatibilita} /></div>}
        <CarteDaStampare stesa={lt.stesa_dati} posate={posate} />
        {lt.synthesis && (
          <section className={stili.responso} style={{ marginTop: ".7rem" }} aria-labelledby="titolo-interpretazione">
            <h2 id="titolo-interpretazione">{s.l_interpretazione}</h2>
            <Markdown testo={lt.synthesis} className={stili.testo} />
            <p className={stili.avvertenza}>{lt.disclaimer}</p>
            <NotaStampa anno={lt.created_at.slice(0, 4)} />
            {lt.commitment && (
              <details className={stili.verifica}>
                <summary>{l.verifica}</summary>
                <p>{l.verifica_testo}</p>
                <code>{lt.commitment}</code>
                {lt.deck_salt && <p>salt: <code>{lt.deck_salt}</code></p>}
              </details>
            )}
          </section>
        )}
      </section>
      <PannelloCondivisione id={id} aperta={condividendo} onChiudi={() => { setCondividendo(false); lettura.ricarica(); }} />
      <Modale aperta={cancellando} titolo={s.cancella_conferma_titolo} onChiudi={() => setCancellando(false)}>
        <p className="prose">{s.cancella_conferma_testo}</p>
        <div className="button-row">
          <button type="button" className="button button-danger" onClick={async () => {
            setCancellando(false);
            await esegui((tok) => cancellaLettura(tok, id));
            router.push(indirizzoV2(R.storia, prefissoIt));
          }}>{s.cancella}</button>
          <button type="button" className="button button-quiet" onClick={() => setCancellando(false)}>{t.comune.annulla}</button>
        </div>
      </Modale>
    </LinguaNomi>
    </ProviderMazzoAttivo>
  );
}
