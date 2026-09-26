"use client";

/* La pagina di una stesa: schema, posizioni, regole, coppie da leggere insieme. */

import Link from "next/link";
import type { Stesa } from "@/lib/api";
import type { ArticoloBreve } from "@/lib/blog";
import { nomePosizione, nomeStesa } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { SchedaArticolo } from "../../blog/componenti/elementi";
import stiliBlog from "../../blog/blog.module.css";
import { BannerMazzo } from "../../componenti/banner-mazzo";
import { Involucro } from "../../componenti/testata";
import { COLORE_SOGGETTO, Tavolo } from "../../leggi/tavolo";
import { TesseraStesa } from "../elenco";
import stili from "../stese.module.css";

export function SchedaStesa({ stesa, altre, articoli = [] }: { stesa: Stesa; altre: Stesa[]; articoli?: ArticoloBreve[] }) {
  const { t, lingua } = useLingua();
  const tipo =
    stesa.categoria === "compatibilita" ? t.tipo_compat : stesa.categoria === "coppia" ? t.tipo_coppia : t.stese_standard_titolo;
  const nomeDi = (n: number) => {
    const p = stesa.posizioni.find((x) => x.n === n);
    return p ? nomePosizione(p, lingua) : String(n);
  };

  return (
    <Involucro pubblica larga titolo={nomeStesa(stesa, lingua)} sottotitolo={undefined}>
      <div className={stili.testata}>
        <span className={stili.pillola}>{tipo}</span>
        {stesa.stile && <span className={stili.pillola}>{t[`stile_${stesa.stile}` as const]}</span>}
        <span className={stili.pillola}>
          {t.stesa_n_carte(stesa.posizioni.length)} · {stesa.mazzo === "maggiori" ? t.maggiori : t.completo}
        </span>
      </div>
      <p className={`oracolo ${stili.lead}`}>{stesa.descrizione}</p>

      <div className={stili.diagramma} role="img" aria-label={t.stesa_diagramma}>
        <Tavolo stesa={stesa} posate={[]} prossima={null} rivelazioneInCorso={false} evidenzia={null}
          nomePartner={undefined} />
      </div>

      <h2 className={stili.sottotitolo}>{t.stesa_posizioni}</h2>
      <ol className={stili.posizioni}>
        {stesa.posizioni.map((p) => (
          <li key={p.n} className={`pannello ${stili.posizione}`}
            style={p.soggetto ? ({ "--soggetto": COLORE_SOGGETTO[p.soggetto] } as React.CSSProperties) : undefined}>
            <span className={stili.numero} aria-label={t.stesa_posizione_n(p.n)}>{p.n}</span>
            <span className={stili.posizioneNome}>{nomePosizione(p, lingua)}</span>
            <p>{p.significato}</p>
            <p className={stili.guida}>{p.domanda}</p>
          </li>
        ))}
      </ol>

      {stesa.regole.length > 0 && (
        <>
          <h2 className={stili.sottotitolo}>{t.stesa_regole}</h2>
          <ul className={stili.regole}>
            {stesa.regole.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </>
      )}

      {stesa.coppie.length > 0 && (
        <ul className={stili.coppie} aria-label={t.stesa_regole}>
          {stesa.coppie.map(([a, b, testo]) => (
            <li key={`${a}-${b}`}>
              <strong>{nomeDi(a)} ↔ {nomeDi(b)}</strong>
              {testo}
            </li>
          ))}
        </ul>
      )}

      {stesa.origine && (
        <>
          <h2 className={stili.sottotitolo}>{t.stesa_origine}</h2>
          <p className="oracolo">{stesa.origine}</p>
        </>
      )}

      <div className={stili.azioni}>
        <Link href={`/leggi?stesa=${stesa.id}`} className="bottone">✦ {t.stesa_fai}</Link>
        <Link href="/stese" className="bottone-secondario">{t.stesa_tutte}</Link>
      </div>

      {articoli.length > 0 && (
        <section className={stiliBlog.blocco} style={{ marginTop: 36 }} aria-label={t.blog_articoli_su_stesa}>
          <h2>{t.blog_articoli_su_stesa}</h2>
          <div className={stiliBlog.griglia}>
            {articoli.map((a) => <SchedaArticolo key={a.slug} articolo={a} />)}
          </div>
        </section>
      )}

      {altre.length > 0 && (
        <>
          <h2 className={stili.sottotitolo}>{t.stesa_altre_categoria}</h2>
          <div className={stili.griglia}>
            {altre.map((s) => <TesseraStesa key={s.id} stesa={s} />)}
          </div>
        </>
      )}
      <BannerMazzo />
    </Involucro>
  );
}
