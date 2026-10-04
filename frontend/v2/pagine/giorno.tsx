"use client";

/* La carta del giorno nella v2: un piccolo incontro senza account (la carta di oggi, uguale per tutti fino a
 * mezzanotte UTC), e per chi è dentro la sua carta personale da girare, con i giorni di fila. Porta a una domanda
 * più ampia: la carta come spunto, non come promessa. */

import { useState } from "react";
import { cartaDiOggi } from "@/lib/api";
import { InvitoNotifiche } from "@/v2/componenti/notifiche";
import { cartaDelGiornoLocale } from "@/v2/lib/notifiche";
import { useSessione } from "@/lib/sessione";
import { f, plurale } from "@/v2/i18n";
import { CartaV2 } from "@/v2/componenti/carta";
import LinkV2 from "@/v2/componenti/link";
import { Pubblicita } from "@/v2/componenti/pubblicita";
import { P, linguaContenuti } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";
import { DiarioNove } from "./blog";
import { nomeDi } from "./carte";

export function Giorno() {
  const sessione = useSessione();
  /* Finché la sessione non è pronta (e sul server) si vede la carta di tutti: l'HTML esce con la carta di oggi. */
  /* Gli spazi pubblicitari (spenti per default): la pagina è corta, il diario è metà del contenuto. A un terzo dopo
   * la carta, a due terzi fra gli articoli recenti e quelli attinenti, alla fine dopo il diario. */
  return (
    <>
      {sessione.autenticata ? <Personale /> : <PerTutti />}
      <Pubblicita posizione="terzo" />
      <DiarioNove inMezzo={<Pubblicita posizione="due_terzi" dentro />} />
      <Pubblicita posizione="fine" />
    </>
  );
}

function PerTutti() {
  const { t, lingua } = useLingua();
  const k = t.giorno;
  const sessione = useSessione();
  const oggi = useCarica(() => cartaDiOggi(linguaContenuti(lingua)), [lingua], { pubblico: true, iniziale: P.oggi(lingua) });
  if (oggi.errore) return <section className="band band-tight"><p className="error">{oggi.errore}</p></section>;
  if (!oggi.dati) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const c = oggi.dati.carta;
  const nome = nomeDi(c, lingua);
  return (
    <section className="band band-tight deck-layout" style={{ alignItems: "start" }}>
      <div style={{ justifySelf: "center" }}><CartaV2 carta={c} rivelata larghezza="min(260px, 70vw)" /></div>
      <div>
        <p className="eyebrow">{k.di_tutti}</p>
        <h2 className="section-title">{nome}</h2>
        <p className="small muted">{[c.lettera_ebraica?.nome, c.elemento_label ?? c.elemento, c.astrologia].filter(Boolean).join(" · ")}</p>
        <div className="prose-block"><p>{oggi.dati.testo}</p>{c.ambiti?.spirito && <p>{c.ambiti.spirito}</p>}</div>
        <p className="section-intro">{k.domanda}</p>
        <div className="button-row">
          <LinkV2 className="button" href={`${R.leggi}?source=daily`}>{k.cta}</LinkV2>
          <LinkV2 className="button button-quiet" href={R.carta(c.slug ?? c.id)}>{f(k.significato, { carta: nome })}</LinkV2>
        </div>
        <p className="notice">{k.personale}</p>
        {sessione.pronta && (
          <div className="button-row" style={{ marginTop: ".8rem" }}>
            <button type="button" className="button button-quiet button-small" onClick={() => sessione.entra(R.giorno)}>{k.entra}</button>
          </div>
        )}
      </div>
    </section>
  );
}

function Personale() {
  const { t, lingua, locale } = useLingua();
  const k = t.giorno;
  const l = t.lettura;
  const giorno = useCarica(cartaDelGiornoLocale);
  const [girata, setGirata] = useState(false);
  if (giorno.errore) return <section className="band band-tight"><p className="error">{giorno.errore}</p></section>;
  const g = giorno.dati;
  if (!g) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const nome = nomeDi(g.carta, lingua);
  return (
    <section className="band band-tight deck-layout" style={{ alignItems: "start" }}>
      <div style={{ justifySelf: "center" }}>
        <CartaV2 carta={g.carta} rivelata={girata} rovescio={g.rovescio} larghezza="min(260px, 70vw)" brilla={!girata}
          onClick={girata ? undefined : () => setGirata(true)} etichetta={girata ? nome : k.gira} />
      </div>
      <div>
        <p className="eyebrow">{k.tua}</p>
        <p className="small muted">
          {new Date(g.giorno).toLocaleDateString(locale, { weekday: "long", day: "numeric", month: "long" })} · {plurale(g.serie, k.serie)}
        </p>
        {!girata ? (
          <button type="button" className="button button-brass" onClick={() => setGirata(true)}>{k.gira}</button>
        ) : (
          <>
            <h2 className="section-title">{nome} <small className="small muted">· {g.rovescio ? l.rovesciata : l.dritta}</small></h2>
            <div className="prose-block"><p>{g.testo}</p>{g.carta.ambiti?.spirito && <p>{g.carta.ambiti.spirito}</p>}</div>
            <p className="section-intro">{k.domanda}</p>
            <div className="button-row">
              <LinkV2 className="button" href={`${R.leggi}?source=daily`}>{k.cta}</LinkV2>
              <LinkV2 className="button button-quiet" href={R.carta(g.carta.slug ?? g.carta.id)}>{f(k.significato, { carta: nome })}</LinkV2>
            </div>
            <InvitoNotifiche />
          </>
        )}
      </div>
    </section>
  );
}
