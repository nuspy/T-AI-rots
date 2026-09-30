"use client";

/* Condividere una lettura, dalla v2. Stessa meccanica del sito (`app/(sito)/leggi/pannello-condivisione.tsx`): il
 * link pubblico, l'immagine composta qui e rifatta dal server in WebP, il testo personale che si salva dopo una
 * pausa, i canali, il contatore delle condivisioni verificate e i premi (decisi dal server). Cambia la
 * destinazione: il link porta alla pagina condivisa della v2 (`/v2/shared/…`), non a quella del sito. */

import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTraccia } from "lanterna-osservatore/react";
import { MISURA_FINALE, componiImmagineV2 } from "./immagine-condivisione";
import { FONDO_CANALE, Logo } from "@/lib/loghi";
import {
  caricaImmagineCondivisione, condividiLettura, leggiCondivisa, leggiProfilo, registraClicCondivisione,
  type CanaleCondivisione, type Condivisioni, type LetturaCondivisa,
} from "@/lib/api";
import { CANALI, LUNGHEZZA_TESTO, SITE_URL, SITO_CANALE, idVisitatore, puoCondividereFile, urlIntento } from "@/lib/condivisione";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useAzione } from "@/v2/lib/usa";
import stili from "./condivisione.module.css";

type Stato = "preparo" | "pronto" | "errore";
type Canale = (typeof CANALI)[number];

const NOMI_RETE: Record<Canale, string> = {
  instagram: "Instagram", facebook: "Facebook", tiktok: "TikTok", x: "X", email: "Email", link: "Link",
};

export const urlCondivisioneV2 = (token: string) => `${SITE_URL}${R.condivisa(token)}`;

interface Props {
  id: string;
  onChiudi: () => void;
}

export function PannelloCondivisione({ aperta, ...resto }: Props & { aperta: boolean }) {
  return aperta ? createPortal(<Contenuto {...resto} />, document.body) : null;
}

function Contenuto({ id, onChiudi }: Props) {
  const { t } = useLingua();
  const l = t.lettura;
  const { token: tokenSessione } = useSessione();
  const { esegui } = useAzione();
  const traccia = useTraccia();

  const [stato, setStato] = useState<Stato>("preparo");
  const [token, setToken] = useState<string | null>(null);
  const [dati, setDati] = useState<LetturaCondivisa | null>(null);
  const [testo, setTesto] = useState("");
  const [anteprima, setAnteprima] = useState<string | null>(null);
  const [avviso, setAvviso] = useState<{ testo: string; href?: string; etichetta?: string } | null>(null);
  const [contatore, setContatore] = useState<Condivisioni | null>(null);

  const file = useRef<File | null>(null);
  const richiesta = useRef(0);
  const sincronizzato = useRef<string | undefined>(undefined);
  const finestra = useRef<HTMLDivElement>(null);
  const ultimi = useRef({ esegui, onChiudi, tokenSessione });
  useEffect(() => { ultimi.current = { esegui, onChiudi, tokenSessione }; });

  const indirizzi = useRef<string[]>([]);
  const rilascia = useCallback(() => {
    indirizzi.current.forEach((u) => URL.revokeObjectURL(u));
    indirizzi.current = [];
  }, []);

  const sincronizza = useCallback(async (nuovoTesto: string | undefined) => {
    const numero = ++richiesta.current;
    const vecchia = () => numero !== richiesta.current;
    if (nuovoTesto !== undefined) sincronizzato.current = nuovoTesto;
    const r = await ultimi.current.esegui((tok) => condividiLettura(tok, id, true, nuovoTesto));
    if (vecchia()) return;
    if (!r?.share_token) { setStato("errore"); return; }
    try {
      const pubblica = await leggiCondivisa(r.share_token);
      const png = await componiImmagineV2(pubblica);
      if (vecchia()) return;
      if (!png) { setStato("errore"); return; }
      const webp = await ultimi.current.esegui((tok) => caricaImmagineCondivisione(tok, id, png));
      if (vecchia()) return;
      if (!webp) { setStato("errore"); return; }
      file.current = new File([webp], "tarots-reading.webp", { type: "image/webp" });
      rilascia();
      const indirizzo = URL.createObjectURL(webp);
      indirizzi.current = [indirizzo];
      setAnteprima(indirizzo);
      setToken(r.share_token);
      setDati(pubblica);
      if (nuovoTesto === undefined) setTesto(r.share_text ?? "");
      sincronizzato.current = nuovoTesto ?? (r.share_text ?? "");
      setStato("pronto");
    } catch {
      if (!vecchia()) setStato("errore");
    }
  }, [id, rilascia]);

  useEffect(() => {
    const avvio = window.setTimeout(() => { void sincronizza(undefined); }, 0);
    leggiProfilo(ultimi.current.tokenSessione).then((p) => setContatore(p.condivisioni), () => undefined);
    const contatoreRichieste = richiesta;
    return () => {
      window.clearTimeout(avvio);
      contatoreRichieste.current++;
      rilascia();
    };
  }, [sincronizza, rilascia]);

  useEffect(() => {
    if (stato === "errore" || sincronizzato.current === undefined || testo === sincronizzato.current) return;
    const pausa = window.setTimeout(() => {
      setStato("preparo");
      setAvviso(null);
      void sincronizza(testo);
    }, 900);
    return () => window.clearTimeout(pausa);
  }, [testo, stato, sincronizza]);

  useEffect(() => {
    const prima = document.activeElement as HTMLElement | null;
    const scroll = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    finestra.current?.focus();
    const tasti = (e: KeyboardEvent) => {
      if (e.key === "Escape") { ultimi.current.onChiudi(); return; }
      if (e.key !== "Tab" || !finestra.current) return;
      const dentro = Array.from(
        finestra.current.querySelectorAll<HTMLElement>("a[href], button:not(:disabled), textarea, [tabindex]:not([tabindex='-1'])"),
      ).filter((el) => el.offsetParent !== null);
      if (!dentro.length) return;
      const [primo, ultimo] = [dentro[0], dentro[dentro.length - 1]];
      if (e.shiftKey && (document.activeElement === primo || document.activeElement === finestra.current)) {
        e.preventDefault(); ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault(); primo.focus();
      }
    };
    window.addEventListener("keydown", tasti);
    return () => {
      window.removeEventListener("keydown", tasti);
      document.body.style.overflow = scroll;
      prima?.focus?.();
    };
  }, []);

  const pronto = stato === "pronto" && !!token && !!dati;
  const url = token ? urlCondivisioneV2(token) : "";
  const testoPost = testo.trim() || dati?.question || "";
  const didascalia = [testoPost, url].filter(Boolean).join("\n\n");

  const registra = (canale: CanaleCondivisione) => {
    traccia("share_completed", { canale });
    registraClicCondivisione(tokenSessione, id, canale, idVisitatore()).then((r) => setContatore(r.contatore), () => undefined);
  };

  const scarica = () => {
    const fl = file.current;
    if (!fl) return;
    const a = document.createElement("a");
    a.href = URL.createObjectURL(fl);
    a.download = "tarots-reading.webp";
    a.click();
    window.setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  };

  const copia = async (valore: string) => {
    try {
      await navigator.clipboard?.writeText(valore);
      return true;
    } catch {
      return false;
    }
  };

  const scegli = async (canale: Canale) => {
    if (!pronto) return;
    if (canale === "link") {
      if (await copia(url)) setAvviso({ testo: l.cond_copiato });
      registra("link");
      return;
    }
    if (canale === "instagram" || canale === "tiktok") {
      const post = file.current;
      if (post && puoCondividereFile(post)) {
        try {
          await navigator.share({ files: [post], text: didascalia, title: "TAROTS chat" });
          registra(canale);
        } catch {
          /* annullato */
        }
        return;
      }
      scarica();
      await copia(didascalia);
      setAvviso({
        testo: f(l.cond_scaricata, { rete: NOMI_RETE[canale] }),
        href: SITO_CANALE[canale],
        etichetta: f(l.cond_apri, { rete: NOMI_RETE[canale] }),
      });
      registra(canale);
    }
  };

  const disattiva = async () => {
    const r = await esegui((tok) => condividiLettura(tok, id, false));
    if (r) onChiudi();
  };

  const messaggio = stato === "errore" ? l.cond_errore : stato === "preparo" ? l.cond_preparo : l.cond_pronta;
  const c = contatore;

  return (
    <div className="dialog-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onChiudi(); }}>
      <div ref={finestra} className={`dialog ${stili.finestra}`} role="dialog" aria-modal="true" aria-labelledby="cond-titolo" tabIndex={-1}>
        <button type="button" className="dialog-close" onClick={onChiudi} aria-label={t.comune.chiudi}>✕</button>
        <h2 id="cond-titolo">{l.cond_titolo}</h2>
        <div className={stili.corpo}>
          <div>
            <div className={`${stili.cornice} ${stato === "preparo" ? stili.aggiorno : ""}`}
              style={{ aspectRatio: `${MISURA_FINALE.w} / ${MISURA_FINALE.h}` }}>
              {anteprima && (
                // eslint-disable-next-line @next/next/no-img-element -- un blob locale
                <img src={anteprima} width={MISURA_FINALE.w} height={MISURA_FINALE.h} alt={l.cond_anteprima} />
              )}
            </div>
            <label className="field" style={{ marginTop: "1rem" }}>
              <span>{l.cond_testo}</span>
              <textarea value={testo} onChange={(e) => setTesto(e.target.value)} maxLength={LUNGHEZZA_TESTO}
                disabled={!dati} rows={2} dir="auto" placeholder={l.cond_testo_segnaposto} aria-describedby="cond-aiuto" />
              <small id="cond-aiuto">{l.cond_testo_aiuto} {testo.length}/{LUNGHEZZA_TESTO}</small>
            </label>
          </div>
          <div>
            <p className={stili.stato} role="status" aria-live="polite">
              {messaggio}{" "}
              {stato === "errore" && (
                <button type="button" className="button button-quiet button-small"
                  onClick={() => { setStato("preparo"); setAvviso(null); void sincronizza(undefined); }}>
                  {t.comune.riprova}
                </button>
              )}
            </p>
            <p className="eyebrow" style={{ marginBottom: ".5rem" }}>{l.cond_su}</p>
            <div className={stili.canali}>
              {CANALI.map((canale) => {
                const nome = canale === "email" ? l.cond_email : canale === "link" ? l.cond_link : NOMI_RETE[canale];
                const intento = pronto ? urlIntento(canale, { url, testo: testoPost, oggetto: "TAROTS chat" }) : null;
                const contenuto = (
                  <>
                    <span className={stili.marchio} style={{ background: FONDO_CANALE[canale] }}><Logo canale={canale} /></span>
                    <span>{nome}</span>
                  </>
                );
                return intento ? (
                  <a key={canale} className={stili.canale} href={intento}
                    {...(canale === "email" ? {} : { target: "_blank", rel: "noopener noreferrer" })}
                    onClick={() => registra(canale)} aria-label={f(l.cond_con, { nome })}>
                    {contenuto}
                  </a>
                ) : (
                  <button key={canale} type="button" className={stili.canale} disabled={!pronto} onClick={() => scegli(canale)}
                    aria-label={f(l.cond_con, { nome })}>
                    {contenuto}
                  </button>
                );
              })}
            </div>
            {avviso && (
              <p className="success" role="status">
                {avviso.testo}{" "}
                {avviso.href && <a className="inline" href={avviso.href} target="_blank" rel="noopener noreferrer">{avviso.etichetta}</a>}
              </p>
            )}
            <button type="button" className="button button-quiet button-small" style={{ marginTop: "1rem" }} disabled={!pronto} onClick={scarica}>
              {l.cond_scarica}
            </button>
            <aside className={stili.premio} aria-labelledby="cond-premio">
              <h3 id="cond-premio">{l.cond_premio_titolo}</h3>
              <ul>
                <li>{f(l.cond_premio_1, { n: c?.soglia ?? 5 })}</li>
                <li>{f(l.cond_premio_2, { n: c?.crediti_iscrizione ?? 5 })}</li>
                <li>{l.cond_premio_3}</li>
              </ul>
              {c && (
                <>
                  <div className={stili.barra} role="progressbar" aria-valuemin={0} aria-valuemax={c.soglia}
                    aria-valuenow={c.soglia - c.prossimo_tra} aria-label={l.cond_premio_titolo}>
                    <span style={{ width: `${((c.soglia - c.prossimo_tra) / c.soglia) * 100}%` }} />
                  </div>
                  <p className="small">{f(l.cond_contatore, { v: c.verificate, m: c.prossimo_tra })}</p>
                </>
              )}
              <p className="small muted">{l.cond_verificata}</p>
            </aside>
            {dati?.speciale && <p className="small muted">{l.cond_speciale}</p>}
            <p className="small muted">{l.cond_attivo}</p>
            <button type="button" className="button button-danger button-small" onClick={disattiva}>{l.cond_disattiva}</button>
          </div>
        </div>
      </div>
    </div>
  );
}
