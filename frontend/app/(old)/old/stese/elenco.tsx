"use client";

/* L'elenco pubblico delle stese: le classiche, poi quelle di compatibilità e di
 * coppia, queste per stile (tradizionale, moderna, di tendenza). */

import Link from "@/app/(old)/old/componenti/link";
import type { Categoria, Stesa, Stile } from "@/lib/api";
import { nomeStesa } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import type { LinguaPubblica } from "@/lib/percorsi";
import { STESE } from "@/lib/seo-testi";
import { BannerMazzo } from "../componenti/banner-mazzo";
import { MiniaturaStesa } from "../componenti/miniatura-stesa";
import { Involucro } from "../componenti/testata";
import stili from "./stese.module.css";

const ORDINE_STILI: Stile[] = ["tradizionale", "moderna", "tendenza"];

export function TesseraStesa({ stesa }: { stesa: Stesa }) {
  const { t, lingua } = useLingua();
  return (
    <Link href={`/stese/${stesa.slug ?? stesa.id}`} className={`pannello ${stili.tessera}`}>
      <MiniaturaStesa stesa={stesa} className={stili.miniatura} />
      <strong className={stili.nome}>{stesa.lang ? stesa.nome : nomeStesa(stesa, lingua)}</strong>
      <span className={stili.meta}>
        {t.stesa_n_carte(stesa.posizioni.length)} · {stesa.mazzo === "maggiori" ? t.maggiori : t.completo}
      </span>
      <p className={stili.descrizione}>{stesa.descrizione}</p>
    </Link>
  );
}

export function ElencoStese({ stese, lingua }: { stese: Stesa[]; lingua: LinguaPubblica }) {
  const { t } = useLingua();
  const per = (c: Categoria) => stese.filter((s) => s.categoria === c);
  const perStile = (c: Categoria) =>
    ORDINE_STILI.map((stile) => ({ stile, elenco: per(c).filter((s) => s.stile === stile) })).filter((g) => g.elenco.length);

  const gruppoSpeciale = (categoria: Categoria, titolo: string, descrizione: string) => (
    <section className={stili.sezione} aria-labelledby={`stese-${categoria}`}>
      <h2 id={`stese-${categoria}`}>{titolo}</h2>
      <p className={stili.introSezione}>{descrizione}</p>
      {perStile(categoria).map(({ stile, elenco }) => (
        <div key={stile}>
          <h3 className={stili.stile}>
            {t[`stile_${stile}` as const]}
            <span>{t[`stile_${stile}_desc` as const]}</span>
          </h3>
          <div className={stili.griglia}>
            {elenco.map((s) => <TesseraStesa key={s.id} stesa={s} />)}
          </div>
        </div>
      ))}
    </section>
  );

  return (
    <Involucro pubblica titolo={STESE.h1(lingua)} sottotitolo={STESE.intro(lingua)}>
      <section className={stili.sezione} aria-labelledby="stese-standard">
        <h2 id="stese-standard">{t.stese_standard_titolo}</h2>
        <p className={stili.introSezione}>{t.stese_standard_testo}</p>
        <div className={stili.griglia}>
          {per("standard").map((s) => <TesseraStesa key={s.id} stesa={s} />)}
        </div>
      </section>
      {gruppoSpeciale("compatibilita", t.tipo_compat, t.tipo_compat_desc)}
      {gruppoSpeciale("coppia", t.tipo_coppia, `${t.tipo_coppia_desc} ${t.stese_speciali_testo}`)}
      <BannerMazzo />
    </Involucro>
  );
}
