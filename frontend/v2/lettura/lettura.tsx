"use client";

/* La lettura della v2, dall'inizio alla fine. Le fasi sono quelle del sito (`app/(sito)/leggi/lettura.tsx`) e le
 * API le stesse: nessuna logica nuova sul server.
 *
 *   preparazione (domanda, tipo, persone, stesa) → intervista → pronto-mescolare → mescolamento → taglio →
 *   scelta → rivelazione → pronto-sintesi → sintesi → completata      (e `crisi`, `annullata`)
 *
 * Cambia la messa in scena: la conversazione a sinistra, la console del rito a destra (il prototipo v2), la
 * domanda prima di tutto. Chi non ha un account fa la lettura gratuita vera (una per browser, il percorso già
 * esistente) e riceve una prima risposta con l'invito a tenere quella completa.
 *
 * Dall'indirizzo: `?id=` riprende una lettura; `?question=` precompila la domanda; `?topic=` la propone da un
 * tema; `?type=` sceglie il tipo; `?spread=` la stesa; `?card=` propone una domanda sulla carta; `?deck=` sceglie
 * le immagini di un mazzo; `?source=` (hero, dock, qr, share…) va solo agli analytics. */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import { useOsservatore, useTraccia } from "lanterna-osservatore/react";
import {
  ErroreApi, aggiornaProfilo, aggiungiAllIntervista, apriLettura, apriLetturaAnonima, apriVentaglio, cancellaPartner, elencaCarte, mieiMazzi, elencaStese, impostazioniPubbliche, leggiDisclaimer, leggiLettura, leggiProfilo, rispondi, rivela, rivelaTutte, scegliCarta, sintesi, type Categoria, type Genere, type Lettura, type Stesa,
} from "@/lib/api";
import { comeLingua, type Lingua } from "@/lib/i18n/lingue";
import { nomeCarta, nomeStesa } from "@/lib/i18n/nomi";
import { ProviderMazzoAttivo } from "@/lib/mazzo-attivo";
import { useSessione } from "@/lib/sessione";
import { dizionarioPronto, f, plurale } from "@/v2/i18n";
import { Dichiarazione } from "@/v2/componenti/dichiarazione";
import LinkV2 from "@/v2/componenti/link";
import { Modale } from "@/v2/componenti/modale";
import { DialogoLimite } from "@/v2/componenti/dialogo-limite";
import { limiteSuperato, type LimiteSuperato } from "@/lib/abbonamenti";
import { DialogoEta } from "@/v2/componenti/privacy-accesso";
import { confermaEta, motivoEta } from "@/lib/privacy";
import { P, linguaContenuti, useConto, useMazzi } from "@/v2/lib/dati";
import { LinguaNomi, useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useCarica, useStretto } from "@/v2/lib/usa";
import { Dialogo, type Battuta } from "./dialogo";
import { FormPersone, partnerDa, personeDaProfilo, personeVuote, type DatiPersone } from "./persone";
import { CarteSvelate } from "./carte-svelate";
import { SceltaMazzo, SceltaStesa, SceltaTipo, StesaNellaConsole, nelTema, temaDi, type TemaLettura } from "./preparazione";
import { NotaStampa } from "@/v2/componenti/stampa";
import { FaseResponso, Responso } from "./responso";
import { Tavolo, type Posata } from "./tavolo";
import { Mescolamento, Taglio, Ventaglio } from "./ventaglio";
import stili from "./lettura.module.css";

type Fase =
  | "preparazione" | "persone" | "intervista" | "pronto-mescolare" | "mescolamento" | "taglio" | "scelta"
  | "rivelazione" | "svelamento" | "pronto-sintesi" | "sintesi" | "completata" | "crisi" | "annullata";

/* `?type=` accetta i nomi inglesi della v2 e quelli italiani del sito. */
const comeCategoria = (v: string | null): Categoria | null => {
  const m: Record<string, Categoria> = {
    standard: "standard", question: "standard",
    compatibilita: "compatibilita", compatibility: "compatibilita",
    coppia: "coppia", couple: "coppia",
    lavoro: "lavoro", work: "lavoro", business: "lavoro",
  };
  return v ? (m[v] ?? null) : null;
};

let contatore = 0;
const nuovoId = () => `b${++contatore}`;

export function LetturaV2() {
  const { t, lingua, prefissoIt } = useLingua();
  const l = t.lettura;
  const sessione = useSessione();
  const router = useRouter();
  const parametri = useSearchParams();
  const traccia = useTraccia();
  const osservatore = useOsservatore();
  const idIniziale = parametri.get("id");

  const stese = useCarica(() => elencaStese(undefined, linguaContenuti(lingua)), [lingua], { pubblico: true, iniziale: P.stese(lingua) });
  const conto = useConto();
  const profilo = useCarica(leggiProfilo);
  const mazzi = useMazzi();
  const posseduti = useCarica(mieiMazzi);
  const omaggi = useCarica(impostazioniPubbliche, [], { pubblico: true, iniziale: P.impostazioni() });
  const cartaParam = parametri.get("card");
  const carte = useCarica(
    () => (cartaParam ? elencaCarte(linguaContenuti(lingua)) : Promise.resolve([])), [cartaParam, lingua], { pubblico: true },
  );

  /* Il mazzo delle immagini: quello dell'indirizzo (`?deck=`, per esempio da un QR), altrimenti il predefinito
   * dell'utente. Il Thoth vive nella cartella piatta: slug `null`. */
  const deckParam = parametri.get("deck");
  const slugMazzo = useMemo(() => {
    const lista = mazzi.dati ?? [];
    const daIndirizzo = lista.find((m) => m.slug === deckParam && !m.predefinito && m.attivo_ora);
    if (daIndirizzo) return daIndirizzo.slug;
    return lista.find((m) => m.id === profilo.dati?.mazzo_predefinito_id && !m.predefinito)?.slug ?? null;
  }, [mazzi.dati, deckParam, profilo.dati]);
  /* I mazzi con cui si può leggere: il predefinito e quelli posseduti (v8.5). Con più d'uno, la preparazione li
   * propone. La scelta si manda all'apertura e la lettura la ricorda; una lettura ripresa usa il suo. */
  const utilizzabili = useMemo(() => {
    const miei = new Set(posseduti.dati?.deck_ids ?? []);
    return (mazzi.dati ?? []).filter((m) => m.attivo_ora && (m.predefinito || miei.has(m.id)));
  }, [mazzi.dati, posseduti.dati]);
  const [mazzoScelto, setMazzoScelto] = useState<string | null | undefined>(undefined);
  const [mazzoLettura, setMazzoLettura] = useState<string | null | undefined>(undefined);
  const slugAttivo = mazzoLettura !== undefined ? mazzoLettura : mazzoScelto !== undefined ? mazzoScelto : slugMazzo;
  const mazzoDaInviare = slugAttivo && utilizzabili.some((m) => m.slug === slugAttivo && !m.predefinito) ? slugAttivo : null;

  const tipoIniziale = comeCategoria(parametri.get("type"));
  const [fase, setFase] = useState<Fase>(idIniziale ? "intervista" : "preparazione");
  const [tema, setTema] = useState<TemaLettura>(temaDi(tipoIniziale));
  const [persone, setPersone] = useState<DatiPersone>(personeVuote);
  const [personeFatte, setPersoneFatte] = useState(false);
  const [nomePartner, setNomePartner] = useState<string | null>(null);
  const [id, setId] = useState<string | null>(idIniziale);
  const [stesaId, setStesaId] = useState<string | null>(parametri.get("spread"));
  const [domanda, setDomanda] = useState(() => {
    const q = parametri.get("question");
    if (q) return q;
    const tema = parametri.get("topic");
    return tema ? (l.temi[tema] ?? "") : "";
  });
  /* Una domanda proposta (da un tema) si aggiorna con la lingua finché non la si modifica: le lingue caricate a
   * parte (l'ungherese…) arrivano dopo il primo rendering, e la proposta nascerebbe in inglese. */
  const domandaToccata = useRef(!!parametri.get("question"));
  const temaParam = parametri.get("topic");
  useEffect(() => {
    if (!domandaToccata.current && temaParam && l.temi[temaParam]) setDomanda(l.temi[temaParam]);
  }, [temaParam, l.temi]);
  const [disclaimer, setDisclaimer] = useState<string | null>(null);
  const [mostraDisclaimer, setMostraDisclaimer] = useState(false);
  const [mostraAcquisto, setMostraAcquisto] = useState(false);
  /* Oltre un limite dell'abbonamento (v9, Fase 2b): il dialogo del condono o del consenso a un credito. */
  const [limite, setLimite] = useState<LimiteSuperato | null>(null);
  const [giaUsata, setGiaUsata] = useState(false);
  /* L'età minima (GDPR, Fase 1): il server la chiede alla prima lettura senza conferma (403 con gli anni). */
  const [eta, setEta] = useState<{ anni: number; insufficiente: boolean } | null>(null);
  const [errore, setErrore] = useState<string | null>(null);
  const [inCorso, setInCorso] = useState(false);

  const [battute, setBattute] = useState<Battuta[]>([]);
  const [attesa, setAttesa] = useState(false);
  const [slotTotali, setSlotTotali] = useState(0);
  const [scelte, setScelte] = useState<Set<number>>(new Set());
  const [posate, setPosate] = useState<Posata[]>([]);
  const [rivelazioneInCorso, setRivelazioneInCorso] = useState(false);
  /* Le carte sono girate e il lettore le sta leggendo tutte insieme (una chiamata sola): un solo momento d'attesa. */
  const [lettoreLegge, setLettoreLegge] = useState(false);
  const scegliendo = useRef(false);

  const [faseResponso, setFaseResponso] = useState("unione");
  const [testoResponso, setTestoResponso] = useState("");
  const [fine, setFine] = useState<{ disclaimer: string; commitment: string | null; saldo: number | null; anonimo: boolean } | null>(null);
  const [domandaLettura, setDomandaLettura] = useState("");
  const [linguaLettura, setLinguaLettura] = useState<Lingua | null>(null);
  const [manuale, setManuale] = useState(false);
  const ll: Lingua = linguaLettura ?? lingua;
  const tl = (dizionarioPronto(ll) ?? t).lettura;

  const stesa: Stesa | undefined = useMemo(() => stese.dati?.find((s) => s.id === stesaId), [stese.dati, stesaId]);
  /* La categoria vera (quella che il backend conosce) viene dalla stesa scelta; senza stesa, dal tema. */
  const categoria: Categoria = stesa?.categoria
    ?? (tema === "amore" ? "compatibilita" : tema === "lavoro" ? ("lavoro" as Categoria) : "standard");
  const speciale = categoria === "compatibilita" || categoria === "coppia";
  const stesePerTema = useMemo(() => (stese.dati ?? []).filter((s) => nelTema(s, tema)), [stese.dati, tema]);

  /* Una stesa dall'indirizzo decide anche il tema; senza stesa si propone la prima del tema. */
  useEffect(() => {
    if (!stese.dati || fase !== "preparazione") return;
    const daIndirizzo = stese.dati.find((s) => s.id === stesaId);
    if (daIndirizzo && !nelTema(daIndirizzo, tema)) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setTema(temaDi(daIndirizzo.categoria));
      return;
    }
    if (!daIndirizzo) {
      const delTema = stese.dati.filter((s) => nelTema(s, tema));
      const prima = delTema.find((s) => s.id === "tre-carte" || s.posizioni.length === 3) ?? delTema[0];
      if (prima) setStesaId(prima.id);
    }
  }, [stese.dati, tema, stesaId, fase]);

  /* `?card=`: una domanda sulla carta, se la domanda è ancora vuota. */
  const cartaProposta = useRef(false);
  useEffect(() => {
    if (cartaProposta.current || !cartaParam || !carte.dati?.length) return;
    cartaProposta.current = true;
    const c = carte.dati.find((x) => x.id === cartaParam || x.slug === cartaParam || Object.values(x.slugs ?? {}).includes(cartaParam));
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (c) setDomanda((d) => d || f(l.domanda_carta, { carta: nomeCarta(c, lingua) }));
  }, [carte.dati, cartaParam, l.domanda_carta, lingua]);

  /* Analytics: ogni fase è un passo dell'imbuto; mai la domanda né le carte. La prima vista porta la sorgente
   * (hero, dock, qr…). */
  useEffect(() => {
    if (sessione.pronta) traccia("lettura_fase", { fase, categoria, anonima: !sessione.autenticata, v2: true });
  }, [traccia, fase, categoria, sessione.pronta, sessione.autenticata]);
  const sorgenteTracciata = useRef(false);
  useEffect(() => {
    const sorgente = parametri.get("source");
    /* Solo quando l'osservatore c'è: prima l'evento andrebbe perso. */
    if (sorgenteTracciata.current || !sorgente || !osservatore) return;
    sorgenteTracciata.current = true;
    traccia(sorgente === "qr" ? "qr_entry" : "reading_entry", { sorgente, mazzo: deckParam ?? "" });
  }, [parametri, traccia, deckParam, osservatore]);

  const precompilato = useRef(false);
  useEffect(() => {
    if (precompilato.current || !profilo.dati) return;
    precompilato.current = true;
    setPersone((prima) => personeDaProfilo(profilo.dati!, prima));
  }, [profilo.dati]);

  const aggiungi = (b: Omit<Battuta, "id">) => setBattute((prima) => [...prima, { ...b, id: nuovoId() }]);
  const vai = useCallback((indirizzo: string) => router.replace(indirizzoV2(indirizzo, prefissoIt)), [router, prefissoIt]);

  /* ---- la ripresa di una lettura ---- */

  const riprendi = useCallback((lt: Lettura) => {
    setMazzoLettura(lt.mazzo ?? null);
    setStesaId(lt.spread_id);
    setTema(temaDi(lt.categoria));
    setNomePartner(lt.persone?.partner.nome ?? null);
    setLinguaLettura(comeLingua(lt.lang));
    setManuale(lt.manuale);
    setDomandaLettura(lt.question);
    setDisclaimer(lt.disclaimer);
    const storia: Battuta[] = [
      { id: nuovoId(), autore: "utente", testo: lt.question },
      ...lt.interview.map((x) => ({ id: nuovoId(), autore: x.ruolo, testo: x.testo })),
    ];
    if (lt.context_summary) storia.push({ id: nuovoId(), autore: "oracolo", titolo: "✦", testo: lt.context_summary });
    /* Le spiegazioni delle carte non stanno nella conversazione (v8.5): escono con l'interpretazione, prima di essa. */
    setBattute(storia);
    setScelte(new Set(lt.picked_slots));
    setSlotTotali(lt.slot_count ?? 0);
    const ordinati = [...lt.cards].sort((a, b) => a.posizione - b.posizione);
    let k = 0;
    setPosate(ordinati.map((c) => ({
      posizione: c.posizione,
      slot: c.calcolata ? null : (lt.picked_slots[k++] ?? null),
      calcolata: c.calcolata,
      rivelata: c.rivelata,
      carta: c.carta,
      rovescio: c.rovescio,
      interpretazione: c.interpretazione,
      dignita: lt.dignita?.[String(c.posizione)] ?? null,
    })));
    if (lt.synthesis) setTestoResponso(lt.synthesis);
    const mappa: Record<string, Fase> = {
      intervista: "intervista", ventaglio: "pronto-mescolare", scelta: "scelta", rivelazione: "rivelazione",
      sintesi: "rivelazione", completata: "completata", annullata: "annullata",
    };
    setFase(mappa[lt.status] ?? "intervista");
    if (lt.status === "completata") setFine({ disclaimer: lt.disclaimer, commitment: lt.commitment, saldo: null, anonimo: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lingua]);

  /* v9.5, i tre pulsanti. L'oracolo fa la prima domanda da sé; dopo ogni risposta il campo si chiude e chi legge
   * sceglie fra «Passa alla lettura», «Voglio dire qualcosa di libero» e «Voglio rispondere a un'altra domanda»
   * (quest'ultima finché non si arriva al massimo). Sotto la prima domanda ci sono già «Passa alla lettura» (se il
   * minimo lo consente) e il testo libero. `modo`: `risposta` (una domanda aspetta), `scelta` (i pulsanti),
   * `libero` (si scrive un testo libero). */
  const [modo, setModo] = useState<"risposta" | "scelta" | "libero">("risposta");
  const [regole, setRegole] = useState({ min: 0, max: 2 });
  const [poste, setPoste] = useState(0);

  const passoIntervista = useCallback(async (
    lid: string, risposta: string | null, opzioni: { basta?: boolean; altra?: boolean } = {},
  ) => {
    setAttesa(true);
    setErrore(null);
    try {
      const passo = await rispondi(sessione.token, lid, risposta, !!opzioni.basta,
        { continua: false, altra: !!opzioni.altra });
      if (passo.min_domande !== undefined && passo.max_domande !== undefined) {
        setRegole({ min: passo.min_domande, max: passo.max_domande });
      }
      if (passo.poste !== undefined) setPoste(passo.poste);
      /* v9.5: il numero della domanda, per vedere dopo quante domande ci si ferma (mai il testo). */
      if (risposta !== null) traccia("interview_answered", { n: passo.poste ?? 0 });
      if (passo.crisi) {
        aggiungi({ autore: "sistema", testo: passo.messaggio ?? "" });
        setFase("crisi");
      } else if (passo.completa) {
        aggiungi({ autore: "oracolo", titolo: "✦", testo: passo.riassunto ?? "", macchina: true });
        setFase("pronto-mescolare");
      } else if (passo.scelta) {
        setModo("scelta");
      } else if (passo.domanda) {
        traccia("interview_question", { n: passo.poste ?? 0 });
        aggiungi({ autore: "oracolo", testo: passo.domanda, macchina: true });
        setModo("risposta");
      }
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : l.err_oracolo);
    } finally {
      setAttesa(false);
    }
  }, [sessione.token, l.err_oracolo, traccia]);

  const passaAllaLettura = () => {
    if (!id) return;
    traccia("interview_choice", { scelta: "lettura", n: poste });
    traccia("interview_skipped", { n: poste });
    void passoIntervista(id, null, { basta: true });
  };
  const altraDomanda = () => {
    if (!id) return;
    traccia("interview_choice", { scelta: "altra", n: poste });
    void passoIntervista(id, null, { altra: true });
  };
  const testoLibero = () => {
    traccia("interview_choice", { scelta: "libero", n: poste });
    setModo("libero");
  };

  const caricata = useRef(false);
  useEffect(() => {
    if (!idIniziale || caricata.current || !sessione.pronta) return;
    if (!sessione.autenticata) {
      /* Una lettura anonima non si riprende dopo un ricaricamento: si ricomincia dalla domanda. */
      caricata.current = true;
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFase("preparazione");
      setId(null);
      vai(R.leggi);
      return;
    }
    caricata.current = true;
    leggiLettura(sessione.token, idIniziale)
      .then((lt) => {
        riprendi(lt);
        const ultima = lt.interview[lt.interview.length - 1];
        if (lt.status !== "intervista") return;
        /* v9.5: nessuna domanda ancora → la prima; l'ultima parola è di chi legge → i pulsanti, senza chiamare il
         * modello; una domanda aspetta → si risponde. Minimo e massimo dalle impostazioni pubbliche. */
        setPoste(lt.interview.filter((x) => x.ruolo === "oracolo").length);
        void impostazioniPubbliche().then((imp) => {
          if (imp.intervista_max_domande) setRegole({ min: imp.intervista_min_domande ?? 0, max: imp.intervista_max_domande });
        }).catch(() => undefined);
        if (!ultima) void passoIntervista(lt.id, null);
        else setModo(ultima.ruolo === "utente" ? "scelta" : "risposta");
      })
      .catch(() => {
        setFase("preparazione");
        setId(null);
        vai(R.leggi);
      });
  }, [idIniziale, sessione.pronta, sessione.autenticata, sessione.token, riprendi, passoIntervista, vai]);

  /* ---- 1. l'apertura ---- */

  /* Con un abbonamento a letture comprese decide il server (v9, Fase 2b): oltre il limite ci sono i condoni, e il
   * dialogo del limite spiega cosa succede. */
  const senzaCrediti = conto.dati !== null && conto.dati.limiti_attivi && conto.dati.saldo <= 0
    && !conto.dati.letture_comprese && (conto.dati.uso?.letture_al_giorno?.restanti ?? 0) <= 0;
  const nomeAltra = persone.nome.trim();
  const domandaPredefinita = speciale
    ? f(categoria === "coppia" ? l.domanda_coppia : l.domanda_compat, { nome: nomeAltra })
    : "";
  const domandaValida = speciale || domanda.trim().length >= 3;

  const scegliTipo = (c: TemaLettura) => {
    setTema(c);
    setErrore(null);
    setPersoneFatte(false);
    setStesaId(null);
  };

  const chiediInizio = async () => {
    if (!domandaValida) { setErrore(l.domanda_corta); return; }
    if (!stesaId) return;
    if (speciale && !personeFatte) { setFase("persone"); return; }
    if (senzaCrediti) { setMostraAcquisto(true); traccia("paywall_viewed", { dove: "inizio" }); return; }
    if (!disclaimer) {
      try {
        setDisclaimer((await leggiDisclaimer(lingua)).testo);
      } catch {
        /* il disclaimer arriva comunque con la lettura */
      }
    }
    setMostraDisclaimer(true);
  };

  const dimenticaPartner = async () => {
    try {
      await cancellaPartner(sessione.token);
      setPersone((p) => ({ ...personeVuote(), tuGenere: p.tuGenere, tuGenereAltro: p.tuGenereAltro, tuTrans: p.tuTrans, tuNascita: p.tuNascita }));
      profilo.ricarica();
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : t.comune.err_operazione);
    }
  };

  const inizia = async (etaAnni?: number, oltreLimite?: "condono" | "credito") => {
    setMostraDisclaimer(false);
    setLimite(null);
    if (!stesaId) return;
    setInCorso(true);
    setErrore(null);
    const testoDomanda = domanda.trim() || domandaPredefinita;
    try {
      if (speciale) {
        const mancanti = profilo.dati?.relazioni.mancanti ?? [];
        if (mancanti.length > 0) {
          await aggiornaProfilo(sessione.token, {
            ...(mancanti.includes("genere") ? {
              gender: persone.tuGenere as Genere,
              gender_custom: persone.tuGenere === "altro" ? persone.tuGenereAltro.trim() : null,
              is_trans: persone.tuTrans,
            } : {}),
            ...(mancanti.includes("nascita") ? { birth_date: persone.tuNascita } : {}),
          });
          profilo.ricarica();
        }
      }
      const a = sessione.autenticata
        ? await apriLettura(sessione.token, {
            spreadId: stesaId, domanda: testoDomanda, lang: lingua, mazzo: mazzoDaInviare, oltreLimite,
            variante: "classica",
            ...(speciale ? { partner: partnerDa(persone), ricordaPartner: persone.ricorda } : {}),
          })
        : await apriLetturaAnonima(stesaId, testoDomanda, lingua, etaAnni, "classica");
      traccia("reading_started", { categoria, anonima: !sessione.autenticata });
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
      /* L'indirizzo prende `?id=`: la lettura l'ha aperta questa pagina, non va «ripresa» (per chi non ha un
       * account la ripresa riporterebbe alla preparazione). */
      caricata.current = true;
      vai(`${R.leggi}?id=${a.id}`);
      setBattute([
        { id: nuovoId(), autore: "utente", testo: testoDomanda },
      ]);
      setFase("intervista");
      setPoste(0);
      setModo("risposta");
      conto.ricarica();
      profilo.ricarica();
      await passoIntervista(a.id, null);
    } catch (e) {
      const dettaglio = e instanceof ErroreApi ? (e.dettaglio as { motivo?: string } | undefined) : undefined;
      const perEta = motivoEta(e);
      const oltre = limiteSuperato(e);
      if (perEta) setEta({ anni: perEta.anni, insufficiente: perEta.motivo === "eta_insufficiente" });
      else if (oltre) { setLimite(oltre); traccia("limit_reached", { limite: oltre.limite, scelta: oltre.scelta }); }
      else if (e instanceof ErroreApi && e.stato === 402) { setMostraAcquisto(true); traccia("paywall_viewed", { dove: "apertura" }); }
      else if (e instanceof ErroreApi && e.stato === 409 && dettaglio?.motivo === "lettura_gratuita_gia_usata") setGiaUsata(true);
      else if (e instanceof ErroreApi && e.stato === 422 && dettaglio?.motivo === "profilo_incompleto") {
        profilo.ricarica();
        setErrore(e.message);
        setFase("persone");
      } else setErrore(e instanceof ErroreApi ? e.message : l.err_lettura);
    } finally {
      setInCorso(false);
    }
  };

  /* ---- 2. l'intervista ---- */

  const suRisposta = (testo: string) => {
    if (!id) return;
    aggiungi({ autore: "utente", testo });
    void passoIntervista(id, testo);
  };

  /* v9.5: «Voglio dire qualcosa di libero». Il testo entra nell'interpretazione; poi tornano i pulsanti. */
  const suLibero = async (testo: string) => {
    if (!id) return;
    aggiungi({ autore: "utente", testo });
    setAttesa(true);
    setErrore(null);
    try {
      const esito = await aggiungiAllIntervista(sessione.token, id, testo);
      if (esito.crisi) {
        aggiungi({ autore: "sistema", testo: esito.messaggio ?? "" });
        setFase("crisi");
        return;
      }
      traccia("interview_addition", { n: poste });
      setModo("scelta");
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : l.err_oracolo);
    } finally {
      setAttesa(false);
    }
  };

  /* Le scelte in fondo alla chat: sotto la prima domanda «Passa alla lettura» (se il minimo lo consente) e il testo
   * libero; dopo una risposta o un testo libero i tre pulsanti, «un'altra domanda» solo prima del massimo. */
  const sceltePossibili: { etichetta: string; azione: () => void; primaria?: boolean }[] = [];
  if (fase === "intervista" && !attesa) {
    const puoiPassare = poste - (modo === "risposta" ? 1 : 0) >= regole.min;
    if (modo === "scelta" && poste < regole.max) sceltePossibili.push({ etichetta: l.scelta_altra, azione: altraDomanda });
    if (modo === "scelta" || (modo === "risposta" && poste <= 1)) {
      sceltePossibili.push({ etichetta: l.scelta_libero, azione: testoLibero });
    }
    if ((modo === "scelta" || (modo === "risposta" && poste <= 1)) && puoiPassare) {
      sceltePossibili.push({ etichetta: l.scelta_lettura, azione: passaAllaLettura, primaria: true });
    }
  }

  /* ---- 3. mescolata, taglio, scelta ---- */

  const mescola = () => {
    if (!id) return;
    setErrore(null);
    setFase("mescolamento");
    traccia("shuffle_started");
  };
  const fermaMescolata = () => {
    setFase("taglio");
    traccia("shuffle_interrupted");
  };
  const taglia = async (frazione: number) => {
    if (!id) return;
    try {
      const v = await apriVentaglio(sessione.token, id, frazione);
      traccia("deck_cut");
      setSlotTotali(v.slot_count);
      setScelte(new Set(v.picked_slots));
      setFase("scelta");
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : l.err_mazzo);
      setFase("pronto-mescolare");
    }
  };
  const scegli = async (slot: number) => {
    if (!id || scegliendo.current || scelte.has(slot)) return;
    scegliendo.current = true;
    try {
      const r = await scegliCarta(sessione.token, id, slot);
      traccia("card_drawn", { n: scelte.size + 1 });
      setScelte((s) => new Set(s).add(slot));
      setPosate((p) => [
        ...p,
        { posizione: r.posizione, slot, calcolata: false, rivelata: false },
        ...(r.tutte_scelte ? r.posizioni_calcolate.map((n) => ({ posizione: n, slot: null, calcolata: true, rivelata: false })) : []),
      ]);
      if (r.tutte_scelte) setTimeout(() => setFase("rivelazione"), 700);
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : l.err_posa);
    } finally {
      scegliendo.current = false;
    }
  };

  /* ---- 4. la rivelazione ---- */

  const prossimaDaRivelare = useMemo(() => {
    const coperte = posate.filter((p) => !p.rivelata).map((p) => p.posizione);
    return coperte.length ? Math.min(...coperte) : null;
  }, [posate]);
  const prossimaDaScegliere = useMemo(() => {
    if (!stesa) return null;
    const occupate = new Set(posate.map((p) => p.posizione));
    return stesa.posizioni.find((p) => !p.calcolata && !occupate.has(p.n))?.n ?? null;
  }, [stesa, posate]);

  /* Una carta: si gira e la sua spiegazione arriva in streaming nella zona dell'interpretazione (v8.5: non più nella
   * conversazione). Restituisce `false` se qualcosa è andato storto. */
  const rivelaCarta = async (posizione: number): Promise<boolean> => {
    if (!id || !stesa) return false;
    setErrore(null);
    const aggiornaPosata = (fn: (p: Posata) => Posata) => setPosate((tutte) => tutte.map((p) => (p.posizione === posizione ? fn(p) : p)));
    try {
      for await (const ev of rivela(sessione.token, id, posizione)) {
        if (ev.tipo === "carta") {
          traccia("card_revealed", { n: posizione });
          aggiornaPosata((p) => ({ ...p, rivelata: true, carta: ev.carta, rovescio: ev.rovescio, dignita: ev.dignita, doppia: ev.doppia_valenza, interpretazione: "" }));
          setLettoreLegge(true);
        } else if (ev.tipo === "token") {
          setLettoreLegge(false);
          aggiornaPosata((p) => ({ ...p, interpretazione: (p.interpretazione ?? "") + ev.testo }));
        } else if (ev.tipo === "sostituisci") {
          aggiornaPosata((p) => ({ ...p, interpretazione: ev.testo }));
        } else if (ev.tipo === "errore") {
          setLettoreLegge(false);
          setErrore(ev.messaggio);
          return false;
        } else if (ev.tipo === "fine") {
          setLettoreLegge(false);
          aggiornaPosata((p) => ({ ...p, interpretazione: ev.interpretazione || p.interpretazione }));
        }
      }
      return true;
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : l.err_giro);
      return false;
    } finally {
      setLettoreLegge(false);
    }
  };

  /* Tutte le carte insieme (v8.6): si girano subito, poi un solo momento d'attesa («il tuo lettore sta leggendo le
   * carte…») mentre una chiamata sola le interpreta tutte, poi le spiegazioni carta per carta. `"vecchio"`: il server
   * non conosce ancora lo svelamento di tutte le carte (404/405), si torna a una carta alla volta. */
  const rivelaInsieme = async (): Promise<boolean | "vecchio"> => {
    if (!id) return false;
    setErrore(null);
    const aggiorna = (posizione: number, fn: (p: Posata) => Posata) => setPosate((tutte) => tutte.map((p) => (p.posizione === posizione ? fn(p) : p)));
    let riuscita = true;
    try {
      for await (const ev of rivelaTutte(sessione.token, id)) {
        if (ev.tipo === "carta") {
          traccia("card_revealed", { n: ev.posizione, tutte: true });
          aggiorna(ev.posizione, (p) => ({ ...p, rivelata: true, carta: ev.carta, rovescio: ev.rovescio, dignita: ev.dignita, doppia: ev.doppia_valenza, interpretazione: "" }));
        } else if (ev.tipo === "fase") {
          if (ev.fase === "lettura") setLettoreLegge(true);
        } else if (ev.tipo === "token") {
          setLettoreLegge(false);
          if (ev.posizione != null) aggiorna(ev.posizione, (p) => ({ ...p, interpretazione: (p.interpretazione ?? "") + ev.testo }));
        } else if (ev.tipo === "sostituisci") {
          if (ev.posizione != null) aggiorna(ev.posizione, (p) => ({ ...p, interpretazione: ev.testo }));
        } else if (ev.tipo === "errore") {
          /* Una carta senza spiegazione (la ritroverà nel responso): le altre arrivano lo stesso. */
          setLettoreLegge(false);
          setErrore(ev.messaggio);
          riuscita = false;
        } else if (ev.tipo === "fine") {
          setLettoreLegge(false);
          aggiorna(ev.posizione, (p) => ({ ...p, interpretazione: ev.interpretazione || p.interpretazione }));
        }
      }
      return riuscita;
    } catch (e) {
      if (e instanceof ErroreApi && (e.stato === 404 || e.stato === 405)) return "vecchio";
      setErrore(e instanceof ErroreApi ? e.message : l.err_giro);
      return false;
    } finally {
      setLettoreLegge(false);
    }
  };

  /* Una sola fase (v8.5): le carte si girano, ciascuna con la sua spiegazione, poi arriva l'interpretazione
   * dell'insieme. Dalla v8.6 le carte si girano tutte insieme e una chiamata sola le interpreta; ogni carta e la
   * sintesi si salvano come prima (e le memorie nascono dalla sintesi, come prima). */
  const rivelaTutto = async () => {
    if (!id || !stesa || rivelazioneInCorso) return;
    setRivelazioneInCorso(true);
    setRitoChiuso(true);
    setFase("svelamento");
    setTimeout(() => document.getElementById("zona-responso")?.scrollIntoView({ behavior: "smooth", block: "start" }), 250);
    try {
      const coperte = posate.filter((p) => !p.rivelata).map((p) => p.posizione).sort((a, b) => a - b);
      if (coperte.length) {
        const esito = await rivelaInsieme();
        if (esito === "vecchio") {
          for (const n of coperte) {
            if (!(await rivelaCarta(n))) { setFase("rivelazione"); return; }
          }
        } else if (!esito) {
          setFase("rivelazione");
          return;
        }
      }
      await chiediResponso();
    } finally {
      setRivelazioneInCorso(false);
    }
  };

  /* ---- 5. l'interpretazione ---- */

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
          setFase("rivelazione");
          return;
        } else if (ev.tipo === "fine") {
          setFine({ disclaimer: ev.disclaimer, commitment: ev.commitment, saldo: ev.saldo, anonimo: !!ev.anonimo });
          setFase("completata");
          traccia("reading_completed", { anonima: !!ev.anonimo });
          conto.ricarica();
        }
      }
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : l.err_responso);
      setFase("rivelazione");
    }
  };

  const nuova = () => {
    setFase("preparazione");
    setTema("standard");
    setStesaId(null);
    setNomePartner(null);
    setPersoneFatte(false);
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
    vai(R.leggi);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const registrati = () => {
    traccia("signup_started", { dove: "anteprima" });
    sessione.registrati();
  };

  /* Il mazzo, il taglio e il ventaglio: a ogni fase si porta in vista la console. */
  useEffect(() => {
    if (fase !== "mescolamento" && fase !== "taglio" && fase !== "scelta" && fase !== "pronto-mescolare") return;
    const attesaScroll = setTimeout(() => {
      document.getElementById("zona-mazzo")?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 350);
    return () => clearTimeout(attesaScroll);
  }, [fase]);

  /* Sul telefono (v8.5): tema e schema si scelgono in due dialoghi all'apertura della pagina (la domanda, se arriva
   * dall'oracolo o da un invito, è già scritta); le fasi del rito si aprono in un dialogo. Chi chiude il dialogo del
   * rito lo ritrova nella pagina. */
  const stretto = useStretto();
  const [sceltaMobile, setSceltaMobile] = useState<"tipo" | "stesa" | null>(null);
  const dialoghiAvviati = useRef(false);
  useEffect(() => {
    if (!stretto || fase !== "preparazione" || dialoghiAvviati.current || idIniziale) return;
    dialoghiAvviati.current = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (!parametri.get("spread")) setSceltaMobile("tipo");
  }, [stretto, fase, idIniziale, parametri]);
  const [ritoChiuso, setRitoChiuso] = useState(false);
  useEffect(() => { setRitoChiuso(false); }, [fase]);

  const nOmaggi = omaggi.dati?.crediti_iscrizione ?? 3;
  const dialoghiComuni = (
    <>
      <Modale aperta={mostraDisclaimer} titolo={l.avviso_titolo} onChiudi={() => setMostraDisclaimer(false)}>
        <p className="prose" dir="auto">{disclaimer ?? ""}</p>
        <div className="button-row">
          <button type="button" className="button button-brass" onClick={() => inizia()} autoFocus>{l.avviso_accetta}</button>
        </div>
      </Modale>
      <Modale aperta={mostraAcquisto} titolo={l.crediti_finiti} onChiudi={() => setMostraAcquisto(false)}>
        <p className="prose">{l.crediti_finiti_testo}</p>
        <div className="button-row">
          <LinkV2 className="button" href={`${R.prezzi}?ritorno=${encodeURIComponent(id ? `${R.leggi}?id=${id}` : R.leggi)}`}>{l.vedi_prezzi}</LinkV2>
          <button type="button" className="button button-quiet" onClick={() => setMostraAcquisto(false)}>{t.comune.chiudi}</button>
        </div>
      </Modale>
      <Modale aperta={sceltaMobile === "tipo"} titolo={l.tipo_titolo} onChiudi={() => setSceltaMobile(null)}>
        <SceltaTipo tema={tema} conTitolo={false} onScegli={(c) => { scegliTipo(c); setSceltaMobile("stesa"); }} />
      </Modale>
      <Modale aperta={sceltaMobile === "stesa"} titolo={l.stesa_titolo} onChiudi={() => setSceltaMobile(null)} larga>
        {speciale && sessione.pronta && !sessione.autenticata ? (
          <div className="notice">
            <p style={{ margin: "0 0 .8rem" }}>{l.tipo_serve_account}</p>
            <button type="button" className="button button-small"
              onClick={() => sessione.entra(`${R.leggi}?type=${categoria}`)}>{l.tipo_entra}</button>
          </div>
        ) : (
          <SceltaStesa stese={stesePerTema} scelta={stesaId} conTitolo={false} conStili={tema === "amore"}
            onScegli={(s) => { setStesaId(s); setSceltaMobile(null); setTimeout(() => document.getElementById("domanda")?.focus(), 80); }} />
        )}
        <div className="button-row">
          <button type="button" className="button button-quiet" onClick={() => setSceltaMobile("tipo")}>{t.comune.indietro}</button>
        </div>
      </Modale>
      <DialogoEta anni={eta?.anni ?? 16} aperta={eta !== null} insufficiente={eta?.insufficiente} onChiudi={() => setEta(null)}
        onConferma={async (anni) => {
          if (sessione.autenticata) {
            try { await confermaEta(sessione.token, anni); } catch { setEta(null); return; }
            setEta(null);
            await inizia();
          } else {
            setEta(null);
            await inizia(anni);
          }
        }} />
      <DialogoLimite dettaglio={limite} onChiudi={() => setLimite(null)} inCorso={inCorso}
        ritorno={id ? `${R.leggi}?id=${id}` : R.leggi} onConsenso={(scelta) => { void inizia(undefined, scelta); }} />
      <Modale aperta={giaUsata} titolo={l.gia_usata_cta} onChiudi={() => setGiaUsata(false)}>
        <p className="prose">{l.gia_usata}</p>
        <div className="button-row">
          <button type="button" className="button button-brass" onClick={registrati}>{l.gia_usata_cta}</button>
        </div>
      </Modale>
    </>
  );

  /* ---- la preparazione ---- */

  if (fase === "preparazione" || fase === "persone") {
    const serveAccount = speciale && sessione.pronta && !sessione.autenticata;
    const nomeTema = l.tipi[tema].nome;
    const sceltaInline = !stretto;
    return (
      <>
        <section className="band band-tight">
          <div className="read-layout">
            <section className="read-panel" aria-labelledby="titolo-conversazione">
              <p className="eyebrow">{l.pannello_conversazione}</p>
              {fase === "preparazione" ? (
                <>
                  <h2 id="titolo-conversazione">{l.domanda_titolo}</h2>
                  <label className="sr-only" htmlFor="domanda">{l.domanda_etichetta}</label>
                  <textarea
                    id="domanda" className={stili.domanda} value={domanda} dir="auto" maxLength={1000} rows={4}
                    placeholder={speciale && domandaPredefinita ? domandaPredefinita : l.domanda_segnaposto}
                    onChange={(e) => { domandaToccata.current = true; setDomanda(e.target.value); setErrore(null); }}
                    onFocus={() => traccia("question_started")}
                  />
                  {speciale && <p className="muted small">{l.domanda_facoltativa}</p>}
                  {sceltaInline ? <SceltaTipo tema={tema} onScegli={scegliTipo} /> : (
                    /* Sul telefono: ciò che si è scelto nei dialoghi, e il modo di cambiarlo. */
                    <div className={stili.sceltaRiassunto}>
                      <span><b>{nomeTema}</b>{stesa ? ` · ${nomeStesa(stesa, lingua)}` : ""}</span>
                      <button type="button" className="button button-quiet button-small" onClick={() => setSceltaMobile("tipo")}>{l.cambia}</button>
                    </div>
                  )}
                  {utilizzabili.length > 1 && (
                    <SceltaMazzo mazzi={utilizzabili} scelto={slugAttivo} onScegli={setMazzoScelto} />
                  )}
                  {serveAccount ? (
                    <div className="notice">
                      <p style={{ margin: "0 0 .8rem" }}>{l.tipo_serve_account}</p>
                      <button type="button" className="button button-small"
                        onClick={() => sessione.entra(`${R.leggi}?type=${categoria}`)}>{l.tipo_entra}</button>
                    </div>
                  ) : (
                    sceltaInline && stese.dati && (
                      <SceltaStesa stese={stesePerTema} scelta={stesaId} onScegli={setStesaId} conStili={tema === "amore"} />
                    )
                  )}
                  {stese.errore && <p className="error" role="alert">{stese.errore}</p>}
                </>
              ) : (
                <>
                  <h2 id="titolo-conversazione">{l.persone_titolo}</h2>
                  <FormPersone
                    dati={persone} onCambia={setPersone} profilo={profilo.dati} errore={errore}
                    onDimentica={dimenticaPartner}
                    onAvanti={() => { setErrore(null); setPersoneFatte(true); setFase("preparazione"); }}
                  />
                  <button type="button" className="button button-quiet button-small" style={{ marginTop: ".8rem" }}
                    onClick={() => setFase("preparazione")}>{t.comune.indietro}</button>
                </>
              )}
            </section>

            <section className="read-panel dark" aria-labelledby="titolo-rito">
              <p className="eyebrow">{l.pannello_rito}</p>
              <div className={stili.console}>
                {/* Il pulsante subito sotto «Il tuo rito»: sul telefono non deve stare in fondo a un pannello lungo. */}
                {fase === "preparazione" && !serveAccount && (
                  <button type="button" className="button button-brass" disabled={!stesaId || inCorso || !domandaValida}
                    onClick={chiediInizio} data-an="rito" data-an-passo="inizia">
                    {inCorso ? t.comune.carica : speciale && !personeFatte ? t.comune.avanti : l.inizia}
                  </button>
                )}
                {fase === "preparazione" && !domandaValida && domanda.length > 0 && <p className="notice dark">{l.domanda_corta}</p>}
                {errore && fase === "preparazione" && <p className="error" role="alert">{errore}</p>}
                <h2 id="titolo-rito" className="console-status">{l.console_attesa}</h2>
                {!(stesa && fase === "preparazione" && !serveAccount) && <p className={stili.consoleTesto}>{l.console_attesa_testo}</p>}
                {/* Ciò che si può leggere se si vuole: in riquadri a parte, chiusi, perché si capisca che è facoltativo. */}
                {stesa && fase === "preparazione" && !serveAccount && (
                  <details className={stili.facoltativo}>
                    <summary>{l.stesa_info}</summary>
                    <StesaNellaConsole stesa={stesa} />
                  </details>
                )}
                {fase === "preparazione" && !serveAccount && (
                  <details className={stili.facoltativo}>
                    <summary>{l.vero_info}</summary>
                    <Dichiarazione breve />
                  </details>
                )}
                {senzaCrediti && (
                  <p className="notice dark">
                    {l.crediti_finiti}. <LinkV2 className="inline" style={{ color: "var(--brass-pale)" }} href={R.prezzi}>{l.vedi_prezzi}</LinkV2>
                  </p>
                )}
              </div>
            </section>
          </div>
        </section>
        {dialoghiComuni}
      </>
    );
  }

  /* ---- la lettura ---- */

  const daScegliere = stesa ? stesa.carte_da_scegliere - posate.filter((p) => !p.calcolata).length : 0;
  const inRito = fase !== "intervista";
  const stato: { etichetta: string; testo?: string } =
    fase === "intervista" ? { etichetta: l.console_intervista, testo: l.console_intervista_testo }
      : fase === "pronto-mescolare" ? { etichetta: l.console_pronto, testo: l.console_pronto_testo }
        : fase === "mescolamento" ? { etichetta: l.console_mescola, testo: l.console_mescola_testo }
          : fase === "taglio" ? { etichetta: l.console_taglio, testo: l.console_taglio_testo }
            : fase === "scelta" ? { etichetta: l.console_scelta, testo: daScegliere === 1 ? l.scegli_uno : f(l.scegli_n, { n: daScegliere }) }
              : fase === "rivelazione" || fase === "pronto-sintesi" || fase === "svelamento" ? { etichetta: l.console_rivela, testo: l.console_rivela_testo }
                : fase === "crisi" ? { etichetta: l.crisi_titolo }
                  : fase === "annullata" ? { etichetta: l.pausa_titolo }
                    : { etichetta: l.console_sintesi };

  const ritoInDialogo = stretto && !ritoChiuso
    && (fase === "mescolamento" || fase === "taglio" || fase === "scelta" || fase === "rivelazione" || fase === "pronto-sintesi");
  const contenutoRito = (
    <>
                <h2 id="titolo-console" className={`console-status ${stili.istruzione}`} aria-live="polite">{stato.etichetta}</h2>
                {stato.testo && <p className={`${stili.consoleTesto} ${stili.soloAmpio}`}>{stato.testo}</p>}
                {fase === "scelta" && <p className={`small ${stili.soloAmpio}`} style={{ margin: 0, color: "#d9cade" }}>{l.console_scelta_sigillo}</p>}
                <LayoutGroup>
                  {stesa && fase !== "crisi" && (
                    <Tavolo
                      stesa={stesa} posate={posate}
                      prossima={fase === "scelta" ? prossimaDaScegliere : fase === "rivelazione" ? prossimaDaRivelare : null}
                      onRivela={() => void rivelaTutto()} rivelazioneInCorso={rivelazioneInCorso}
                      evidenzia={fase === "scelta" ? "scelta" : fase === "rivelazione" ? "rivelazione" : null}
                      nomePartner={nomePartner} manuale={manuale}
                    />
                  )}
                  <div className={stili.zona}>
                    <AnimatePresence mode="wait">
                      {fase === "mescolamento" && (
                        <motion.div key="m" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                          <Mescolamento onFerma={fermaMescolata} />
                        </motion.div>
                      )}
                      {fase === "taglio" && (
                        <motion.div key="t" style={{ width: "100%" }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                          <Taglio onTaglia={taglia} />
                        </motion.div>
                      )}
                    </AnimatePresence>
                    {fase === "scelta" && (
                      <Ventaglio quante={slotTotali} scelte={scelte} attivo={daScegliere > 0} onScegli={scegli} />
                    )}
                  </div>
                </LayoutGroup>
                {fase === "pronto-mescolare" && (
                  <button type="button" className={`button button-brass ${stili.pulsa}`} onClick={mescola}>{l.mescola}</button>
                )}
                {fase === "mescolamento" && (
                  <button type="button" className="button button-light" onClick={fermaMescolata}>{l.ferma}</button>
                )}
                {(fase === "rivelazione" || fase === "pronto-sintesi") && (
                  <button type="button" className={`button button-brass ${stili.pulsa}`} disabled={rivelazioneInCorso} onClick={() => void rivelaTutto()}
                    data-an="rito" data-an-passo="rivela_e_interpreta">
                    {l.rivela_tutto}
                  </button>
                )}
                {(fase === "crisi" || fase === "annullata") && (
                  <button type="button" className="button button-light" onClick={nuova}>{l.nuova}</button>
                )}
                {errore && fase !== "intervista" && <p className="error" role="alert">{errore}</p>}
    </>
  );

  return (
    <ProviderMazzoAttivo slug={slugAttivo}>
      <LinguaNomi valore={linguaLettura}>
        <section className="band band-tight">
          <div className={stili.scena}>
            <small>
              {stesa ? `${nomeStesa(stesa, ll)} · ${plurale(stesa.posizioni.length, tl.n_carte)}` : ""}
              {nomePartner ? ` · ${f(tl.tu_e, { nome: nomePartner })}` : ""}
            </small>
            {domandaLettura && <q dir="auto">{domandaLettura}</q>}
          </div>

          <div className={`read-layout ${inRito ? stili.inRito : ""}`}>
            <section className="read-panel" aria-labelledby="titolo-dialogo" id="pannello-dialogo">
              <p className="eyebrow">{l.pannello_conversazione}</p>
              <h2 id="titolo-dialogo" className="sr-only">{l.pannello_conversazione}</h2>
              <Dialogo battute={battute} attesa={attesa}
                inputAttivo={fase === "intervista" && (modo === "risposta" || modo === "libero")}
                libero={modo === "libero"}
                onRispondi={modo === "libero" ? (t) => { void suLibero(t); } : suRisposta}
                scelte={sceltePossibili} />
              {errore && fase === "intervista" && (
                <div className="button-row" style={{ marginTop: ".8rem" }}>
                  <p className="error" role="alert" style={{ flex: "1 1 100%" }}>{errore}</p>
                  {id && !attesa && <button type="button" className="button button-quiet button-small" onClick={() => passoIntervista(id, null)}>{l.riprova}</button>}
                </div>
              )}
            </section>

            <section className={`read-panel dark ${stili.pannelloRito}`} aria-labelledby="titolo-console" id="zona-mazzo">
              <p className={`eyebrow ${stili.soloAmpio}`}>{l.pannello_rito}</p>
              {ritoInDialogo ? (
                <div className={stili.console}>
                  <h2 id="titolo-console" className={`console-status ${stili.istruzione}`}>{stato.etichetta}</h2>
                  <button type="button" className="button button-light" onClick={() => setRitoChiuso(false)}>{l.rito_riapri}</button>
                </div>
              ) : (
                <div className={stili.console}>{contenutoRito}</div>
              )}
            </section>
          </div>
        </section>

        <Modale aperta={ritoInDialogo} titolo={stato.etichetta} onChiudi={() => setRitoChiuso(true)} larga scura>
          {/* Nel dialogo il titolo è già l'istruzione: niente doppione, niente spiegazioni lunghe. */}
          <div className={`${stili.console} ${stili.ritoInDialogo}`}>{contenutoRito}</div>
        </Modale>

        {(fase === "svelamento" || fase === "sintesi" || fase === "completata" || posate.some((p) => p.rivelata)) && stesa && id && (
          <section className="band band-tight" id="zona-responso" style={{ paddingTop: 0 }}>
            <CarteSvelate stesa={stesa} posate={posate} attiva={fase === "svelamento" || rivelazioneInCorso} lettoreLegge={lettoreLegge} />
            {fase === "sintesi" && !testoResponso && <FaseResponso fase={faseResponso} />}
            {testoResponso && (
              <Responso
                id={id} testo={testoResponso} finito={fase === "completata"}
                disclaimer={fine?.disclaimer ?? disclaimer ?? ""} commitment={fine?.commitment ?? null} saldo={fine?.saldo ?? null}
                anonimo={fine?.anonimo ?? !sessione.autenticata} omaggi={nOmaggi} onNuova={nuova} onRegistrati={registrati}
              />
            )}
            {fase === "completata" && <NotaStampa />}
          </section>
        )}
        {dialoghiComuni}
      </LinguaNomi>
    </ProviderMazzoAttivo>
  );
}
