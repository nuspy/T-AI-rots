"use client";

/* La carta del giorno: gratuita, la stessa per tutta la giornata, con la
 * serie dei giorni consecutivi. È il piccolo rito che fa tornare. */

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { cartaDelGiorno } from "@/lib/api";
import { nomeCarta } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { useCarica } from "@/lib/usa";
import { Carta } from "../componenti/carta";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";

export default function PaginaGiorno() {
  const { t } = useLingua();
  return (
    <Involucro titolo={t.nav_giorno} sottotitolo={t.giorno_sottotitolo}>
      <Giorno />
    </Involucro>
  );
}

function Giorno() {
  const { t, lingua, locale } = useLingua();
  const giorno = useCarica(cartaDelGiorno);
  const [girata, setGirata] = useState(false);
  if (giorno.errore) return <p className={stili.errore}>{giorno.errore}</p>;
  const g = giorno.dati;
  if (!g) return null;
  return (
    <div className={stili.cartaGrande}>
      <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
        <Carta carta={g.carta} rivelata={girata} rovescio={g.rovescio} larghezza={250}
          brilla={!girata} onClick={() => setGirata(true)} etichetta={girata ? nomeCarta(g.carta, lingua) : t.rivela} />
      </motion.div>
      <div>
        <p className={stili.nota}>
          {new Date(g.giorno).toLocaleDateString(locale, { weekday: "long", day: "numeric", month: "long" })}
          {" · "}🔥 {t.giorni_di_fila(g.serie)}
        </p>
        {!girata && <button className="bottone" style={{ marginTop: 18 }} onClick={() => setGirata(true)}>{t.rivela}</button>}
        {girata && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
            <h2>{nomeCarta(g.carta, lingua)} <span className={stili.nota}>· {g.rovescio ? t.rovesciata : t.dritta}</span></h2>
            <p className={stili.etichetta}>{g.carta.lettera_ebraica?.nome} {g.carta.lettera_ebraica?.glifo} · {g.carta.astrologia}</p>
            <p className="oracolo">{g.testo}</p>
            {g.carta.ambiti?.spirito && <p className="oracolo">{g.carta.ambiti.spirito}</p>}
            <p className={stili.nota}>{g.carta.parole_chiave.join(" · ")}</p>
            <div className={stili.linea} style={{ marginTop: 18 }}>
              <Link href="/leggi" className="bottone">✦ {t.inizia}</Link>
              <Link href={`/carte/${g.carta.id}`} className="bottone-secondario">{nomeCarta(g.carta, lingua)}</Link>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
