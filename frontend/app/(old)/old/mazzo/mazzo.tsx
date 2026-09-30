"use client";

/* La pagina del mazzo: come una scheda prodotto di un oggetto da collezione. È
 * un'anteprima — il mazzo è in preparazione — e lo dice: niente prezzo inventato né
 * pulsante d'acquisto che non compra. La «foto» in testa è una scena composta con le
 * carte vere del mazzo; se in `public/mazzo/foto-mazzo.webp` c'è una fotografia vera
 * (o generata), la sostituisce. */

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "@/app/(old)/old/componenti/link";
import {
  apriOrdine, elencaIndirizzi, elencaMazzi, euro, leggiOrdine, mieiMazzi, urlPdfGratuito,
  type Carta as TipoCarta, type Mazzo, type RigaOrdine, type TipoVoceOrdine,
} from "@/lib/api";
import { nomeCarta } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useAzione, useCarica, useToken } from "@/lib/usa";
import { BottonePdf } from "../componenti/bottone-pdf";
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

export function PaginaMazzo({ carte, mazziIniziali = null }: { carte: TipoCarta[]; mazziIniziali?: Mazzo[] | null }) {
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
            <a href="#negozio" className={`bottone ${stili.cta}`}>❖ {t.mazzo_cta}</a>
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
              <Link href={`/carte/${c.slug ?? c.id}`} className={stili.cartaVetrina}>
                {/* eslint-disable-next-line @next/next/no-img-element -- la carta vera */}
                <img src={`/cards/${c.id}.${ESTENSIONE}`} alt={c.nome ?? nomeCarta(c, lingua)} width={360} height={640}
                  loading="lazy" />
                <span>{c.nome ?? nomeCarta(c, lingua)}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section id="negozio" className={stili.sezione} aria-labelledby="negozio-titolo">
        <h2 id="negozio-titolo">{t.negozio_titolo}</h2>
        <p className={`oracolo ${stili.sottotitolo}`} style={{ fontSize: "1.05rem" }}>{t.negozio_sottotitolo}</p>
        <Suspense fallback={null}>
          <Negozio inizialiMazzi={mazziIniziali} />
        </Suspense>
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

/* ---- il negozio: elenco mazzi + carrello (v5, Fase B3) ---- */

interface VoceLocale {
  deckId: number;
  tipo: TipoVoceOrdine;
  nome: string;
  prezzoUnitario: number;
  valuta: string;
  quantita: number;
}

function chiaveVoce(deckId: number, tipo: TipoVoceOrdine): string {
  return `${deckId}:${tipo}`;
}

function Negozio({ inizialiMazzi }: { inizialiMazzi: Mazzo[] | null }) {
  const { t, locale } = useLingua();
  const sessione = useSessione();
  const token = useToken();
  const parametri = useSearchParams();

  const mazzi = useCarica(useCallback(() => elencaMazzi(), []), [], { pubblico: true });
  const posseduti = useCarica(mieiMazzi);
  const indirizzi = useCarica(elencaIndirizzi);
  const { esegui, inCorso, errore } = useAzione();
  const [indirizzoScelto, setIndirizzoScelto] = useState<string | null>(null);

  const elenco = mazzi.dati ?? inizialiMazzi ?? [];
  const idPosseduti = new Set(posseduti.dati?.deck_ids ?? []);

  const [carrello, setCarrello] = useState<Map<string, VoceLocale>>(new Map());
  const [esito, setEsito] = useState<{ buono: boolean; messaggio: string } | null>(null);
  const [ordinePagato, setOrdinePagato] = useState<{ id: string; righePdf: RigaOrdine[] } | null>(null);

  /* Il ritorno dal pagamento (`?ordine=…`): come per i piani, lo stato vero si chiede al server. */
  useEffect(() => {
    const ordineId = parametri.get("ordine");
    if (!ordineId) return;
    let annullato = false;
    leggiOrdine(token, ordineId)
      .then((o) => {
        if (annullato) return;
        if (o.status === "pagato") {
          setEsito({ buono: true, messaggio: t.negozio_ordine_pagato });
          setCarrello(new Map());
          setOrdinePagato({ id: ordineId, righePdf: o.righe.filter((r) => r.tipo === "pdf") });
          posseduti.ricarica();
        } else if (o.status !== "aperto") {
          setEsito({ buono: false, messaggio: t.negozio_ordine_annullato });
        }
      })
      .catch(() => { if (!annullato) setEsito({ buono: false, messaggio: t.negozio_ordine_non_verificato }); });
    return () => { annullato = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [parametri, token]);

  const aggiungi = useCallback((m: Mazzo, tipo: TipoVoceOrdine) => {
    const prezzo =
      tipo === "digitale" ? (m.offerta_attiva ? (m.prezzo_digitale_scontato ?? m.prezzo_digitale) : m.prezzo_digitale)
      : tipo === "pdf" ? m.prezzo_stampa
      : m.prezzo_fisico;
    if (prezzo == null) return;
    setCarrello((prima) => {
      const nuovo = new Map(prima);
      const chiave = chiaveVoce(m.id, tipo);
      const esistente = nuovo.get(chiave);
      nuovo.set(chiave, {
        deckId: m.id, tipo, nome: m.nome, prezzoUnitario: prezzo, valuta: m.valuta,
        quantita: (esistente?.quantita ?? 0) + 1,
      });
      return nuovo;
    });
  }, []);

  const rimuovi = (chiave: string) =>
    setCarrello((prima) => { const nuovo = new Map(prima); nuovo.delete(chiave); return nuovo; });

  const voci = Array.from(carrello.values());
  const totaleGrezzo = voci.reduce((s, v) => s + v.prezzoUnitario * v.quantita, 0);
  const valutaCarrello = voci[0]?.valuta ?? "EUR";
  const richiedeIndirizzo = voci.some((v) => v.tipo === "fisico");
  const elencoIndirizzi = indirizzi.dati?.indirizzi ?? [];
  const indirizzoAttivo = indirizzoScelto ?? elencoIndirizzi.find((i) => i.predefinito)?.id ?? elencoIndirizzi[0]?.id ?? null;

  const completaOrdine = async () => {
    if (!sessione.autenticata) { sessione.entra(); return; }
    if (richiedeIndirizzo && !indirizzoAttivo) return;
    const corpo = voci.map((v) => ({ deck_id: v.deckId, tipo: v.tipo, quantita: v.quantita }));
    const r = await esegui((tok) => apriOrdine(tok, corpo, undefined, richiedeIndirizzo ? indirizzoAttivo ?? undefined : undefined));
    if (r?.url) window.location.assign(r.url);
  };

  return (
    <>
      {esito && (
        <div className={esito.buono ? stili.avvisoBuono : stili.avviso} role="status">
          <p style={{ margin: 0 }}>{esito.messaggio}</p>
          {ordinePagato?.righePdf.map((r) => (
            <BottonePdf
              key={r.deck_id} ordineId={ordinePagato.id} deckId={r.deck_id}
              nome={elenco.find((m) => m.id === r.deck_id)?.nome ?? ""}
            />
          ))}
        </div>
      )}
      {mazzi.errore && <p className={stili.erroreNegozio}>{mazzi.errore}</p>}
      {elenco.length === 0 && !mazzi.inCorso && <p className={stili.avviso}>{t.negozio_vuoto}</p>}

      <ul className={stili.negozioGriglia}>
        {elenco.map((m) => (
          <SchedaMazzo
            key={m.id} mazzo={m} posseduto={m.predefinito || idPosseduti.has(m.id)}
            inCarrelloDigitale={carrello.get(chiaveVoce(m.id, "digitale"))?.quantita ?? 0}
            inCarrelloPdf={carrello.get(chiaveVoce(m.id, "pdf"))?.quantita ?? 0}
            inCarrelloFisico={carrello.get(chiaveVoce(m.id, "fisico"))?.quantita ?? 0}
            onAggiungi={aggiungi}
          />
        ))}
      </ul>

      <div className={`pannello ${stili.carrello}`}>
        <h3 className={stili.carrelloTitolo}>{t.negozio_carrello_titolo}</h3>
        {voci.length === 0 ? (
          <p className={stili.avviso}>{t.negozio_carrello_vuoto}</p>
        ) : (
          <>
            <ul className={stili.righeCarrello}>
              {voci.map((v) => (
                <li key={chiaveVoce(v.deckId, v.tipo)}>
                  <span>
                    {t.negozio_carrello_voce(
                      v.nome, v.tipo === "digitale" ? t.negozio_digitale : v.tipo === "pdf" ? t.negozio_pdf : t.negozio_fisico,
                    )}
                    {v.quantita > 1 ? ` × ${v.quantita}` : ""}
                  </span>
                  <span className={stili.righeCarrelloPrezzo}>{euro(v.prezzoUnitario * v.quantita, v.valuta, locale)}</span>
                  <button
                    type="button" className="bottone-secondario" onClick={() => rimuovi(chiaveVoce(v.deckId, v.tipo))}
                  >
                    {t.negozio_carrello_rimuovi}
                  </button>
                </li>
              ))}
            </ul>
            <p className={stili.totaleCarrello}>{t.negozio_carrello_totale}: {euro(totaleGrezzo, valutaCarrello, locale)}</p>
            <p className={stili.avviso}>{t.negozio_carrello_nota_sconto}</p>
            {richiedeIndirizzo && sessione.autenticata && (
              <div className={stili.nota}>
                <strong style={{ display: "block", marginBottom: 4 }}>{t.negozio_indirizzo_titolo}</strong>
                {elencoIndirizzi.length === 0 ? (
                  <p>
                    {t.negozio_indirizzo_manca}{" "}
                    <Link href="/profilo">{t.negozio_indirizzo_vai_al_profilo}</Link>
                  </p>
                ) : (
                  <select value={indirizzoAttivo ?? ""} onChange={(e) => setIndirizzoScelto(e.target.value)}>
                    {elencoIndirizzi.map((i) => (
                      <option key={i.id} value={i.id}>{i.nome} — {i.via}, {i.citta}</option>
                    ))}
                  </select>
                )}
              </div>
            )}
            <button
              className="bottone" disabled={inCorso || (richiedeIndirizzo && sessione.autenticata && !indirizzoAttivo)}
              onClick={completaOrdine}
            >
              {inCorso
                ? t.negozio_ordine_in_corso
                : sessione.autenticata ? t.negozio_completa_ordine : t.negozio_entra_per_acquistare}
            </button>
            {errore && <p className={stili.erroreNegozio}>{errore}</p>}
          </>
        )}
      </div>
    </>
  );
}

function SchedaMazzo({
  mazzo, posseduto, inCarrelloDigitale, inCarrelloPdf, inCarrelloFisico, onAggiungi,
}: {
  mazzo: Mazzo;
  posseduto: boolean;
  inCarrelloDigitale: number;
  inCarrelloPdf: number;
  inCarrelloFisico: number;
  onAggiungi: (m: Mazzo, tipo: TipoVoceOrdine) => void;
}) {
  const { t, locale } = useLingua();
  const scontato = mazzo.offerta_attiva && mazzo.prezzo_digitale_scontato != null;
  const prezzoDigitale = scontato ? mazzo.prezzo_digitale_scontato! : mazzo.prezzo_digitale;

  return (
    <li className={`pannello ${stili.mazzoScheda}`}>
      {/* eslint-disable-next-line @next/next/no-img-element -- il dorso, finché il mazzo non ha una grafica propria */}
      <img src={`/cards/dorso.${ESTENSIONE}`} alt="" width={90} height={160} className={stili.mazzoSchedaDorso} />
      <div className={stili.mazzoSchedaCorpo}>
        <strong>{mazzo.nome}</strong>
        {mazzo.descrizione && <p className={stili.nota}>{mazzo.descrizione}</p>}
        {posseduto ? (
          <p className={stili.etichettaPosseduto}>{mazzo.predefinito ? t.negozio_incluso : t.negozio_posseduto}</p>
        ) : (
          <>
            {mazzo.prezzo_digitale != null && (
              <div className={stili.rigaPrezzo}>
                <span>{t.negozio_digitale}</span>
                <span>
                  {scontato && <s className={stili.nota}>{euro(mazzo.prezzo_digitale, mazzo.valuta, locale)}</s>}{" "}
                  {euro(prezzoDigitale!, mazzo.valuta, locale)}
                </span>
                <button type="button" className="bottone-secondario" onClick={() => onAggiungi(mazzo, "digitale")}
                  data-an="carrello_aggiunto" data-an-mazzo={mazzo.slug} data-an-tipo="digitale">
                  {t.negozio_aggiungi}
                </button>
              </div>
            )}
            {scontato && mazzo.offerta_valido_fino && (
              <p className={stili.nota}>{t.negozio_offerta_fino(new Date(mazzo.offerta_valido_fino).toLocaleDateString(locale))}</p>
            )}
            {mazzo.prezzo_stampa === 0 && (
              <div className={stili.rigaPrezzo}>
                <span>{t.negozio_pdf}</span>
                <a href={urlPdfGratuito(mazzo.slug)} download className="bottone-secondario">
                  {t.negozio_scarica_pdf_gratis}
                </a>
              </div>
            )}
            {mazzo.prezzo_stampa != null && mazzo.prezzo_stampa > 0 && (
              <div className={stili.rigaPrezzo}>
                <span>{t.negozio_pdf}</span>
                <span>{euro(mazzo.prezzo_stampa, mazzo.valuta, locale)}</span>
                <button type="button" className="bottone-secondario" onClick={() => onAggiungi(mazzo, "pdf")}
                  data-an="carrello_aggiunto" data-an-mazzo={mazzo.slug} data-an-tipo="pdf">
                  {t.negozio_aggiungi}
                </button>
              </div>
            )}
            {mazzo.prezzo_fisico != null && (
              <div className={stili.rigaPrezzo}>
                <span>{t.negozio_fisico}</span>
                <span>{euro(mazzo.prezzo_fisico, mazzo.valuta, locale)}</span>
                <button type="button" className="bottone-secondario" onClick={() => onAggiungi(mazzo, "fisico")}
                  data-an="carrello_aggiunto" data-an-mazzo={mazzo.slug} data-an-tipo="fisico">
                  {t.negozio_aggiungi}
                </button>
              </div>
            )}
            {(inCarrelloDigitale > 0 || inCarrelloPdf > 0 || inCarrelloFisico > 0) && (
              <p className={stili.nota}>
                {t.negozio_nel_carrello}: {inCarrelloDigitale + inCarrelloPdf + inCarrelloFisico}
              </p>
            )}
          </>
        )}
      </div>
    </li>
  );
}

