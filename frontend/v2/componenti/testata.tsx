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
import { SincroniaLinguaProfilo, salvaNelProfilo, segnaScelta } from "@/v2/lib/lingua-profilo";
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

/* Le icone delle sezioni del menu, che sul telefono prendono il posto delle scritte (sotto, l'etichetta corta). */
const ICONE_MENU: Record<Voce, string> = {
  leggi: "M7 3h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2ZM11 7.5l1.1 2.2 2.4.4-1.7 1.7.4 2.4-2.2-1.2-2.2 1.2.4-2.4-1.7-1.7 2.4-.4Z",
  fisica: "M3.5 8 10 4.5l5.5 11.5-6.5 3.5ZM13.5 4.5l6 2.5-4 10.5",
  giorno: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8ZM12 2.5v2M12 19.5v2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M2.5 12h2M19.5 12h2M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4",
  diario: "M5 4h9a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3V4ZM5 17a3 3 0 0 1 3-3h9M9 8h5",
  esplora: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM15.5 8.5l-2 5-5 2 2-5Z",
  storia: "M3.5 12a8.5 8.5 0 1 0 2.6-6.1M3 4v4h4M12 7.5V12l3 2",
  negozio: "M6 8h12l-1 12H7L6 8ZM9 8V6.5a3 3 0 0 1 6 0V8",
};

function IconaMenu({ voce }: { voce: Voce }) {
  return (
    <svg className="nav-icona" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={ICONE_MENU[voce]} />
    </svg>
  );
}

function Icona({ nome }: { nome: keyof typeof ICONE }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={ICONE[nome]} />
    </svg>
  );
}

/* Quale voce del menu accendere: ogni sezione possiede alcune pagine. I mazzi stanno sotto «Esplora» (v8.5): al loro
 * posto la carta del giorno; il diario e la lettura delle proprie carte hanno una voce loro. Le etichette lunghe
 * vanno su due righe (`\n` nel dizionario) per stare nella barra. */
type Voce = "leggi" | "fisica" | "giorno" | "diario" | "esplora" | "storia" | "negozio";
const SEZIONI: { chiave: Voce; href: string; pagine: string[] }[] = [
  { chiave: "leggi", href: R.leggi, pagine: [R.leggi] },
  { chiave: "fisica", href: R.fisica, pagine: [R.fisica] },
  { chiave: "giorno", href: R.giorno, pagine: [R.giorno] },
  { chiave: "diario", href: R.blog, pagine: [R.blog] },
  { chiave: "esplora", href: R.esplora, pagine: [R.esplora, R.stese, R.carte, R.mazzi, R.voto] },
  { chiave: "storia", href: R.storia, pagine: [R.storia, R.profilo] },
  { chiave: "negozio", href: R.negozio, pagine: [R.negozio, R.carrello] },
];

export function useEntra() {
  const sessione = useSessione();
  return () => sessione.entra(`${window.location.pathname}${window.location.search}`);
}

export function SelettoreLingua() {
  const { t, lingua, imposta, prefissoIt } = useLingua();
  const sessione = useSessione();
  const router = useRouter();
  const percorso = usePathname() ?? R.home;
  const cambia = (valore: string) => {
    const l = comeLingua(valore);
    if (!l) return;
    imposta(l);
    /* v9, Fase 2d: una scelta esplicita. Chi è dentro la porta anche nel profilo (oracolo, email, notifiche). */
    segnaScelta();
    if (sessione.autenticata) void salvaNelProfilo(sessione.token, l);
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
  const nomi: Record<Voce, string> = {
    leggi: t.comune.nav_leggi, fisica: t.comune.nav_fisica, giorno: t.comune.nav_giorno, diario: t.comune.nav_diario,
    esplora: t.comune.nav_esplora, storia: t.comune.nav_storia, negozio: t.comune.nav_negozio,
  };
  /* Sul telefono: icona ed etichetta corta (le lunghe restano per computer e lettori di schermo). */
  const brevi: Record<Voce, string> = {
    leggi: t.comune.nav_breve_leggi, fisica: t.comune.nav_breve_fisica, giorno: t.comune.nav_breve_giorno,
    diario: t.comune.nav_breve_diario, esplora: t.comune.nav_breve_esplora, storia: t.comune.nav_breve_storia,
    negozio: t.comune.nav_breve_negozio,
  };

  return (
    <header className="site-header">
      <SincroniaLinguaProfilo />
      <LinkV2 className="brand" href={R.home} aria-label={t.comune.aria_home}>
        <span className="brand-mark" aria-hidden="true">✦</span>
        <span className="brand-name">TAROTS <em>chat</em></span>
      </LinkV2>
      <nav className="primary-nav" aria-label={t.comune.aria_nav}>
        {SEZIONI.map((s) => (
          <LinkV2 key={s.chiave} href={s.href} aria-current={attiva === s.chiave ? "page" : undefined}
            className={`nav-voce nav-${s.chiave}`} aria-label={nomi[s.chiave].replace(/\n/g, " ")} title={nomi[s.chiave].replace(/\n/g, " ")}>
            <span className="nav-lungo" aria-hidden="true">{nomi[s.chiave]}</span>
            <IconaMenu voce={s.chiave} />
            <span className="nav-breve" aria-hidden="true">{brevi[s.chiave]}</span>
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
              <span className="hdr-label">{t.comune.testata_entra}</span>
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
