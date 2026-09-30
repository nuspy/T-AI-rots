"use client";

/* Il modulo delle letture di compatibilità e di coppia: i dati mancanti della
 * scheda di chi consulta (genere, data di nascita: si salvano nel profilo e non
 * si chiedono più) e i dati dell'altra persona, con la casella «ricorda».
 *
 * Il cognome dell'altra persona è facoltativo e resta nello storico: non arriva
 * mai all'intelligenza artificiale. L'avviso sotto il modulo lo dice a chi lo
 * compila: sono dati di una persona che non ha dato il consenso.
 */

import { useState } from "react";
import type { Genere, PartnerInvio, Profilo } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { CampiGenere } from "../componenti/campi-genere";
import campi from "../componenti/campi.module.css";
import stili from "./leggi.module.css";

export interface DatiPersone {
  /* Di chi consulta: solo se mancano nella scheda. */
  tuGenere: Genere | "";
  tuGenereAltro: string;
  tuTrans: boolean;
  tuNascita: string;
  /* L'altra persona. */
  nome: string;
  cognome: string;
  genere: Genere | "";
  genereAltro: string;
  trans: boolean;
  nascita: string;
  ricorda: boolean;
}

export const personeVuote = (): DatiPersone => ({
  tuGenere: "", tuGenereAltro: "", tuTrans: false, tuNascita: "",
  nome: "", cognome: "", genere: "", genereAltro: "", trans: false, nascita: "", ricorda: false,
});

/* La data odierna nel formato del campo `date`, per il limite massimo. */
const oggi = () => new Date().toISOString().slice(0, 10);

const nascitaValida = (v: string) => /^\d{4}-\d{2}-\d{2}$/.test(v) && v >= "1900-01-01" && v <= oggi();

export type ErroriPersone = Partial<Record<"tuGenere" | "tuGenereAltro" | "tuNascita" | "nome" | "genere" | "genereAltro" | "nascita", string>>;

/** Cosa manca o non va, campo per campo. Vuoto se il modulo si può inviare. */
export function verificaPersone(
  d: DatiPersone, mancanti: readonly string[], t: ReturnType<typeof useLingua>["t"],
): ErroriPersone {
  const e: ErroriPersone = {};
  if (mancanti.includes("genere")) {
    if (!d.tuGenere) e.tuGenere = t.err_persone_genere;
    else if (d.tuGenere === "altro" && !d.tuGenereAltro.trim()) e.tuGenereAltro = t.err_persone_altro;
  }
  if (mancanti.includes("nascita") && !nascitaValida(d.tuNascita)) e.tuNascita = t.err_persone_nascita;
  if (!d.nome.trim()) e.nome = t.err_persone_nome;
  if (!d.genere) e.genere = t.err_persone_genere;
  else if (d.genere === "altro" && !d.genereAltro.trim()) e.genereAltro = t.err_persone_altro;
  if (!nascitaValida(d.nascita)) e.nascita = t.err_persone_nascita;
  return e;
}

/** I dati dell'altra persona come li vuole il server. */
export function partnerDa(d: DatiPersone): PartnerInvio {
  return {
    nome: d.nome.trim(),
    ...(d.cognome.trim() ? { cognome: d.cognome.trim() } : {}),
    genere: d.genere as Genere,
    ...(d.genere === "altro" ? { genere_altro: d.genereAltro.trim() } : {}),
    trans: d.trans,
    nascita: d.nascita,
  };
}

/** Il modulo precompilato dal partner ricordato nel profilo. */
export function personeDaProfilo(profilo: Profilo, attuali: DatiPersone): DatiPersone {
  const p = profilo.partner_ricordato;
  if (!p) return attuali;
  return {
    ...attuali,
    nome: p.nome,
    cognome: p.cognome ?? "",
    genere: p.genere,
    genereAltro: p.genere_altro ?? "",
    trans: p.trans,
    nascita: p.nascita,
    ricorda: true,
  };
}

export function FormPersone({
  dati,
  onCambia,
  profilo,
  onAvanti,
  onIndietro,
  onDimentica,
  errore,
}: {
  dati: DatiPersone;
  onCambia: (d: DatiPersone) => void;
  profilo: Profilo | null;
  onAvanti: () => void;
  onIndietro: () => void;
  onDimentica: () => void;
  errore: string | null;
}) {
  const { t } = useLingua();
  const [provato, setProvato] = useState(false);
  const mancanti = profilo?.relazioni.mancanti ?? [];
  const errori = provato ? verificaPersone(dati, mancanti, t) : {};
  const ricordato = profilo?.partner_ricordato ?? null;
  const cambia = (parte: Partial<DatiPersone>) => onCambia({ ...dati, ...parte });

  const avanti = () => {
    setProvato(true);
    if (Object.keys(verificaPersone(dati, mancanti, t)).length === 0) onAvanti();
  };

  return (
    <form
      className={stili.scelta}
      noValidate
      onSubmit={(e) => {
        e.preventDefault();
        avanti();
      }}
    >
      {mancanti.length > 0 && (
        <section className={`pannello ${stili.sezioneForm}`}>
          <h2 className={stili.passo}>{t.persone_di_te}</h2>
          <p className={stili.guida}>{t.persone_di_te_testo}</p>
          {mancanti.includes("genere") && (
            <CampiGenere
              genere={dati.tuGenere}
              altro={dati.tuGenereAltro}
              trans={dati.tuTrans}
              onGenere={(g) => cambia({ tuGenere: g })}
              onAltro={(v) => cambia({ tuGenereAltro: v })}
              onTrans={(v) => cambia({ tuTrans: v })}
              errore={errori.tuGenere}
              erroreAltro={errori.tuGenereAltro}
            />
          )}
          {mancanti.includes("nascita") && (
            <label className={`${campi.campo} ${errori.tuNascita ? campi.campoErrore : ""}`}>
              {t.persone_nascita}
              <input
                type="date"
                value={dati.tuNascita}
                min="1900-01-01"
                max={oggi()}
                onChange={(e) => cambia({ tuNascita: e.target.value })}
                aria-invalid={!!errori.tuNascita}
              />
              {errori.tuNascita && <span className={campi.errore} role="alert">{errori.tuNascita}</span>}
            </label>
          )}
        </section>
      )}

      <section className={`pannello ${stili.sezioneForm}`}>
        <h2 className={stili.passo}>{t.persone_partner}</h2>
        {ricordato && (
          <div className={stili.bannerRicordato} role="status">
            <span>{t.persone_ripresi(ricordato.nome)}</span>
            <button type="button" className="bottone-secondario" onClick={onDimentica}>
              {t.persone_dimentica}
            </button>
          </div>
        )}
        <div className={campi.riga}>
          <label className={`${campi.campo} ${errori.nome ? campi.campoErrore : ""}`}>
            {t.persone_nome}
            <input
              value={dati.nome}
              onChange={(e) => cambia({ nome: e.target.value })}
              maxLength={40}
              autoComplete="off"
              dir="auto"
              aria-invalid={!!errori.nome}
            />
            {errori.nome && <span className={campi.errore} role="alert">{errori.nome}</span>}
          </label>
          <label className={campi.campo}>
            {t.persone_cognome}
            <input
              value={dati.cognome}
              onChange={(e) => cambia({ cognome: e.target.value })}
              maxLength={60}
              autoComplete="off"
              dir="auto"
            />
          </label>
        </div>
        <CampiGenere
          genere={dati.genere}
          altro={dati.genereAltro}
          trans={dati.trans}
          onGenere={(g) => cambia({ genere: g })}
          onAltro={(v) => cambia({ genereAltro: v })}
          onTrans={(v) => cambia({ trans: v })}
          errore={errori.genere}
          erroreAltro={errori.genereAltro}
        />
        <label className={`${campi.campo} ${errori.nascita ? campi.campoErrore : ""}`}>
          {t.persone_nascita}
          <input
            type="date"
            value={dati.nascita}
            min="1900-01-01"
            max={oggi()}
            onChange={(e) => cambia({ nascita: e.target.value })}
            aria-invalid={!!errori.nascita}
          />
          {errori.nascita && <span className={campi.errore} role="alert">{errori.nascita}</span>}
        </label>
        <label className={campi.casella}>
          <input type="checkbox" checked={dati.ricorda} onChange={(e) => cambia({ ricorda: e.target.checked })} />
          {t.persone_ricorda}
        </label>
        <p className={stili.avvisoPrivacy}>{t.persone_privacy}</p>
      </section>

      {(errore || provato && Object.keys(errori).length > 0) && (
        <p className={stili.errore} role="alert">{errore ?? t.err_profilo_incompleto}</p>
      )}
      <div className={stili.azioniCentro}>
        <button type="button" className="bottone-secondario" onClick={onIndietro}>{t.indietro}</button>
        <button type="submit" className="bottone">{t.avanti}</button>
      </div>
    </form>
  );
}
