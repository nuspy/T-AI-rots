"use client";

/* Il profilo: la data di nascita per le carte personali, il genere e il partner
 * ricordato per le letture di compatibilità e di coppia, il codice invito. */

import { useState } from "react";
import {
  aggiornaProfilo, cancellaPartner, caricaAvatar, leggiProfilo, riscattaInvito, togliAvatar, type Genere,
} from "@/lib/api";
import { urlMedia } from "@/lib/blog";
import { useLingua } from "@/lib/lingua";
import { useSessione, AUTH_DISATTIVATA } from "@/lib/sessione";
import { URL_ACCOUNT, leggiStato2fa } from "@/lib/sicurezza";
import { useAzione, useCarica } from "@/lib/usa";
import { Carta } from "../componenti/carta";
import { CampiGenere } from "../componenti/campi-genere";
import { Involucro } from "../componenti/testata";
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
  const [codice, setCodice] = useState(() => {
    try {
      return typeof window !== "undefined" ? (window.localStorage.getItem("invito") ?? "") : "";
    } catch {
      return "";
    }
  });
  const [esito, setEsito] = useState<string | null>(null);
  const [copiato, setCopiato] = useState(false);
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
        <p className={stili.nota}>{t.invita_testo}</p>
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
                try { window.localStorage.removeItem("invito"); } catch { /* pazienza */ }
                profilo.ricarica();
              }
            }}>
              {t.riscatta}
            </button>
          </div>
        )}
        {esito && <p className={stili.avvisoBuono}>{esito}</p>}
      </section>
    </>
  );
}
