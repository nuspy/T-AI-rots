"use client";

/* Il dock del lettore: l'ingresso conversazionale che resta con te fra le pagine (specifica v2, §6-7).
 *
 * Chi non ha fatto l'accesso scrive la sua domanda e comincia la lettura gratuita (`/v2/read?question=…`): è il
 * percorso anonimo già esistente e già limitato (una lettura per browser), non una chat libera senza account —
 * aprire l'inferenza a chiunque sarebbe un costo e un abuso senza limite.
 *
 * Chi è dentro trova la conversazione vera con il suo lettore (la chat proattiva del sito): lo storico, la
 * riapertura dopo un po' di silenzio («Last week you asked…»), le proposte di lettura. Quando il lettore scrive
 * da sé, il dock mostra un punto e, se il suono è acceso, un rintocco.
 *
 * Non compare dove c'è già una conversazione in pagina: la home (la domanda sta nell'eroe), la lettura, la
 * lettura delle proprie carte e le letture condivise. */

import { useCallback, useEffect, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { avviaChat, impostazioniChat, inviaMessaggioChat, storicoChat, type TurnoChat } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2, senzaPrefisso } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";

const CHIAVE_MUTO = "tarots.chat.muto";

const leggiMuto = () => {
  try {
    return window.localStorage.getItem(CHIAVE_MUTO) === "1";
  } catch {
    return false;
  }
};

const NASCOSTO = [R.leggi, R.fisica, `${R.home}/shared`];

export function DockLettore() {
  const { t, prefissoIt } = useLingua();
  const sessione = useSessione();
  const router = useRouter();
  const percorso = senzaPrefisso(usePathname() ?? R.home);
  const impostazioni = useCarica(impostazioniChat);

  const [aperto, setAperto] = useState(false);
  const [muto, setMuto] = useState(false);
  const [turni, setTurni] = useState<TurnoChat[]>([]);
  const [testo, setTesto] = useState("");
  const [inCorso, setInCorso] = useState(false);
  const [nuovo, setNuovo] = useState(false);
  const audio = useRef<HTMLAudioElement | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const caricato = useRef(false);
  const corpo = useRef<HTMLDivElement | null>(null);

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => setMuto(leggiMuto()), []);

  useEffect(() => {
    if (!sessione.autenticata || caricato.current) return;
    caricato.current = true;
    void storicoChat(sessione.token).then((r) => setTurni(r.turni)).catch(() => undefined);
  }, [sessione.autenticata, sessione.token]);

  const suona = useCallback(() => {
    if (!muto) audio.current?.play().catch(() => undefined);
  }, [muto]);

  const apertura = useCallback(async () => {
    const r = await avviaChat(sessione.token).catch(() => null);
    if (!r?.turno) return;
    setTurni((prima) => [...prima, r.turno!]);
    setNuovo(true);
    suona();
  }, [sessione.token, suona, setNuovo, setTurni]);

  /* Il silenzio: dopo i minuti decisi dalla console il lettore riapre da sé la conversazione. Riparte a ogni
   * turno. Solo per chi è dentro: per un visitatore non c'è una conversazione da riaprire. */
  useEffect(() => {
    if (!sessione.autenticata || !impostazioni.dati) return;
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => { void apertura(); }, impostazioni.dati.proattiva_minuti_inattivita * 60_000);
    return () => { if (timer.current) clearTimeout(timer.current); };
  }, [sessione.autenticata, impostazioni.dati, turni.length, apertura]);

  const ultimo = turni[turni.length - 1];
  useEffect(() => {
    const c = corpo.current;
    if (!c || !ultimo || !aperto) return;
    if (ultimo.ruolo === "utente") { c.scrollTo({ top: c.scrollHeight, behavior: "smooth" }); return; }
    const el = c.querySelector<HTMLElement>(`[data-turno="${CSS.escape(ultimo.id)}"]`);
    if (el) c.scrollTo({ top: el.offsetTop - 8, behavior: "smooth" });
  }, [ultimo?.id, ultimo?.ruolo, aperto]); // eslint-disable-line react-hooks/exhaustive-deps

  if (percorso === R.home || NASCOSTO.some((p) => percorso === p || percorso.startsWith(`${p}/`))) return null;

  const vai = (indirizzo: string) => router.push(indirizzoV2(indirizzo, prefissoIt));

  const invia = async () => {
    const pulito = testo.trim();
    if (!pulito) return;
    if (!sessione.autenticata) {
      vai(`${R.leggi}?question=${encodeURIComponent(pulito)}&source=dock`);
      return;
    }
    if (inCorso) return;
    setTesto("");
    setInCorso(true);
    setTurni((prima) => [...prima, { id: `locale-${Date.now()}`, ruolo: "utente", testo: pulito, proposta: null, creato: null }]);
    const r = await inviaMessaggioChat(sessione.token, pulito).catch(() => null);
    setInCorso(false);
    if (r?.turno) setTurni((prima) => [...prima, r.turno!]);
  };

  const alterna = () => {
    setAperto((a) => !a);
    setNuovo(false);
  };

  const cambiaMuto = () => {
    const v = !muto;
    setMuto(v);
    try {
      window.localStorage.setItem(CHIAVE_MUTO, v ? "1" : "0");
    } catch {
      /* preferenza persa: pazienza */
    }
  };

  const dentro = sessione.autenticata;
  return (
    <div className="dock">
      {dentro && <audio ref={audio} src="/suoni/chime.wav" preload="none" />}
      {aperto && (
        <section className="dock-panel" id="dock-lettore" aria-labelledby="dock-titolo">
          <div className="dock-head">
            <h2 id="dock-titolo">{dentro ? t.comune.dock_titolo : t.comune.dock_titolo_anonimo}</h2>
            <div>
              {dentro && (
                <button type="button" onClick={cambiaMuto} aria-label={muto ? t.comune.dock_muto : t.comune.dock_suono}
                  title={muto ? t.comune.dock_muto : t.comune.dock_suono}>
                  {muto ? "🔇" : "🔊"}
                </button>
              )}
              <button type="button" onClick={alterna} aria-label={t.comune.chiudi}>✕</button>
            </div>
          </div>
          <div className="dock-body" ref={corpo} role="log" aria-live="polite">
            {!dentro && <p className="intro">{t.comune.dock_testo_anonimo}</p>}
            {dentro && turni.length === 0 && <p className="intro">{t.comune.dock_vuoto}</p>}
            {dentro && turni.map((turno) => (
              <div key={turno.id} data-turno={turno.id} style={{ display: "grid" }}>
                <p className={`message ${turno.ruolo === "utente" ? "message-user" : ""}`} dir="auto">{turno.testo}</p>
                {turno.proposta && (
                  <button
                    type="button" className="button button-light button-small" style={{ marginTop: ".5rem", justifySelf: "start" }}
                    onClick={() => vai(`${R.leggi}?question=${encodeURIComponent(turno.proposta!.argomento)}&type=${turno.proposta!.categoria}&source=dock`)}
                  >
                    {f(t.comune.dock_proposta, { argomento: turno.proposta.argomento })}
                  </button>
                )}
              </div>
            ))}
            {inCorso && <span className="typing" aria-label={t.comune.dock_attesa}><span /><span /><span /></span>}
          </div>
          <form className="dock-form" onSubmit={(e) => { e.preventDefault(); void invia(); }}>
            <textarea
              value={testo} rows={1} maxLength={2000} dir="auto"
              placeholder={dentro ? t.comune.dock_segnaposto : t.comune.dock_segnaposto_anonimo}
              aria-label={dentro ? t.comune.dock_segnaposto : t.comune.dock_segnaposto_anonimo}
              onChange={(e) => setTesto(e.target.value)}
            />
            <button type="submit" className="button button-brass" disabled={!testo.trim() || (dentro && inCorso)}>
              {dentro ? t.comune.dock_invia : t.comune.dock_invia_anonimo}
            </button>
          </form>
        </section>
      )}
      <button type="button" className="dock-toggle" onClick={alterna} aria-expanded={aperto} aria-controls="dock-lettore"
        aria-label={t.comune.dock_apri} data-an="dock_apri">
        {nuovo && <span className="dot" aria-hidden="true" />}
        <span aria-hidden="true">✦</span>
        <span className="label-long" aria-hidden="true">{t.comune.dock_apri}</span>
      </button>
    </div>
  );
}
