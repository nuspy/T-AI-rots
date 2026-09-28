"use client";

/* Il profilo: la data di nascita per le carte personali, il genere e il partner
 * ricordato per le letture di compatibilità e di coppia, il codice invito. */

import { useState } from "react";
import {
  aggiornaProfilo, cancellaPartner, caricaAvatar, creaIndirizzo, elencaIndirizzi, elencaMemorie, elencaOrdini,
  eliminaIndirizzo, eliminaMemoria, eliminaMemorieSelezionate, eliminaTutteLeMemorie,
  euro, impostazioniPubbliche, leggiProfilo, modificaIndirizzo, modificaMemoria, riscattaInvito, togliAvatar,
  type Genere, type Indirizzo, type IndirizzoInvio, type Memoria, type Ordine,
} from "@/lib/api";
import { urlMedia } from "@/lib/blog";
import { dimenticaInvito, leggiInvito } from "@/lib/inviti";
import { useLingua } from "@/lib/lingua";
import { useSessione, AUTH_DISATTIVATA } from "@/lib/sessione";
import { URL_ACCOUNT, leggiStato2fa } from "@/lib/sicurezza";
import { useAzione, useCarica } from "@/lib/usa";
import { BottonePdf } from "../componenti/bottone-pdf";
import { Carta } from "../componenti/carta";
import { CampiGenere } from "../componenti/campi-genere";
import { Modale } from "../componenti/modale";
import { Involucro } from "../componenti/testata";
import { componiBigliettino, scaricaBlob } from "./bigliettino-invito";
import stili from "../pagine.module.css";

export default function PaginaProfilo() {
  const { t } = useLingua();
  return (
    <Involucro titolo={t.nav_profilo}>
      <Profilo />
    </Involucro>
  );
}

function Profilo() {
  const { t, locale } = useLingua();
  const profilo = useCarica(leggiProfilo);
  const { esegui, inCorso, errore } = useAzione();
  const sessione = useSessione();
  const stato2fa = useCarica(leggiStato2fa);
  /* La casella del promemoria risponde subito al tocco: `null` finché non la si tocca,
   * così vale quello del profilo. */
  const [promemoria, setPromemoria] = useState<boolean | null>(null);
  const [nomePubblico, setNomePubblico] = useState<string | null>(null);
  const [erroreAvatar, setErroreAvatar] = useState<string | null>(null);
  const [nomeSalvato, setNomeSalvato] = useState(false);
  const [nascita, setNascita] = useState<string | null>(null);
  /* Il genere: `null` finché non si tocca, così vale quello del profilo. */
  const [genere, setGenere] = useState<Genere | "" | null>(null);
  const [genereAltro, setGenereAltro] = useState<string | null>(null);
  const [trans, setTrans] = useState<boolean | null>(null);
  const [codice, setCodice] = useState(() => leggiInvito() ?? "");
  const [esito, setEsito] = useState<string | null>(null);
  const [copiato, setCopiato] = useState(false);
  const [scaricando, setScaricando] = useState(false);
  const impostazioni = useCarica(impostazioniPubbliche, [], { pubblico: true });
  const p = profilo.dati;
  if (profilo.errore) return <p className={stili.errore}>{profilo.errore}</p>;
  if (!p) return null;

  const invito = typeof window !== "undefined" ? `${window.location.origin}/?invito=${p.referral_code}` : "";

  return (
    <>
      <section className={`pannello ${stili.scheda} ${stili.sezione}`}>
        <span className={stili.etichetta}>{p.email}</span>
        <h2 className={stili.sezioneTitolo}>{t.profilo_carte}</h2>
        <p className={stili.nota}>{t.profilo_carte_testo}</p>
        <div className={stili.linea}>
          <label className={stili.campo}>
            {t.data_nascita}
            <input type="date" value={nascita ?? p.birth_date ?? ""} onChange={(e) => setNascita(e.target.value)} />
          </label>
          <button className="bottone" disabled={inCorso || !nascita}
            onClick={async () => { await esegui((tok) => aggiornaProfilo(tok, { birth_date: nascita })); profilo.ricarica(); }}>
            {t.salva}
          </button>
        </div>
        {errore && <p className={stili.errore}>{errore}</p>}
        {p.carta_anima && p.carta_anno && (
          <div className={stili.carteRiga}>
            {[[t.carta_anima, p.carta_anima], [t.carta_anno, p.carta_anno]].map(([titolo, c]) => (
              <div key={titolo as string} style={{ textAlign: "center" }}>
                <Carta carta={c as typeof p.carta_anima} rivelata larghezza={150} />
                <p className={stili.etichetta} style={{ marginTop: 8 }}>{titolo as string}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className={`pannello ${stili.scheda} ${stili.sezione}`}>
        <h2 className={stili.sezioneTitolo}>{t.profilo_genere_titolo}</h2>
        <p className={stili.nota}>{t.profilo_genere_testo}</p>
        <CampiGenere
          genere={genere ?? p.gender ?? ""}
          altro={genereAltro ?? p.gender_custom ?? ""}
          trans={trans ?? p.is_trans}
          onGenere={setGenere}
          onAltro={setGenereAltro}
          onTrans={setTrans}
        />
        <div className={stili.linea}>
          <button
            className="bottone"
            disabled={inCorso || (genere ?? p.gender ?? "") === "" || (genere === null && genereAltro === null && trans === null)}
            onClick={async () => {
              const g = (genere ?? p.gender) as Genere;
              await esegui((tok) => aggiornaProfilo(tok, {
                gender: g,
                gender_custom: g === "altro" ? (genereAltro ?? p.gender_custom ?? "") : null,
                is_trans: trans ?? p.is_trans,
              }));
              setGenere(null);
              setGenereAltro(null);
              setTrans(null);
              profilo.ricarica();
            }}
          >
            {t.salva}
          </button>
        </div>
      </section>

      <section className={`pannello ${stili.scheda} ${stili.sezione}`}>
        <h2 className={stili.sezioneTitolo}>{t.profilo_partner_titolo}</h2>
        {p.partner_ricordato ? (
          <>
            <p className={stili.nota}>
              {[p.partner_ricordato.nome, p.partner_ricordato.cognome].filter(Boolean).join(" ")}
              {" · "}
              {new Date(p.partner_ricordato.nascita).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" })}
            </p>
            <div className={stili.linea}>
              <button
                className="bottone-secondario"
                disabled={inCorso}
                onClick={async () => {
                  if (!window.confirm(t.profilo_partner_conferma)) return;
                  await esegui((tok) => cancellaPartner(tok));
                  profilo.ricarica();
                }}
              >
                {t.profilo_partner_cancella}
              </button>
            </div>
          </>
        ) : (
          <p className={stili.nota}>{t.profilo_partner_vuoto}</p>
        )}
      </section>

      <section className={`pannello ${stili.scheda} ${stili.sezione}`} aria-labelledby="profilo-immagine">
        <h2 id="profilo-immagine" className={stili.sezioneTitolo}>{t.prof_avatar_titolo}</h2>
        <p className={stili.nota}>{t.prof_avatar_testo}</p>
        <div className={stili.avatarRiga}>
          {p.avatar ? (
            // eslint-disable-next-line @next/next/no-img-element -- l'avatar, già ridotto a 256 px dal server
            <img className={stili.avatarGrande} src={urlMedia(p.avatar) ?? ""} alt="" width={96} height={96} />
          ) : (
            <span className={stili.avatarGrande} aria-hidden="true">{(p.nome_mostrato[0] ?? "?").toUpperCase()}</span>
          )}
          <div className={stili.linea}>
            <label className={`bottone-secondario ${stili.tocco} ${stili.caricaFile}`}>
              {t.prof_avatar_carica}
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                disabled={inCorso}
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  e.target.value = "";
                  if (!file) return;
                  setErroreAvatar(null);
                  const r = await esegui((tok) => caricaAvatar(tok, file));
                  if (r) profilo.ricarica();
                  else setErroreAvatar(t.prof_avatar_errore);
                }}
              />
            </label>
            {p.avatar && (
              <button
                className={`bottone-secondario ${stili.tocco}`}
                disabled={inCorso}
                onClick={async () => { await esegui((tok) => togliAvatar(tok)); profilo.ricarica(); }}
              >
                {t.prof_avatar_togli}
              </button>
            )}
          </div>
        </div>
        {erroreAvatar && <p className={stili.errore} role="alert">{erroreAvatar}</p>}
        <div className={stili.linea} style={{ marginTop: 18 }}>
          <label className={stili.campo}>
            {t.prof_nome_pubblico}
            <input
              type="text"
              maxLength={60}
              value={nomePubblico ?? p.nome_pubblico ?? ""}
              placeholder={p.nome_mostrato}
              onChange={(e) => { setNomePubblico(e.target.value); setNomeSalvato(false); }}
            />
          </label>
          <button
            className={`bottone ${stili.tocco}`}
            disabled={inCorso || nomePubblico === null}
            onClick={async () => {
              const r = await esegui((tok) => aggiornaProfilo(tok, { nome_pubblico: nomePubblico ?? "" }));
              if (r) { setNomeSalvato(true); setNomePubblico(null); profilo.ricarica(); }
            }}
          >
            {t.salva}
          </button>
        </div>
        <p className={stili.nota}>{t.prof_nome_pubblico_testo}</p>
        {nomeSalvato && <p className={stili.avvisoBuono} role="status">{t.prof_nome_salvato}</p>}
      </section>

      {!AUTH_DISATTIVATA && (
        <section className={`pannello ${stili.scheda} ${stili.sezione}`} aria-labelledby="profilo-sicurezza">
          <h2 id="profilo-sicurezza" className={stili.sezioneTitolo}>{t.sic_profilo_titolo}</h2>
          <p className={stili.nota}>{t.sic_testo}</p>
          <p className={stili.stato2fa} role="status">
            <strong>{t.sic_stato}: </strong>
            {stato2fa.dati === "attiva"
              ? `✓ ${t.sic_stato_attiva}`
              : stato2fa.dati === "spenta"
                ? t.sic_stato_spenta
                : stato2fa.dati === "ignota"
                  ? t.sic_stato_ignota
                  : "…"}
          </p>
          <div className={stili.linea}>
            {stato2fa.dati !== "attiva" && (
              <button className={`bottone ${stili.tocco}`} onClick={sessione.attiva2fa}>{t.sic_attiva_2fa}</button>
            )}
            <a className={`bottone-secondario ${stili.tocco}`} href={URL_ACCOUNT} target="_blank" rel="noopener noreferrer">
              {t.sic_gestisci}
            </a>
          </div>
          {stato2fa.dati !== "attiva" && (
            <label className={stili.casellaProfilo}>
              <input
                type="checkbox"
                checked={promemoria ?? p.promemoria_2fa}
                onChange={async (e) => {
                  const valore = e.target.checked;
                  setPromemoria(valore);
                  await esegui((tok) => aggiornaProfilo(tok, { promemoria_2fa: valore }));
                  profilo.ricarica();
                }}
              />
              <span>{t.sic_promemoria}</span>
            </label>
          )}
        </section>
      )}

      <section className={`pannello ${stili.scheda} ${stili.sezione}`} aria-labelledby="profilo-condivisioni">
        <h2 id="profilo-condivisioni" className={stili.sezioneTitolo}>{t.prof_cond_titolo}</h2>
        <p className={stili.nota}>{t.prof_cond_testo(p.condivisioni.soglia, p.condivisioni.crediti_iscrizione)}</p>
        <div
          className={stili.barra}
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={p.condivisioni.soglia}
          aria-valuenow={p.condivisioni.soglia - p.condivisioni.prossimo_tra}
          aria-label={t.prof_cond_titolo}
        >
          <span style={{ width: `${((p.condivisioni.soglia - p.condivisioni.prossimo_tra) / p.condivisioni.soglia) * 100}%` }} />
        </div>
        <p className={stili.nota}>{t.prof_cond_prossimo(p.condivisioni.prossimo_tra)}</p>
        <dl className={stili.contatori}>
          <div>
            <dt>{t.prof_cond_verificate}</dt>
            <dd>{p.condivisioni.verificate}</dd>
          </div>
          <div>
            <dt>{t.prof_cond_premi}</dt>
            <dd>{p.condivisioni.premi}</dd>
          </div>
          <div>
            <dt>{t.prof_cond_iscritti}</dt>
            <dd>{p.condivisioni.iscrizioni}</dd>
          </div>
        </dl>
      </section>

      <section className={`pannello ${stili.scheda} ${stili.sezione}`}>
        <h2 className={stili.sezioneTitolo}>{t.invita_titolo}</h2>
        {impostazioni.dati && (
          <>
            <p className={stili.nota}>
              {t.invita_testo(impostazioni.dati.crediti_iscrizione, impostazioni.dati.crediti_invito)}
            </p>
            <p className={stili.nota}>{t.invita_commissione(impostazioni.dati.commissione_referral_percentuale)}</p>
          </>
        )}
        <span className={stili.codice}>{p.referral_code}</span>
        <div className={stili.linea}>
          <button className="bottone-secondario" onClick={async () => {
            if (navigator.share) {
              try { await navigator.share({ title: "TAROTS chat", text: t.invito_testo_condivisione(p.referral_code ?? ""), url: invito }); return; } catch { /* annullato */ }
            }
            await navigator.clipboard?.writeText(`${p.referral_code} — ${invito}`);
            setCopiato(true);
          }}>
            {copiato ? t.copiato : t.condividi_codice}
          </button>
          <button className="bottone-secondario" disabled={scaricando || !p.referral_code} onClick={async () => {
            if (!p.referral_code) return;
            setScaricando(true);
            try {
              const omaggio = impostazioni.dati ? t.bigliettino_omaggio(impostazioni.dati.crediti_invito) : "";
              const blob = await componiBigliettino(p.referral_code, t.bigliettino_claim, omaggio, locale);
              if (blob) scaricaBlob(blob, `tarots-chat-invito-${p.referral_code}.png`);
            } finally {
              setScaricando(false);
            }
          }}>
            {t.bigliettino_scarica}
          </button>
        </div>
        {!p.invitato && (
          <div className={stili.linea}>
            <label className={stili.campo}>
              {t.hai_codice}
              <input value={codice} onChange={(e) => setCodice(e.target.value.toUpperCase())} maxLength={16} />
            </label>
            <button className="bottone" disabled={inCorso || codice.length < 4} onClick={async () => {
              const r = await esegui((tok) => riscattaInvito(tok, codice));
              if (r) {
                setEsito(t.letture_regalo(r.crediti));
                dimenticaInvito();
                profilo.ricarica();
              }
            }}>
              {t.riscatta}
            </button>
          </div>
        )}
        {esito && <p className={stili.avvisoBuono}>{esito}</p>}
      </section>

      <SezioneOrdini />
      <SezioneIndirizzi />
      <SezioneMemoria />
    </>
  );
}

function SezioneOrdini() {
  const { t, locale } = useLingua();
  const ordini = useCarica(elencaOrdini);
  const elenco = ordini.dati?.ordini ?? [];

  return (
    <section className={`pannello ${stili.scheda} ${stili.sezione}`} aria-labelledby="profilo-ordini">
      <h2 id="profilo-ordini" className={stili.sezioneTitolo}>{t.profilo_ordini_titolo}</h2>
      <p className={stili.nota}>{t.profilo_ordini_testo}</p>

      {elenco.length === 0 ? (
        <p className={stili.nota}>{t.profilo_ordini_vuoto}</p>
      ) : (
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 14 }}>
          {elenco.map((o) => <VoceOrdine key={o.id} ordine={o} locale={locale} />)}
        </ul>
      )}
    </section>
  );
}

function VoceOrdine({ ordine, locale }: { ordine: Ordine; locale: string }) {
  const { t } = useLingua();
  const etichettaStato = t.profilo_ordini_stato[ordine.status] ?? ordine.status;
  const righePdf = ordine.righe.filter((r) => r.tipo === "pdf");
  return (
    <li className={stili.linea} style={{ flexDirection: "column", alignItems: "stretch", gap: 6 }}>
      <div className={stili.linea} style={{ justifyContent: "space-between" }}>
        <span className={stili.etichetta}>
          {ordine.creato ? new Date(ordine.creato).toLocaleDateString(locale) : ""} · {etichettaStato}
        </span>
        <strong>{euro(ordine.importo_totale, ordine.valuta, locale)}</strong>
      </div>
      <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 4 }}>
        {ordine.righe.map((r) => (
          <li key={r.id} className={stili.nota}>
            mazzo #{r.deck_id} — {r.tipo}{r.quantita > 1 ? ` × ${r.quantita}` : ""}
            {r.tipo === "fisico" && r.stato_evasione && ` · ${t.profilo_ordini_evasione[r.stato_evasione] ?? r.stato_evasione}`}
          </li>
        ))}
      </ul>
      {ordine.sconto_scaglioni > 0 && (
        <p className={stili.nota}>−{euro(ordine.sconto_scaglioni, ordine.valuta, locale)} ({t.profilo_ordini_sconto_scaglioni})</p>
      )}
      {ordine.status === "pagato" && righePdf.map((r) => (
        <BottonePdf key={r.id} ordineId={ordine.id} deckId={r.deck_id} nome={`mazzo-${r.deck_id}`} />
      ))}
    </li>
  );
}

function SezioneIndirizzi() {
  const { t } = useLingua();
  const indirizzi = useCarica(elencaIndirizzi);
  const { esegui, inCorso, errore } = useAzione();
  const [inAggiunta, setInAggiunta] = useState(false);
  const [form, setForm] = useState<IndirizzoInvio>({ nome: "", via: "", citta: "", cap: "", paese: "" });

  const elenco = indirizzi.dati?.indirizzi ?? [];
  const pronto = form.nome.trim() && form.via.trim() && form.citta.trim() && form.cap.trim() && form.paese.trim().length === 2;

  const salva = async () => {
    const r = await esegui((tok) => creaIndirizzo(tok, form));
    if (r) {
      setInAggiunta(false);
      setForm({ nome: "", via: "", citta: "", cap: "", paese: "" });
      indirizzi.ricarica();
    }
  };

  return (
    <section className={`pannello ${stili.scheda} ${stili.sezione}`} aria-labelledby="profilo-indirizzi">
      <h2 id="profilo-indirizzi" className={stili.sezioneTitolo}>{t.indirizzi_titolo}</h2>
      <p className={stili.nota}>{t.indirizzi_testo}</p>

      {elenco.length === 0 && !inAggiunta && <p className={stili.nota}>{t.indirizzi_vuoto}</p>}

      {elenco.length > 0 && (
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 10 }}>
          {elenco.map((i) => <RigaIndirizzo key={i.id} indirizzo={i} onCambio={indirizzi.ricarica} />)}
        </ul>
      )}

      {inAggiunta ? (
        <div style={{ display: "grid", gap: 10, marginTop: 10 }}>
          <label className={stili.campo}>
            {t.indirizzi_nome}
            <input value={form.nome} onChange={(e) => setForm((f) => ({ ...f, nome: e.target.value }))} />
          </label>
          <label className={stili.campo}>
            {t.indirizzi_via}
            <input value={form.via} onChange={(e) => setForm((f) => ({ ...f, via: e.target.value }))} />
          </label>
          <div className={stili.linea}>
            <label className={stili.campo}>
              {t.indirizzi_citta}
              <input value={form.citta} onChange={(e) => setForm((f) => ({ ...f, citta: e.target.value }))} />
            </label>
            <label className={stili.campo}>
              {t.indirizzi_cap}
              <input value={form.cap} onChange={(e) => setForm((f) => ({ ...f, cap: e.target.value }))} />
            </label>
          </div>
          <div className={stili.linea}>
            <label className={stili.campo}>
              {t.indirizzi_provincia}
              <input value={form.provincia ?? ""} onChange={(e) => setForm((f) => ({ ...f, provincia: e.target.value }))} />
            </label>
            <label className={stili.campo}>
              {t.indirizzi_paese}
              <input
                value={form.paese} maxLength={2}
                onChange={(e) => setForm((f) => ({ ...f, paese: e.target.value.toUpperCase() }))}
              />
            </label>
          </div>
          <label className={stili.campo}>
            {t.indirizzi_telefono}
            <input value={form.telefono ?? ""} onChange={(e) => setForm((f) => ({ ...f, telefono: e.target.value }))} />
          </label>
          <div className={stili.linea}>
            <button className="bottone" disabled={inCorso || !pronto} onClick={salva}>{t.indirizzi_salva}</button>
            <button className="bottone-secondario" onClick={() => setInAggiunta(false)}>{t.indirizzi_annulla}</button>
          </div>
          {errore && <p className={stili.errore}>{errore}</p>}
        </div>
      ) : (
        <button className="bottone-secondario" style={{ marginTop: 10 }} onClick={() => setInAggiunta(true)}>
          {t.indirizzi_aggiungi}
        </button>
      )}
    </section>
  );
}

function RigaIndirizzo({ indirizzo, onCambio }: { indirizzo: Indirizzo; onCambio: () => void }) {
  const { t } = useLingua();
  const { esegui, inCorso } = useAzione();
  return (
    <li className={stili.linea} style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
      <div>
        <strong>{indirizzo.nome}</strong>
        {indirizzo.predefinito && <span className={stili.etichetta} style={{ marginLeft: 8 }}>{t.indirizzi_predefinito}</span>}
        <p className={stili.nota}>
          {indirizzo.via}, {indirizzo.cap} {indirizzo.citta}
          {indirizzo.provincia ? ` (${indirizzo.provincia})` : ""}, {indirizzo.paese}
        </p>
      </div>
      <div className={stili.linea}>
        {!indirizzo.predefinito && (
          <button
            className="bottone-secondario" disabled={inCorso}
            onClick={async () => { await esegui((tok) => modificaIndirizzo(tok, indirizzo.id, { predefinito: true })); onCambio(); }}
          >
            {t.indirizzi_imposta_predefinito}
          </button>
        )}
        <button
          className="bottone-secondario" disabled={inCorso}
          onClick={async () => { await esegui((tok) => eliminaIndirizzo(tok, indirizzo.id)); onCambio(); }}
        >
          {t.indirizzi_elimina}
        </button>
      </div>
    </li>
  );
}

/* Memoria (v6, Fase D): elenco, modifica in linea, cancellazione singola e multipla con doppia
 * conferma. Il bottone in fondo è testato: "cancella selezionate" se ce n'è almeno una, altrimenti
 * "cancella tutte" — mai i due insieme, per non lasciare ambiguo su cosa sta per succedere. */
function SezioneMemoria() {
  const { t } = useLingua();
  const memorie = useCarica(elencaMemorie);
  const { esegui, inCorso } = useAzione();
  const [selezionate, setSelezionate] = useState<Set<string>>(new Set());
  const [confermaAperta, setConfermaAperta] = useState(false);
  const [passoConferma, setPassoConferma] = useState<1 | 2>(1);
  const [checkConferma, setCheckConferma] = useState(false);

  const elenco = memorie.dati?.memorie ?? [];
  const haSelezionate = selezionate.size > 0;

  const toggleSelezione = (id: string) => {
    setSelezionate((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const chiudiConferma = () => {
    setConfermaAperta(false);
    setPassoConferma(1);
    setCheckConferma(false);
  };

  const confermaCancellazione = async () => {
    if (haSelezionate) {
      await esegui((tok) => eliminaMemorieSelezionate(tok, [...selezionate]));
    } else {
      await esegui((tok) => eliminaTutteLeMemorie(tok));
    }
    setSelezionate(new Set());
    chiudiConferma();
    memorie.ricarica();
  };

  return (
    <section className={`pannello ${stili.scheda} ${stili.sezione}`} aria-labelledby="profilo-memoria">
      <h2 id="profilo-memoria" className={stili.sezioneTitolo}>{t.memoria_titolo}</h2>
      <p className={stili.nota}>{t.memoria_testo}</p>

      {elenco.length === 0 ? (
        <p className={stili.nota}>{t.memoria_vuoto}</p>
      ) : (
        <>
          <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 10 }}>
            {elenco.map((m) => (
              <RigaMemoria
                key={m.id} memoria={m}
                selezionata={selezionate.has(m.id)}
                onSeleziona={() => toggleSelezione(m.id)}
                onCambio={memorie.ricarica}
              />
            ))}
          </ul>
          <button className="bottone-secondario" style={{ marginTop: 10 }} onClick={() => setConfermaAperta(true)}>
            {haSelezionate ? t.memoria_bottone_cancella_selezionate : t.memoria_bottone_cancella_tutte}
          </button>
        </>
      )}

      <Modale aperta={confermaAperta} titolo={t.memoria_conferma_titolo} onChiudi={chiudiConferma}>
        {passoConferma === 1 ? (
          <>
            <p>{haSelezionate ? t.memoria_conferma_testo(selezionate.size) : t.memoria_conferma_testo_tutte}</p>
            <div className={stili.linea} style={{ marginTop: 14 }}>
              <button className="bottone" onClick={() => setPassoConferma(2)}>{t.memoria_conferma_continua}</button>
              <button className="bottone-secondario" onClick={chiudiConferma}>{t.memoria_conferma_annulla}</button>
            </div>
          </>
        ) : (
          <>
            <label style={{ display: "flex", gap: 8, alignItems: "center", margin: "4px 0 14px" }}>
              <input type="checkbox" checked={checkConferma} onChange={(e) => setCheckConferma(e.target.checked)} />
              {t.memoria_conferma_checkbox}
            </label>
            <div className={stili.linea}>
              <button className="bottone" disabled={!checkConferma || inCorso} onClick={confermaCancellazione}>
                {t.memoria_conferma_conferma}
              </button>
              <button className="bottone-secondario" onClick={chiudiConferma}>{t.memoria_conferma_annulla}</button>
            </div>
          </>
        )}
      </Modale>
    </section>
  );
}

function RigaMemoria({
  memoria, selezionata, onSeleziona, onCambio,
}: {
  memoria: Memoria; selezionata: boolean; onSeleziona: () => void; onCambio: () => void;
}) {
  const { t } = useLingua();
  const { esegui, inCorso } = useAzione();
  const [inModifica, setInModifica] = useState(false);
  const [contenuto, setContenuto] = useState(memoria.contenuto);
  const [campo, setCampo] = useState(memoria.campo_attinenza);

  const annullaModifica = () => {
    setInModifica(false);
    setContenuto(memoria.contenuto);
    setCampo(memoria.campo_attinenza);
  };

  const salvaModifica = async () => {
    await esegui((tok) => modificaMemoria(tok, memoria.id, { contenuto: contenuto.trim(), campo_attinenza: campo.trim() }));
    setInModifica(false);
    onCambio();
  };

  return (
    <li className={stili.linea} style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className={stili.linea} style={{ gap: 8 }}>
          <span className={stili.etichetta}>
            {memoria.tipo === "stabile" ? t.memoria_tipo_stabile : t.memoria_tipo_variabile}
          </span>
          <span className={stili.etichetta}>{memoria.campo_attinenza}</span>
        </div>
        {inModifica ? (
          <div style={{ display: "grid", gap: 8, marginTop: 8 }}>
            <textarea
              value={contenuto} rows={3} style={{ width: "100%", resize: "vertical" }}
              onChange={(e) => setContenuto(e.target.value)}
            />
            <input value={campo} onChange={(e) => setCampo(e.target.value)} />
            <div className={stili.linea}>
              <button className="bottone" disabled={inCorso || !contenuto.trim()} onClick={salvaModifica}>
                {t.memoria_modifica_salva}
              </button>
              <button className="bottone-secondario" onClick={annullaModifica}>{t.memoria_modifica_annulla}</button>
            </div>
          </div>
        ) : (
          <p className={stili.nota}>{memoria.contenuto}</p>
        )}
      </div>
      <div className={stili.linea} style={{ gap: 6, flexShrink: 0 }}>
        <input
          type="checkbox" checked={selezionata} onChange={onSeleziona}
          title={t.memoria_tooltip_seleziona} aria-label={t.memoria_tooltip_seleziona}
          style={{ width: 22, height: 22 }}
        />
        <button
          className="bottone-secondario" style={{ minWidth: 44, minHeight: 44, padding: 0 }}
          title={t.memoria_tooltip_modifica} aria-label={t.memoria_tooltip_modifica}
          onClick={() => setInModifica((v) => !v)}
        >
          ✎
        </button>
        <button
          className="bottone-secondario" style={{ minWidth: 44, minHeight: 44, padding: 0 }}
          title={t.memoria_tooltip_elimina} aria-label={t.memoria_tooltip_elimina} disabled={inCorso}
          onClick={async () => { await esegui((tok) => eliminaMemoria(tok, memoria.id)); onCambio(); }}
        >
          🗑
        </button>
      </div>
    </li>
  );
}
