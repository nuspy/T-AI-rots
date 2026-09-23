"use client";

/* La consultazione, dall'inizio alla fine.
 *
 * Le fasi seguono gli stati della lettura sul server:
 *
 *   stesa → intervista → pronto-mescolare → mescolamento → scelta →
 *   rivelazione → pronto-sintesi → sintesi → completata
 *
 * con `crisi` come uscita di sicurezza. L'identificativo della lettura sta
 * nell'indirizzo (`?id=…`): una pagina ricaricata, o il ritorno da un
 * pagamento, riprende la lettura dal punto in cui era.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import {
  ErroreApi,
  apriLettura,
  apriVentaglio,
  elencaStese,
  leggiConto,
  leggiDisclaimer,
  leggiLettura,
  rispondi,
  rivela,
  scegliCarta,
  sintesi,
  type Lettura,
  type Stesa,
} from "@/lib/api";
import { useLingua } from "@/lib/lingua";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import { Acquisto, Disclaimer } from "../componenti/modale";
import { Dialogo, type Battuta } from "./dialogo";
import { FaseResponso, Responso } from "./responso";
import { SceltaStesa } from "./scelta-stesa";
import { Tavolo, type Posata } from "./tavolo";
import { Mescolamento, Ventaglio } from "./ventaglio";
import stili from "./leggi.module.css";

type Fase =
  | "stesa" | "intervista" | "pronto-mescolare" | "mescolamento" | "scelta"
  | "rivelazione" | "pronto-sintesi" | "sintesi" | "completata" | "crisi" | "annullata";

let contatore = 0;
const nuovoId = () => `b${++contatore}`;

export function Lettura() {
  const { t, lingua } = useLingua();
  const sessione = useSessione();
  const router = useRouter();
  const parametri = useSearchParams();
  const idIniziale = parametri.get("id");

  const stese = useCarica(useCallback(() => elencaStese(), []), [], { pubblico: true });
  const conto = useCarica(leggiConto);

  const [fase, setFase] = useState<Fase>(idIniziale ? "intervista" : "stesa");
  const [id, setId] = useState<string | null>(idIniziale);
  const [stesaId, setStesaId] = useState<string | null>(parametri.get("stesa"));
  const [domanda, setDomanda] = useState("");
  const [disclaimer, setDisclaimer] = useState<string | null>(null);
  const [mostraDisclaimer, setMostraDisclaimer] = useState(false);
  const [mostraAcquisto, setMostraAcquisto] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);
  const [inCorso, setInCorso] = useState(false);

  const [battute, setBattute] = useState<Battuta[]>([]);
  const [attesa, setAttesa] = useState(false);

  const [slotTotali, setSlotTotali] = useState(0);
  const [scelte, setScelte] = useState<Set<number>>(new Set());
  const [posate, setPosate] = useState<Posata[]>([]);
  const [rivelazioneInCorso, setRivelazioneInCorso] = useState(false);
  const scegliendo = useRef(false);

  const [faseResponso, setFaseResponso] = useState("unione");
  const [testoResponso, setTestoResponso] = useState("");
  const [fine, setFine] = useState<{ disclaimer: string; commitment: string | null; saldo: number | null } | null>(null);
  const [condiviso, setCondiviso] = useState<string | null>(null);
  const [domandaLettura, setDomandaLettura] = useState("");

  const stesa: Stesa | undefined = useMemo(
    () => stese.dati?.find((s) => s.id === stesaId),
    [stese.dati, stesaId],
  );

  const aggiungi = (b: Omit<Battuta, "id">) => setBattute((prima) => [...prima, { ...b, id: nuovoId() }]);

  /* ---- ripresa di una lettura esistente ---- */

  const riprendi = useCallback(
    (l: Lettura) => {
      setStesaId(l.spread_id);
      setDomandaLettura(l.question);
      setDisclaimer(l.disclaimer);
      setCondiviso(l.share_token);
      const storia: Battuta[] = [
        { id: nuovoId(), autore: "sistema", testo: l.disclaimer },
        { id: nuovoId(), autore: "utente", testo: l.question },
        ...l.interview.map((x) => ({ id: nuovoId(), autore: x.ruolo, testo: x.testo })),
      ];
      if (l.context_summary) storia.push({ id: nuovoId(), autore: "oracolo", titolo: "✦", testo: l.context_summary });
      const posizioni = new Map(l.stesa_dati.posizioni.map((p) => [p.n, p]));
      for (const c of l.cards) {
        if (c.rivelata && c.interpretazione && c.carta) {
          storia.push({
            id: nuovoId(),
            autore: "oracolo",
            titolo: `${c.posizione}. ${posizioni.get(c.posizione)?.nome} — ${c.carta.nome_it}`,
            testo: c.interpretazione,
          });
        }
      }
      setBattute(storia);
      const slotScelti = l.picked_slots;
      setScelte(new Set(slotScelti));
      setSlotTotali(l.slot_count ?? 0);
      const ordinati = [...l.cards].sort((a, b) => a.posizione - b.posizione);
      let k = 0;
      setPosate(
        ordinati.map((c) => ({
          posizione: c.posizione,
          slot: c.calcolata ? null : (slotScelti[k++] ?? null),
          calcolata: c.calcolata,
          rivelata: c.rivelata,
          carta: c.carta,
          rovescio: c.rovescio,
          interpretazione: c.interpretazione,
          dignita: l.dignita?.[String(c.posizione)] ?? null,
        })),
      );
      if (l.synthesis) setTestoResponso(l.synthesis);
      const mappa: Record<string, Fase> = {
        intervista: "intervista",
        ventaglio: "pronto-mescolare",
        scelta: "scelta",
        rivelazione: "rivelazione",
        sintesi: "pronto-sintesi",
        completata: "completata",
        annullata: "annullata",
      };
      setFase(mappa[l.status] ?? "intervista");
      if (l.status === "completata") {
        setFine({ disclaimer: l.disclaimer, commitment: l.commitment, saldo: null });
      }
      return l;
    },
    [],
  );

  const passoIntervista = useCallback(
    async (lid: string, risposta: string | null) => {
      setAttesa(true);
      setErrore(null);
      try {
        const passo = await rispondi(sessione.token, lid, risposta);
        if (passo.crisi) {
          aggiungi({ autore: "sistema", testo: passo.messaggio ?? "" });
          setFase("crisi");
        } else if (passo.completa) {
          aggiungi({ autore: "oracolo", titolo: "✦", testo: passo.riassunto ?? "", macchina: true });
          setFase("pronto-mescolare");
        } else if (passo.domanda) {
          aggiungi({ autore: "oracolo", testo: passo.domanda, macchina: true });
        }
      } catch (e) {
        setErrore(e instanceof ErroreApi ? e.message : "L'oracolo non ha risposto.");
      } finally {
        setAttesa(false);
      }
    },
    [sessione.token],
  );

  /* All'arrivo con `?id=` la lettura si ricarica una volta sola. */
  const caricata = useRef(false);
  useEffect(() => {
    if (!idIniziale || caricata.current || !sessione.autenticata) return;
    caricata.current = true;
    leggiLettura(sessione.token, idIniziale)
      .then((l) => {
        riprendi(l);
        const ultima = l.interview[l.interview.length - 1];
        if (l.status === "intervista" && (!ultima || ultima.ruolo === "utente")) {
          void passoIntervista(l.id, null);
        }
      })
      .catch(() => {
        setFase("stesa");
        setId(null);
        router.replace("/leggi");
      });
  }, [idIniziale, sessione.autenticata, sessione.token, riprendi, passoIntervista, router]);

  /* ---- 1. apertura ---- */

  const senzaCrediti =
    conto.dati !== null &&
    conto.dati.limiti_attivi &&
    conto.dati.saldo <= 0 &&
    (conto.dati.uso?.letture_al_giorno?.restanti ?? 0) <= 0;

  const chiediInizio = async () => {
    if (senzaCrediti) {
      setMostraAcquisto(true);
      return;
    }
    if (!disclaimer) {
      try {
        setDisclaimer((await leggiDisclaimer(lingua)).testo);
      } catch {
        /* il disclaimer arriva comunque con la lettura */
      }
    }
    setMostraDisclaimer(true);
  };

  const inizia = async () => {
    setMostraDisclaimer(false);
    if (!stesaId) return;
    setInCorso(true);
    setErrore(null);
    try {
      const a = await apriLettura(sessione.token, stesaId, domanda.trim(), lingua);
      if (a.crisi) {
        setBattute([{ id: nuovoId(), autore: "sistema", testo: a.messaggio ?? "" }]);
        setFase("crisi");
        return;
      }
      if (!a.id) return;
      setId(a.id);
      setDomandaLettura(domanda.trim());
      router.replace(`/leggi?id=${a.id}`);
      setBattute([
        { id: nuovoId(), autore: "sistema", testo: a.disclaimer ?? "" },
        { id: nuovoId(), autore: "utente", testo: domanda.trim() },
      ]);
      setFase("intervista");
      conto.ricarica();
      await passoIntervista(a.id, null);
    } catch (e) {
      if (e instanceof ErroreApi && e.stato === 402) setMostraAcquisto(true);
      else setErrore(e instanceof ErroreApi ? e.message : "La lettura non è partita.");
    } finally {
      setInCorso(false);
    }
  };

  /* ---- 2. intervista ---- */

  const suRisposta = (testo: string) => {
    if (!id) return;
    aggiungi({ autore: "utente", testo });
    void passoIntervista(id, testo);
  };

  /* ---- 3. mescolamento e scelta ---- */

  const mescola = async () => {
    if (!id) return;
    setFase("mescolamento");
    setErrore(null);
    try {
      const [v] = await Promise.all([
        apriVentaglio(sessione.token, id),
        new Promise((ok) => setTimeout(ok, 2200)),
      ]);
      setSlotTotali(v.slot_count);
      setScelte(new Set(v.picked_slots));
      setFase("scelta");
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "Il mazzo non si è aperto.");
      setFase("pronto-mescolare");
    }
  };

  const scegli = async (slot: number) => {
    if (!id || scegliendo.current || scelte.has(slot)) return;
    scegliendo.current = true;
    try {
      const r = await scegliCarta(sessione.token, id, slot);
      setScelte((s) => new Set(s).add(slot));
      setPosate((p) => [
        ...p,
        { posizione: r.posizione, slot, calcolata: false, rivelata: false },
        ...(r.tutte_scelte
          ? r.posizioni_calcolate.map((n) => ({ posizione: n, slot: null, calcolata: true, rivelata: false }))
          : []),
      ]);
      if (r.tutte_scelte) setTimeout(() => setFase("rivelazione"), 700);
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "La carta non è stata posata.");
    } finally {
      scegliendo.current = false;
    }
  };

  /* ---- 4. rivelazione ---- */

  const prossimaDaRivelare = useMemo(() => {
    const coperte = posate.filter((p) => !p.rivelata).map((p) => p.posizione);
    return coperte.length ? Math.min(...coperte) : null;
  }, [posate]);

  const prossimaDaScegliere = useMemo(() => {
    if (!stesa) return null;
    const occupate = new Set(posate.map((p) => p.posizione));
    return stesa.posizioni.find((p) => !p.calcolata && !occupate.has(p.n))?.n ?? null;
  }, [stesa, posate]);

  const rivelaCarta = async (posizione: number) => {
    if (!id || !stesa || rivelazioneInCorso) return;
    setRivelazioneInCorso(true);
    setErrore(null);
    const pos = stesa.posizioni.find((p) => p.n === posizione);
    const bid = nuovoId();
    const aggiornaPosata = (f: (p: Posata) => Posata) =>
      setPosate((tutte) => tutte.map((p) => (p.posizione === posizione ? f(p) : p)));
    const aggiornaBattuta = (f: (b: Battuta) => Battuta) =>
      setBattute((tutte) => tutte.map((b) => (b.id === bid ? f(b) : b)));
    try {
      for await (const ev of rivela(sessione.token, id, posizione)) {
        if (ev.tipo === "carta") {
          aggiornaPosata((p) => ({
            ...p, rivelata: true, carta: ev.carta, rovescio: ev.rovescio, dignita: ev.dignita, doppia: ev.doppia_valenza,
          }));
          setBattute((b) => [
            ...b,
            {
              id: bid,
              autore: "oracolo",
              titolo: `${posizione}. ${lingua === "en" ? pos?.nome_en : pos?.nome} — ${ev.carta.nome_it}${ev.rovescio ? ` (${t.rovesciata})` : ""}`,
              testo: "",
              inCorso: true,
            },
          ]);
        } else if (ev.tipo === "token") {
          aggiornaBattuta((b) => ({ ...b, testo: b.testo + ev.testo }));
          aggiornaPosata((p) => ({ ...p, interpretazione: (p.interpretazione ?? "") + ev.testo }));
        } else if (ev.tipo === "sostituisci") {
          aggiornaBattuta((b) => ({ ...b, testo: ev.testo }));
          aggiornaPosata((p) => ({ ...p, interpretazione: ev.testo }));
        } else if (ev.tipo === "errore") {
          setErrore(ev.messaggio);
        } else if (ev.tipo === "fine") {
          aggiornaBattuta((b) => ({ ...b, testo: ev.interpretazione || b.testo, inCorso: false }));
          aggiornaPosata((p) => ({ ...p, interpretazione: ev.interpretazione || p.interpretazione }));
          if (ev.ultima) setFase("pronto-sintesi");
        }
      }
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "La carta non si è girata.");
    } finally {
      setRivelazioneInCorso(false);
    }
  };

  /* ---- 5. responso ---- */

  const chiediResponso = async () => {
    if (!id) return;
    setFase("sintesi");
    setFaseResponso("unione");
    setTestoResponso("");
    setErrore(null);
    try {
      for await (const ev of sintesi(sessione.token, id)) {
        if (ev.tipo === "fase") setFaseResponso(ev.fase);
        else if (ev.tipo === "token") setTestoResponso((x) => x + ev.testo);
        else if (ev.tipo === "errore") {
          setErrore(ev.messaggio);
          setFase("pronto-sintesi");
          return;
        } else if (ev.tipo === "fine") {
          setFine({ disclaimer: ev.disclaimer, commitment: ev.commitment, saldo: ev.saldo });
          setFase("completata");
          conto.ricarica();
        }
      }
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "Il responso non è arrivato.");
      setFase("pronto-sintesi");
    }
  };

  const nuova = () => {
    setFase("stesa");
    setId(null);
    setBattute([]);
    setPosate([]);
    setScelte(new Set());
    setTestoResponso("");
    setFine(null);
    setDomanda("");
    setCondiviso(null);
    caricata.current = true;
    router.replace("/leggi");
  };

  /* ---- disegno ---- */

  if (fase === "stesa") {
    return (
      <>
        {stese.errore && <p className={stili.errore}>{stese.errore}</p>}
        {senzaCrediti && (
          <p className={`pannello ${stili.bandaCrediti}`}>
            {t.crediti_finiti}. <a href="/piano?ritorno=/leggi">{t.compra}</a>
          </p>
        )}
        {stese.dati && (
          <SceltaStesa
            stese={stese.dati}
            scelta={stesaId}
            onScegli={setStesaId}
            domanda={domanda}
            onDomanda={setDomanda}
            onInizia={chiediInizio}
            inCorso={inCorso}
            errore={errore}
          />
        )}
        <Disclaimer
          aperta={mostraDisclaimer}
          testo={disclaimer ?? ""}
          onAccetta={inizia}
          onChiudi={() => setMostraDisclaimer(false)}
        />
        <Acquisto aperta={mostraAcquisto} onChiudi={() => setMostraAcquisto(false)} ritorno="/leggi" />
      </>
    );
  }

  const daScegliere = stesa ? stesa.carte_da_scegliere - posate.filter((p) => !p.calcolata).length : 0;

  return (
    <div className={stili.consulto}>
      <div className={stili.colonnaTavolo}>
        <div className={stili.intestazione}>
          <span className={stili.stesaEtichetta}>{stesa ? (lingua === "en" ? stesa.nome_en : stesa.nome) : ""}</span>
          <p className={`oracolo ${stili.domandaTitolo}`}>«{domandaLettura}»</p>
        </div>

        <LayoutGroup>
          {stesa && (
            <Tavolo
              stesa={stesa}
              posate={posate}
              prossima={fase === "scelta" ? prossimaDaScegliere : fase === "rivelazione" ? prossimaDaRivelare : null}
              onRivela={rivelaCarta}
              rivelazioneInCorso={rivelazioneInCorso}
              evidenzia={fase === "scelta" ? "scelta" : fase === "rivelazione" ? "rivelazione" : null}
            />
          )}

          <AnimatePresence mode="wait">
            {fase === "mescolamento" && (
              <motion.div key="m" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className={stili.zonaAzione}>
                <Mescolamento />
                <p className="oracolo">{t.mescolando}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {fase === "scelta" && (
            <div className={stili.zonaVentaglio}>
              <p className={stili.istruzione}>{t.scegli_n(daScegliere)}</p>
              <Ventaglio quante={slotTotali} scelte={scelte} attivo={daScegliere > 0} onScegli={scegli} />
            </div>
          )}
        </LayoutGroup>

        <div className={stili.zonaAzione}>
          {fase === "pronto-mescolare" && (
            <motion.button className="bottone" onClick={mescola} initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}>
              ✦ {t.mescola}
            </motion.button>
          )}
          {fase === "rivelazione" && prossimaDaRivelare !== null && (
            <>
              <p className={stili.istruzione}>{t.tocca_per_rivelare}</p>
              <button className="bottone-secondario" disabled={rivelazioneInCorso}
                onClick={() => rivelaCarta(prossimaDaRivelare)}>
                {t.rivela} {prossimaDaRivelare}
              </button>
            </>
          )}
          {fase === "pronto-sintesi" && (
            <motion.button className="bottone" onClick={chiediResponso} initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}>
              ✦ {t.responso}
            </motion.button>
          )}
          {errore && <p className={stili.errore} role="alert">{errore}</p>}
        </div>
      </div>

      <div className={stili.colonnaDialogo}>
        <Dialogo
          battute={battute}
          attesa={attesa}
          inputAttivo={fase === "intervista"}
          onRispondi={suRisposta}
        />
      </div>

      {(fase === "sintesi" || fase === "completata") && stesa && id && (
        <div className={stili.zonaResponso}>
          {fase === "sintesi" && !testoResponso && <FaseResponso fase={faseResponso} />}
          {testoResponso && (
            <Responso
              id={id}
              domanda={domandaLettura}
              stesa={stesa}
              posate={posate}
              testo={testoResponso}
              finito={fase === "completata"}
              disclaimer={fine?.disclaimer ?? disclaimer ?? ""}
              commitment={fine?.commitment ?? null}
              condivisoIniziale={condiviso}
              saldo={fine?.saldo ?? null}
              onNuova={nuova}
            />
          )}
        </div>
      )}

      {(fase === "crisi" || fase === "annullata") && (
        <div className={stili.zonaResponso}>
          <button className="bottone-secondario" onClick={nuova}>{t.nuova_lettura}</button>
        </div>
      )}
      <Acquisto aperta={mostraAcquisto} onChiudi={() => setMostraAcquisto(false)} ritorno="/leggi" />
    </div>
  );
}
