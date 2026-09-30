"use client";

/* La parte che si disegna nel browser di chi apre il link: domanda, carte e
 * responso. Niente colloquio, niente nome. Nelle letture di coppia l'altra persona
 * non ha nome: il server ha scritto «qualcuno di speciale» e questa pagina mostra
 * il simbolo del suo genere.
 *
 * Due cose in più rispetto a una pagina di sola lettura, entrambe per chi ha
 * condiviso: dopo qualche secondo a schermo il browser dice al server che il link è
 * stato aperto (è ciò che rende «verificata» una condivisione), e ricorda da quale
 * link si arriva, così che l'iscrizione, se avviene, sia attribuita
 * (`AttribuzioneCondivisione`). */

import { useCallback, useEffect } from "react";
import Link from "@/app/(sito)/componenti/link";
import { leggiCondivisa, registraVisita } from "@/lib/api";
import { CREDITI_ISCRIZIONE, idVisitatore, ricordaOrigine } from "@/lib/condivisione";
import { comeLingua, nomeStesa } from "@/lib/i18n";
import { LinguaNomi, useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { LATO_SIMBOLO, PERCORSI_SIMBOLI, simboloDi } from "@/lib/simboli";
import { useCarica } from "@/lib/usa";
import { Markdown } from "../../componenti/markdown";
import { Involucro } from "../../componenti/testata";
import { Tavolo, type Posata } from "../../leggi/tavolo";
import stili from "../../leggi/leggi.module.css";

/* Quanto deve restare aperta la pagina per contare come una visita vera. */
const SECONDI_DI_LETTURA = 4;

export function PaginaCondivisa({ token }: { token: string }) {
  return (
    <Involucro larga pubblica>
      <Condivisa token={token} />
    </Involucro>
  );
}

/* Il simbolo grafico dell'altra persona, tracciato a solo contorno come sulle carte. */
function SimboloPartner({ nome }: { nome: string | null }) {
  const simbolo = simboloDi(nome);
  return (
    <svg
      className={stili.simboloPartner}
      viewBox={`0 0 ${LATO_SIMBOLO} ${LATO_SIMBOLO}`}
      aria-hidden="true"
      focusable="false"
    >
      <path
        d={PERCORSI_SIMBOLI[simbolo]}
        fill={simbolo === "stella" ? "rgba(241,214,142,0.16)" : "none"}
        stroke="currentColor"
        strokeWidth="3.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function Condivisa({ token }: { token: string }) {
  const { t, lingua } = useLingua();
  const sessione = useSessione();
  const l = useCarica(useCallback(() => leggiCondivisa(token), [token]), [token], { pubblico: true });
  const esiste = !!l.dati;

  /* La lettura esiste ed è aperta a schermo: si ricorda il link e, dopo qualche
   * secondo di pagina visibile, si conta la visita. Un crawler non esegue questo
   * codice, e il server scarta comunque i suoi User-Agent. */
  useEffect(() => {
    if (!esiste) return;
    ricordaOrigine(token);
    const timer = window.setTimeout(() => {
      if (document.visibilityState === "visible") void registraVisita(token, idVisitatore());
    }, SECONDI_DI_LETTURA * 1000);
    return () => window.clearTimeout(timer);
  }, [esiste, token]);

  if (l.errore) return <p className={stili.errore}>{l.errore}</p>;
  if (!l.dati || !l.dati.stesa) return null;
  const d = l.dati;
  const posate: Posata[] = d.cards.map((c) => ({ ...c, slot: null, dignita: null }));
  /* Chi riceve il link legge nella lingua del quesito: i nomi la seguono. */
  const ll = comeLingua(d.lang) ?? lingua;
  return (
    <LinguaNomi valore={ll}>
      <div>
        <div className={stili.intestazione}>
          <span className={stili.stesaEtichetta}>{nomeStesa(d.stesa!, ll)}</span>
          {d.share_text && <p className={`oracolo ${stili.testoCondiviso}`} dir="auto">{d.share_text}</p>}
          {d.speciale && (
            <p className={stili.altraPersona}>
              <SimboloPartner nome={d.partner_simbolo} />
              <span dir="auto">{d.partner_frase}</span>
            </p>
          )}
          <p className={`oracolo ${stili.domandaTitolo}`} dir="auto">«{d.question}»</p>
        </div>
        <Tavolo
          stesa={d.stesa!}
          posate={posate}
          prossima={null}
          rivelazioneInCorso={false}
          evidenzia={null}
          nomePartner={d.partner_frase}
        />
        <div className={stili.zonaResponso}>
          <section className={`pannello ${stili.responso}`}>
            <h2 className={stili.responsoTitolo}>✦ {t.il_responso} ✦</h2>
            {d.synthesis && <Markdown testo={d.synthesis} className={`oracolo ${stili.responsoTesto}`} />}
            <p className={stili.disclaimerFinale}>{d.disclaimer}</p>
            {!sessione.autenticata && (
              <p className={stili.avviso}>{t.pub_invito(CREDITI_ISCRIZIONE)}</p>
            )}
            <div className={stili.azioniCentro}>
              {!sessione.autenticata && (
                <button className="bottone" onClick={sessione.registrati}>✦ {t.pub_iscriviti}</button>
              )}
              <Link href="/leggi" className={sessione.autenticata ? "bottone" : "bottone-secondario"}>
                ✦ {t.inizia}
              </Link>
              <Link href="/carta-del-giorno" className="bottone-secondario">☉ {t.nav_giorno}</Link>
            </div>
          </section>
        </div>
      </div>
    </LinguaNomi>
  );
}
