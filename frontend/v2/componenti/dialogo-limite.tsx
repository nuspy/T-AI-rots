"use client";

/* Oltre un limite dell'abbonamento (v9, Fase 2b): quale limite, quante letture fatte nel periodo, e poi una delle tre
 * strade — il condono (le prime letture oltre il limite sono un regalo, e lo si dice con calore), il consenso a usare
 * un credito, o i pacchetti se i crediti sono finiti. La lettura riparte solo con un clic esplicito. */

import type { LimiteSuperato } from "@/lib/abbonamenti";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { Modale } from "@/v2/componenti/modale";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";

export function DialogoLimite({
  dettaglio, onChiudi, onConsenso, ritorno, inCorso = false,
}: {
  dettaglio: LimiteSuperato | null;
  onChiudi: () => void;
  onConsenso: (scelta: "condono" | "credito") => void;
  /** Dove tornare dopo l'acquisto di un pacchetto (la lettura interrotta). */
  ritorno: string;
  inCorso?: boolean;
}) {
  const { t, locale } = useLingua();
  const k = t.abbonamento;
  if (!dettaglio) return null;
  const titolo = k[`limite_titolo_${dettaglio.limite}` as const] ?? k.limite_titolo_letture_al_giorno;
  const periodo = k[`limite_periodo_${dettaglio.limite}` as const] ?? "";
  const condono = dettaglio.condoni_rimasti > 0;
  const libera = dettaglio.si_libera
    ? new Date(dettaglio.si_libera).toLocaleString(locale, { day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" })
    : null;

  return (
    <Modale aperta titolo={condono ? k.condono_titolo : titolo} onChiudi={onChiudi}>
      <div className="dialogo-limite">
        {condono && <p className="dialogo-limite-sopra">{titolo}</p>}
        <p>{f(k.limite_testo, { valore: dettaglio.valore, periodo, fatte: dettaglio.letture_fatte })}</p>
        {condono ? (
          <p className="dialogo-limite-dono">{f(k.condono_testo, { rimasti: dettaglio.condoni_rimasti - 1 })}</p>
        ) : dettaglio.scelta === "credito" ? (
          <p>{f(k.credito_domanda, { saldo: dettaglio.saldo })}</p>
        ) : (
          <p>{k.acquisto_testo}</p>
        )}
        {libera && !condono && <p className="small muted">{f(k.limite_si_libera, { data: libera })}</p>}
      </div>
      <div className="button-row">
        {condono ? (
          <button type="button" className="button button-brass" autoFocus disabled={inCorso} onClick={() => onConsenso("condono")}
            data-an="limite_condono">{k.condono_cta}</button>
        ) : dettaglio.scelta === "credito" ? (
          <button type="button" className="button button-brass" autoFocus disabled={inCorso} onClick={() => onConsenso("credito")}
            data-an="limite_credito">{k.credito_cta}</button>
        ) : (
          <LinkV2 className="button button-brass" href={`${R.prezzi}?ritorno=${encodeURIComponent(ritorno)}`} data-an="limite_acquisto">
            {k.acquisto_cta}
          </LinkV2>
        )}
        <button type="button" className="button button-quiet" onClick={onChiudi}>{k.non_ora}</button>
      </div>
    </Modale>
  );
}
