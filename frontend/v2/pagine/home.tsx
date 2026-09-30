"use client";

/* La home della v2, nell'ordine della specifica (§15): la domanda, l'esperienza, i temi, il rito, la memoria, la
 * differenza, i mazzi, le carte fisiche, il metodo, dal gratuito alla lettura completa, la condivisione, il
 * diario, le domande, l'ultimo invito. Una pagina che non si allunga per ripetere: ogni sezione fa una cosa. */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useTraccia } from "lanterna-osservatore/react";
import { impostazioniPubbliche } from "@/lib/api";
import { urlMedia } from "@/lib/blog";
import { salvaInvito } from "@/lib/inviti";
import { f } from "@/v2/i18n";
import { ImmagineCarta } from "@/v2/componenti/carta";
import { Dichiarazione } from "@/v2/componenti/dichiarazione";
import LinkV2 from "@/v2/componenti/link";
import { P, articoli, useMazzi } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";

export function Home() {
  const { t, lingua, prefissoIt } = useLingua();
  const h = t.home;
  const router = useRouter();
  const traccia = useTraccia();
  const [domanda, setDomanda] = useState("");
  const [avviso, setAvviso] = useState(false);
  const omaggi = useCarica(impostazioniPubbliche, [], { pubblico: true, iniziale: P.impostazioni() });
  const mazzi = useMazzi();
  const diario = useCarica(() => articoli(lingua, { per_pagina: 3 }), [lingua], { pubblico: true, iniziale: P.articoli(lingua, { per_pagina: 3 }) });

  /* Chi arriva da un invito porta il codice nell'indirizzo: si ricorda fino alla registrazione. */
  useEffect(() => {
    const codice = new URLSearchParams(window.location.search).get("invito");
    if (codice) salvaInvito(codice);
  }, []);

  const chiedi = (e: React.FormEvent) => {
    e.preventDefault();
    const pulita = domanda.trim();
    if (pulita.length < 3) {
      setAvviso(true);
      return;
    }
    traccia("question_submitted", { entry: "hero" });
    router.push(indirizzoV2(`${R.leggi}?question=${encodeURIComponent(pulita)}&source=hero`, prefissoIt));
  };

  const nIscrizione = omaggi.dati?.crediti_iscrizione ?? 3;
  const nInvito = omaggi.dati?.crediti_invito ?? 5;
  const disponibile = (mazzi.dati ?? []).find((m) => m.predefinito) ?? mazzi.dati?.[0];
  const articoliDiario = diario.dati?.articoli ?? [];

  return (
    <>
      <section className="hero" aria-labelledby="titolo-eroe">
        <div className="hero-copy">
          <p className="eyebrow">{h.eyebrow}</p>
          <h1 id="titolo-eroe" className="display">{h.titolo_1}<em>{h.titolo_em}</em>{h.titolo_2}</h1>
          <p className="lede">{h.lede}</p>
          <form className="question-form" onSubmit={chiedi} noValidate>
            <label className="sr-only" htmlFor="domanda-eroe">{h.domanda_etichetta}</label>
            <input
              id="domanda-eroe" name="question" maxLength={1000} autoComplete="off" dir="auto"
              placeholder={h.domanda_segnaposto} value={domanda}
              onChange={(e) => { setDomanda(e.target.value); setAvviso(false); }}
              aria-describedby={avviso ? "domanda-avviso" : undefined}
            />
            <button className="button button-brass" type="submit" data-an="hero_cta_click" data-an-dove="domanda">
              {h.domanda_invia}
            </button>
          </form>
          {avviso && <p id="domanda-avviso" className="notice" role="status">{h.domanda_breve}</p>}
          <div className="minor-cta">
            <LinkV2 href={`${R.leggi}?source=hero`} data-an="hero_cta_click" data-an-dove="gratis">{h.cta_gratis}</LinkV2>
            <LinkV2 href={R.fisica}>{h.cta_fisiche}</LinkV2>
            <LinkV2 href={R.giorno}>{h.cta_giorno}</LinkV2>
          </div>
          <div className="trust-strip"><span>{h.fiducia_1}</span><span>{h.fiducia_2}</span><span>{h.fiducia_3}</span></div>
        </div>
        <div className="ritual-object" role="img" aria-label={h.oggetto_aria}>
          <div className="hero-card"><ImmagineCarta id="maj-06" alt={h.oggetto_carta} priorita /></div>
          <p className="orbit-note"><strong>{h.nota_titolo}</strong>{h.nota_testo}</p>
        </div>
      </section>

      <section className="experience" aria-labelledby="titolo-demo">
        <div className="band">
          <div className="section-head">
            <div>
              <p className="eyebrow">{h.demo_eyebrow}</p>
              <h2 id="titolo-demo" className="section-title">{h.demo_titolo}</h2>
            </div>
            <p className="section-intro">{h.demo_intro}</p>
          </div>
          <div className="demo-stage">
            <div className="demo-copy">
              <p className="eyebrow">{h.demo_contesto}</p>
              <div className="chat-thread" aria-label={h.demo_esempio}>
                <p className="message message-user">{h.demo_1}</p>
                <p className="message">{h.demo_2}</p>
                <p className="message message-user">{h.demo_3}</p>
              </div>
            </div>
            <div className="demo-ritual">
              <p className="eyebrow">{h.demo_carte}</p>
              <div className="ritual-preview" aria-hidden="true">
                {[0, 1, 2].map((i) => <ImmagineCarta key={i} id="dorso" alt="" classe="card-back" />)}
                <span className="demo-caption">{h.demo_didascalia}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="band" aria-labelledby="titolo-temi">
        <div className="section-head">
          <div>
            <p className="eyebrow">{h.temi_eyebrow}</p>
            <h2 id="titolo-temi" className="section-title">{h.temi_titolo}</h2>
          </div>
          <LinkV2 className="button button-quiet" href={R.leggi}>{h.temi_cta}</LinkV2>
        </div>
        <div className="topic-grid">
          {h.temi.map((tema) => (
            <LinkV2 key={tema.chiave} className="topic" href={`${R.leggi}?topic=${tema.chiave}`} data-an="tema" data-an-tema={tema.chiave}>
              <span className="topic-icon" aria-hidden="true">{tema.simbolo}</span>
              <b>{tema.nome}</b>
              <small>{tema.nota}</small>
            </LinkV2>
          ))}
        </div>
      </section>

      <section className="band band-tight" aria-labelledby="titolo-rito">
        <p className="eyebrow">{h.rito_eyebrow}</p>
        <h2 id="titolo-rito" className="section-title">{h.rito_titolo}</h2>
        <ol className="ritual-steps list-plain">
          {h.rito_passi.map((p, i) => (
            <li key={p.titolo} className="ritual-step">
              <span aria-hidden="true">{i + 1}</span><b>{p.titolo}</b><p>{p.testo}</p>
            </li>
          ))}
        </ol>
        <Dichiarazione />
      </section>

      <section className="memory" aria-labelledby="titolo-memoria">
        <div className="band memory-layout">
          <figure className="memory-card" style={{ margin: 0 }}>
            <span className="memory-label">{h.memoria_etichetta}</span>
            <p>{h.memoria_citazione}</p>
            <footer>{h.memoria_piede}</footer>
          </figure>
          <div>
            <p className="eyebrow">{h.memoria_eyebrow}</p>
            <h2 id="titolo-memoria" className="section-title">{h.memoria_titolo}</h2>
            <ul className="memory-list">
              {h.memoria_voci.map((v) => <li key={v.titolo}><strong>{v.titolo}</strong><span>{v.testo}</span></li>)}
            </ul>
            <LinkV2 className="button button-quiet" href={R.storia}>{h.memoria_cta}</LinkV2>
          </div>
        </div>
      </section>

      <section className="band" aria-labelledby="titolo-differenza">
        <p className="eyebrow" id="titolo-differenza">{h.diff_eyebrow}</p>
        <div className="difference-grid">
          {h.diff.map((d) => (
            <article key={d.titolo} className="difference">
              <span aria-hidden="true">{d.simbolo}</span><h3>{d.titolo}</h3><p>{d.testo}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="band deck-layout" aria-labelledby="titolo-mazzi">
        <div className="deck-spread" aria-hidden="true">
          {["maj-17", "maj-06", "maj-02"].map((id) => <ImmagineCarta key={id} id={id} alt="" />)}
        </div>
        <div>
          <span className="available">{h.mazzi_disponibile}</span>
          <p className="eyebrow">{h.mazzi_eyebrow}</p>
          <h2 id="titolo-mazzi" className="section-title">{h.mazzi_titolo}</h2>
          <p className="section-intro">{h.mazzi_intro}</p>
          <div className="future-decks" aria-label={h.mazzi_futuri_aria}>
            {h.mazzi_futuri.map((m) => <span key={m}>{m}</span>)}
          </div>
          <div className="button-row">
            <LinkV2 className="button button-quiet" href={disponibile ? R.mazzo(disponibile.slug) : R.mazzi}>{h.mazzi_cta}</LinkV2>
            <LinkV2 className="button button-quiet" href={R.voto}>{h.mazzi_voto}</LinkV2>
          </div>
        </div>
      </section>

      <section className="physical" aria-labelledby="titolo-fisico">
        <div className="band physical-layout">
          <div>
            <p className="eyebrow">{h.fisico_eyebrow}</p>
            <h2 id="titolo-fisico" className="section-title">{h.fisico_titolo}</h2>
            <p className="section-intro">{h.fisico_intro}</p>
            <LinkV2 className="button" href={R.fisica} data-an="cta_fisica">{h.fisico_cta}</LinkV2>
          </div>
          <div className="physical-card">
            <ImmagineCarta id="maj-09" alt={h.fisico_carta_alt} />
            <div><h3>{h.fisico_scheda_titolo}</h3><p>{h.fisico_scheda_testo}</p></div>
          </div>
        </div>
      </section>

      <section className="band band-tight" aria-labelledby="titolo-metodo">
        <p className="eyebrow">{h.metodo_eyebrow}</p>
        <h2 id="titolo-metodo" className="section-title">{h.metodo_titolo}</h2>
        <div className="method-grid">
          {h.metodo.map((m) => <div key={m.titolo}><h3>{m.titolo}</h3><p>{m.testo}</p></div>)}
        </div>
      </section>

      <section id="method" className="funnel" aria-labelledby="titolo-funnel">
        <div className="band">
          <p className="eyebrow">{h.funnel_eyebrow}</p>
          <h2 id="titolo-funnel" className="section-title">{h.funnel_titolo}</h2>
          <p className="section-intro">{f(h.funnel_intro, { n: nIscrizione })}</p>
          <div className="funnel-steps">
            {h.funnel_passi.map((p) => <div key={p.etichetta} className="funnel-step"><b>{p.etichetta}</b><p>{p.testo}</p></div>)}
          </div>
        </div>
      </section>

      <section className="band band-tight" aria-labelledby="titolo-condividi">
        <div className="share-band">
          <div>
            <p className="eyebrow">{h.cond_eyebrow}</p>
            <h2 id="titolo-condividi" className="section-title" style={{ fontSize: "clamp(1.6rem, 3vw, 2.4rem)" }}>{h.cond_titolo}</h2>
            <p>{f(h.cond_testo, { n: nInvito })}</p>
          </div>
          <div><LinkV2 className="button button-quiet" href={`${R.profilo}#invito`}>{h.cond_cta}</LinkV2></div>
        </div>
      </section>

      <section className="band" aria-labelledby="titolo-diario">
        <div className="section-head">
          <div>
            <p className="eyebrow">{h.diario_eyebrow}</p>
            <h2 id="titolo-diario" className="section-title">{h.diario_titolo}</h2>
          </div>
          <LinkV2 className="button button-quiet" href={R.blog}>{h.diario_cta}</LinkV2>
        </div>
        <div className="content-grid">
          {articoliDiario.length > 0
            ? articoliDiario.map((a) => (
                <LinkV2 key={a.slug} className="article" href={R.articolo(a.slug)}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={urlMedia(a.immagine?.mini ?? a.immagine?.url) ?? "/cards/maj-06.webp"} alt="" loading="lazy" />
                  <small>{a.sezione?.nome ?? a.tags[0]?.nome ?? h.diario_eyebrow}</small>
                  <h3>{a.titolo}</h3>
                </LinkV2>
              ))
            : [
                { href: R.carte, img: "maj-06", ...h.diario_riserva[0] },
                { href: R.stese, img: "maj-17", ...h.diario_riserva[1] },
                { href: R.giorno, img: "maj-02", ...h.diario_riserva[2] },
              ].map((a) => (
                <LinkV2 key={a.href} className="article" href={a.href}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={`/cards/${a.img}.webp`} alt="" loading="lazy" />
                  <small>{a.etichetta}</small>
                  <h3>{a.titolo}</h3>
                </LinkV2>
              ))}
        </div>
      </section>

      <section className="band faq" aria-labelledby="titolo-faq">
        <div>
          <p className="eyebrow">{h.faq_eyebrow}</p>
          <h2 id="titolo-faq" className="section-title">{h.faq_titolo}</h2>
        </div>
        <div className="faq-list">
          {h.faq.map((q) => (
            <details key={q.d} className="faq-item"><summary>{q.d}</summary><p>{q.r}</p></details>
          ))}
        </div>
      </section>

      <section className="final" aria-labelledby="titolo-finale">
        <div className="band">
          <p className="eyebrow">{h.finale_eyebrow}</p>
          <h2 id="titolo-finale" className="display">{h.finale_titolo}</h2>
          <p>{h.finale_testo}</p>
          <LinkV2 className="button button-brass" href={R.leggi} data-an="hero_cta_click" data-an-dove="finale">{h.cta_gratis}</LinkV2>
        </div>
      </section>
    </>
  );
}
