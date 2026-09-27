"use client";

/* Le mattonelle di una stesa (o di una categoria di letture speciali) in home: solo il titolo e lo schema, senza
 * descrizione a vista — la descrizione sta nel dialogo che si apre al clic, con un collegamento a «maggiori
 * dettagli» verso la pagina vera. Meno testo in home, la stessa informazione a un clic di distanza. */

import { useState } from "react";
import type { Stesa } from "@/lib/api";
import { nomeStesa } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { MiniaturaStesa } from "./miniatura-stesa";
import { Modale } from "./modale";
import Link from "./link";
import stili from "./mattonella-lettura.module.css";

export function MattonellaStesa({ stesa }: { stesa: Stesa }) {
  const { t, lingua } = useLingua();
  const [aperta, setAperta] = useState(false);
  const nome = nomeStesa(stesa, lingua);

  return (
    <>
      <button type="button" className={`pannello ${stili.mattonella}`} onClick={() => setAperta(true)}>
        <MiniaturaStesa stesa={stesa} className={stili.miniatura} />
        <strong>{nome}</strong>
      </button>
      <Modale aperta={aperta} titolo={nome} onChiudi={() => setAperta(false)}>
        <p className={stili.descrizione}>{stesa.descrizione}</p>
        <div className={stili.azioni}>
          <Link href={`/stese/${stesa.slug ?? stesa.id}`} className="bottone">{t.stesa_dettagli}</Link>
          <button type="button" className="bottone-secondario" onClick={() => setAperta(false)}>{t.chiudi}</button>
        </div>
      </Modale>
    </>
  );
}

/** Una categoria di letture speciali (compatibilità, coppia): non una singola stesa, ma una famiglia. «Maggiori
 *  dettagli» qui apre direttamente la lettura, perché non esiste una pagina di dettaglio per la categoria. */
export function MattonellaCategoria({
  simbolo, titolo, descrizione, href,
}: {
  simbolo: string;
  titolo: string;
  descrizione: string;
  href: string;
}) {
  const { t } = useLingua();
  const [aperta, setAperta] = useState(false);

  return (
    <>
      <button type="button" className={`pannello ${stili.mattonella}`} onClick={() => setAperta(true)}>
        <span className={stili.simbolo} aria-hidden="true">{simbolo}</span>
        <strong>{titolo}</strong>
      </button>
      <Modale aperta={aperta} titolo={titolo} onChiudi={() => setAperta(false)}>
        <p className={stili.descrizione}>{descrizione}</p>
        <div className={stili.azioni}>
          <Link href={href} className="bottone">✦ {t.inizia_speciale}</Link>
          <button type="button" className="bottone-secondario" onClick={() => setAperta(false)}>{t.chiudi}</button>
        </div>
      </Modale>
    </>
  );
}
