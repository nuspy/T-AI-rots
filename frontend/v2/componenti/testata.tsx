"use client";

/* La testata della v2: marchio, cinque sezioni (Shop compreso), poi a destra il carrello, la lingua, i crediti col
 * saldo (portano all'acquisto), il profilo e l'invito a cominciare. Carrello, crediti e profilo sono icone con una
 * scritta piccola sotto e il suggerimento al passaggio: meno spazio, sempre leggibili, mai solo al passaggio del
 * mouse (la scritta resta visibile, anche sul telefono). Solo destinazioni della v2 (specifica v2, §19). */

import { usePathname, useRouter } from "next/navigation";
import { ADMIN_URL, useSessione } from "@/lib/sessione";
import { LINGUE, comeLingua, f, plurale } from "@/v2/i18n";
import { useCarrello } from "@/v2/lib/carrello";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2, senzaPrefisso } from "@/v2/lib/percorsi";
import LinkV2 from "./link";
import { useConto } from "@/v2/lib/dati";

/* Icone a tratto, 24×24, colore del testo: nessuna libreria per quattro disegni. */
const ICONE = {
  carrello: "M3 4h2l2.2 10.2a1.5 1.5 0 0 0 1.5 1.2h8.6a1.5 1.5 0 0 0 1.5-1.1L21 8H6.2M9.5 20a1 1 0 1 0 0-.01M17.5 20a1 1 0 1 0 0-.01",
  crediti: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM12 7.5l1.3 2.9 3.2.3-2.4 2.1.7 3.1L12 14.3l-2.8 1.6.7-3.1-2.4-2.1 3.2-.3Z",
  profilo: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4.5 20.5c.9-3.6 3.9-5.5 7.5-5.5s6.6 1.9 7.5 5.5",
  entra: "M10 17l5-5-5-5M15 12H3M14 4h5a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-5",
} as const;

function Icona({ nome }: { nome: keyof typeof ICONE }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={ICONE[nome]} />
    </svg>
  );
}

/* Quale voce del menu accendere: ogni sezione possiede alcune pagine. */
const SEZIONI: { chiave: "leggi" | "mazzi" | "esplora" | "storia" | "negozio"; href: string; pagine: string[] }[] = [
  { chiave: "leggi", href: R.leggi, pagine: [R.leggi, R.fisica, R.giorno] },
  { chiave: "mazzi", href: R.mazzi, pagine: [R.mazzi, R.carte, R.voto] },
  { chiave: "esplora", href: R.esplora, pagine: [R.esplora, R.blog, R.stese] },
  { chiave: "storia", href: R.storia, pagine: [R.storia, R.profilo] },
  { chiave: "negozio", href: R.negozio, pagine: [R.negozio, R.carrello] },
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
    /* Un indirizzo `/it/…` dice «italiano»: scegliendo un'altra lingua si va all'indirizzo inglese della stessa
     * pagina, scegliendo l'italiano a quello italiano (`/cards/x` → `/it/carte/x`). */
    const qui = `${senzaPrefisso(percorso)}${window.location.search}`;
    if (prefissoIt && l !== "it") router.replace(indirizzoV2(qui, false));
    else if (!prefissoIt && l === "it") router.replace(indirizzoV2(qui, true));
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

/* Il saldo dei crediti: si rilegge a ogni cambio di pagina (una lettura consuma crediti). */
function Crediti({ percorso }: { percorso: string }) {
  const { t } = useLingua();
  const k = t.comune;
  const sessione = useSessione();
  const conto = useConto([percorso]);
  const saldo = sessione.autenticata ? conto.dati?.saldo : undefined;
  const titolo = saldo == null ? k.testata_crediti_tip : f(k.testata_crediti_tip_n, { n: plurale(saldo, k.testata_crediti_n) });
  return (
    <LinkV2 className="hdr-icon hdr-credits" href={R.prezzi} title={titolo} aria-label={titolo}
      aria-current={percorso === R.prezzi ? "page" : undefined}>
      <Icona nome="crediti" />
      <span className="hdr-label">{saldo == null ? k.testata_crediti : <b>{saldo}</b>}</span>
    </LinkV2>
  );
}

function IconaCarrello({ percorso }: { percorso: string }) {
  const { t } = useLingua();
  const k = t.comune;
  const { pezzi } = useCarrello();
  const titolo = pezzi ? f(k.testata_carrello_tip_n, { n: pezzi }) : k.testata_carrello_tip;
  return (
    <LinkV2 className="hdr-icon" href={R.carrello} title={titolo} aria-label={titolo}
      aria-current={percorso === R.carrello ? "page" : undefined}>
      <Icona nome="carrello" />
      {pezzi > 0 && <span className="hdr-badge" aria-hidden="true">{pezzi > 99 ? "99+" : pezzi}</span>}
      <span className="hdr-label">{k.testata_carrello}</span>
    </LinkV2>
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
        <span className="brand-name">TAROTS <em>chat</em></span>
      </LinkV2>
      <nav className="primary-nav" aria-label={t.comune.aria_nav}>
        {SEZIONI.map((s) => (
          <LinkV2 key={s.chiave} href={s.href} aria-current={attiva === s.chiave ? "page" : undefined}>
            {nomi[s.chiave]}
          </LinkV2>
        ))}
      </nav>
      <div className="header-actions">
        <IconaCarrello percorso={percorso} />
        <SelettoreLingua />
        <Crediti percorso={percorso} />
        {sessione.autenticata ? (
          <>
            {sessione.admin && ADMIN_URL && (
              <a className="text-link hide-sm" href={ADMIN_URL}>{t.comune.admin}</a>
            )}
            <LinkV2 className="hdr-icon" href={R.profilo} title={sessione.nome ?? t.comune.profilo}
              aria-current={percorso === R.profilo ? "page" : undefined}>
              <Icona nome="profilo" />
              <span className="hdr-label">{t.comune.testata_profilo}</span>
            </LinkV2>
          </>
        ) : (
          sessione.pronta && (
            <button type="button" className="hdr-icon" onClick={entra} title={t.comune.entra}>
              <Icona nome="entra" />
              <span className="hdr-label">{t.comune.entra}</span>
            </button>
          )
        )}
        <LinkV2 className="button button-brass button-small" href={R.leggi} data-an="cta_testata">
          {t.comune.inizia_lettura}
        </LinkV2>
      </div>
    </header>
  );
}
