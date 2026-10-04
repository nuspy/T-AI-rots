"use client";

/* La biblioteca delle carte e la pagina di una carta, nella v2: l'immagine ha spazio per essere vista, poi la
 * porta verso una domanda (specifica v2, §14: ARTICOLO → CARTA → SIGNIFICATO → MAZZO → DOMANDA → LETTURA). I testi
 * delle carte arrivano dall'API nella lingua dei contenuti (italiano o inglese).
 *
 * Gli spazi pubblicitari (`Pubblicita`, spenti per default) stanno nei modelli: nella biblioteca fra i terzi della
 * griglia e in fondo, nella scheda dentro il testo e dopo la scheda. */

import { Fragment, useState } from "react";
import { elencaCarte, leggiCarta, type Carta } from "@/lib/api";
import { nomeCarta } from "@/lib/i18n/nomi";
import { f } from "@/v2/i18n";
import { ImmagineCarta } from "@/v2/componenti/carta";
import LinkV2 from "@/v2/componenti/link";
import { Pubblicita } from "@/v2/componenti/pubblicita";
import { P, linguaContenuti } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { inTerzi, type Posizione } from "@/v2/lib/pubblicita";
import { useCarica } from "@/v2/lib/usa";
import { DiarioNove } from "./blog";

const FILTRI = ["tutte", "maggiori", "bastoni", "coppe", "spade", "dischi"] as const;
const POSIZIONI_GRIGLIA: Posizione[] = ["terzo", "due_terzi", "fine"];

export const nomeDi = (c: Carta, lingua: string) =>
  (c.lang === linguaContenuti(lingua) && c.nome) || nomeCarta(c, lingua as Parameters<typeof nomeCarta>[1]);

export function Biblioteca() {
  const { t, lingua } = useLingua();
  const k = t.carte;
  const carte = useCarica(() => elencaCarte(linguaContenuti(lingua)), [lingua], { pubblico: true, iniziale: P.carte(lingua) });
  const [filtro, setFiltro] = useState<(typeof FILTRI)[number]>("tutte");
  const visibili = (carte.dati ?? []).filter((c) =>
    filtro === "tutte" ? true : filtro === "maggiori" ? c.arcano === "maggiore" : c.seme === filtro);
  return (
    <section className="band band-tight">
      <div className="chips" role="group" aria-label={k.filtri_aria} style={{ marginBottom: ".7rem" }}>
        {FILTRI.map((x) => (
          <button key={x} type="button" className="chip" aria-pressed={x === filtro} onClick={() => setFiltro(x)}>{k.filtri[x]}</button>
        ))}
      </div>
      {carte.errore && <p className="error">{carte.errore}</p>}
      {/* La griglia in tre parti, tagliate a fine riga, con gli spazi pubblicitari fra l'una e l'altra e in fondo
          (spenti, le tre parti si leggono come una griglia sola). */}
      {inTerzi(visibili).filter((parte) => parte.length > 0).map((parte, i, parti) => (
        <Fragment key={i}>
          <div className="cards-grid">
            {parte.map((c) => (
              <LinkV2 key={c.id} className="card-tile" href={R.carta(c.slug ?? c.id)}>
                <ImmagineCarta id={c.id} alt={nomeDi(c, lingua)} mazzo={null} />
                <span>{nomeDi(c, lingua)}</span>
                {c.arcano_label && <small>{c.arcano === "maggiore" ? c.numero_romano : c.seme_label}</small>}
              </LinkV2>
            ))}
          </div>
          <Pubblicita posizione={parti.length === 3 ? POSIZIONI_GRIGLIA[i] : "fine"} dentro />
        </Fragment>
      ))}
    </section>
  );
}

export function SchedaCarta({ id }: { id: string }) {
  const { t, lingua } = useLingua();
  const k = t.carte;
  const carta = useCarica(() => leggiCarta(id, linguaContenuti(lingua)), [id, lingua], { pubblico: true, iniziale: P.carta(id, lingua) });
  const tutte = useCarica(() => elencaCarte(linguaContenuti(lingua)), [lingua], { pubblico: true, iniziale: P.carte(lingua) });

  if (carta.errore) {
    return (
      <section className="band band-tight">
        <p className="section-intro">{k.non_trovata}</p>
        <LinkV2 className="button button-quiet" href={R.carte}>{k.torna}</LinkV2>
      </section>
    );
  }
  const c = carta.dati;
  if (!c) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const nome = nomeDi(c, lingua);
  const elenco = tutte.dati ?? [];
  const i = elenco.findIndex((x) => x.id === c.id);
  const prima = i > 0 ? elenco[i - 1] : null;
  const dopo = i >= 0 && i < elenco.length - 1 ? elenco[i + 1] : null;
  const corrispondenze = [
    c.lettera_ebraica && `${c.lettera_ebraica.nome} ${c.lettera_ebraica.glifo}`,
    c.percorso && f(k.sentiero, { n: c.percorso }) + (c.collega ? ` (${c.collega.join(" – ")})` : ""),
    c.sefira, c.elemento_label ?? c.elemento, c.astrologia,
  ].filter(Boolean);

  return (
    <>
      <section className="subhero subhero-compact">
        <p className="eyebrow">{f(k.carta_eyebrow, { arcano: c.arcano_label ?? (c.arcano === "maggiore" ? k.filtri.maggiori : c.seme_label ?? "") })}</p>
        <h1 className="display">{nome}</h1>
        {c.titolo_thoth && <p className="section-intro">{c.titolo_thoth}</p>}
      </section>
      <section className="band band-tight deck-layout" style={{ alignItems: "start" }}>
        <div style={{ maxWidth: 300, justifySelf: "center", width: "100%" }}>
          <ImmagineCarta id={c.id} alt={nome} mazzo={null} priorita classe="card-large" />
          <p className="small muted" style={{ marginTop: "1rem" }}>{c.parole_chiave.join(" · ")}</p>
        </div>
        <div>
          <p className="eyebrow">{k.carta_riflessione}</p>
          <h2 className="section-title">{f(k.carta_domanda, { carta: nome })}</h2>
          <p className="section-intro">{k.carta_nota}</p>
          <div className="button-row" style={{ margin: ".5rem 0 .85rem" }}>
            <LinkV2 className="button" href={`${R.leggi}?card=${encodeURIComponent(c.slug ?? c.id)}&source=card`}>{k.cta_leggi}</LinkV2>
            <LinkV2 className="button button-quiet" href={R.fisica}>{k.cta_fisica}</LinkV2>
          </div>

          <div className="prose-block">
            {c.dritto && (<><h3>{k.dritta}</h3><p>{c.dritto}</p></>)}
            {Object.entries(c.significati ?? {}).map(([chiave, v]) => (
              <div key={chiave}><h3>{k.livelli[chiave] ?? chiave}</h3><p>{v}</p></div>
            ))}
            {/* Spazi pubblicitari (spenti per default): a un terzo dopo i significati, a due terzi dopo rovesciata e
                ambiti, alla fine dopo la scheda, prima del diario. */}
            <Pubblicita posizione="terzo" dentro />
            {c.rovescio && (<><h3>{k.rovesciata}</h3><p className="small muted">{k.rovesciata_nota}</p><p>{c.rovescio}</p></>)}
            {Object.keys(c.ambiti ?? {}).length > 0 && (
              <>
                <h3>{k.ambiti_titolo}</h3>
                {Object.entries(c.ambiti ?? {}).map(([chiave, v]) => <p key={chiave}><b>{k.ambiti[chiave] ?? chiave}.</b> {v}</p>)}
              </>
            )}
            <Pubblicita posizione="due_terzi" dentro />
            <h3>{k.corrispondenze}</h3>
            <p className="small">{corrispondenze.join(" · ")}</p>
            {c.nota_crowley && (<><h3>{k.crowley}</h3><p>{c.nota_crowley}</p></>)}
          </div>

          <nav className="pager" aria-label={k.torna}>
            {prima ? <LinkV2 className="inline" href={R.carta(prima.slug ?? prima.id)} rel="prev">← {nomeDi(prima, lingua)}</LinkV2> : <span />}
            {dopo ? <LinkV2 className="inline" href={R.carta(dopo.slug ?? dopo.id)} rel="next">{nomeDi(dopo, lingua)} →</LinkV2> : <span />}
          </nav>
        </div>
      </section>
      <Pubblicita posizione="fine" />
      <DiarioNove contesto={{ carta: c.id }} />
    </>
  );
}
