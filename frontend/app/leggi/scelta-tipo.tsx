"use client";

/* Il primo passo: che lettura vuoi fare. Tre tessere, una per tipo. */

import { motion } from "framer-motion";
import type { Categoria } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import stili from "./leggi.module.css";

export function SceltaTipo({ onScegli }: { onScegli: (categoria: Categoria) => void }) {
  const { t } = useLingua();
  const tipi: { id: Categoria; segno: string; nome: string; descrizione: string }[] = [
    { id: "standard", segno: "✦", nome: t.tipo_standard, descrizione: t.tipo_standard_desc },
    { id: "compatibilita", segno: "◐", nome: t.tipo_compat, descrizione: t.tipo_compat_desc },
    { id: "coppia", segno: "❖", nome: t.tipo_coppia, descrizione: t.tipo_coppia_desc },
  ];
  return (
    <div className={stili.scelta}>
      <h2 className={stili.passo}>{t.tipo_titolo}</h2>
      <div className={stili.tipi}>
        {tipi.map((tipo, i) => (
          <motion.button
            key={tipo.id}
            type="button"
            className={stili.tipo}
            onClick={() => onScegli(tipo.id)}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 * i, type: "spring", stiffness: 160, damping: 20 }}
            whileHover={{ y: -4 }}
          >
            <span className={stili.tipoSegno} aria-hidden="true">{tipo.segno}</span>
            <span className={stili.tipoNome}>{tipo.nome}</span>
            <span className={stili.tipoTesto}>{tipo.descrizione}</span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
