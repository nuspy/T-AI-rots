"use client";

/* L'offerta di passare il sito alla lingua in cui si sta scrivendo (9/10), una riga discreta sotto la conversazione:
 * «Stai scrivendo in italiano. Vuoi il sito in italiano? [Passa all'italiano] [×]». È scritta in QUELLA lingua se ne
 * abbiamo i testi; le lingue non ancora tradotte sono copie dell'inglese, e allora parla inglese col nome inglese della
 * lingua («You're writing in German…»). Il dizionario si carica qui, una volta. Mai automatica: un tocco cambia, la ✕
 * la chiude. */

import { useEffect, useState } from "react";
import { caricaDizionario, dizionarioPronto, f, type Dizionario, type Lingua } from "@/v2/i18n";
import stili from "./lettura.module.css";

function nomeLingua(codice: Lingua, inLingua: string): string {
  try {
    return new Intl.DisplayNames([inLingua], { type: "language" }).of(codice) ?? codice;
  } catch {
    return codice;
  }
}

export function OffertaLingua({ lingua, onCambia, onChiudi }: {
  lingua: Lingua;
  onCambia: () => void;
  onChiudi: () => void;
}) {
  const [caricato, setCaricato] = useState<{ lingua: Lingua; d: Dizionario } | null>(null);
  useEffect(() => {
    if (dizionarioPronto(lingua)) return;
    let annullato = false;
    void caricaDizionario(lingua).then((d) => { if (!annullato) setCaricato({ lingua, d }); });
    return () => { annullato = true; };
  }, [lingua]);
  const diz = dizionarioPronto(lingua) ?? (caricato?.lingua === lingua ? caricato.d : null);
  if (!diz) return null;
  const d = diz.lettura;
  const copia = lingua !== "en" && d.offerta_lingua === dizionarioPronto("en")!.lettura.offerta_lingua;
  const parla = copia ? "en" : lingua;
  return (
    <div className={stili.offertaLingua} lang={parla} role="status">
      <p dir="auto">{f(d.offerta_lingua, { lingua: nomeLingua(lingua, parla) })}</p>
      <button type="button" className="button button-small" onClick={onCambia}>{d.offerta_lingua_si}</button>
      <button type="button" className={stili.offertaChiudi} aria-label={d.offerta_lingua_no} title={d.offerta_lingua_no}
        onClick={onChiudi}>
        <span aria-hidden="true">×</span>
      </button>
    </div>
  );
}
