"use client";

/* La scelta della stesa: le tavole in miniatura, ognuna con la sua
 * disposizione disegnata, e la domanda.
 *
 * Serve alla lettura standard e alle due speciali. Per le speciali le stese si
 * scelgono per STILE (tradizionale, moderna, di tendenza) e la domanda è
 * facoltativa: se resta vuota parte con quella di ripiego («Compatibilità con
 * Marco»).
 */

import { motion } from "framer-motion";
import type { Stesa, Stile } from "@/lib/api";
import { nomePosizione, nomeStesa } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { MiniaturaStesa } from "../componenti/miniatura-stesa";
import stili from "./leggi.module.css";

const ORDINE_STILI: Stile[] = ["tradizionale", "moderna", "tendenza"];

export function SceltaStesa({
  stese,
  scelta,
  onScegli,
  domanda,
  onDomanda,
  onInizia,
  inCorso,
  errore,
  conStili = false,
  domandaFacoltativa = false,
  domandaPredefinita = "",
  onIndietro,
  testoInizia,
}: {
  stese: Stesa[];
  scelta: string | null;
  onScegli: (id: string) => void;
  domanda: string;
  onDomanda: (d: string) => void;
  onInizia: () => void;
  inCorso: boolean;
  errore: string | null;
  /* Le letture speciali: si sceglie prima lo stile, poi la stesa. */
  conStili?: boolean;
  /* La domanda si può lasciare vuota: parte quella di ripiego. */
  domandaFacoltativa?: boolean;
  domandaPredefinita?: string;
  onIndietro?: () => void;
  testoInizia?: string;
}) {
  const { t, lingua } = useLingua();
  const selezionata = stese.find((s) => s.id === scelta);
  const stiliOfferti = ORDINE_STILI.filter((s) => stese.some((x) => x.stile === s));
  const stileAttivo: Stile | null = conStili ? (selezionata?.stile ?? stiliOfferti[0] ?? null) : null;
  const visibili = conStili ? stese.filter((s) => s.stile === stileAttivo) : stese;
  const etichettaStile: Record<Stile, string> = {
    tradizionale: t.stile_tradizionale,
    moderna: t.stile_moderna,
    tendenza: t.stile_tendenza,
  };
  const descrizioneStile: Record<Stile, string> = {
    tradizionale: t.stile_tradizionale_desc,
    moderna: t.stile_moderna_desc,
    tendenza: t.stile_tendenza_desc,
  };
  const puoIniziare = !!scelta && !inCorso && (domandaFacoltativa || domanda.trim().length >= 3);

  return (
    <div className={stili.scelta}>
      <h2 className={stili.passo}><span>I</span> {conStili ? t.stile_titolo : t.scegli_stesa}</h2>

      {conStili && (
        <div className={stili.stiliRiga} role="group" aria-label={t.stile_titolo}>
          {stiliOfferti.map((s) => (
            <button
              key={s}
              type="button"
              className={s === stileAttivo ? stili.stilePillolaAttiva : stili.stilePillola}
              aria-pressed={s === stileAttivo}
              onClick={() => {
                const prima = stese.find((x) => x.stile === s);
                if (prima) onScegli(prima.id);
              }}
            >
              {etichettaStile[s]}
              <span className={stili.stileConteggio}>{stese.filter((x) => x.stile === s).length}</span>
            </button>
          ))}
        </div>
      )}
      {stileAttivo && <p className={stili.guida}>{descrizioneStile[stileAttivo]}</p>}

      <div className={visibili.length <= 2 ? stili.steseCentrate : stili.stese}>
        {visibili.map((s, i) => (
          <motion.button
            key={s.id}
            type="button"
            className={s.id === scelta ? stili.stesaScelta : stili.stesa}
            onClick={() => onScegli(s.id)}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 * i, type: "spring", stiffness: 160, damping: 20 }}
            whileHover={{ y: -4 }}
            aria-pressed={s.id === scelta}
          >
            <MiniaturaStesa stesa={s} animata className={stili.miniatura} />
            <span className={stili.stesaNome}>{nomeStesa(s, lingua)}</span>
            <span className={stili.stesaDettagli}>
              {s.posizioni.length} {t.carte} · {s.mazzo === "maggiori" ? t.maggiori : t.completo}
            </span>
          </motion.button>
        ))}
      </div>

      {selezionata && (
        <motion.div key={selezionata.id} className={`pannello ${stili.descrizioneStesa}`}
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <p className="oracolo">{selezionata.descrizione}</p>
          <p className={stili.origine}>{selezionata.origine}</p>
          <ol className={stili.posizioniElenco}>
            {selezionata.posizioni.map((p) => (
              <li key={p.n}><strong>{nomePosizione(p, lingua)}</strong> — {p.significato}</li>
            ))}
          </ol>
        </motion.div>
      )}

      <h2 className={stili.passo}><span>II</span> {t.la_tua_domanda}</h2>
      {domandaFacoltativa && <p className={stili.guida}>{t.domanda_facoltativa}</p>}
      <textarea
        className={stili.domanda}
        value={domanda}
        onChange={(e) => onDomanda(e.target.value)}
        placeholder={domandaFacoltativa && domandaPredefinita ? domandaPredefinita : t.domanda_segnaposto}
        dir="auto"
        maxLength={1000}
        rows={3}
        aria-label={t.la_tua_domanda}
      />
      {errore && <p className={stili.errore} role="alert">{errore}</p>}
      <div className={stili.azioniCentro}>
        {onIndietro && (
          <button type="button" className="bottone-secondario" onClick={onIndietro}>{t.indietro}</button>
        )}
        <button className="bottone" disabled={!puoIniziare} onClick={onInizia}>
          ✦ {testoInizia ?? t.inizia}
        </button>
      </div>
    </div>
  );
}
