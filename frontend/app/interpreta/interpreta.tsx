"use client";

/* "Interpreta i miei tarocchi" (v5): il mazzo è fisico, già estratto — niente ventaglio, l'utente
 * dice quali carte sono uscite e in quale posizione, poi la lettura procede come sempre (domanda,
 * intervista, interpretazione, sintesi).
 *
 * Fasi, solo locali finché non si crea la lettura vera:
 *   stesa → posizionamento → domanda
 * Alla conferma si chiama la stessa POST /readings di sempre, con `manual_cards`, e si passa la mano
 * alla pagina di lettura normale (`/leggi?id=…`), che da lì in poi non sa — e non deve sapere —
 * che le carte non sono uscite dal ventaglio. */

import { useCallback, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ErroreApi, apriLettura, elencaCarte, elencaStese, leggiDisclaimer, type Stesa,
} from "@/lib/api";
import { nomeStesa } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import { Disclaimer } from "../componenti/modale";
import { MiniaturaStesa } from "../componenti/miniatura-stesa";
import { Tavolo, type Posata } from "../leggi/tavolo";
import { DialogoCarta } from "./dialogo-carta";
import stili from "../leggi/leggi.module.css";
import propri from "./interpreta.module.css";

type Fase = "stesa" | "posizionamento" | "domanda";

export function Interpreta() {
  const { t, lingua } = useLingua();
  const sessione = useSessione();
  const router = useRouter();

  const stese = useCarica(useCallback(() => elencaStese("standard", lingua), [lingua]), [lingua], { pubblico: true });
  const carte = useCarica(useCallback(() => elencaCarte(lingua), [lingua]), [lingua], { pubblico: true });

  const [fase, setFase] = useState<Fase>("stesa");
  const [stesaId, setStesaId] = useState<string | null>(null);
  const [assegnazioni, setAssegnazioni] = useState<Record<number, string>>({});
  const [posizioneAttiva, setPosizioneAttiva] = useState<number | null>(null);
  const [domanda, setDomanda] = useState("");
  const [disclaimer, setDisclaimer] = useState<string | null>(null);
  const [mostraDisclaimer, setMostraDisclaimer] = useState(false);
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);

  const stesa: Stesa | undefined = useMemo(() => stese.dati?.find((s) => s.id === stesaId), [stese.dati, stesaId]);
  const posizioniDaRiempire = useMemo(
    () => (stesa ? stesa.posizioni.filter((p) => !p.calcolata) : []),
    [stesa],
  );
  const complete = stesa ? posizioniDaRiempire.every((p) => assegnazioni[p.n]) : false;
  const occupate = useMemo(() => new Set(Object.values(assegnazioni)), [assegnazioni]);

  const posate: Posata[] = useMemo(
    () =>
      Object.entries(assegnazioni).map(([posizione, cardId]) => ({
        posizione: Number(posizione),
        slot: null,
        calcolata: false,
        rivelata: false,
        carta: (carte.dati ?? []).find((c) => c.id === cardId),
      })),
    [assegnazioni, carte.dati],
  );

  const nomePosizioneAttiva =
    posizioneAttiva !== null ? stesa?.posizioni.find((p) => p.n === posizioneAttiva)?.nome ?? "" : "";

  const scegliStesa = (id: string) => {
    setStesaId(id);
    setAssegnazioni({});
    setFase("posizionamento");
  };

  const confermaCarta = (cardId: string) => {
    if (posizioneAttiva === null) return;
    setAssegnazioni((a) => ({ ...a, [posizioneAttiva]: cardId }));
  };

  const chiediDomanda = async () => {
    if (!disclaimer) {
      try {
        setDisclaimer((await leggiDisclaimer(lingua)).testo);
      } catch {
        /* il disclaimer arriva comunque con la lettura */
      }
    }
    setFase("domanda");
  };

  const apri = async () => {
    if (!stesaId || domanda.trim().length < 3) return;
    setMostraDisclaimer(false);
    setInCorso(true);
    setErrore(null);
    try {
      const a = await apriLettura(sessione.token, {
        spreadId: stesaId,
        domanda: domanda.trim(),
        lang: lingua,
        manualCards: Object.entries(assegnazioni).map(([posizione, cardId]) => ({
          posizione: Number(posizione), cardId,
        })),
      });
      if (a.id) router.replace(`/leggi?id=${a.id}`);
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : t.err_lettura);
      setInCorso(false);
    }
  };

  if (fase === "stesa" || !stesa) {
    return (
      <div className={propri.pagina}>
        <h1 className={stili.passo}>{t.interpreta_titolo}</h1>
        <p className="oracolo">{t.interpreta_intro}</p>
        <h2 className={stili.passo}><span>I</span> {t.interpreta_scegli_stesa}</h2>
        {stese.errore && <p className={stili.errore}>{stese.errore}</p>}
        <div className={stili.stese}>
          {(stese.dati ?? []).map((s, i) => (
            <motion.button
              key={s.id}
              type="button"
              className={stili.stesa}
              onClick={() => scegliStesa(s.id)}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.06 * i, type: "spring", stiffness: 160, damping: 20 }}
              whileHover={{ y: -4 }}
            >
              <MiniaturaStesa stesa={s} animata className={stili.miniatura} />
              <span className={stili.stesaNome}>{nomeStesa(s, lingua)}</span>
            </motion.button>
          ))}
        </div>
      </div>
    );
  }

  if (fase === "posizionamento") {
    return (
      <div className={propri.pagina}>
        <h2 className={stili.passo}><span>II</span> {t.interpreta_posiziona_titolo}</h2>
        <p className={stili.istruzione}>{t.interpreta_posiziona_istruzione}</p>
        <Tavolo
          stesa={stesa}
          posate={posate}
          prossima={null}
          rivelazioneInCorso={false}
          evidenzia={null}
          manuale
          onSelezionaPosizione={setPosizioneAttiva}
        />
        {errore && <p className={stili.errore} role="alert">{errore}</p>}
        <div className={stili.azioniCentro}>
          <button type="button" className="bottone-secondario" onClick={() => setFase("stesa")}>{t.indietro}</button>
          <button type="button" className="bottone" disabled={!complete} onClick={chiediDomanda}>
            ✦ {t.interpreta_posizionamento_completo}
          </button>
        </div>
        <DialogoCarta
          aperta={posizioneAttiva !== null}
          nomePosizione={nomePosizioneAttiva}
          carte={carte.dati ?? []}
          occupate={occupate}
          onConferma={confermaCarta}
          onChiudi={() => setPosizioneAttiva(null)}
        />
      </div>
    );
  }

  return (
    <div className={propri.pagina}>
      <h2 className={stili.passo}><span>III</span> {t.la_tua_domanda}</h2>
      <textarea
        className={stili.domanda}
        value={domanda}
        onChange={(e) => setDomanda(e.target.value)}
        placeholder={t.domanda_segnaposto}
        dir="auto"
        maxLength={1000}
        rows={3}
        aria-label={t.la_tua_domanda}
      />
      {errore && <p className={stili.errore} role="alert">{errore}</p>}
      <div className={stili.azioniCentro}>
        <button type="button" className="bottone-secondario" onClick={() => setFase("posizionamento")}>{t.indietro}</button>
        <button className="bottone" disabled={domanda.trim().length < 3 || inCorso} onClick={() => setMostraDisclaimer(true)}>
          ✦ {t.inizia}
        </button>
      </div>
      <Disclaimer
        aperta={mostraDisclaimer}
        testo={disclaimer ?? ""}
        onAccetta={apri}
        onChiudi={() => setMostraDisclaimer(false)}
      />
    </div>
  );
}
