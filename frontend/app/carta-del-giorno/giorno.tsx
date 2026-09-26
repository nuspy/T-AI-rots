"use client";

/* La carta del giorno.
 *
 * Due cose sotto lo stesso indirizzo. Per chi non ha un account: **la carta di oggi per tutti**, la stessa per
 * chiunque fino a mezzanotte (UTC), scritta dal server — è ciò che trova chi cerca «tarot card of the day». Per chi
 * ha un account: la sua carta personale, gratuita, con la serie dei giorni di fila: il piccolo rito che fa tornare. */

import { useState } from "react";
import Link from "@/app/componenti/link";
import { motion } from "framer-motion";
import { cartaDelGiorno, type CartaOggi } from "@/lib/api";
import { nomeCarta } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import type { LinguaPubblica } from "@/lib/percorsi";
import { GIORNO, nomeBreve } from "@/lib/seo-testi";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import { Carta } from "../componenti/carta";
import { Involucro } from "../componenti/testata";
import stili from "../pagine.module.css";

/** La data del giorno scritta per esteso: in UTC, perché server e browser scrivano lo stesso testo. */
function dataPerEsteso(giorno: string, lingua: LinguaPubblica): string {
  return new Intl.DateTimeFormat(lingua === "it" ? "it-IT" : "en-GB", { dateStyle: "full", timeZone: "UTC" }).format(
    new Date(`${giorno}T12:00:00Z`),
  );
}

export function PaginaGiorno({ oggi, lingua }: { oggi: CartaOggi | null; lingua: LinguaPubblica }) {
  return (
    <Involucro
      pubblica
      titolo={GIORNO.h1(lingua)}
      sottotitolo={oggi ? GIORNO.sottotitolo(lingua, dataPerEsteso(oggi.giorno, lingua), nomeBreve(oggi.carta.nome ?? oggi.carta.nome_it)) : GIORNO.intro(lingua)}
    >
      <Giorno oggi={oggi} lingua={lingua} />
    </Involucro>
  );
}

function Giorno({ oggi, lingua: linguaPagina }: { oggi: CartaOggi | null; lingua: LinguaPubblica }) {
  const sessione = useSessione();
  if (sessione.autenticata) return <Personale />;
  return oggi ? <PerTutti oggi={oggi} lingua={linguaPagina} /> : null;
}

/* La carta di oggi, uguale per tutti: tutto il testo è già nell'HTML. */
function PerTutti({ oggi, lingua }: { oggi: CartaOggi; lingua: LinguaPubblica }) {
  const { t } = useLingua();
  const sessione = useSessione();
  const c = oggi.carta;
  const nome = c.nome ?? c.nome_it;
  return (
    <div className={stili.cartaGrande}>
      <Carta carta={c} rivelata larghezza={250} />
      <article>
        <p className={`oracolo ${stili.lead}`}>{GIORNO.intro(lingua)}</p>
        <h2>{nome}</h2>
        <p className={stili.etichetta}>{[c.lettera_ebraica?.nome, c.elemento_label ?? c.elemento, c.astrologia].filter(Boolean).join(" · ")}</p>
        <p className="oracolo">{oggi.testo}</p>
        {c.ambiti?.spirito && <p className="oracolo">{c.ambiti.spirito}</p>}
        <p className={stili.nota}>{c.parole_chiave.join(" · ")}</p>
        <div className={stili.linea} style={{ marginTop: 18 }}>
          <Link href={`/carte/${c.slug ?? c.id}`} className="bottone-secondario">{GIORNO.pienoSignificato(lingua, nomeBreve(nome))}</Link>
          <Link href="/leggi" className="bottone">✦ {t.inizia}</Link>
        </div>
        <p className={stili.nota} style={{ marginTop: 22 }}>{GIORNO.personale(lingua)}</p>
        {sessione.pronta && (
          <div className={stili.linea}>
            <button className="bottone-secondario" onClick={() => sessione.registrati()}>{t.registrati}</button>
            <button className="bottone-secondario" onClick={() => sessione.entra("/carta-del-giorno")}>{t.entra}</button>
          </div>
        )}
      </article>
    </div>
  );
}

/* La carta personale di chi ha un account: si gira, con la serie dei giorni di fila. */
function Personale() {
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
