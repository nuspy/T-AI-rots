"use client";

/* Il profilo nella v2: le parti di una storia personale. Parità con il profilo del sito — carte personali, genere e
 * persona ricordata, immagine e nome pubblico, sicurezza (2FA), registro linguistico, mazzo predefinito,
 * condivisioni, inviti, ordini con PDF, indirizzi, opposizione alle statistiche — con due differenze: la memoria
 * vive in «La mia storia» (dove la specifica v2 la vuole visibile), e l'invito porta alla v2. */

import { useState } from "react";
import { componiBigliettino, scaricaBlob } from "@/app/(sito)/profilo/bigliettino-invito";
import {
  aggiornaProfilo, cancellaPartner, caricaAvatar, creaIndirizzo, elencaIndirizzi, elencaMazzi, elencaMieiMazzi,
  elencaOrdini, eliminaIndirizzo, euro, impostaPreferenzaStatistiche, impostazioniPubbliche, leggiPreferenzaStatistiche,
  leggiProfilo, modificaIndirizzo, riscattaInvito, togliAvatar, type Genere, type Indirizzo, type IndirizzoInvio, type Ordine,
} from "@/lib/api";
import { urlMedia } from "@/lib/blog";
import { dimenticaInvito, leggiInvito } from "@/lib/inviti";
import { AUTH_DISATTIVATA, useSessione } from "@/lib/sessione";
import { URL_ACCOUNT, leggiStato2fa } from "@/lib/sicurezza";
import { f, plurale } from "@/v2/i18n";
import { CartaV2 } from "@/v2/componenti/carta";
import LinkV2 from "@/v2/componenti/link";
import { Modale } from "@/v2/componenti/modale";
import { CampiGenere } from "@/v2/lettura/persone";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";
import { BottonePdfV2 } from "./negozio";

function Sezione({ id, titolo, children }: { id: string; titolo: string; children: React.ReactNode }) {
  return (
    <section className="panel" id={id} aria-labelledby={`${id}-t`}>
      <h2 id={`${id}-t`}>{titolo}</h2>
      {children}
    </section>
  );
}

export function Profilo() {
  const { t } = useLingua();
  const sessione = useSessione();
  if (!sessione.pronta) return null;
  if (!sessione.autenticata) {
    return (
      <section className="band band-tight">
        <p className="section-intro">{t.profilo.fuori}</p>
        <button type="button" className="button" onClick={() => sessione.entra(R.profilo)}>{t.profilo.entra}</button>
      </section>
    );
  }
  return <Dentro />;
}

function Dentro() {
  const { t, locale } = useLingua();
  const k = t.profilo;
  const sessione = useSessione();
  const profilo = useCarica(leggiProfilo);
  const { esegui, inCorso, errore } = useAzione();
  const stato2fa = useCarica(leggiStato2fa);
  const tutti = useCarica(elencaMazzi, [], { pubblico: true });
  const miei = useCarica(elencaMieiMazzi);
  const omaggi = useCarica(impostazioniPubbliche, [], { pubblico: true });
  const [nascita, setNascita] = useState<string | null>(null);
  const [genere, setGenere] = useState<Genere | "" | null>(null);
  const [genereAltro, setGenereAltro] = useState<string | null>(null);
  const [trans, setTrans] = useState<boolean | null>(null);
  const [nomePubblico, setNomePubblico] = useState<string | null>(null);
  const [nomeSalvato, setNomeSalvato] = useState(false);
  const [erroreAvatar, setErroreAvatar] = useState(false);
  const [codice, setCodice] = useState(() => leggiInvito() ?? "");
  const [esitoInvito, setEsitoInvito] = useState<string | null>(null);
  const [copiato, setCopiato] = useState(false);
  const [scaricando, setScaricando] = useState(false);
  const [dimentica, setDimentica] = useState(false);

  if (profilo.errore) return <section className="band band-tight"><p className="error">{profilo.errore}</p></section>;
  const p = profilo.dati;
  if (!p) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const invito = typeof window !== "undefined" ? `${window.location.origin}${R.home}?invito=${p.referral_code}` : "";
  const utilizzabili = (tutti.dati ?? []).filter((m) => m.predefinito || m.prezzo_digitale === null || (miei.dati?.deck_ids ?? []).includes(m.id));
  const c = p.condivisioni;

  return (
    <section className="band band-tight">
      <div className="share-band" style={{ marginBottom: "1.4rem" }}>
        <div><p className="eyebrow">{p.email}</p><p>{k.storia_link}</p></div>
        <div className="button-row">
          <LinkV2 className="button" href={R.storia}>{k.storia_cta}</LinkV2>
          <button type="button" className="button button-quiet" onClick={sessione.esci}>{k.esci}</button>
        </div>
      </div>
      {errore && <p className="error">{errore}</p>}
      <div className="profile-grid">
        <Sezione id="carte" titolo={k.carte_titolo}>
          <p className="small">{k.carte_testo}</p>
          <div className="button-row" style={{ alignItems: "end" }}>
            <label className="field" style={{ margin: 0 }}><span>{k.nascita}</span>
              <input type="date" value={nascita ?? p.birth_date ?? ""} onChange={(e) => setNascita(e.target.value)} /></label>
            <button type="button" className="button button-small" disabled={inCorso || !nascita}
              onClick={async () => { await esegui((tok) => aggiornaProfilo(tok, { birth_date: nascita })); profilo.ricarica(); }}>{t.comune.salva}</button>
          </div>
          {p.carta_anima && p.carta_anno && (
            <div className="button-row" style={{ marginTop: "1.2rem", gap: "1.4rem" }}>
              {([[k.carta_anima, p.carta_anima], [k.carta_anno, p.carta_anno]] as const).map(([titolo, carta]) => (
                <div key={titolo} style={{ textAlign: "center" }}>
                  <CartaV2 carta={carta} rivelata larghezza={120} /><p className="small">{titolo}</p>
                </div>
              ))}
            </div>
          )}
        </Sezione>

        <Sezione id="genere" titolo={k.genere_titolo}>
          <p className="small">{k.genere_testo}</p>
          <CampiGenere genere={genere ?? p.gender ?? ""} altro={genereAltro ?? p.gender_custom ?? ""} trans={trans ?? p.is_trans}
            onGenere={setGenere} onAltro={setGenereAltro} onTrans={setTrans} />
          <button type="button" className="button button-small"
            disabled={inCorso || (genere ?? p.gender ?? "") === "" || (genere === null && genereAltro === null && trans === null)}
            onClick={async () => {
              const g = (genere ?? p.gender) as Genere;
              await esegui((tok) => aggiornaProfilo(tok, { gender: g, gender_custom: g === "altro" ? (genereAltro ?? p.gender_custom ?? "") : null, is_trans: trans ?? p.is_trans }));
              setGenere(null); setGenereAltro(null); setTrans(null); profilo.ricarica();
            }}>{t.comune.salva}</button>
          <h3 style={{ marginTop: "1.6rem" }}>{k.partner_titolo}</h3>
          {p.partner_ricordato ? (
            <>
              <p className="small">{[p.partner_ricordato.nome, p.partner_ricordato.cognome].filter(Boolean).join(" ")} · {new Date(p.partner_ricordato.nascita).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" })}</p>
              <button type="button" className="button button-danger button-small" onClick={() => setDimentica(true)}>{k.partner_dimentica}</button>
            </>
          ) : <p className="small muted">{k.partner_vuoto}</p>}
        </Sezione>

        <Sezione id="registro" titolo={k.registro_titolo}>
          <p className="small">{k.registro_testo}</p>
          <label className="field"><span className="sr-only">{k.registro_titolo}</span>
            <select value={p.registro_linguistico} onChange={async (e) => {
              const v = e.target.value as "esoterico" | "quotidiano";
              await esegui((tok) => aggiornaProfilo(tok, { registro_linguistico: v })); profilo.ricarica();
            }}>
              <option value="esoterico">{k.registro_esoterico}</option>
              <option value="quotidiano">{k.registro_quotidiano}</option>
            </select>
          </label>
          {utilizzabili.length > 1 && (
            <>
              <h3>{k.mazzo_titolo}</h3>
              <p className="small">{k.mazzo_testo}</p>
              <label className="field"><span className="sr-only">{k.mazzo_titolo}</span>
                <select value={p.mazzo_predefinito_id ?? ""} onChange={async (e) => {
                  const id = e.target.value === "" ? 0 : Number(e.target.value);
                  await esegui((tok) => aggiornaProfilo(tok, { mazzo_predefinito_id: id })); profilo.ricarica();
                }}>
                  {utilizzabili.map((m) => <option key={m.id} value={m.predefinito ? "" : m.id}>{m.nome}{m.predefinito ? ` ${k.mazzo_predefinito}` : ""}</option>)}
                </select>
              </label>
            </>
          )}
        </Sezione>

        <Sezione id="invito" titolo={k.invito_titolo}>
          {omaggi.dati && (
            <>
              <p className="small">{f(k.invito_testo, { iscrizione: omaggi.dati.crediti_iscrizione, invito: omaggi.dati.crediti_invito })}</p>
              <p className="small">{f(k.invito_commissione, { percentuale: omaggi.dati.commissione_referral_percentuale })}</p>
            </>
          )}
          <p className="invite-code">{p.referral_code}</p>
          <div className="button-row">
            <button type="button" className="button button-small" data-an="share_started" data-an-cosa="invito" onClick={async () => {
              if (navigator.share) { try { await navigator.share({ title: "TAROTS chat", text: f(k.invito_testo_condivisione, { codice: p.referral_code ?? "" }), url: invito }); return; } catch { /* annullato */ } }
              await navigator.clipboard?.writeText(`${p.referral_code} — ${invito}`); setCopiato(true);
            }}>{copiato ? k.invito_copiato : k.invito_condividi}</button>
            <button type="button" className="button button-quiet button-small" disabled={scaricando || !p.referral_code} onClick={async () => {
              if (!p.referral_code) return;
              setScaricando(true);
              try {
                const omaggio = omaggi.dati ? f(k.bigliettino_omaggio, { n: omaggi.dati.crediti_invito }) : "";
                const blob = await componiBigliettino(p.referral_code, k.bigliettino_claim, omaggio, locale);
                if (blob) scaricaBlob(blob, `tarots-chat-invite-${p.referral_code}.png`);
              } finally { setScaricando(false); }
            }}>{k.bigliettino}</button>
          </div>
          {!p.invitato && (
            <div className="button-row" style={{ alignItems: "end", marginTop: "1rem" }}>
              <label className="field" style={{ margin: 0 }}><span>{k.hai_codice}</span>
                <input value={codice} maxLength={16} onChange={(e) => setCodice(e.target.value.toUpperCase())} /></label>
              <button type="button" className="button button-small" disabled={inCorso || codice.length < 4} onClick={async () => {
                const r = await esegui((tok) => riscattaInvito(tok, codice));
                if (r) { setEsitoInvito(f(k.regalo, { n: r.crediti })); dimenticaInvito(); profilo.ricarica(); }
              }}>{k.riscatta}</button>
            </div>
          )}
          {esitoInvito && <p className="success" role="status">{esitoInvito}</p>}
          <h3 style={{ marginTop: "1.6rem" }}>{k.cond_titolo}</h3>
          <p className="small">{f(k.cond_testo, { soglia: c.soglia, crediti: c.crediti_iscrizione })}</p>
          <div className="stat-bar" role="progressbar" aria-valuemin={0} aria-valuemax={c.soglia} aria-valuenow={c.soglia - c.prossimo_tra} aria-label={k.cond_titolo}>
            <span style={{ width: `${((c.soglia - c.prossimo_tra) / c.soglia) * 100}%` }} />
          </div>
          <p className="small">{plurale(c.prossimo_tra, k.cond_prossimo)}</p>
          <div className="stat-row">
            <div><b>{c.verificate}</b><span>{k.cond_verificate}</span></div>
            <div><b>{c.premi}</b><span>{k.cond_premi}</span></div>
            <div><b>{c.iscrizioni}</b><span>{k.cond_iscritti}</span></div>
          </div>
        </Sezione>

        <Sezione id="immagine" titolo={k.avatar_titolo}>
          <p className="small">{k.avatar_testo}</p>
          <div className="button-row">
            {p.avatar
              // eslint-disable-next-line @next/next/no-img-element
              ? <img src={urlMedia(p.avatar) ?? ""} alt="" width={72} height={72} style={{ width: 72, height: 72, objectFit: "cover", border: "2px solid #f5e6bf" }} />
              : <span aria-hidden="true" className="avatar-letter">{(p.nome_mostrato[0] ?? "?").toUpperCase()}</span>}
            <label className="button button-quiet button-small" style={{ cursor: "pointer" }}>
              {k.avatar_carica}
              <input type="file" accept="image/png,image/jpeg,image/webp" className="sr-only" disabled={inCorso} onChange={async (e) => {
                const file = e.target.files?.[0];
                e.target.value = "";
                if (!file) return;
                setErroreAvatar(false);
                const r = await esegui((tok) => caricaAvatar(tok, file));
                if (r) profilo.ricarica(); else setErroreAvatar(true);
              }} />
            </label>
            {p.avatar && <button type="button" className="button button-quiet button-small" disabled={inCorso}
              onClick={async () => { await esegui((tok) => togliAvatar(tok)); profilo.ricarica(); }}>{k.avatar_togli}</button>}
          </div>
          {erroreAvatar && <p className="error" role="alert">{k.avatar_errore}</p>}
          <div className="button-row" style={{ alignItems: "end", marginTop: "1rem" }}>
            <label className="field" style={{ margin: 0 }}><span>{k.nome_pubblico}</span>
              <input maxLength={60} value={nomePubblico ?? p.nome_pubblico ?? ""} placeholder={p.nome_mostrato}
                onChange={(e) => { setNomePubblico(e.target.value); setNomeSalvato(false); }} /></label>
            <button type="button" className="button button-small" disabled={inCorso || nomePubblico === null} onClick={async () => {
              const r = await esegui((tok) => aggiornaProfilo(tok, { nome_pubblico: nomePubblico ?? "" }));
              if (r) { setNomeSalvato(true); setNomePubblico(null); profilo.ricarica(); }
            }}>{t.comune.salva}</button>
          </div>
          <p className="small muted">{k.nome_pubblico_testo}</p>
          {nomeSalvato && <p className="success" role="status">{k.nome_salvato}</p>}
        </Sezione>

        {!AUTH_DISATTIVATA && (
          <Sezione id="sicurezza" titolo={k.sic_titolo}>
            <p className="small">{k.sic_testo}</p>
            <p role="status"><b>{k.sic_stato}:</b> {stato2fa.dati === "attiva" ? `✓ ${k.sic_attiva}` : stato2fa.dati === "spenta" ? k.sic_spenta : stato2fa.dati === "ignota" ? k.sic_ignota : "…"}</p>
            <div className="button-row">
              {stato2fa.dati !== "attiva" && <button type="button" className="button button-small" onClick={sessione.attiva2fa}>{k.sic_attiva_ora}</button>}
              <a className="button button-quiet button-small" href={URL_ACCOUNT} target="_blank" rel="noopener noreferrer">{k.sic_gestisci}</a>
            </div>
            {stato2fa.dati !== "attiva" && (
              <label className="check">
                <input type="checkbox" checked={p.promemoria_2fa} onChange={async (e) => {
                  const v = e.target.checked;
                  await esegui((tok) => aggiornaProfilo(tok, { promemoria_2fa: v })); profilo.ricarica();
                }} />
                <span>{k.sic_promemoria}</span>
              </label>
            )}
          </Sezione>
        )}

        <Ordini />
        <Indirizzi />
        <Statistiche />
      </div>

      <Modale aperta={dimentica} titolo={k.partner_conferma} onChiudi={() => setDimentica(false)}>
        <div className="button-row">
          <button type="button" className="button button-danger" onClick={async () => {
            setDimentica(false); await esegui((tok) => cancellaPartner(tok)); profilo.ricarica();
          }}>{k.partner_dimentica}</button>
          <button type="button" className="button button-quiet" onClick={() => setDimentica(false)}>{t.comune.annulla}</button>
        </div>
      </Modale>
    </section>
  );
}

function Statistiche() {
  const { t } = useLingua();
  const k = t.profilo;
  const pref = useCarica(leggiPreferenzaStatistiche);
  const { esegui, inCorso, errore } = useAzione();
  if (!pref.dati) return null;
  return (
    <Sezione id="statistiche" titolo={k.stat_titolo}>
      <p className="small">{k.stat_testo} <LinkV2 className="inline" href={R.privacy}>{k.stat_privacy}</LinkV2></p>
      <label className="check">
        <input type="checkbox" checked={pref.dati.opposizione} disabled={inCorso} onChange={async (e) => {
          await esegui((tok) => impostaPreferenzaStatistiche(tok, e.target.checked)); pref.ricarica();
        }} />
        <span>{k.stat_opponi}</span>
      </label>
      {errore && <p className="error">{errore}</p>}
    </Sezione>
  );
}

function Ordini() {
  const { t, locale } = useLingua();
  const k = t.profilo;
  const ordini = useCarica(elencaOrdini);
  const mazzi = useCarica(elencaMazzi, [], { pubblico: true });
  const nome = (id: number) => mazzi.dati?.find((m) => m.id === id)?.nome ?? `#${id}`;
  const elenco = ordini.dati?.ordini ?? [];
  return (
    <Sezione id="ordini" titolo={k.ordini_titolo}>
      {elenco.length === 0 ? <p className="small muted">{k.ordini_vuoto}</p> : (
        <ul className="list-plain">
          {elenco.map((o: Ordine) => (
            <li key={o.id} className="memory-entry">
              <small>{o.creato ? new Date(o.creato).toLocaleDateString(locale) : ""} · {k.ordini_stato[o.status] ?? o.status}</small>
              <h3>{euro(o.importo_totale, o.valuta, locale)}</h3>
              <ul className="list-plain small">
                {o.righe.map((r) => (
                  <li key={r.id}>
                    {nome(r.deck_id)} — {k.ordini_tipo[r.tipo] ?? r.tipo}{r.quantita > 1 ? ` × ${r.quantita}` : ""}
                    {r.tipo === "fisico" && r.stato_evasione && ` · ${k.ordini_evasione[r.stato_evasione] ?? r.stato_evasione}`}
                  </li>
                ))}
              </ul>
              {o.sconto_scaglioni > 0 && <p className="small">−{euro(o.sconto_scaglioni, o.valuta, locale)} ({k.ordini_sconto})</p>}
              {o.status === "pagato" && o.righe.filter((r) => r.tipo === "pdf").map((r) => (
                <BottonePdfV2 key={r.id} ordineId={o.id} deckId={r.deck_id} nome={nome(r.deck_id)} />
              ))}
            </li>
          ))}
        </ul>
      )}
    </Sezione>
  );
}

function Indirizzi() {
  const { t } = useLingua();
  const k = t.profilo;
  const indirizzi = useCarica(elencaIndirizzi);
  const { esegui, inCorso, errore } = useAzione();
  const [aggiunta, setAggiunta] = useState(false);
  const vuoto: IndirizzoInvio = { nome: "", via: "", citta: "", cap: "", paese: "" };
  const [form, setForm] = useState<IndirizzoInvio>(vuoto);
  const elenco = indirizzi.dati?.indirizzi ?? [];
  const pronto = form.nome.trim() && form.via.trim() && form.citta.trim() && form.cap.trim() && form.paese.trim().length === 2;
  const campo = (chiave: keyof IndirizzoInvio, etichetta: string, extra: Partial<React.InputHTMLAttributes<HTMLInputElement>> = {}) => (
    <label className="field"><span>{etichetta}</span>
      <input value={(form[chiave] as string | undefined) ?? ""} {...extra}
        onChange={(e) => setForm((x) => ({ ...x, [chiave]: chiave === "paese" ? e.target.value.toUpperCase() : e.target.value }))} />
    </label>
  );
  return (
    <Sezione id="indirizzi" titolo={k.indirizzi_titolo}>
      <p className="small">{k.indirizzi_testo}</p>
      {elenco.length === 0 && !aggiunta && <p className="small muted">{k.indirizzi_vuoto}</p>}
      <ul className="list-plain">
        {elenco.map((i: Indirizzo) => (
          <li key={i.id} className="memory-entry">
            {i.predefinito && <small>{k.indirizzi_predefinito}</small>}
            <h3>{i.nome}</h3>
            <p>{i.via}, {i.cap} {i.citta}{i.provincia ? ` (${i.provincia})` : ""}, {i.paese}</p>
            <div className="button-row" style={{ marginTop: ".5rem" }}>
              {!i.predefinito && <button type="button" className="button button-quiet button-small" disabled={inCorso}
                onClick={async () => { await esegui((tok) => modificaIndirizzo(tok, i.id, { predefinito: true })); indirizzi.ricarica(); }}>{k.indirizzi_imposta}</button>}
              <button type="button" className="button button-danger button-small" disabled={inCorso}
                onClick={async () => { await esegui((tok) => eliminaIndirizzo(tok, i.id)); indirizzi.ricarica(); }}>{k.indirizzi_elimina}</button>
            </div>
          </li>
        ))}
      </ul>
      {aggiunta ? (
        <div style={{ marginTop: "1rem" }}>
          {campo("nome", k.indirizzi_nome, { autoComplete: "name" })}
          {campo("via", k.indirizzi_via, { autoComplete: "street-address" })}
          <div className="form-grid">{campo("citta", k.indirizzi_citta, { autoComplete: "address-level2" })}{campo("cap", k.indirizzi_cap, { autoComplete: "postal-code" })}</div>
          <div className="form-grid">{campo("provincia", k.indirizzi_provincia)}{campo("paese", k.indirizzi_paese, { maxLength: 2, autoComplete: "country" })}</div>
          {campo("telefono", k.indirizzi_telefono, { autoComplete: "tel", type: "tel" })}
          <div className="button-row">
            <button type="button" className="button button-small" disabled={inCorso || !pronto} onClick={async () => {
              const r = await esegui((tok) => creaIndirizzo(tok, form));
              if (r) { setAggiunta(false); setForm(vuoto); indirizzi.ricarica(); }
            }}>{k.indirizzi_salva}</button>
            <button type="button" className="button button-quiet button-small" onClick={() => setAggiunta(false)}>{t.comune.annulla}</button>
          </div>
          {errore && <p className="error">{errore}</p>}
        </div>
      ) : (
        <button type="button" className="button button-quiet button-small" style={{ marginTop: ".8rem" }} onClick={() => setAggiunta(true)}>{k.indirizzi_aggiungi}</button>
      )}
    </Sezione>
  );
}
