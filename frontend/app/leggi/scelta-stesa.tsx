"use client";

/* La scelta della stesa: cinque tavole in miniatura, ognuna con la sua
 * disposizione disegnata, e la domanda. */

import { motion } from "framer-motion";
import type { Stesa } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import stili from "./leggi.module.css";

function Miniatura({ stesa }: { stesa: Stesa }) {
  /* Le posizioni vere della stesa, in scala: la miniatura è la stesa. */
  return (
    <svg viewBox="0 0 100 64" className={stili.miniatura} aria-hidden="true">
      {stesa.posizioni.map((p, i) => {
        const w = stesa.posizioni.length > 8 ? 6 : 9;
        const h = w * 1.6;
        return (
          <motion.rect
            key={p.n}
            x={p.x * 100 - w / 2}
            y={p.y * 64 - h / 2}
            width={w}
            height={h}
            rx={1.2}
            fill={p.calcolata ? "rgba(185,164,255,0.35)" : "rgba(216,180,90,0.25)"}
            stroke="#d8b45a"
            strokeWidth={0.6}
            transform={p.rotazione ? `rotate(${p.rotazione} ${p.x * 100} ${p.y * 64})` : undefined}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * i, duration: 0.4 }}
          />
        );
      })}
    </svg>
  );
}

export function SceltaStesa({
  stese,
  scelta,
  onScegli,
  domanda,
  onDomanda,
  onInizia,
  inCorso,
  errore,
}: {
  stese: Stesa[];
  scelta: string | null;
  onScegli: (id: string) => void;
  domanda: string;
  onDomanda: (d: string) => void;
  onInizia: () => void;
  inCorso: boolean;
  errore: string | null;
}) {
  const { t, lingua } = useLingua();
  const selezionata = stese.find((s) => s.id === scelta);
  return (
    <div className={stili.scelta}>
      <h2 className={stili.passo}><span>I</span> {t.scegli_stesa}</h2>
      <div className={stili.stese}>
        {stese.map((s, i) => (
          <motion.button
            key={s.id}
            className={s.id === scelta ? stili.stesaScelta : stili.stesa}
            onClick={() => onScegli(s.id)}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 * i, type: "spring", stiffness: 160, damping: 20 }}
            whileHover={{ y: -4 }}
            aria-pressed={s.id === scelta}
          >
            <Miniatura stesa={s} />
            <span className={stili.stesaNome}>{lingua === "en" ? s.nome_en : s.nome}</span>
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
              <li key={p.n}><strong>{p.nome}</strong> — {p.significato}</li>
            ))}
          </ol>
        </motion.div>
      )}

      <h2 className={stili.passo}><span>II</span> {t.la_tua_domanda}</h2>
      <textarea
        className={stili.domanda}
        value={domanda}
        onChange={(e) => onDomanda(e.target.value)}
        placeholder={t.domanda_segnaposto}
        maxLength={1000}
        rows={3}
        aria-label={t.la_tua_domanda}
      />
      {errore && <p className={stili.errore} role="alert">{errore}</p>}
      <div className={stili.azioniCentro}>
        <button className="bottone" disabled={!scelta || domanda.trim().length < 3 || inCorso} onClick={onInizia}>
          ✦ {t.inizia}
        </button>
      </div>
    </div>
  );
}
