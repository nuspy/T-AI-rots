"use client";

/* L'oracolo: la barra fissa in fondo alla finestra, su ogni pagina (specifica v2, §6-7; v8.5).
 *
 * Chiusa, la barra mostra ciò che l'oracolo propone da solo: per chi è dentro l'ultimo messaggio della chat
 * proattiva (nato dalle sue memorie e dalle sue letture); per chi non ha un account un tema scelto a caso, che
 * porta a una lettura gratuita. Un tocco (o un clic) sulla barra la fa crescere in verticale: due righe di chat,
 * scorrevoli per lo storico, la proposta «Leggi le carte su…» e il campo per rispondere. Esc o ✕ la richiudono.
 *
 * Chi non ha fatto l'accesso scrive la sua domanda e comincia la lettura gratuita (`/read?question=…`): è il
 * percorso anonimo già limitato (una lettura per browser), non una chat libera senza account.
 *
 * Costi: ogni apertura proattiva è un'inferenza. Per chi è dentro l'oracolo apre da solo al caricamento (solo se
 * l'ultima sua proposta ha più di 12 ore) e dopo il silenzio deciso dalla console, ma al più N volte per visita
 * (sessione del browser): N si sceglie in console (Impostazioni → Chat proattiva, predefinito 3). Chi non ha un
 * account vede temi già scritti nei dizionari, uno a caso: nessuna inferenza.
 *
 * La pagina lascia in fondo lo spazio della barra (`--oracolo-h`, misurata dal vivo), e ciò che sta in fondo (il
 * banner dei cookie, la barra del carrello) si appoggia sopra. Non compare dove c'è già una conversazione in pagina:
 * la lettura, la lettura delle proprie carte e le letture condivise. */

import { useCallback, useEffect, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { avviaChat, impostazioniChat, inviaMessaggioChat, storicoChat, type TurnoChat } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2, senzaPrefisso } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";

const CHIAVE_MUTO = "tarots.chat.muto";
const CHIAVE_APERTURA = "tarots.oracolo.aperto";
/* Quante aperture automatiche ha già fatto l'oracolo in questa visita (sessione del browser). */
const CHIAVE_CONTEGGIO = "tarots.oracolo.inferenze";

const leggiConteggio = () => {
  try {
    return Number(window.sessionStorage.getItem(CHIAVE_CONTEGGIO) ?? 0) || 0;
  } catch {
    return 0;
  }
};
const contaUna = () => {
  try {
    window.sessionStorage.setItem(CHIAVE_CONTEGGIO, String(leggiConteggio() + 1));
  } catch {
    /* senza archivio di sessione il tetto vale per caricamento */
  }
};
const DODICI_ORE = 12 * 3600 * 1000;

const leggiMuto = () => {
  try {
    return window.localStorage.getItem(CHIAVE_MUTO) === "1";
  } catch {
    return false;
  }
};

const NASCOSTO = [R.leggi, R.fisica, R.condivise];

export function DockLettore() {
  const { t, prefissoIt } = useLingua();
  const c = t.comune;
  const sessione = useSessione();
  const router = useRouter();
  const percorso = senzaPrefisso(usePathname() ?? R.home);
  const impostazioni = useCarica(impostazioniChat);
  const dentro = sessione.autenticata;

  const [aperto, setAperto] = useState(false);
  const [muto, setMuto] = useState(false);
  const [turni, setTurni] = useState<TurnoChat[]>([]);
  const [testo, setTesto] = useState("");
  const [inCorso, setInCorso] = useState(false);
  const [nuovo, setNuovo] = useState(false);
  /* Il tema proposto a chi non ha un account: scelto dopo il montaggio (sul server non c'è caso). */
  const [tema, setTema] = useState(0);
  const audio = useRef<HTMLAudioElement | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const caricato = useRef(false);
  const corpo = useRef<HTMLDivElement | null>(null);
  const barra = useRef<HTMLDivElement | null>(null);
  const campo = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMuto(leggiMuto());
    setTema(Math.floor(Math.random() * 1000));
  }, []);

  const suona = useCallback(() => {
    if (!muto) audio.current?.play().catch(() => undefined);
  }, [muto]);

  const tetto = impostazioni.dati?.proattiva_max_per_visita ?? 3;
  const apertura = useCallback(async (conSuono: boolean) => {
    if (leggiConteggio() >= tetto) return;
    contaUna();
    const r = await avviaChat(sessione.token).catch(() => null);
    if (!r?.turno) return;
    setTurni((prima) => [...prima, r.turno!]);
    setNuovo(true);
    if (conSuono) suona();
  }, [sessione.token, suona, setNuovo, setTurni, tetto]);

  /* Lo storico, e la prima proposta del giorno: se l'ultima proposta dell'oracolo è vecchia, ne apre una nuova (una
   * volta per sessione del browser, senza rintocco: la pagina è appena stata aperta). */
  useEffect(() => {
    if (!dentro || caricato.current) return;
    caricato.current = true;
    void storicoChat(sessione.token).then((r) => {
      setTurni(r.turni);
      const ultimaAi = [...r.turni].reverse().find((x) => x.ruolo === "ai");
      const vecchia = !ultimaAi?.creato || Date.now() - new Date(ultimaAi.creato).getTime() > DODICI_ORE;
      let giaFatta = false;
      try {
        giaFatta = window.sessionStorage.getItem(CHIAVE_APERTURA) === "1";
        window.sessionStorage.setItem(CHIAVE_APERTURA, "1");
      } catch {
        /* senza archivio di sessione: al più un'apertura per caricamento */
      }
      if (vecchia && !giaFatta) void apertura(false);
    }).catch(() => undefined);
  }, [dentro, sessione.token, apertura]);

  /* Il silenzio: dopo i minuti decisi dalla console il lettore riapre da sé la conversazione. Riparte a ogni turno. */
  useEffect(() => {
    if (!dentro || !impostazioni.dati) return;
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => { void apertura(true); }, impostazioni.dati.proattiva_minuti_inattivita * 60_000);
    return () => { if (timer.current) clearTimeout(timer.current); };
  }, [dentro, impostazioni.dati, turni.length, apertura]);

  /* Aperta: la conversazione scorre in fondo, il campo prende il fuoco; Esc la richiude. */
  const ultimo = turni[turni.length - 1];
  useEffect(() => {
    if (!aperto) return;
    const el = corpo.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [aperto, ultimo?.id, inCorso]);
  /* Aperta: Esc, o un tocco (clic) in qualunque altra parte della pagina, la riporta piccola sull'ultima riga. */
  useEffect(() => {
    if (!aperto) return;
    campo.current?.focus();
    const tasto = (e: KeyboardEvent) => { if (e.key === "Escape") setAperto(false); };
    const fuori = (e: PointerEvent) => {
      if (barra.current && !barra.current.contains(e.target as Node)) setAperto(false);
    };
    document.addEventListener("keydown", tasto);
    document.addEventListener("pointerdown", fuori);
    return () => {
      document.removeEventListener("keydown", tasto);
      document.removeEventListener("pointerdown", fuori);
    };
  }, [aperto]);

  const nascosta = NASCOSTO.some((p) => percorso === p || percorso.startsWith(`${p}/`));

  /* L'altezza della barra diventa lo spazio in fondo alla pagina: nessun contenuto resta sotto la barra. */
  useEffect(() => {
    const radice = document.documentElement;
    const el = barra.current;
    if (nascosta || !el) { radice.style.setProperty("--oracolo-h", "0px"); return; }
    const misura = () => radice.style.setProperty("--oracolo-h", `${Math.ceil(el.getBoundingClientRect().height)}px`);
    misura();
    const osservatore = new ResizeObserver(misura);
    osservatore.observe(el);
    return () => { osservatore.disconnect(); radice.style.setProperty("--oracolo-h", "0px"); };
  }, [nascosta]);

  if (nascosta) return null;

  const vai = (indirizzo: string) => router.push(indirizzoV2(indirizzo, prefissoIt));
  const temi = c.oracolo_temi;
  const temaScelto = temi[tema % temi.length];
  const ultimaAi = [...turni].reverse().find((x) => x.ruolo === "ai") ?? null;
  const proposta = dentro ? (ultimaAi?.testo ?? c.dock_vuoto) : temaScelto.testo;

  const invia = async () => {
    const pulito = testo.trim();
    if (!pulito) return;
    if (!dentro) {
      vai(`${R.leggi}?question=${encodeURIComponent(pulito)}&source=dock`);
      return;
    }
    if (inCorso) return;
    setNuovo(false);
    setTesto("");
    setInCorso(true);
    setTurni((prima) => [...prima, { id: `locale-${Date.now()}`, ruolo: "utente", testo: pulito, proposta: null, creato: null }]);
    const r = await inviaMessaggioChat(sessione.token, pulito).catch(() => null);
    setInCorso(false);
    if (r?.turno) setTurni((prima) => [...prima, r.turno!]);
  };

  const apri = () => { setAperto(true); setNuovo(false); };

  const cambiaMuto = () => {
    const v = !muto;
    setMuto(v);
    try {
      window.localStorage.setItem(CHIAVE_MUTO, v ? "1" : "0");
    } catch {
      /* preferenza persa: pazienza */
    }
  };

  return (
    <div className={`oracolo ${aperto ? "oracolo-aperto" : ""}`} ref={barra}>
      {dentro && <audio ref={audio} src="/suoni/chime.wav" preload="none" />}
      {!aperto ? (
        /* Chiusa: la proposta dell'oracolo al posto del campo; un tocco ovunque la apre. */
        <button type="button" className="oracolo-barra oracolo-chiusa" onClick={apri} aria-expanded={false}
          aria-label={`${c.oracolo_apri}: ${proposta}`} data-an="dock_apri">
          <span className="oracolo-segno" aria-hidden="true">
            ✦{nuovo && <span className="dot" />}
          </span>
          <span className="oracolo-proposta" dir="auto">{proposta}</span>
          <span className="button button-brass oracolo-invia" aria-hidden="true">
            <span className="oracolo-invia-testo">{dentro ? c.dock_invia : c.dock_invia_anonimo}</span>
            <span className="oracolo-invia-icona">→</span>
          </span>
        </button>
      ) : (
        <section className="oracolo-barra oracolo-espansa" aria-label={dentro ? c.dock_titolo : c.dock_titolo_anonimo}>
          <div className="oracolo-testa">
            <span className="oracolo-segno" aria-hidden="true">✦</span>
            <strong>{dentro ? c.dock_titolo : c.dock_titolo_anonimo}</strong>
            <span className="oracolo-azioni">
              {dentro && (
                <button type="button" onClick={cambiaMuto} aria-label={muto ? c.dock_muto : c.dock_suono}
                  title={muto ? c.dock_muto : c.dock_suono}>{muto ? "🔇" : "🔊"}</button>
              )}
              <button type="button" onClick={() => setAperto(false)} aria-label={c.chiudi} title={c.chiudi}>✕</button>
            </span>
          </div>
          <div className="oracolo-chat" ref={corpo} role="log" aria-live="polite">
            {dentro ? (
              <>
                {turni.length === 0 && <p className="message">{c.dock_vuoto}</p>}
                {turni.map((turno) => (
                  <div key={turno.id} className="oracolo-turno">
                    <p className={`message ${turno.ruolo === "utente" ? "message-user" : ""}`} dir="auto">{turno.testo}</p>
                    {turno.proposta && (
                      <button type="button" className="button button-light button-small"
                        onClick={() => vai(`${R.leggi}?question=${encodeURIComponent(turno.proposta!.argomento)}&type=${turno.proposta!.categoria}&source=dock`)}>
                        {f(c.dock_proposta, { argomento: turno.proposta.argomento })}
                      </button>
                    )}
                  </div>
                ))}
                {inCorso && <span className="typing" aria-label={c.dock_attesa}><span /><span /><span /></span>}
              </>
            ) : (
              <div className="oracolo-turno">
                <p className="message" dir="auto">{temaScelto.testo}</p>
                <button type="button" className="button button-light button-small" data-an="dock_tema"
                  onClick={() => vai(`${R.leggi}?question=${encodeURIComponent(temaScelto.domanda)}&source=dock`)}>
                  {c.oracolo_leggi}
                </button>
              </div>
            )}
          </div>
          <form className="oracolo-campo" onSubmit={(e) => { e.preventDefault(); void invia(); }}>
            <textarea
              ref={campo} value={testo} rows={1} maxLength={2000} dir="auto"
              placeholder={dentro ? c.dock_segnaposto : c.dock_segnaposto_anonimo}
              aria-label={dentro ? c.dock_segnaposto : c.dock_segnaposto_anonimo}
              onChange={(e) => setTesto(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void invia(); } }}
            />
            <button type="submit" className="button button-brass oracolo-invia" disabled={!testo.trim() || (dentro && inCorso)}
              data-an="dock_invia">
              <span className="oracolo-invia-testo">{dentro ? c.dock_invia : c.dock_invia_anonimo}</span>
              <span className="oracolo-invia-icona" aria-hidden="true">→</span>
            </button>
          </form>
        </section>
      )}
    </div>
  );
}
