"use client";

/* Le persone delle letture di compatibilità e di coppia: i dati che mancano a chi consulta (genere, data di
 * nascita: restano nel profilo e non si chiedono più) e quelli dell'altra persona, con «ricorda». Stesse regole
 * del sito (`app/(sito)/leggi/form-persone.tsx`): il cognome non arriva mai all'AI, nessun campo sull'orientamento,
 * «preferisco non dirlo» è una risposta valida. */

import { useId, useState } from "react";
import type { Genere, PartnerInvio, Profilo } from "@/lib/api";
import { f, type Dizionario } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import stili from "./lettura.module.css";

export interface DatiPersone {
  tuGenere: Genere | "";
  tuGenereAltro: string;
  tuTrans: boolean;
  tuNascita: string;
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

const oggi = () => new Date().toISOString().slice(0, 10);
const nascitaValida = (v: string) => /^\d{4}-\d{2}-\d{2}$/.test(v) && v >= "1900-01-01" && v <= oggi();

type Errori = Partial<Record<"tuGenere" | "tuGenereAltro" | "tuNascita" | "nome" | "genere" | "genereAltro" | "nascita", string>>;

export function verificaPersone(d: DatiPersone, mancanti: readonly string[], t: Dizionario): Errori {
  const l = t.lettura;
  const e: Errori = {};
  if (mancanti.includes("genere")) {
    if (!d.tuGenere) e.tuGenere = l.err_genere;
    else if (d.tuGenere === "altro" && !d.tuGenereAltro.trim()) e.tuGenereAltro = l.err_altro;
  }
  if (mancanti.includes("nascita") && !nascitaValida(d.tuNascita)) e.tuNascita = l.err_nascita;
  if (!d.nome.trim()) e.nome = l.err_nome;
  if (!d.genere) e.genere = l.err_genere;
  else if (d.genere === "altro" && !d.genereAltro.trim()) e.genereAltro = l.err_altro;
  if (!nascitaValida(d.nascita)) e.nascita = l.err_nascita;
  return e;
}

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

export function personeDaProfilo(profilo: Profilo, attuali: DatiPersone): DatiPersone {
  const p = profilo.partner_ricordato;
  if (!p) return attuali;
  return {
    ...attuali,
    nome: p.nome, cognome: p.cognome ?? "", genere: p.genere, genereAltro: p.genere_altro ?? "",
    trans: p.trans, nascita: p.nascita, ricorda: true,
  };
}

const GENERI: Genere[] = ["donna", "uomo", "non_binario", "altro", "non_dice"];

export function CampiGenere({
  genere, altro, trans, onGenere, onAltro, onTrans, errore, erroreAltro,
}: {
  genere: Genere | "";
  altro: string;
  trans: boolean;
  onGenere: (g: Genere | "") => void;
  onAltro: (v: string) => void;
  onTrans: (v: boolean) => void;
  errore?: string;
  erroreAltro?: string;
}) {
  const { t } = useLingua();
  const l = t.lettura;
  const id = useId();
  return (
    <>
      <div className="form-grid">
        <label className="field">
          <span>{l.persone_genere}</span>
          <select value={genere} onChange={(e) => onGenere(e.target.value as Genere | "")} aria-invalid={!!errore}
            aria-describedby={errore ? `${id}-e` : undefined}>
            <option value="">{l.persone_genere_scegli}</option>
            {GENERI.map((g) => <option key={g} value={g}>{l.generi[g]}</option>)}
          </select>
          {errore && <small id={`${id}-e`} className="error" role="alert">{errore}</small>}
        </label>
        {genere === "altro" && (
          <label className="field">
            <span>{l.persone_genere_altro}</span>
            <input value={altro} onChange={(e) => onAltro(e.target.value)} maxLength={30} dir="auto" aria-invalid={!!erroreAltro} />
            {erroreAltro && <small className="error" role="alert">{erroreAltro}</small>}
          </label>
        )}
      </div>
      <label className="check">
        <input type="checkbox" checked={trans} onChange={(e) => onTrans(e.target.checked)} />
        <span>{l.persone_trans}</span>
      </label>
    </>
  );
}

export function FormPersone({
  dati, onCambia, profilo, onAvanti, onDimentica, errore,
}: {
  dati: DatiPersone;
  onCambia: (d: DatiPersone) => void;
  profilo: Profilo | null;
  onAvanti: () => void;
  onDimentica: () => void;
  errore: string | null;
}) {
  const { t } = useLingua();
  const l = t.lettura;
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
    <form noValidate onSubmit={(e) => { e.preventDefault(); avanti(); }}>
      {mancanti.length > 0 && (
        <fieldset className="field">
          <legend className={stili.passo}>{l.persone_di_te}</legend>
          <p className="muted small">{l.persone_di_te_testo}</p>
          {mancanti.includes("genere") && (
            <CampiGenere
              genere={dati.tuGenere} altro={dati.tuGenereAltro} trans={dati.tuTrans}
              onGenere={(g) => cambia({ tuGenere: g })} onAltro={(v) => cambia({ tuGenereAltro: v })}
              onTrans={(v) => cambia({ tuTrans: v })} errore={errori.tuGenere} erroreAltro={errori.tuGenereAltro}
            />
          )}
          {mancanti.includes("nascita") && (
            <label className="field">
              <span>{l.persone_nascita}</span>
              <input type="date" value={dati.tuNascita} min="1900-01-01" max={oggi()}
                onChange={(e) => cambia({ tuNascita: e.target.value })} aria-invalid={!!errori.tuNascita} />
              {errori.tuNascita && <small className="error" role="alert">{errori.tuNascita}</small>}
            </label>
          )}
        </fieldset>
      )}

      <h3 className={stili.passo}>{l.persone_altra}</h3>
      {ricordato && (
        <div className={stili.ricordato} role="status">
          <span>{f(l.persone_ripresi, { nome: ricordato.nome })}</span>
          <button type="button" className="button button-quiet button-small" onClick={onDimentica}>{l.persone_dimentica}</button>
        </div>
      )}
      <div className="form-grid">
        <label className="field">
          <span>{l.persone_nome}</span>
          <input value={dati.nome} onChange={(e) => cambia({ nome: e.target.value })} maxLength={40} autoComplete="off"
            dir="auto" aria-invalid={!!errori.nome} />
          {errori.nome && <small className="error" role="alert">{errori.nome}</small>}
        </label>
        <label className="field">
          <span>{l.persone_cognome}</span>
          <input value={dati.cognome} onChange={(e) => cambia({ cognome: e.target.value })} maxLength={60} autoComplete="off" dir="auto" />
        </label>
      </div>
      <CampiGenere
        genere={dati.genere} altro={dati.genereAltro} trans={dati.trans}
        onGenere={(g) => cambia({ genere: g })} onAltro={(v) => cambia({ genereAltro: v })}
        onTrans={(v) => cambia({ trans: v })} errore={errori.genere} erroreAltro={errori.genereAltro}
      />
      <label className="field">
        <span>{l.persone_nascita}</span>
        <input type="date" value={dati.nascita} min="1900-01-01" max={oggi()}
          onChange={(e) => cambia({ nascita: e.target.value })} aria-invalid={!!errori.nascita} />
        {errori.nascita && <small className="error" role="alert">{errori.nascita}</small>}
      </label>
      <label className="check">
        <input type="checkbox" checked={dati.ricorda} onChange={(e) => cambia({ ricorda: e.target.checked })} />
        <span>{l.persone_ricorda}</span>
      </label>
      <p className="notice">{l.persone_privacy}</p>
      {(errore || (provato && Object.keys(errori).length > 0)) && (
        <p className="error" role="alert">{errore ?? l.err_incompleto}</p>
      )}
      <div className="button-row" style={{ marginTop: "1rem" }}>
        <button type="submit" className="button">{t.comune.avanti}</button>
      </div>
    </form>
  );
}
