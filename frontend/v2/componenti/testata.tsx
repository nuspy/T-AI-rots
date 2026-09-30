"use client";

/* La testata della v2: marchio, cinque sezioni, lingua, accesso e l'invito a cominciare. Solo destinazioni della
 * v2 (specifica v2, §19). */

import { usePathname, useRouter } from "next/navigation";
import { ADMIN_URL, useSessione } from "@/lib/sessione";
import { LINGUE, comeLingua } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { R, senzaPrefisso } from "@/v2/lib/percorsi";
import LinkV2 from "./link";

/* Quale voce del menu accendere: ogni sezione possiede alcune pagine. */
const SEZIONI: { chiave: "leggi" | "mazzi" | "esplora" | "storia" | "negozio"; href: string; pagine: string[] }[] = [
  { chiave: "leggi", href: R.leggi, pagine: [R.leggi, R.fisica, R.giorno, R.prezzi] },
  { chiave: "mazzi", href: R.mazzi, pagine: [R.mazzi, R.carte, R.voto] },
  { chiave: "esplora", href: R.esplora, pagine: [R.esplora, R.blog, R.stese] },
  { chiave: "storia", href: R.storia, pagine: [R.storia, R.profilo] },
  { chiave: "negozio", href: R.negozio, pagine: [R.negozio] },
];

export function useEntra() {
  const sessione = useSessione();
  return () => sessione.entra(`${window.location.pathname}${window.location.search}`);
}

export function SelettoreLingua() {
  const { t, lingua, imposta, prefissoIt } = useLingua();
  const router = useRouter();
  const percorso = usePathname() ?? R.home;
  const cambia = (valore: string) => {
    const l = comeLingua(valore);
    if (!l) return;
    imposta(l);
    /* Un indirizzo `/it/v2/…` dice «italiano»: scegliendo un'altra lingua si toglie il prefisso. */
    if (prefissoIt && l !== "it") router.replace(`${senzaPrefisso(percorso)}${window.location.search}`);
  };
  return (
    <label className="lang-select">
      <span className="sr-only">{t.comune.aria_lingua}</span>
      <select value={lingua} onChange={(e) => cambia(e.target.value)}>
        {LINGUE.map((l) => <option key={l.codice} value={l.codice}>{l.nome}</option>)}
      </select>
    </label>
  );
}

export function Testata() {
  const { t } = useLingua();
  const sessione = useSessione();
  const entra = useEntra();
  const percorso = senzaPrefisso(usePathname() ?? R.home);
  const attiva = SEZIONI.find((s) => s.pagine.some((p) => percorso === p || percorso.startsWith(`${p}/`)))?.chiave;
  const nomi = {
    leggi: t.comune.nav_leggi, mazzi: t.comune.nav_mazzi, esplora: t.comune.nav_esplora,
    storia: t.comune.nav_storia, negozio: t.comune.nav_negozio,
  };

  return (
    <header className="site-header">
      <LinkV2 className="brand" href={R.home} aria-label={t.comune.aria_home}>
        <span className="brand-mark" aria-hidden="true">✦</span>
        <span>TAROTS <em>chat</em></span>
      </LinkV2>
      <nav className="primary-nav" aria-label={t.comune.aria_nav}>
        {SEZIONI.map((s) => (
          <LinkV2 key={s.chiave} href={s.href} aria-current={attiva === s.chiave ? "page" : undefined}>
            {nomi[s.chiave]}
          </LinkV2>
        ))}
      </nav>
      <div className="header-actions">
        <SelettoreLingua />
        {sessione.autenticata ? (
          <>
            {sessione.admin && ADMIN_URL && (
              <a className="text-link hide-sm" href={ADMIN_URL}>{t.comune.admin}</a>
            )}
            <LinkV2 className="text-link hide-sm" href={R.profilo}>{sessione.nome ?? t.comune.profilo}</LinkV2>
          </>
        ) : (
          sessione.pronta && <button type="button" className="text-link" onClick={entra}>{t.comune.entra}</button>
        )}
        <LinkV2 className="button button-brass button-small" href={R.leggi} data-an="cta_testata">
          {t.comune.inizia_lettura}
        </LinkV2>
      </div>
    </header>
  );
}
