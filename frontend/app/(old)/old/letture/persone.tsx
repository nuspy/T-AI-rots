"use client";

/* Nel dettaglio di una lettura speciale: le due persone e la compatibilità
 * zodiacale calcolata dal server. Il server manda codici (segno, aspetto,
 * armonia, elemento) e qui si traducono nella lingua dell'interfaccia. */

import type { Compatibilita, Genere, PersoneLettura } from "@/lib/api";
import { nomeCarta } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import pag from "../pagine.module.css";

/* Un dizionario indicizzato da codici del server: un codice sconosciuto si mostra com'è. */
const voce = (dizionario: object, codice: string) => (dizionario as Record<string, string>)[codice] ?? codice;

function Persona({
  titolo, cognome, genere, altro, trans, nascita, segno, cuspide,
}: {
  titolo: string;
  cognome?: string | null;
  genere: Genere | null;
  altro: string | null;
  trans: boolean;
  nascita: string;
  segno: string;
  cuspide: string | null;
}) {
  const { t, locale } = useLingua();
  const testoGenere = genere === "altro" && altro ? altro : genere ? t.generi[genere] : "";
  return (
    <div>
      <p className={pag.etichetta}>{titolo}{cognome ? ` ${cognome}` : ""}</p>
      <p className={pag.nota}>
        {[
          testoGenere ? `${testoGenere}${trans ? `, ${t.persona_trans}` : ""}` : "",
          new Date(nascita).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" }),
          segno + (cuspide ? ` (${cuspide})` : ""),
        ].filter(Boolean).join(" · ")}
      </p>
    </div>
  );
}

export function PersoneLettura({
  persone, compatibilita,
}: { persone: PersoneLettura; compatibilita: Compatibilita | null }) {
  const { t, lingua } = useLingua();
  const p = persone.partner;
  const segno = (codice: string | undefined) => (codice ? voce(t.segni, codice) : "");
  const cuspide = (s?: { cuspide: boolean; vicino: string | null }) =>
    s?.cuspide && s.vicino ? t.cuspide_di(segno(s.vicino)) : null;
  const c = compatibilita;
  return (
    <>
      <span className={pag.etichetta}>{t.le_persone}</span>
      <Persona
        titolo={t.tu}
        genere={persone.tu.genere}
        altro={persone.tu.genere_altro}
        trans={persone.tu.trans}
        nascita={persone.tu.nascita}
        segno={segno(c?.segni.tu.codice)}
        cuspide={cuspide(c?.segni.tu)}
      />
      <Persona
        titolo={p.nome}
        cognome={p.cognome}
        genere={p.genere}
        altro={p.genere_altro}
        trans={p.trans}
        nascita={p.nascita}
        segno={segno(c?.segni.partner.codice)}
        cuspide={cuspide(c?.segni.partner)}
      />
      {c && (
        <>
          <span className={pag.etichetta}>{t.compat_zodiacale}</span>
          <p className={pag.nota}>
            {t.aspetto_titolo}: <strong>{voce(t.aspetti, c.aspetto)}</strong> · {t.armonia_titolo}:{" "}
            <strong>{voce(t.armonie, c.armonia)}</strong>
          </p>
          <p className={pag.nota}>
            {t.elementi_titolo}: {voce(t.elementi, c.segni.tu.elemento)} / {voce(t.elementi, c.segni.partner.elemento)}
            {" · "}{voce(t.relazioni_elementi, c.relazione_elementi)}
          </p>
          <p className={pag.nota}>{t.carta_coppia}: {nomeCarta(c.carta_coppia, lingua)}</p>
          <p className={pag.nota}>{t.compat_avviso}</p>
        </>
      )}
    </>
  );
}
