"use client";

/* La testata e l'involucro delle pagine, sul modello di Personalities:
 * voci in alto su schermo largo, in basso sul telefono, dove stanno sotto il
 * pollice. */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLingua } from "@/lib/lingua";
import { AUTH_DISATTIVATA, useSessione } from "@/lib/sessione";
import stili from "./testata.module.css";

export function Testata() {
  const { t, cambia } = useLingua();
  const sessione = useSessione();
  const percorso = usePathname();
  const voci = [
    { href: "/leggi", etichetta: t.nav_leggi, segno: "✦" },
    { href: "/letture", etichetta: t.nav_letture, segno: "☰" },
    { href: "/carta-del-giorno", etichetta: t.nav_giorno, segno: "☉" },
    { href: "/carte", etichetta: t.nav_carte, segno: "◈" },
    { href: "/piano", etichetta: t.nav_piano, segno: "◇" },
  ];
  const attiva = (href: string) => percorso === href || percorso.startsWith(`${href}/`);

  return (
    <>
      <header className={stili.testata}>
        <Link href="/" className={stili.marchio}>
          T<span>·</span>AI<span>·</span>rots
        </Link>
        <nav className={stili.voci} aria-label="Sezioni">
          {voci.map((v) => (
            <Link key={v.href} href={v.href} className={attiva(v.href) ? stili.voceAttiva : stili.voce}
              aria-current={attiva(v.href) ? "page" : undefined}>
              {v.etichetta}
            </Link>
          ))}
        </nav>
        <div className={stili.azioni}>
          <button className={stili.lingua} onClick={cambia} aria-label="Lingua">{t.lingua}</button>
          {sessione.autenticata ? (
            <>
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
      <nav className={stili.barraBassa} aria-label="Sezioni">
        {voci.map((v) => (
          <Link key={v.href} href={v.href} className={attiva(v.href) ? stili.schedaAttiva : stili.scheda}>
            <span aria-hidden="true" className={stili.segno}>{v.segno}</span>
            {v.etichetta}
          </Link>
        ))}
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
