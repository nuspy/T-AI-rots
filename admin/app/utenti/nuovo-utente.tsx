"use client";

import Link from "next/link";
import { useState } from "react";
import { creaUtente } from "@/lib/api";
import { useAzione } from "@/lib/usa";
import stili from "../comuni.module.css";

/* Aggiungere un utente a mano.
 *
 * L'email è anche il nome utente (il realm entra con l'email). La password la
 * sceglie chi crea l'account e la comunica alla persona: non viene mai
 * mostrata di nuovo né registrata, e la persona può cambiarla dal profilo. */
export function NuovoUtente({ dopoCreazione }: { dopoCreazione: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [aperto, setAperto] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nome, setNome] = useState("");
  const [mostra, setMostra] = useState(false);
  const [creato, setCreato] = useState<{ id: number; email: string } | null>(null);

  const valido = email.trim() !== "" && password !== "";

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valido) return;
    setCreato(null);
    const fatto = await esegui((t) =>
      creaUtente(t, { email: email.trim(), password, nome: nome.trim() || undefined }),
    );
    if (fatto) {
      setCreato({ id: fatto.id, email: fatto.email ?? email.trim() });
      setEmail("");
      setPassword("");
      setNome("");
      setMostra(false);
      setAperto(false);
      dopoCreazione();
    }
  };

  if (!aperto) {
    return (
      <div style={{ marginBottom: "1.25rem" }}>
        <button className={stili.primaria} onClick={() => setAperto(true)}>
          Nuovo utente
        </button>
        {creato && (
          <p className={stili.esito} role="status">
            Utente creato:{" "}
            <Link href={`/utenti/${creato.id}`} className={stili.collegamento}>
              {creato.email}
            </Link>
            . Comunicagli la password: da qui non si rivede.
          </p>
        )}
      </div>
    );
  }

  return (
    <section className={stili.riquadro} style={{ marginBottom: "1.25rem" }}>
      <h2 className={stili.riquadroTitolo}>Nuovo utente</h2>
      <p className={stili.riquadroNota}>
        L&apos;account nasce subito, con l&apos;email già verificata, il piano gratuito e il regalo d&apos;iscrizione
        come chi si iscrive da sé. Entra con questa email e questa password.
      </p>
      <form onSubmit={invia}>
        <label className={stili.campo}>
          <span className={stili.campoEtichetta}>Email (è anche il nome utente)</span>
          <input
            className={stili.ingresso}
            type="email"
            inputMode="email"
            autoComplete="off"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            maxLength={254}
            required
          />
        </label>
        <label className={stili.campo}>
          <span className={stili.campoEtichetta}>Password</span>
          <input
            className={stili.ingresso}
            type={mostra ? "text" : "password"}
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            maxLength={128}
            required
          />
          <span className={stili.campoAiuto}>
            Almeno 6 caratteri, diversa dall&apos;email.{" "}
            <button type="button" className={stili.collegamento} onClick={() => setMostra((m) => !m)}>
              {mostra ? "Nascondi" : "Mostra"}
            </button>
          </span>
        </label>
        <label className={stili.campo}>
          <span className={stili.campoEtichetta}>Nome (facoltativo)</span>
          <input
            className={stili.ingresso}
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            maxLength={100}
          />
        </label>
        {errore && <p className={stili.errore}>{errore}</p>}
        <div className={stili.riga}>
          <button className={stili.primaria} type="submit" disabled={!valido || inCorso}>
            {inCorso ? "Creazione…" : "Crea utente"}
          </button>
          <button className={stili.secondaria} type="button" onClick={() => setAperto(false)} disabled={inCorso}>
            Annulla
          </button>
        </div>
      </form>
    </section>
  );
}
