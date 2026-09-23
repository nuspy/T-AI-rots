"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AUTENTICAZIONE_SPENTA, useSessione } from "@/lib/sessione";
import stili from "./guscio.module.css";

const SEZIONI = [
  { href: "/", etichetta: "Statistiche" },
  { href: "/utenti", etichetta: "Utenti" },
  { href: "/pagamenti", etichetta: "Pagamenti" },
  { href: "/catalogo", etichetta: "Catalogo" },
  { href: "/report", etichetta: "Report" },
  { href: "/registro", etichetta: "Registro" },
  { href: "/modelli", etichetta: "Modelli" },
];

/* Una voce è attiva anche sulle sue pagine interne: dal dettaglio di un
 * utente si deve capire di essere ancora in «Utenti». La radice fa
 * eccezione, o sarebbe attiva ovunque. */
function attiva(percorso: string, href: string): boolean {
  return href === "/" ? percorso === "/" : percorso === href || percorso.startsWith(`${href}/`);
}

/* Il telaio della console: accesso, navigazione, e il perimetro del ruolo.
 *
 * Il controllo del ruolo è qui e non su ogni pagina — ma è **cortesia**, non
 * sicurezza: quella sta nel backend, che risponde 403 a chiunque non abbia
 * `admin` a prescindere da cosa mostri l'interfaccia. Serve a non far vedere
 * a un utente comune una console piena di pulsanti che falliranno tutti.
 */
export function Guscio({ children }: { children: React.ReactNode }) {
  const sessione = useSessione();
  const percorso = usePathname();

  if (sessione.inCaricamento) {
    return <p className={stili.attesa}>Verifica della sessione…</p>;
  }

  if (!sessione.autenticato) {
    return (
      <div className={stili.soglia}>
        <div className={stili.sogliaColonna}>
          <h1 className={stili.sogliaTitolo}>T-AI-rots · Console</h1>
          <p className={stili.sogliaTesto}>
            Amministrazione di utenti, pagamenti, catalogo e modelli. Serve un
            account con ruolo di amministratore.
          </p>
          <button className={stili.entra} onClick={sessione.entra}>
            Entra
          </button>
        </div>
      </div>
    );
  }

  const amministratore = sessione.ruoli.includes("admin");

  return (
    <div className={stili.telaio}>
      <header className={stili.testata}>
        <Link href="/" className={stili.marchio}>
          T-AI-rots <small>· Console</small>
        </Link>

        {amministratore && (
          <nav className={stili.navigazione}>
            {SEZIONI.map((s) => (
              <Link
                key={s.href}
                href={s.href}
                className={attiva(percorso, s.href) ? stili.voceAttiva : stili.voce}
                aria-current={attiva(percorso, s.href) ? "page" : undefined}
              >
                {s.etichetta}
              </Link>
            ))}
          </nav>
        )}

        {AUTENTICAZIONE_SPENTA ? (
          <span
            className={stili.sviluppo}
            title="NEXT_PUBLIC_AUTH_DISABLED=true: le richieste partono senza token."
          >
            Auth disattivata
          </span>
        ) : (
          <>
            <span className={stili.chi}>{sessione.chi}</span>
            <button className={stili.esci} onClick={sessione.esci}>
              Esci
            </button>
          </>
        )}
      </header>

      <main className={stili.contenuto}>
        {amministratore ? (
          children
        ) : (
          <div className={stili.negato}>
            <h2>Non hai accesso alla console</h2>
            <p>
              Il tuo account non porta il ruolo <code>admin</code>. Chi
              amministra la piattaforma può assegnartelo da Keycloak.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
