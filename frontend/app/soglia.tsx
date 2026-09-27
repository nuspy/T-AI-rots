"use client";

/* La soglia: chi arriva vede subito le carte muoversi e capisce cosa succede
 * in una lettura, prima ancora di registrarsi. */

import { useCallback, useEffect } from "react";
import Link from "@/app/componenti/link";
import { motion } from "framer-motion";
import { elencaCarte, elencaStese } from "@/lib/api";
import { salvaInvito } from "@/lib/inviti";
import { useLingua } from "@/lib/lingua";
import { nomeStesa } from "@/lib/i18n";
import { useCarica } from "@/lib/usa";
import { BannerMazzo } from "./componenti/banner-mazzo";
import { Carta } from "./componenti/carta";
import { Marchio } from "./componenti/marchio";
import { Testata } from "./componenti/testata";
import stili from "./soglia.module.css";

export function Soglia() {
  const { t, lingua } = useLingua();
  const carte = useCarica(useCallback(() => elencaCarte(), []), [], { pubblico: true });
  const stese = useCarica(useCallback(() => elencaStese("standard"), []), [], { pubblico: true });
  const maggiori = (carte.dati ?? []).filter((c) => c.arcano === "maggiore");
  const scelte = [0, 1, 2, 17, 19, 21].map((n) => maggiori.find((c) => c.numero === n)).filter(Boolean);
  const passi = t.home_passi;

  /* Chi arriva da un invito porta il codice nell'indirizzo: lo si ricorda
   * fino alla registrazione, e il profilo lo propone da riscattare. */
  useEffect(() => {
    const codice = new URLSearchParams(window.location.search).get("invito");
    if (codice) salvaInvito(codice);
  }, []);

  return (
    <div className={stili.soglia}>
      <Testata />
      <section className={stili.eroe}>
        <div className={stili.eroeTesto}>
          <motion.p className={stili.sovratitolo} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
            ✦ {t.sovratitolo} ✦
          </motion.p>
          <div className={stili.logo}>
            <Marchio variante="blocco" priorita />
          </div>
          <h1 className={stili.h1}>{t.home_h1}</h1>
          <motion.p className={`oracolo ${stili.motto}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 1 }}>
            {t.motto}
          </motion.p>
          <motion.div className={stili.inviti} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}>
            <Link href="/leggi" className="bottone">✦ {t.inizia}</Link>
            <Link href="/carta-del-giorno" className="bottone-secondario">☉ {t.nav_giorno}</Link>
          </motion.div>
        </div>
        <div className={stili.eroeCarte} aria-hidden="true">
          {scelte.map((c, i) => (
            <motion.div
              key={c!.id}
              className={stili.cartaVolante}
              style={{ left: `${8 + i * 14}%`, zIndex: i === 2 ? 10 : i }}
              initial={{ opacity: 0, y: 80, rotate: -30 + i * 12 }}
              animate={{ opacity: 1, y: [0, -14, 0], rotate: -22 + i * 9 }}
              transition={{
                opacity: { delay: 0.3 + i * 0.12, duration: 0.8 },
                rotate: { delay: 0.3 + i * 0.12, duration: 0.8 },
                y: { duration: 4 + i * 0.4, repeat: Infinity, ease: "easeInOut", delay: i * 0.3 },
              }}
            >
              <Carta carta={c} rivelata={i % 2 === 0} larghezza={150} />
            </motion.div>
          ))}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2>{t.home_come}</h2>
        <div className={stili.passi}>
          {passi.map(([titolo, testo], i) => (
            <motion.div key={titolo} className={`pannello ${stili.passo}`} initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <span className={stili.numeroPasso}>{["I", "II", "III", "IV"][i]}</span>
              <h3>{titolo}</h3>
              <p>{testo}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className={stili.sezione}>
        <h2>{t.home_stese}</h2>
        <div className={stili.stese}>
          {(stese.dati ?? []).map((s) => (
            <Link key={s.id} href={`/leggi?stesa=${s.id}`} className={`pannello ${stili.stesa}`}>
              <strong>{nomeStesa(s, lingua)}</strong>
              <span>{s.posizioni.length} {t.carte} · {s.mazzo === "maggiori" ? t.maggiori : t.completo}</span>
              <p>{s.descrizione}</p>
            </Link>
          ))}
        </div>
        <p className={stili.introSezione}>
          <Link href="/stese">{t.stesa_tutte} →</Link>
        </p>
      </section>

      <section className={stili.sezione}>
        <h2>{t.home_speciali}</h2>
        <p className={stili.introSezione}>{t.home_speciali_testo}</p>
        <div className={stili.speciali}>
          {([["compatibilita", t.tipo_compat, t.tipo_compat_desc], ["coppia", t.tipo_coppia, t.tipo_coppia_desc]] as const).map(
            ([tipo, nome, descrizione]) => (
              <Link key={tipo} href={`/leggi?tipo=${tipo}`} className={`pannello ${stili.stesa}`}>
                <strong>{nome}</strong>
                <p>{descrizione}</p>
              </Link>
            ),
          )}
        </div>
      </section>

      <section className={stili.sezione}>
        <BannerMazzo />
      </section>

      <section className={stili.sezione}>
        <h2>{t.home_rigore}</h2>
        <div className={stili.rigore}>
          <p className="oracolo">{t.home_rigore_1}</p>
          <p className="oracolo">{t.home_rigore_2}</p>
        </div>
        <p className={stili.avvertenza}>{t.home_avvertenza}</p>
      </section>
    </div>
  );
}
