"use client";

/* La soglia: chi arriva vede subito le carte muoversi e capisce cosa succede
 * in una lettura, prima ancora di registrarsi. */

import { useCallback, useEffect, useState } from "react";
import Link from "@/app/componenti/link";
import { motion } from "framer-motion";
import { elencaCarte, elencaStese, votoHome } from "@/lib/api";
import { salvaInvito } from "@/lib/inviti";
import { useLingua } from "@/lib/lingua";
import { useCarica } from "@/lib/usa";
import { BannerInterpreta } from "./componenti/banner-interpreta";
import { BannerMazzo } from "./componenti/banner-mazzo";
import { Carta } from "./componenti/carta";
import { CtaIscrizione } from "./componenti/cta-iscrizione";
import { Marchio } from "./componenti/marchio";
import { MattonellaCategoria, MattonellaStesa } from "./componenti/mattonella-lettura";
import { Modale } from "./componenti/modale";
import { Testata } from "./componenti/testata";
import paginaStili from "./pagine.module.css";
import stili from "./soglia.module.css";

export function Soglia() {
  const { t, lingua } = useLingua();
  const carte = useCarica(useCallback(() => elencaCarte(lingua), [lingua]), [lingua], { pubblico: true });
  const stese = useCarica(useCallback(() => elencaStese("standard", lingua), [lingua]), [lingua], { pubblico: true });
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
              <Carta carta={c} rivelata={i % 2 === 0} larghezza="clamp(64px, 18vw, 150px)" />
            </motion.div>
          ))}
        </div>
      </section>

      {/* La carta del giorno: uno spazio suo, non un link anonimo — dice subito che è gratis e perché guardarla. */}
      <section className={stili.sezione}>
        <Link href="/carta-del-giorno" className={`pannello ${stili.cartaGiorno}`}>
          <span className={stili.cartaGiornoSimbolo} aria-hidden="true">☉</span>
          <div>
            <strong>{t.home_carta_giorno_titolo}</strong>
            <p>{t.home_carta_giorno_testo}</p>
          </div>
          <span className={stili.cartaGiornoCta}>{t.home_carta_giorno_cta} →</span>
        </Link>
      </section>

      {/* Una delle funzioni distintive del sito, in cima alla pagina: leggere le proprie carte fisiche
          merita la stessa visibilità della carta del giorno, non uno scroll in fondo per trovarla. */}
      <section className={stili.sezione}>
        <BannerInterpreta />
      </section>

      <CtaIscrizione />

      {/* Come funziona: un'infografica, non un testo da leggere — tre passi, un'icona e una parola ciascuno. */}
      <section className={stili.sezione}>
        <h2>{t.home_come}</h2>
        <div className={stili.passi}>
          {passi.map((p, i) => (
            <motion.div key={p.etichetta} className={stili.passo} initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.12 }}>
              <span className={stili.passoIcona} aria-hidden="true">{p.icona}</span>
              <span className={stili.passoEtichetta}>{p.etichetta}</span>
              {i < passi.length - 1 && <span className={stili.passoFreccia} aria-hidden="true">→</span>}
            </motion.div>
          ))}
        </div>
      </section>

      <CtaIscrizione />

      {/* Le stese tradizionali e le letture speciali, in una sezione sola: titolo e schema soltanto, la
          descrizione sta nel dialogo al clic. */}
      <section className={stili.sezione}>
        <h2>{t.home_stese_sezione}</h2>
        <h3 className={stili.sottotitoloSezione}>{t.home_stese}</h3>
        <div className={stili.mattonelle}>
          {(stese.dati ?? []).map((s) => <MattonellaStesa key={s.id} stesa={s} />)}
        </div>
        <p className={stili.introSezione}>
          <Link href="/stese">{t.stesa_tutte} →</Link>
        </p>

        <h3 className={stili.sottotitoloSezione}>{t.home_speciali}</h3>
        <div className={stili.mattonelle}>
          <MattonellaCategoria
            simbolo="♀" titolo={t.tipo_compat} descrizione={t.tipo_compat_desc} href="/leggi?tipo=compatibilita"
          />
          <MattonellaCategoria
            simbolo="☽" titolo={t.tipo_coppia} descrizione={t.tipo_coppia_desc} href="/leggi?tipo=coppia"
          />
        </div>
      </section>

      <CtaIscrizione />

      <section className={stili.sezione}>
        <BannerMazzo />
      </section>

      {/* Vota il prossimo mazzo (v7, Fase K + "tornate elettorali"): CTA se c'è una tornata aperta,
          risultato dell'ultima con miniature ingrandibili se una tornata si è appena chiusa. */}
      <VotoRiepilogoHome />

      <section className={stili.sezione}>
        <h2>{t.home_rigore}</h2>
        <div className={stili.rigore}>
          <p className="oracolo">{t.home_rigore_1}</p>
          <p className="oracolo">{t.home_rigore_2}</p>
        </div>
        <p className={stili.avvertenza}>{t.home_avvertenza}</p>
      </section>

      <CtaIscrizione />
    </div>
  );
}

/** Vota il prossimo mazzo, in home: pubblico, nessun account richiesto (`GET /voto/home`). Se c'è
 * una tornata aperta mostra la CTA verso `/vota-mazzo`; se l'ultima si è appena chiusa, mostra ogni
 * mazzo che era in corsa (non solo il vincitore) con le sue miniature ingrandibili in un dialogo. */
function VotoRiepilogoHome() {
  const { t } = useLingua();
  const dati = useCarica(votoHome, [], { pubblico: true });
  const [ingrandita, setIngrandita] = useState<{ url: string; titolo: string } | null>(null);
  const d = dati.dati;
  if (!d || (!d.voto_aperto && !d.risultato_recente)) return null;

  return (
    <>
      {d.voto_aperto && (
        <section className={stili.sezione}>
          <Link href="/vota-mazzo" className={`pannello ${stili.cartaGiorno}`}>
            <span className={stili.cartaGiornoSimbolo} aria-hidden="true">★</span>
            <div>
              <strong>{t.home_vota_titolo}</strong>
              <p>{t.home_vota_testo}</p>
            </div>
            <span className={stili.cartaGiornoCta}>{t.vota_bottone} →</span>
          </Link>
        </section>
      )}

      {d.risultato_recente && (
        <section className={stili.sezione}>
          <div className="pannello" style={{ padding: 24 }}>
            <h2>{t.home_vota_risultato_titolo}</h2>
            <div className={paginaStili.carteRiga}>
              {d.risultato_recente.candidati.flatMap((c) =>
                c.campioni.filter((camp) => camp.url).map((camp, i) => (
                  <button
                    key={`${c.nome}-${i}`}
                    type="button"
                    onClick={() => setIngrandita({ url: camp.url as string, titolo: `${c.nome} · ${t.vota_percentuale(c.percentuale)}` })}
                    style={{
                      display: "flex", flexDirection: "column", alignItems: "center", gap: 6,
                      border: "none", background: "none", cursor: "zoom-in", padding: 0, color: "inherit",
                    }}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={camp.url as string} alt={camp.etichetta ?? c.nome} width={110} style={{ borderRadius: 8 }} />
                    <span style={{ fontSize: "0.82rem", color: "var(--testo-debole)" }}>{c.nome} · {t.vota_percentuale(c.percentuale)}</span>
                  </button>
                )),
              )}
            </div>
            <p style={{ marginTop: 14 }}>
              <Link href="/vota-mazzo">{t.vota_vedi_statistiche} →</Link>
            </p>
          </div>
        </section>
      )}

      <Modale aperta={!!ingrandita} titolo={ingrandita?.titolo ?? ""} onChiudi={() => setIngrandita(null)}>
        {ingrandita && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={ingrandita.url} alt={ingrandita.titolo} style={{ maxWidth: "100%", borderRadius: 12, display: "block" }} />
        )}
      </Modale>
    </>
  );
}
