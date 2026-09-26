"use client";

/* La scheda di una carta: l'immagine, le attribuzioni, i significati.
 *
 * È la porta d'ingresso di chi cerca «The Star tarot card meaning»: il testo si articola in sezioni con un titolo
 * che è una domanda o una parola chiave (che cosa significa, rovesciata, in amore e lavoro, corrispondenze), e si
 * chiude con le domande frequenti — le stesse che leggono i motori di ricerca come dati strutturati.
 * La lingua dei testi è quella dell'indirizzo (`lingua`), non quella scelta per le etichette. */

import Link from "@/app/componenti/link";
import type { Carta as TipoCarta } from "@/lib/api";
import type { ArticoloBreve } from "@/lib/blog";
import { useLingua } from "@/lib/lingua";
import type { LinguaPubblica } from "@/lib/percorsi";
import { CARTA, seoCarta } from "@/lib/seo-testi";
import { SchedaArticolo } from "../../blog/componenti/elementi";
import stiliBlog from "../../blog/blog.module.css";
import { BannerMazzo } from "../../componenti/banner-mazzo";
import { Carta } from "../../componenti/carta";
import { Involucro } from "../../componenti/testata";
import stili from "../../pagine.module.css";

export interface Vicina {
  slug: string;
  nome: string;
}

export function SchedaCarta({
  carta: c, articoli = [], lingua, precedente, successiva,
}: {
  carta: TipoCarta;
  articoli?: ArticoloBreve[];
  lingua: LinguaPubblica;
  precedente?: Vicina | null;
  successiva?: Vicina | null;
}) {
  const { t } = useLingua();
  const s = seoCarta(c);
  const livelli = CARTA.livelli(lingua);
  const ambiti = CARTA.ambiti(lingua);
  const domande = CARTA.domande(lingua, s);
  const attribuzioniGrezze = [
    c.lettera_ebraica && `${c.lettera_ebraica.nome} ${c.lettera_ebraica.glifo} (${c.lettera_ebraica.valore})`,
    c.percorso && `${t.sentiero} ${c.percorso}${c.collega ? `: ${c.collega.join(" – ")}` : ""}`,
    c.sefira, c.elemento_label ?? c.elemento, c.astrologia,
  ].filter(Boolean).join(" · ");

  return (
    <Involucro pubblica titolo={CARTA.h1(lingua, s)} sottotitolo={CARTA.sottotitolo(lingua, s)}>
      <div className={stili.cartaGrande}>
        <Carta carta={c} rivelata larghezza={250} />
        <article className={stili.articoloCarta}>
          <p className={`oracolo ${stili.lead}`}>{CARTA.intro(lingua, s)}</p>
          <p className={stili.nota}>{c.parole_chiave.join(" · ")}</p>

          <section className={stili.sezioneCarta} aria-labelledby="significato">
            <h2 id="significato">{CARTA.h2Significato(lingua, s)}</h2>
            <p className="oracolo">{c.dritto}</p>
            {Object.entries(c.significati ?? {}).map(([k, v]) => (
              <div key={k}>
                <h3>{livelli[k] ?? k}</h3>
                <p className="oracolo">{v}</p>
              </div>
            ))}
          </section>

          {c.rovescio && (
            <section className={stili.sezioneCarta} aria-labelledby="rovescia">
              <h2 id="rovescia">{CARTA.h2Rovescia(lingua, s)}</h2>
              <p className={stili.nota}>{CARTA.notaRovescia(lingua)}</p>
              <p className="oracolo">{c.rovescio}</p>
            </section>
          )}

          {Object.keys(c.ambiti ?? {}).length > 0 && (
            <section className={stili.sezioneCarta} aria-labelledby="ambiti">
              <h2 id="ambiti">{CARTA.h2Ambiti(lingua, s)}</h2>
              {Object.entries(c.ambiti ?? {}).map(([k, v]) => (
                <div key={k}>
                  <h3>{ambiti[k] ?? k}</h3>
                  <p className="oracolo">{v}</p>
                </div>
              ))}
            </section>
          )}

          <section className={stili.sezioneCarta} aria-labelledby="corrispondenze">
            <h2 id="corrispondenze">{CARTA.h2Corrispondenze(lingua, s)}</h2>
            <p className={stili.etichetta}>{attribuzioniGrezze}</p>
          </section>

          {c.nota_crowley && (
            <section className={stili.sezioneCarta} aria-labelledby="crowley">
              <h2 id="crowley">{CARTA.h2Crowley(lingua, s)}</h2>
              <p className="oracolo">{c.nota_crowley}</p>
            </section>
          )}

          {domande.length > 0 && (
            <section className={stili.sezioneCarta} aria-labelledby="domande">
              <h2 id="domande">{CARTA.h2Domande(lingua)}</h2>
              <div className={stili.domande}>
                {domande.map((d) => (
                  <details key={d.d}>
                    <summary>{d.d}</summary>
                    <p>{d.r}</p>
                  </details>
                ))}
              </div>
            </section>
          )}

          <div className={stili.linea} style={{ marginTop: 20 }}>
            <Link href="/leggi" className="bottone">✦ {CARTA.cta(lingua, s)}</Link>
            <Link href="/carte" className="bottone-secondario">{t.nav_carte}</Link>
          </div>
        </article>
      </div>

      {(precedente || successiva) && (
        <nav className={stili.vicine} aria-label={t.nav_carte}>
          {precedente ? (
            <Link href={`/carte/${precedente.slug}`} rel="prev">← {CARTA.precedente(lingua)}: {precedente.nome}</Link>
          ) : <span />}
          {successiva ? (
            <Link href={`/carte/${successiva.slug}`} rel="next">{CARTA.successiva(lingua)}: {successiva.nome} →</Link>
          ) : <span />}
        </nav>
      )}

      {articoli.length > 0 && (
        <section className={stiliBlog.blocco} style={{ marginTop: 36 }} aria-label={t.blog_articoli_su_carta}>
          <h2>{t.blog_articoli_su_carta}</h2>
          <div className={stiliBlog.griglia}>
            {articoli.map((a) => <SchedaArticolo key={a.slug} articolo={a} />)}
          </div>
        </section>
      )}
      <BannerMazzo />
    </Involucro>
  );
}
