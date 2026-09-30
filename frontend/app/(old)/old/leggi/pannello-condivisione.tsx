"use client";

/* Il pannello di condivisione di una lettura.
 *
 * Aprendolo la lettura ottiene il suo link pubblico e la sua immagine, composta qui
 * (PNG 800×600), caricata sul server e da lì tornata come WebP 400×300 molto
 * compresso: è quella che si mostra in anteprima, si allega ai fogli di condivisione e
 * i social leggono dal link. Così, quando si preme un pulsante, tutto è già pronto — i social leggono l'anteprima dal link, e il
 * foglio di condivisione del telefono vuole essere aperto subito dopo il tocco.
 * Il testo personalizzato si salva dopo una breve pausa di scrittura e rifà le
 * immagini.
 *
 * Il premio: ogni cinque condivisioni verificate una lettura in omaggio, e cinque
 * letture per ogni persona che si iscrive dal link. Il pannello lo dice accanto ai
 * pulsanti, con il contatore. Che la condivisione sia «verificata» lo decide il
 * server: qui si segnala soltanto che si è usato un pulsante. */

import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import {
  caricaImmagineCondivisione, condividiLettura, leggiCondivisa, leggiProfilo, registraClicCondivisione,
  type CanaleCondivisione, type Condivisioni, type LetturaCondivisa,
} from "@/lib/api";
import {
  CANALI, LUNGHEZZA_TESTO, SITO_CANALE, idVisitatore, puoCondividereFile, urlCondivisione, urlIntento,
} from "@/lib/condivisione";
import { useLingua } from "@/lib/lingua";
import { useAzione, useToken } from "@/lib/usa";
import { MISURA_FINALE, componiImmagine } from "@/lib/immagine-condivisione";
import { FONDO_CANALE, Logo } from "@/lib/loghi";
import stili from "./condivisione.module.css";

type Stato = "preparo" | "pronto" | "errore";
type Canale = (typeof CANALI)[number];

const NOMI_RETE: Record<Canale, string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
  x: "X",
  email: "Email",
  link: "Link",
};

interface Props {
  id: string;
  onChiudi: () => void;
  /* Il link pubblico della lettura: `null` quando lo si disattiva. */
  onLink: (token: string | null) => void;
}

/* Il pannello si monta a ogni apertura e si smonta alla chiusura: ogni volta parte
 * da zero (link, immagini, contatore) e non lascia nulla in giro. Sta in un portale
 * sul `body`: dentro la pagina, i contesti di sovrapposizione delle schede e delle
 * carte del tavolo lo coprirebbero, qualunque `z-index` abbia. */
export function PannelloCondivisione({ aperta, ...resto }: Props & { aperta: boolean }) {
  return aperta ? createPortal(<Contenuto {...resto} />, document.body) : null;
}

function Contenuto({ id, onChiudi, onLink }: Props) {
  const { t } = useLingua();
  const tokenSessione = useToken();
  const { esegui } = useAzione();

  const [stato, setStato] = useState<Stato>("preparo");
  const [token, setToken] = useState<string | null>(null);
  const [dati, setDati] = useState<LetturaCondivisa | null>(null);
  const [testo, setTesto] = useState("");
  const [anteprima, setAnteprima] = useState<string | null>(null);
  const [avviso, setAvviso] = useState<{ testo: string; href?: string; etichetta?: string } | null>(null);
  const [contatore, setContatore] = useState<Condivisioni | null>(null);

  /* Cose che vivono fuori dal ciclo di rendering. */
  const file = useRef<File | null>(null);
  const richiesta = useRef(0);
  const sincronizzato = useRef<string | undefined>(undefined);
  const finestra = useRef<HTMLDivElement>(null);
  /* Le funzioni e il token che cambiano a ogni rendering del chiamante stanno in un
   * riferimento: se stessero fra le dipendenze degli effetti, ogni rendering
   * rifarebbe il link e le immagini. */
  const ultimi = useRef({ esegui, onLink, onChiudi, tokenSessione });
  useEffect(() => { ultimi.current = { esegui, onLink, onChiudi, tokenSessione }; });

  const indirizzi = useRef<string[]>([]);
  const rilascia = useCallback(() => {
    indirizzi.current.forEach((u) => URL.revokeObjectURL(u));
    indirizzi.current = [];
  }, []);

  /* Ottiene il link, ricompone e ricarica le immagini. Una richiesta più recente
   * annulla l'esito di quella in corso: si scrive piano, ma si scrive. */
  const sincronizza = useCallback(async (nuovoTesto: string | undefined) => {
    const numero = ++richiesta.current;
    const vecchia = () => numero !== richiesta.current;
    if (nuovoTesto !== undefined) sincronizzato.current = nuovoTesto;
    const r = await ultimi.current.esegui((tok) => condividiLettura(tok, id, true, nuovoTesto));
    if (vecchia()) return;
    if (!r?.share_token) { setStato("errore"); return; }
    try {
      const pubblica = await leggiCondivisa(r.share_token);
      const png = await componiImmagine(pubblica);
      if (vecchia()) return;
      if (!png) { setStato("errore"); return; }
      /* Il server risponde con l'immagine finale: si mostra e si condivide quella. */
      const webp = await ultimi.current.esegui((tok) => caricaImmagineCondivisione(tok, id, png));
      if (vecchia()) return;
      if (!webp) { setStato("errore"); return; }
      file.current = new File([webp], "lettura-tarots.webp", { type: "image/webp" });
      rilascia();
      const indirizzo = URL.createObjectURL(webp);
      indirizzi.current = [indirizzo];
      setAnteprima(indirizzo);
      setToken(r.share_token);
      setDati(pubblica);
      if (nuovoTesto === undefined) setTesto(r.share_text ?? "");
      sincronizzato.current = nuovoTesto ?? (r.share_text ?? "");
      ultimi.current.onLink(r.share_token);
      setStato("pronto");
    } catch {
      if (!vecchia()) setStato("errore");
    }
  }, [id, rilascia]);

  /* All'apertura: link, immagini e contatore. */
  useEffect(() => {
    const avvio = window.setTimeout(() => { void sincronizza(undefined); }, 0);
    leggiProfilo(ultimi.current.tokenSessione).then((p) => setContatore(p.condivisioni), () => undefined);
    return () => {
      window.clearTimeout(avvio);
      // eslint-disable-next-line react-hooks/exhaustive-deps -- un contatore, non un nodo: serve il valore di adesso
      richiesta.current++;
      rilascia();
    };
  }, [sincronizza, rilascia]);

  /* Il testo personalizzato: dopo una pausa di scrittura si salva e si rifanno le immagini. */
  useEffect(() => {
    if (stato === "errore" || sincronizzato.current === undefined || testo === sincronizzato.current) return;
    const pausa = window.setTimeout(() => {
      setStato("preparo");
      setAvviso(null);
      void sincronizza(testo);
    }, 900);
    return () => window.clearTimeout(pausa);
  }, [testo, stato, sincronizza]);

  /* Finestra modale: Esc chiude, Tab resta dentro, la pagina sotto non scorre. */
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
      const primo = dentro[0];
      const ultimo = dentro[dentro.length - 1];
      if (e.shiftKey && (document.activeElement === primo || document.activeElement === finestra.current)) {
        e.preventDefault();
        ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault();
        primo.focus();
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
  const url = token ? urlCondivisione(token) : "";
  const testoPost = testo.trim() || dati?.question || "";
  const didascalia = [testoPost, url].filter(Boolean).join("\n\n");

  const registra = (canale: CanaleCondivisione) => {
    registraClicCondivisione(tokenSessione, id, canale, idVisitatore()).then(
      (r) => setContatore(r.contatore),
      () => undefined,
    );
  };

  const scarica = () => {
    const f = file.current;
    if (!f) return;
    const a = document.createElement("a");
    a.href = URL.createObjectURL(f);
    a.download = "lettura-tarots.webp";
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

  /* Facebook, X e la posta si aprono da soli (sono collegamenti): qui restano i
   * canali che vogliono un gesto. */
  const scegli = async (canale: Canale) => {
    if (!pronto) return;
    if (canale === "link") {
      if (await copia(url)) setAvviso({ testo: t.cond_copiato });
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
          /* annullato: nessun clic da registrare */
        }
        return;
      }
      scarica();
      await copia(didascalia);
      setAvviso({
        testo: t.cond_scaricata(NOMI_RETE[canale]),
        href: SITO_CANALE[canale],
        etichetta: t.cond_apri(NOMI_RETE[canale]),
      });
      registra(canale);
    }
  };

  const disattiva = async () => {
    const r = await esegui((tok) => condividiLettura(tok, id, false));
    if (!r) return;
    onLink(null);
    onChiudi();
  };

  const messaggio =
    stato === "errore" ? t.cond_errore : stato === "preparo" ? t.cond_preparo : t.cond_pronta;
  const c = contatore;

  return (
    <div className={stili.sfondo} onClick={onChiudi}>
      <div
        ref={finestra}
        className={`pannello ${stili.finestra}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="cond-titolo"
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        <header className={stili.testata}>
          <h2 id="cond-titolo" className={stili.titolo}>✦ {t.cond_titolo}</h2>
          <button className={stili.chiudi} onClick={onChiudi} aria-label={t.chiudi}>×</button>
        </header>

        <div className={stili.corpo}>
          <div className={stili.anteprima}>
            <div
              className={`${stili.cornice} ${stato === "preparo" ? stili.aggiorno : ""}`}
              style={{ aspectRatio: `${MISURA_FINALE.w} / ${MISURA_FINALE.h}` }}
            >
              {anteprima && (
                // eslint-disable-next-line @next/next/no-img-element -- un blob locale: l'ottimizzatore non lo vede
                <img src={anteprima} width={MISURA_FINALE.w} height={MISURA_FINALE.h} alt={t.cond_anteprima} />
              )}
            </div>
          </div>

          <div className={stili.comandi}>
            <label className={stili.campoTesto}>
              <span>{t.cond_testo_etichetta}</span>
              <textarea
                value={testo}
                onChange={(e) => setTesto(e.target.value)}
                maxLength={LUNGHEZZA_TESTO}
                disabled={!dati}
                rows={2}
                dir="auto"
                placeholder={t.cond_testo_segnaposto}
                aria-describedby="cond-aiuto"
              />
              <span id="cond-aiuto" className={stili.aiuto}>
                {t.cond_testo_aiuto} {testo.length}/{LUNGHEZZA_TESTO}
              </span>
            </label>

            <p className={stili.stato} role="status" aria-live="polite">
              {messaggio}
              {stato === "errore" && (
                <button
                  className={stili.riprova}
                  onClick={() => { setStato("preparo"); setAvviso(null); void sincronizza(undefined); }}
                >
                  {t.riprova}
                </button>
              )}
            </p>

            <p className={stili.etichettaCanali}>{t.cond_condividi_su}</p>
            <div className={stili.canali}>
              {CANALI.map((canale) => {
                const rete = NOMI_RETE[canale];
                const nome = canale === "email" ? t.cond_email : canale === "link" ? t.cond_solo_link : rete;
                const intento = pronto
                  ? urlIntento(canale, { url, testo: testoPost, oggetto: "TAROTS chat" })
                  : null;
                const contenuto = (
                  <>
                    <span className={stili.marchio} style={{ background: FONDO_CANALE[canale] }}>
                      <Logo canale={canale} />
                    </span>
                    <span>{nome}</span>
                  </>
                );
                return intento ? (
                  <a
                    key={canale}
                    className={stili.canale}
                    href={intento}
                    {...(canale === "email" ? {} : { target: "_blank", rel: "noopener noreferrer" })}
                    onClick={() => registra(canale)}
                    aria-label={t.cond_condividi_con(nome)}
                  >
                    {contenuto}
                  </a>
                ) : (
                  <button
                    key={canale}
                    className={stili.canale}
                    disabled={!pronto}
                    onClick={() => scegli(canale)}
                    aria-label={t.cond_condividi_con(nome)}
                  >
                    {contenuto}
                  </button>
                );
              })}
            </div>

            {avviso && (
              <p className={stili.avviso} role="status">
                {avviso.testo}{" "}
                {avviso.href && <a href={avviso.href} target="_blank" rel="noopener noreferrer">{avviso.etichetta}</a>}
              </p>
            )}

            <button className={`bottone-secondario ${stili.scarica}`} disabled={!pronto} onClick={scarica}>
              {t.cond_scarica}
            </button>

            <aside className={stili.premio} aria-labelledby="cond-premio">
              <h3 id="cond-premio">✦ {t.cond_premio_titolo}</h3>
              <ul>
                <li>{t.cond_premio_1(c?.soglia ?? 5)}</li>
                <li>{t.cond_premio_2(c?.crediti_iscrizione ?? 5)}</li>
                <li>{t.cond_premio_3}</li>
              </ul>
              {c && (
                <>
                  <div
                    className={stili.barra}
                    role="progressbar"
                    aria-valuemin={0}
                    aria-valuemax={c.soglia}
                    aria-valuenow={c.soglia - c.prossimo_tra}
                    aria-label={t.cond_premio_titolo}
                  >
                    <span style={{ width: `${((c.soglia - c.prossimo_tra) / c.soglia) * 100}%` }} />
                  </div>
                  <p className={stili.contatore}>{t.cond_contatore(c.verificate, c.prossimo_tra)}</p>
                </>
              )}
              <p className={stili.aiuto}>{t.cond_verificata_spiega}</p>
            </aside>

            {dati?.speciale && <p className={stili.aiuto}>{t.cond_speciale_nota}</p>}
            <p className={stili.aiuto}>{t.cond_link_attivo}</p>
            <button className={stili.disattiva} onClick={disattiva}>{t.cond_disattiva}</button>
          </div>
        </div>
      </div>
    </div>
  );
}
