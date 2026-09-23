"use client";

import { use, useCallback } from "react";
import Link from "next/link";
import { leggiCarta } from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useCarica } from "@/lib/usa";
import { Carta } from "../../componenti/carta";
import { Involucro } from "../../componenti/testata";
import stili from "../../pagine.module.css";

const LIVELLI: Record<string, string> = {
  essoterico: "Significato essoterico",
  psicologico: "Livello psicologico",
  iniziatico: "Livello iniziatico",
  ombra: "Ombra",
};

export default function PaginaCarta({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { t } = useLingua();
  const carta = useCarica(useCallback(() => leggiCarta(id), [id]), [id], { pubblico: true });
  const c = carta.dati;
  return (
    <Involucro pubblica titolo={c?.nome_it} sottotitolo={c ? `${c.nome_thoth}${c.titolo_thoth ? ` — ${c.titolo_thoth}` : ""}` : undefined}>
      {carta.errore && <p className={stili.errore}>{carta.errore}</p>}
      {c && (
        <div className={stili.cartaGrande}>
          <Carta carta={c} rivelata larghezza={250} />
          <div>
            <p className={stili.etichetta}>
              {[c.lettera_ebraica && `${c.lettera_ebraica.nome} ${c.lettera_ebraica.glifo} (${c.lettera_ebraica.valore})`,
                c.percorso && `sentiero ${c.percorso}${c.collega ? `: ${c.collega.join(" – ")}` : ""}`,
                c.sefira, c.elemento, c.astrologia].filter(Boolean).join(" · ")}
            </p>
            <p className={stili.nota}>{c.parole_chiave.join(" · ")}</p>
            <dl className={stili.livelli}>
              {Object.entries(c.significati ?? {}).map(([k, v]) => (
                <div key={k}><dt>{LIVELLI[k] ?? k}</dt><dd className="oracolo">{v}</dd></div>
              ))}
              <dt>{t.dritta}</dt><dd className="oracolo">{c.dritto}</dd>
              <dt>{t.rovesciata}</dt><dd className="oracolo">{c.rovescio}</dd>
              {Object.entries(c.ambiti ?? {}).map(([k, v]) => (
                <div key={k}><dt>{k}</dt><dd className="oracolo">{v}</dd></div>
              ))}
              {c.nota_crowley && <><dt>Crowley</dt><dd className="oracolo">{c.nota_crowley}</dd></>}
            </dl>
            <div className={stili.linea} style={{ marginTop: 20 }}>
              <Link href="/leggi" className="bottone">✦ {t.inizia}</Link>
              <Link href="/carte" className="bottone-secondario">{t.nav_carte}</Link>
            </div>
          </div>
        </div>
      )}
    </Involucro>
  );
}
