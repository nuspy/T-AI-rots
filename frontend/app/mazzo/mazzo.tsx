"use client";

/* La pagina del mazzo: come una scheda prodotto di un oggetto da collezione. È
 * un'anteprima — il mazzo è in preparazione — e lo dice: niente prezzo inventato né
 * pulsante d'acquisto che non compra. La «foto» in testa è una scena composta con le
 * carte vere del mazzo; se in `public/mazzo/foto-mazzo.webp` c'è una fotografia vera
 * (o generata), la sostituisce. */

import { useEffect, useState } from "react";
import Link from "next/link";
import type { Carta as TipoCarta } from "@/lib/api";
import { nomeCarta } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { ESTENSIONE } from "../componenti/carta";
import { Involucro } from "../componenti/testata";
import stili from "./mazzo.module.css";

const FOTO = "/mazzo/foto-mazzo.webp";

/* La scena: la scatola con il dorso sul coperchio, il mazzo appoggiato e cinque carte
 * aperte a ventaglio, su velluto notte con un cono di luce. */
function Scena() {
  /* La fotografia si mostra solo se esiste: si controlla dopo l'idratazione. Un `onError`
   * sull'immagine scritta dal server scatterebbe prima che React lo colleghi, e resterebbe
   * l'icona dell'immagine rotta. */
  const [foto, setFoto] = useState(false);
  useEffect(() => {
    const prova = new window.Image();
    prova.onload = () => setFoto(true);
    prova.src = FOTO;
  }, []);
  const ventaglio = ["maj-17", "maj-19", "maj-21", "maj-02", "maj-11"];
  return (
    <div className={stili.scena} role="img" aria-label="Il mazzo di TAROTS chat: scatola, mazzo e carte aperte a ventaglio">
      <div className={stili.luce} aria-hidden="true" />
      <div className={stili.scatola} aria-hidden="true">
        <div className={stili.coperchio}>
          <span className={stili.filo} />
          <span className={stili.titoloScatola}>TAROTS <em>chat</em></span>
          {/* eslint-disable-next-line @next/next/no-img-element -- il dorso vero, sul coperchio */}
          <img src={`/cards/dorso.${ESTENSIONE}`} alt="" width={180} height={320} />
          <span className={stili.sottoScatola}>Tarocco di Thoth</span>
        </div>
      </div>
      <div className={stili.mazzoImpilato} aria-hidden="true">
        {[0, 1, 2, 3, 4, 5].map((i) => (
          // eslint-disable-next-line @next/next/no-img-element -- decorativa
          <img key={i} src={`/cards/dorso.${ESTENSIONE}`} alt="" width={120} height={213}
            style={{ transform: `translate(${i * 1.6}px, ${-i * 2.4}px)` }} />
        ))}
      </div>
      <div className={stili.ventaglio} aria-hidden="true">
        {ventaglio.map((id, i) => (
          // eslint-disable-next-line @next/next/no-img-element -- decorativa
          <img key={id} src={`/cards/${id}.${ESTENSIONE}`} alt="" width={120} height={213} loading="lazy"
            style={{ ["--giro" as string]: `${-26 + i * 13}deg`, ["--ordine" as string]: i }} />
        ))}
      </div>
      <span className={stili.polvere} aria-hidden="true" />
      {foto && (
        // eslint-disable-next-line @next/next/no-img-element -- la fotografia, se c'è, copre la scena
        <img className={stili.foto} src={FOTO} alt="" />
      )}
    </div>
  );
}

export function PaginaMazzo({ carte }: { carte: TipoCarta[] }) {
  const { t, lingua } = useLingua();
  return (
    <Involucro pubblica larga>
      <section className={stili.eroe} aria-labelledby="mazzo-titolo">
        <div className={stili.eroeTesto}>
          <p className={stili.etichetta}>{t.mazzo_anteprima}</p>
          <h1 id="mazzo-titolo" className={stili.titolo}>{t.mazzo_titolo}</h1>
          <p className={`oracolo ${stili.sottotitolo}`}>{t.mazzo_sottotitolo}</p>
          <p className={stili.avviso}>{t.mazzo_cta_testo}</p>
          <div className={stili.azioni}>
            <button className={`bottone ${stili.cta}`} disabled aria-disabled="true">❖ {t.mazzo_cta}</button>
            <Link href="/leggi" className={`bottone-secondario ${stili.cta}`}>✦ {t.mazzo_prova}</Link>
          </div>
        </div>
        <Scena />
      </section>

      <section className={stili.sezione} aria-labelledby="mazzo-punti">
        <h2 id="mazzo-punti">{t.mazzo_punti_titolo}</h2>
        <ul className={stili.punti}>
          {t.mazzo_punti.map(([titolo, testo], i) => (
            <li key={titolo} className={`pannello ${stili.punto}`}>
              <span className={stili.numeroPunto} aria-hidden="true">{["I", "II", "III", "IV"][i]}</span>
              <strong>{titolo}</strong>
              <p>{testo}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className={stili.sezione} aria-labelledby="mazzo-carte">
        <h2 id="mazzo-carte">{t.mazzo_carte_titolo}</h2>
        <ul className={stili.vetrina}>
          {carte.map((c) => (
            <li key={c.id}>
              <Link href={`/carte/${c.id}`} className={stili.cartaVetrina}>
                {/* eslint-disable-next-line @next/next/no-img-element -- la carta vera */}
                <img src={`/cards/${c.id}.${ESTENSIONE}`} alt={nomeCarta(c, lingua)} width={360} height={640}
                  loading="lazy" />
                <span>{nomeCarta(c, lingua)}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section className={`${stili.sezione} ${stili.dorso}`} aria-labelledby="mazzo-dorso">
        {/* eslint-disable-next-line @next/next/no-img-element -- il dorso vero */}
        <img src={`/cards/dorso.${ESTENSIONE}`} alt="" width={360} height={640} loading="lazy" />
        <div>
          <h2 id="mazzo-dorso">{t.mazzo_dorso_titolo}</h2>
          <p className="oracolo">{t.mazzo_dorso_testo}</p>
          <div className={stili.azioni}>
            <Link href="/carte" className={`bottone-secondario ${stili.cta}`}>{t.nav_carte}</Link>
            <Link href="/stese" className={`bottone-secondario ${stili.cta}`}>{t.nav_stese}</Link>
          </div>
        </div>
      </section>
    </Involucro>
  );
}
