"use client";

/* Una lettura condivisa, nella v2 (specifica v2, §13): ogni condivisione è una porta d'ingresso. Chi apre il link
 * vede le parole di chi ha condiviso, la domanda, le carte e l'interpretazione — mai il nome, mai il colloquio —
 * e l'invito a cominciare la propria lettura, gratuita.
 *
 * Come nel sito: dopo qualche secondo di pagina visibile la visita si conta (è ciò che rende «verificata» una
 * condivisione), e il link si ricorda per attribuire un'eventuale iscrizione a chi l'ha condiviso. */

import { ProviderMazzoAttivo } from "@/lib/mazzo-attivo";
import { useEffect } from "react";
import { Markdown } from "@/lib/markdown";
import { impostazioniPubbliche, leggiCondivisa, registraVisita } from "@/lib/api";
import { CREDITI_ISCRIZIONE, idVisitatore, ricordaOrigine } from "@/lib/condivisione";
import { comeLingua } from "@/lib/i18n/lingue";
import { nomeStesa } from "@/lib/i18n/nomi";
import { useSessione } from "@/lib/sessione";
import { LATO_SIMBOLO, PERCORSI_SIMBOLI, simboloDi } from "@/lib/simboli";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { Tavolo, type Posata } from "@/v2/lettura/tavolo";
import stili from "@/v2/lettura/lettura.module.css";
import { P } from "@/v2/lib/dati";
import { LinguaNomi, useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";

const SECONDI_DI_LETTURA = 4;

function SimboloPartner({ nome }: { nome: string | null }) {
  const simbolo = simboloDi(nome);
  return (
    <svg viewBox={`0 0 ${LATO_SIMBOLO} ${LATO_SIMBOLO}`} width="28" height="28" aria-hidden="true" focusable="false"
      style={{ verticalAlign: "middle", marginRight: ".4rem", color: "var(--brass-pale)" }}>
      <path d={PERCORSI_SIMBOLI[simbolo]} fill="none" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Condivisa({ token }: { token: string }) {
  const { t, lingua } = useLingua();
  const c = t.condivisa;
  const sessione = useSessione();
  const l = useCarica(() => leggiCondivisa(token), [token], { pubblico: true, iniziale: P.condivisa(token) });
  const omaggi = useCarica(impostazioniPubbliche, [], { pubblico: true, iniziale: P.impostazioni() });
  const esiste = !!l.dati;

  useEffect(() => {
    if (!esiste) return;
    ricordaOrigine(token);
    const timer = window.setTimeout(() => {
      if (document.visibilityState === "visible") void registraVisita(token, idVisitatore());
    }, SECONDI_DI_LETTURA * 1000);
    return () => window.clearTimeout(timer);
  }, [esiste, token]);

  if (l.errore) {
    return (
      <section className="band band-tight">
        <p className="eyebrow">{c.eyebrow}</p>
        <h1 className="display" style={{ fontSize: "clamp(2rem, 4vw, 3.4rem)" }}>{c.non_trovata_titolo}</h1>
        <p className="section-intro">{c.non_trovata_testo}</p>
        <LinkV2 className="button button-brass" href={`${R.leggi}?source=share`}>{c.inizia}</LinkV2>
      </section>
    );
  }
  if (!l.dati || !l.dati.stesa) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const d = l.dati;
  const stesa = d.stesa!;
  const posate: Posata[] = d.cards.map((x) => ({ ...x, slot: null, dignita: null }));
  const ll = comeLingua(d.lang) ?? lingua;
  const invitoN = omaggi.dati?.crediti_iscrizione ?? CREDITI_ISCRIZIONE;

  return (
    <ProviderMazzoAttivo slug={d.mazzo ?? null}>
    <LinguaNomi valore={ll}>
      <section className="subhero subhero-compact">
        <p className="eyebrow">{c.eyebrow}</p>
        <div className="static-share">
          <q dir="auto">{d.share_text || c.titolo_predefinito}</q>
          <p>{c.nota}</p>
        </div>
      </section>
      <section className="band band-tight">
        <div className={stili.scena}>
          <small>{nomeStesa(stesa, ll)}</small>
          {d.speciale && d.partner_frase && (
            <p style={{ margin: 0 }}><SimboloPartner nome={d.partner_simbolo} /><span dir="auto">{d.partner_frase}</span></p>
          )}
          <q dir="auto">{d.question}</q>
        </div>
        <div className="read-panel dark">
          <Tavolo stesa={stesa} posate={posate} prossima={null} rivelazioneInCorso={false} evidenzia={null} nomePartner={d.partner_frase} />
        </div>
        {d.synthesis && (
          <section className={stili.responso} style={{ marginTop: "2rem" }} aria-labelledby="titolo-condivisa">
            <h2 id="titolo-condivisa">{c.l_interpretazione}</h2>
            <Markdown testo={d.synthesis} className={stili.testo} />
            <p className={stili.avvertenza}>{d.disclaimer}</p>
          </section>
        )}
      </section>
      <section className="final">
        <div className="band">
          <h2 className="display">{c.invito_titolo}</h2>
          <p>{f(c.invito_testo, { n: invitoN })}</p>
          <div className="button-row" style={{ justifyContent: "center" }}>
            <LinkV2 className="button button-brass" href={`${R.leggi}?source=share`} data-an="cta_condivisa">{c.inizia}</LinkV2>
            {!sessione.autenticata && sessione.pronta && (
              <button type="button" className="button button-light" onClick={sessione.registrati} data-an="cta_iscrizione" data-an-dove="condivisa">
                {c.iscriviti}
              </button>
            )}
            <LinkV2 className="button button-light" href={R.giorno}>{c.giorno}</LinkV2>
          </div>
        </div>
      </section>
    </LinguaNomi>
    </ProviderMazzoAttivo>
  );
}
