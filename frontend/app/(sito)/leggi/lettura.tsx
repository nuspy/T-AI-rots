"use client";

/* La consultazione, dall'inizio alla fine.
 *
 * Le fasi seguono gli stati della lettura sul server:
 *
 *   tipo → [persone → stile | stesa] → intervista → pronto-mescolare →
 *   mescolamento → taglio → scelta → rivelazione → pronto-sintesi → sintesi →
 *   completata
 *
 * Le prime fasi sono solo del client. La lettura standard passa da `stesa`; le
 * letture di compatibilità e di coppia da `persone` (i dati di chi consulta che
 * mancano e quelli dell'altra persona) e da `stile` (la stesa, per stile). Dopo
 * l'apertura il percorso è lo stesso per tutte.
 *
 * con `crisi` come uscita di sicurezza. L'identificativo della lettura sta
 * nell'indirizzo (`?id=…`): una pagina ricaricata, o il ritorno da un
 * pagamento, riprende la lettura dal punto in cui era.
 *
 * Il mescolamento dura finché chi consulta non clicca il mazzo; poi taglia il
 * mazzo cliccando nel punto voluto, e solo allora il server lo fissa.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import { useTraccia } from "lanterna-osservatore/react";
import {
  ErroreApi,
  aggiornaProfilo,
  apriLettura,
  apriLetturaAnonima,
  apriVentaglio,
  cancellaPartner,
  elencaMazzi,
  elencaStese,
  leggiConto,
  leggiDisclaimer,
  leggiLettura,
  leggiProfilo,
  rispondi,
  rivela,
  scegliCarta,
  sintesi,
  type Categoria,
  type Genere,
  type Lettura,
  type Stesa,
} from "@/lib/api";
import Link from "@/app/(sito)/componenti/link";
import { comeLingua, dizionario, nomeCarta, nomePosizione, nomeStesa, type Lingua } from "@/lib/i18n";
import { LinguaNomi, useLingua } from "@/lib/lingua";
import { ProviderMazzoAttivo } from "@/lib/mazzo-attivo";
import { useSessione } from "@/lib/sessione";
import { useCarica } from "@/lib/usa";
import { Acquisto, Disclaimer } from "../componenti/modale";
import { Dialogo, type Battuta } from "./dialogo";
import { FormPersone, partnerDa, personeDaProfilo, personeVuote, type DatiPersone } from "./form-persone";
import { FaseResponso, Responso } from "./responso";
import { SceltaStesa } from "./scelta-stesa";
import { SceltaTipo } from "./scelta-tipo";
import { Tavolo, type Posata } from "./tavolo";
import { Mescolamento, Taglio, Ventaglio } from "./ventaglio";
import stili from "./leggi.module.css";

type Fase =
  | "tipo" | "persone" | "stile" | "stesa" | "intervista" | "pronto-mescolare" | "mescolamento" | "taglio" | "scelta"
  | "rivelazione" | "pronto-sintesi" | "sintesi" | "completata" | "crisi" | "annullata";

const comeCategoria = (v: string | null): Categoria | null =>
  v === "standard" || v === "compatibilita" || v === "coppia" ? v : null;

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
  const profilo = useCarica(leggiProfilo);
  /* v7, Fase J: il mazzo di default dell'utente, se ne ha scelto uno diverso dal predefinito
   * globale — precompila l'artwork della lettura, senza un cambio a metà stesa (fuori scope qui). */
  const mazziDisponibili = useCarica(() => elencaMazzi(), [], { pubblico: true });
  const slugMazzoAttivo = mazziDisponibili.dati?.find(
    (m) => m.id === profilo.dati?.mazzo_predefinito_id && !m.predefinito,
  )?.slug ?? null;

  /* Dall'indirizzo: `?id=` riprende una lettura; `?tipo=` salta la scelta del tipo;
   * `?stesa=` (i link della soglia) porta alla stesa, o ai dati delle persone se
   * la stesa è di compatibilità o di coppia (lo si sa quando le stese arrivano). */
  const tipoIniziale = comeCategoria(parametri.get("tipo"));
  const stesaIniziale = parametri.get("stesa");
  const [fase, setFase] = useState<Fase>(
    idIniziale ? "intervista"
      : tipoIniziale === "standard" || (!tipoIniziale && stesaIniziale) ? "stesa"
        : tipoIniziale ? "persone" : "tipo",
  );
  const [categoria, setCategoria] = useState<Categoria>(tipoIniziale ?? "standard");
  const [persone, setPersone] = useState<DatiPersone>(personeVuote);
  const [nomePartner, setNomePartner] = useState<string | null>(null);
  const [id, setId] = useState<string | null>(idIniziale);
  const [stesaId, setStesaId] = useState<string | null>(stesaIniziale);
  /* `?domanda=` (dalla chat proattiva, v6 Fase E, o dal banner "fammi una domanda", Fase F):
   * precompila il campo del quesito senza inviarlo — resta modificabile dall'utente. Letto una
   * sola volta al mount, come `idIniziale`/`tipoIniziale`. */
  const [domanda, setDomanda] = useState(() => parametri.get("domanda") ?? "");
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
  const [fine, setFine] = useState<
    { disclaimer: string; commitment: string | null; saldo: number | null; anonimo?: boolean } | null
  >(null);
  const [domandaLettura, setDomandaLettura] = useState("");
  /* La lingua del quesito, ricavata dal server all'apertura e salvata con la
   * lettura: domande, interpretazioni e responso escono in questa lingua, e i
   * nomi di carte e stese la seguono. Ogni nuovo quesito la rinnova. */
  const [linguaLettura, setLinguaLettura] = useState<Lingua | null>(null);
  /* "Interpreta i miei tarocchi" (v5): il mazzo è fisico — le carte si vedono scoperte da subito. */
  const [manuale, setManuale] = useState(false);
  const ll: Lingua = linguaLettura ?? lingua;

  const stesa: Stesa | undefined = useMemo(
    () => stese.dati?.find((s) => s.id === stesaId),
    [stese.dati, stesaId],
  );
  const stesePerCategoria = useMemo(
    () => (stese.dati ?? []).filter((s) => s.categoria === categoria),
    [stese.dati, categoria],
  );
  const speciale = categoria !== "standard";

  /* Analytics (v8): ogni fase raggiunta è un passo dell'imbuto della lettura. Solo la fase e il
   * tipo, mai la domanda né le carte. */
  const traccia = useTraccia();
  useEffect(() => {
    // Solo a sessione pronta: prima «autenticata» vale falso per tutti e la stessa fase uscirebbe due volte.
    if (sessione.pronta) traccia("lettura_fase", { fase, categoria, anonima: !sessione.autenticata });
  }, [traccia, fase, categoria, sessione.pronta, sessione.autenticata]);

  /* Il modulo si precompila una volta dal partner ricordato nel profilo. */
  const precompilato = useRef(false);
  useEffect(() => {
    if (precompilato.current || !profilo.dati) return;
    precompilato.current = true;
    setPersone((prima) => personeDaProfilo(profilo.dati!, prima));
  }, [profilo.dati]);

  /* `?stesa=<speciale>`: appena si sa di che categoria è, si passa ai dati delle persone. */
  useEffect(() => {
    if (fase !== "stesa" || !stese.dati || !stesaId) return;
    const s = stese.dati.find((x) => x.id === stesaId);
    if (s && s.categoria !== "standard") {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setCategoria(s.categoria);
      setFase("persone");
    }
  }, [fase, stese.dati, stesaId]);

  const aggiungi = (b: Omit<Battuta, "id">) => setBattute((prima) => [...prima, { ...b, id: nuovoId() }]);

  /* ---- ripresa di una lettura esistente ---- */

  const riprendi = useCallback(
    (l: Lettura) => {
      setStesaId(l.spread_id);
      setCategoria(l.categoria);
      setNomePartner(l.persone?.partner.nome ?? null);
      setLinguaLettura(comeLingua(l.lang));
      setManuale(l.manuale);
      setDomandaLettura(l.question);
      setDisclaimer(l.disclaimer);
      const storia: Battuta[] = [
        { id: nuovoId(), autore: "utente", testo: l.question },
        ...l.interview.map((x) => ({ id: nuovoId(), autore: x.ruolo, testo: x.testo })),
      ];
      if (l.context_summary) storia.push({ id: nuovoId(), autore: "oracolo", titolo: "✦", testo: l.context_summary });
      const lingueLettura = comeLingua(l.lang) ?? lingua;
      const posizioni = new Map(l.stesa_dati.posizioni.map((p) => [p.n, p]));
      for (const c of l.cards) {
        if (c.rivelata && c.interpretazione && c.carta) {
          storia.push({
            id: nuovoId(),
            autore: "oracolo",
            titolo: `${c.posizione}. ${nomePosizione(posizioni.get(c.posizione)!, lingueLettura)} — ${nomeCarta(c.carta, lingueLettura)}`,
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
    [lingua],
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
        setErrore(e instanceof ErroreApi ? e.message : t.err_oracolo);
      } finally {
        setAttesa(false);
      }
    },
    [sessione.token, t.err_oracolo],
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
        setFase("tipo");
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

  /* La domanda di ripiego delle letture speciali, nella lingua dell'interfaccia:
   * il quesito è breve e decide la lingua della lettura, che così è quella del sito. */
  const nomeAltra = persone.nome.trim();
  const domandaPredefinita = speciale
    ? (categoria === "coppia" ? t.domanda_default_coppia(nomeAltra) : t.domanda_default_compat(nomeAltra))
    : "";

  const scegliTipo = (c: Categoria) => {
    setCategoria(c);
    setStesaId(null);
    setErrore(null);
    setFase(c === "standard" ? "stesa" : "persone");
  };

  /* «Dimentica»: si cancella il partner ricordato e si svuota il modulo, non i dati di chi consulta. */
  const dimenticaPartner = async () => {
    try {
      await cancellaPartner(sessione.token);
      setPersone((p) => ({
        ...personeVuote(), tuGenere: p.tuGenere, tuGenereAltro: p.tuGenereAltro, tuTrans: p.tuTrans, tuNascita: p.tuNascita,
      }));
      profilo.ricarica();
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : t.err_operazione);
    }
  };

  const inizia = async () => {
    setMostraDisclaimer(false);
    if (!stesaId) return;
    setInCorso(true);
    setErrore(null);
    const testoDomanda = domanda.trim() || domandaPredefinita;
    try {
      if (speciale) {
        /* La scheda si completa prima: sesso e data di nascita restano nel profilo
         * anche se poi il pagamento fallisce, e non si chiedono più. */
        const mancanti = profilo.dati?.relazioni.mancanti ?? [];
        if (mancanti.length > 0) {
          await aggiornaProfilo(sessione.token, {
            ...(mancanti.includes("genere")
              ? {
                  gender: persone.tuGenere as Genere,
                  gender_custom: persone.tuGenere === "altro" ? persone.tuGenereAltro.trim() : null,
                  is_trans: persone.tuTrans,
                }
              : {}),
            ...(mancanti.includes("nascita") ? { birth_date: persone.tuNascita } : {}),
          });
          profilo.ricarica();
        }
      }
      // v6, Fase F: senza login, solo la lettura standard gratuita — niente crediti, niente dati
      // di una seconda persona. `speciale` non è raggiungibile senza autenticazione (la scelta del
      // tipo passa dal profilo), ma il ramo resta comunque protetto per chiarezza.
      const a = sessione.autenticata
        ? await apriLettura(sessione.token, {
            spreadId: stesaId,
            domanda: testoDomanda,
            lang: lingua,
            ...(speciale ? { partner: partnerDa(persone), ricordaPartner: persone.ricorda } : {}),
          })
        : await apriLetturaAnonima(stesaId, testoDomanda, lingua);
      if (a.crisi) {
        setLinguaLettura(null);
        setBattute([{ id: nuovoId(), autore: "sistema", testo: a.messaggio ?? "" }]);
        setFase("crisi");
        return;
      }
      if (!a.id) return;
      setLinguaLettura(comeLingua(a.lang) ?? lingua);
      setId(a.id);
      setNomePartner(speciale ? nomeAltra : null);
      setDomandaLettura(testoDomanda);
      router.replace(`/leggi?id=${a.id}`);
      setBattute([
        { id: nuovoId(), autore: "utente", testo: testoDomanda },
      ]);
      setFase("intervista");
      conto.ricarica();
      profilo.ricarica();
      await passoIntervista(a.id, null);
    } catch (e) {
      const dettaglio = e instanceof ErroreApi ? (e.dettaglio as { motivo?: string } | undefined) : undefined;
      if (e instanceof ErroreApi && e.stato === 402) setMostraAcquisto(true);
      else if (e instanceof ErroreApi && e.stato === 409 && dettaglio?.motivo === "lettura_gratuita_gia_usata") {
        setErrore(t.invito_gia_usata);
      } else if (e instanceof ErroreApi && e.stato === 422 && dettaglio?.motivo === "profilo_incompleto") {
        /* La scheda è ancora incompleta: si torna ai dati, che ora si vedono. */
        profilo.ricarica();
        setErrore(e.message);
        setFase("persone");
      } else setErrore(e instanceof ErroreApi ? e.message : t.err_lettura);
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

  const mescola = () => {
    if (!id) return;
    setErrore(null);
    setFase("mescolamento");
  };

  /* Il clic sul mazzo ferma la mescolata e passa al taglio. */
  const fermaMescolata = () => setFase("taglio");

  /* Il taglio arriva quando le metà si sono già scambiate: il server fissa il
   * mazzo tagliato dove ha cliccato chi consulta. */
  const taglia = async (frazione: number) => {
    if (!id) return;
    try {
      const v = await apriVentaglio(sessione.token, id, frazione);
      setSlotTotali(v.slot_count);
      setScelte(new Set(v.picked_slots));
      setFase("scelta");
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : t.err_mazzo);
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
      setErrore(e instanceof ErroreApi ? e.message : t.err_posa);
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
              titolo: `${posizione}. ${pos ? nomePosizione(pos, ll) : ""} — ${nomeCarta(ev.carta, ll)}${ev.rovescio ? ` (${dizionario(ll).rovesciata})` : ""}`,
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
      setErrore(e instanceof ErroreApi ? e.message : t.err_giro);
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
          setFine({ disclaimer: ev.disclaimer, commitment: ev.commitment, saldo: ev.saldo, anonimo: ev.anonimo });
          setFase("completata");
          conto.ricarica();
        }
      }
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : t.err_responso);
      setFase("pronto-sintesi");
    }
  };

  const nuova = () => {
    setFase("tipo");
    setCategoria("standard");
    setStesaId(null);
    setNomePartner(null);
    profilo.ricarica();
    setId(null);
    setBattute([]);
    setPosate([]);
    setScelte(new Set());
    setTestoResponso("");
    setFine(null);
    setDomanda("");
    setLinguaLettura(null);
    setManuale(false);
    caricata.current = true;
    router.replace("/leggi");
  };

  /* Il mazzo, il taglio e il ventaglio stanno sotto il tavolo, che è alto: a
   * ogni fase si porta in vista la zona, o chi consulta dovrebbe cercarla. */
  useEffect(() => {
    if (fase !== "mescolamento" && fase !== "taglio" && fase !== "scelta") return;
    const attesa = setTimeout(() => {
      document.getElementById("zona-mazzo")?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 350);
    return () => clearTimeout(attesa);
  }, [fase]);

  /* ---- disegno ---- */

  if (fase === "tipo" || fase === "persone" || fase === "stile" || fase === "stesa") {
    return (
      <>
        {stese.errore && <p className={stili.errore}>{stese.errore}</p>}
        {senzaCrediti && (
          <p className={`pannello ${stili.bandaCrediti}`}>
            {t.crediti_finiti}. <Link href="/piano?ritorno=/leggi">{t.compra}</Link>
          </p>
        )}
        {fase === "tipo" && <SceltaTipo onScegli={scegliTipo} />}
        {fase === "persone" && (
          <FormPersone
            dati={persone}
            onCambia={setPersone}
            profilo={profilo.dati}
            onAvanti={() => {
              setErrore(null);
              setStesaId((s) => (stesePerCategoria.some((x) => x.id === s) ? s : (stesePerCategoria[0]?.id ?? null)));
              setFase("stile");
            }}
            onIndietro={() => setFase("tipo")}
            onDimentica={dimenticaPartner}
            errore={errore}
          />
        )}
        {(fase === "stile" || fase === "stesa") && stese.dati && (
          <>
            {fase === "stesa" && (
              <div className={stili.azioniCentro}>
                <button type="button" className="bottone-secondario" onClick={() => setFase("tipo")}>
                  {t.cambia_tipo}
                </button>
              </div>
            )}
            <SceltaStesa
              stese={stesePerCategoria}
              scelta={stesaId}
              onScegli={setStesaId}
              domanda={domanda}
              onDomanda={setDomanda}
              onInizia={chiediInizio}
              inCorso={inCorso}
              errore={errore}
              conStili={speciale}
              domandaFacoltativa={speciale}
              domandaPredefinita={domandaPredefinita}
              onIndietro={speciale ? () => setFase("persone") : undefined}
              testoInizia={speciale ? t.inizia_speciale : undefined}
            />
          </>
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

  /* Il responso sta FUORI dal contenitore delle due colonne: la barra del
   * dialogo è `sticky`, e uno sticky resta fermo finché il suo contenitore
   * non finisce. Con il responso dentro, la barra lo attraversava. */
  return (
    <ProviderMazzoAttivo slug={slugMazzoAttivo}>
    <LinguaNomi valore={linguaLettura}>
    <div className={stili.consulto}>
      <div className={stili.colonnaTavolo}>
        <div className={stili.intestazione}>
          <span className={stili.stesaEtichetta}>
            {stesa ? nomeStesa(stesa, ll) : ""}
            {nomePartner ? ` · ${dizionario(ll).tu_e(nomePartner)}` : ""}
          </span>
          <p className={`oracolo ${stili.domandaTitolo}`} dir="auto">«{domandaLettura}»</p>
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
              nomePartner={nomePartner}
              manuale={manuale}
            />
          )}

          <AnimatePresence mode="wait">
            {fase === "mescolamento" && (
              <motion.div key="m" id="zona-mazzo" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className={stili.zonaAzione}>
                <Mescolamento onFerma={fermaMescolata} />
                <div className={`pannello ${stili.suggerimento}`} role="status">
                  <span className={stili.suggerimentoSigillo} aria-hidden="true">✦</span>
                  <p className="oracolo">{t.mescolando}</p>
                  <p className={stili.istruzione}>{t.ferma_mescolata}</p>
                </div>
              </motion.div>
            )}
            {fase === "taglio" && (
              <motion.div key="t" id="zona-mazzo" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className={stili.zonaAzione}>
                <div className={`pannello ${stili.suggerimento}`} role="status">
                  <span className={stili.suggerimentoSigillo} aria-hidden="true">✂</span>
                  <p className="oracolo">{t.taglia_mazzo}</p>
                  <p className={stili.istruzione}>{t.taglia_istruzione}</p>
                </div>
                <Taglio onTaglia={taglia} />
              </motion.div>
            )}
          </AnimatePresence>

          {fase === "scelta" && (
            <div id="zona-mazzo" className={stili.zonaVentaglio}>
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
          {errore && fase === "intervista" && id && !attesa && (
            <button className="bottone-secondario" onClick={() => passoIntervista(id, null)}>{t.riprova}</button>
          )}
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
    </div>

      {(fase === "sintesi" || fase === "completata") && stesa && id && (
        <div className={stili.zonaResponso}>
          {fase === "sintesi" && !testoResponso && <FaseResponso fase={faseResponso} />}
          {testoResponso && (
            <Responso
              id={id}
              testo={testoResponso}
              finito={fase === "completata"}
              disclaimer={fine?.disclaimer ?? disclaimer ?? ""}
              commitment={fine?.commitment ?? null}
              saldo={fine?.saldo ?? null}
              onNuova={nuova}
              anonimo={fine?.anonimo ?? false}
              onRegistrati={() => sessione.registrati()}
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
    </LinguaNomi>
    </ProviderMazzoAttivo>
  );
}
