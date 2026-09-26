"use client";

/* La testata e l'involucro delle pagine, sul modello di Personalities:
 * voci in alto su schermo largo, in basso sul telefono, dove stanno sotto il
 * pollice.
 *
 * Le voci sono più di cinque, e la barra in basso non ne regge di più (i pollici
 * hanno un limite): quattro stanno sempre in vista, le altre dietro «Altro», che sul
 * telefono si apre sopra la barra e sul computer sotto la testata. */

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LINGUE, comeLingua } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { ADMIN_URL, AUTH_DISATTIVATA, useSessione } from "@/lib/sessione";
import stili from "./testata.module.css";

interface Voce {
  href: string;
  etichetta: string;
  segno: string;
}

/* «Altro»: le voci che non stanno nella barra. Aperto per una pagina: cambiando
 * pagina si richiude da solo, senza un effetto che lo faccia. */
function MenuAltro({
  voci, etichetta, titolo, percorso, attiva, classeBottone,
}: {
  voci: Voce[];
  etichetta: string;
  titolo: string;
  percorso: string;
  attiva: (href: string) => boolean;
  classeBottone: string;
}) {
  const [apertoSu, setApertoSu] = useState<string | null>(null);
  const aperto = apertoSu === percorso;
  const radice = useRef<HTMLDivElement>(null);
  const bottone = useRef<HTMLButtonElement>(null);
  const contiene = voci.some((v) => attiva(v.href));

  useEffect(() => {
    if (!aperto) return;
    const fuori = (e: PointerEvent) => {
      if (radice.current && !radice.current.contains(e.target as Node)) setApertoSu(null);
    };
    const tasti = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setApertoSu(null);
        bottone.current?.focus();
      }
    };
    document.addEventListener("pointerdown", fuori);
    document.addEventListener("keydown", tasti);
    return () => {
      document.removeEventListener("pointerdown", fuori);
      document.removeEventListener("keydown", tasti);
    };
  }, [aperto]);

  return (
    <div ref={radice} className={stili.altroWrap}>
      <button
        ref={bottone}
        className={`${classeBottone} ${contiene ? stili.altroAttivo : ""}`}
        aria-expanded={aperto}
        aria-controls="menu-altro"
        onClick={() => setApertoSu(aperto ? null : percorso)}
      >
        <span aria-hidden="true" className={stili.segno}>⋯</span>
        {etichetta}
      </button>
      {aperto && (
        <div id="menu-altro" className={stili.altroPannello} role="group" aria-label={titolo}>
          {voci.map((v) => (
            <Link key={v.href} href={v.href} className={attiva(v.href) ? stili.altroVoceAttiva : stili.altroVoce}
              aria-current={attiva(v.href) ? "page" : undefined}>
              <span aria-hidden="true">{v.segno}</span>
              {v.etichetta}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function Testata() {
  const { t, lingua, imposta } = useLingua();
  const sessione = useSessione();
  const percorso = usePathname();
  const V = {
    leggi: { href: "/leggi", etichetta: t.nav_leggi, segno: "✦" },
    letture: { href: "/letture", etichetta: t.nav_letture, segno: "☰" },
    carte: { href: "/carte", etichetta: t.nav_carte, segno: "◈" },
    stese: { href: "/stese", etichetta: t.nav_stese, segno: "▦" },
    giorno: { href: "/carta-del-giorno", etichetta: t.nav_giorno, segno: "☉" },
    mazzo: { href: "/mazzo", etichetta: t.nav_mazzo, segno: "❖" },
    blog: { href: "/blog", etichetta: t.nav_blog, segno: "✎" },
    piano: { href: "/piano", etichetta: t.nav_piano, segno: "◇" },
  };
  /* Chi non ha un account non ha «Le mie letture»: al suo posto il blog, che è la porta d'ingresso
   * dei contenuti. Per chi è registrato il blog sta sotto «Altro». */
  const voci: Voce[] = sessione.autenticata ? [V.leggi, V.letture, V.carte, V.stese] : [V.leggi, V.carte, V.stese, V.blog];
  const altre: Voce[] = sessione.autenticata ? [V.giorno, V.blog, V.mazzo, V.piano] : [V.giorno, V.mazzo, V.piano];
  const attiva = (href: string) => percorso === href || percorso.startsWith(`${href}/`);

  return (
    <>
      <header className={stili.testata}>
        <Link href="/" className={stili.marchio}>
          T<span>·</span>AI<span>·</span>rots
        </Link>
        <nav className={stili.voci} aria-label={t.aria_sezioni}>
          {voci.map((v) => (
            <Link key={v.href} href={v.href} className={attiva(v.href) ? stili.voceAttiva : stili.voce}
              aria-current={attiva(v.href) ? "page" : undefined}>
              {v.etichetta}
            </Link>
          ))}
          <MenuAltro voci={altre} etichetta={t.nav_altro} titolo={t.nav_altro_titolo} percorso={percorso}
            attiva={attiva} classeBottone={stili.voce} />
        </nav>
        <div className={stili.azioni}>
          <select
            className={stili.lingua}
            value={lingua}
            onChange={(e) => {
              const scelta = comeLingua(e.target.value);
              if (scelta) imposta(scelta);
            }}
            aria-label={t.aria_lingua}
          >
            {LINGUE.map((l) => (
              <option key={l.codice} value={l.codice} lang={l.codice}>{l.nome}</option>
            ))}
          </select>
          {sessione.autenticata ? (
            <>
              {sessione.admin && (
                /* La console è un'altra applicazione: un collegamento vero, non `Link`. */
                <a href={ADMIN_URL} className={stili.voce}>{t.nav_admin}</a>
              )}
              <Link href="/profilo" className={stili.voce}>{t.nav_profilo}</Link>
              {!AUTH_DISATTIVATA && (
                <button className={stili.esci} onClick={sessione.esci}>{t.esci}</button>
              )}
            </>
          ) : (
            sessione.pronta && (
              <>
                <button className={stili.esci} onClick={() => sessione.entra(percorso)}>{t.entra}</button>
                <button className="bottone" onClick={sessione.registrati}>{t.registrati}</button>
              </>
            )
          )}
        </div>
      </header>
      <nav className={stili.barraBassa} aria-label={t.aria_sezioni}>
        {voci.map((v) => (
          <Link key={v.href} href={v.href} className={attiva(v.href) ? stili.schedaAttiva : stili.scheda}>
            <span aria-hidden="true" className={stili.segno}>{v.segno}</span>
            {v.etichetta}
          </Link>
        ))}
        <MenuAltro voci={altre} etichetta={t.nav_altro} titolo={t.nav_altro_titolo} percorso={percorso}
          attiva={attiva} classeBottone={stili.scheda} />
      </nav>
    </>
  );
}

/** L'involucro delle pagine: testata, accesso richiesto, titolo. */
export function Involucro({
  titolo,
  sottotitolo,
  pubblica = false,
  larga = false,
  children,
}: {
  titolo?: string;
  sottotitolo?: string;
  pubblica?: boolean;
  larga?: boolean;
  children: React.ReactNode;
}) {
  const sessione = useSessione();
  const { t } = useLingua();
  const percorso = usePathname();

  let corpo: React.ReactNode = children;
  if (!pubblica && !sessione.pronta) {
    corpo = <p className={stili.attesa}>{t.verifica_sessione}</p>;
  } else if (!pubblica && !sessione.autenticata) {
    corpo = (
      <div className={`pannello ${stili.soglia}`}>
        <p className="oracolo">{t.serve_account}</p>
        <div className={stili.sogliaAzioni}>
          <button className="bottone" onClick={() => sessione.entra(percorso)}>{t.entra}</button>
          <button className="bottone-secondario" onClick={sessione.registrati}>{t.registrati}</button>
        </div>
      </div>
    );
  }

  return (
    <div className={stili.pagina}>
      <Testata />
      <main className={larga ? stili.contenutoLargo : stili.contenuto}>
        {titolo && <h1 className={stili.titolo}>{titolo}</h1>}
        {sottotitolo && <p className={stili.sottotitolo}>{sottotitolo}</p>}
        {corpo}
      </main>
    </div>
  );
}
