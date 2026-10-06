"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef } from "react";
import { AUTENTICAZIONE_SPENTA, useSessione } from "@/lib/sessione";
import { useTraduzione } from "@/lib/usa-traduzione";
import { Logo } from "./logo";
import { AvvisoTraduzioneConsole, SceltaLinguaConsole, useLinguaConsole } from "./traduzione-console";
import stili from "./guscio.module.css";

const SEZIONI = [
  { href: "/", etichetta: "Statistiche" },
  { href: "/analytics", etichetta: "Analytics" },
  { href: "/utenti", etichetta: "Utenti" },
  { href: "/pagamenti", etichetta: "Pagamenti" },
  { href: "/abbonamenti", etichetta: "Abbonamenti" },
  { href: "/catalogo", etichetta: "Catalogo" },
  { href: "/coupon", etichetta: "Coupon" },
  { href: "/mazzi", etichetta: "Mazzi" },
  { href: "/voto-mazzi", etichetta: "Vota il prossimo mazzo" },
  { href: "/ordini", etichetta: "Ordini" },
  { href: "/blog", etichetta: "Blog" },
  { href: "/seo", etichetta: "SEO" },
  { href: "/social", etichetta: "Social" },
  { href: "/pubblicita", etichetta: "Advertisements" },
  { href: "/notifiche", etichetta: "Notifications" },
  { href: "/report", etichetta: "Report" },
  { href: "/registro", etichetta: "Registro" },
  { href: "/modelli", etichetta: "Modelli" },
  { href: "/costi", etichetta: "Costi" },
  { href: "/backup", etichetta: "Backup" },
  { href: "/conservazione", etichetta: "Conservazione dati" },
  { href: "/impostazioni", etichetta: "Impostazioni" },
  { href: "/accesso-social", etichetta: "Accesso con i social" },
  { href: "/app-mobili", etichetta: "App mobili" },
  { href: "/account", etichetta: "Account" },
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
  /* v9.5: la console in un'altra lingua con la traduzione automatica del browser (temporanea): si traducono la
   * navigazione e il contenuto, dall'italiano. I nuovi testi delle pagine li segue il motore da sé. */
  const [lingua] = useLinguaConsole();
  const navigazione = useRef<HTMLElement>(null);
  const contenuto = useRef<HTMLElement>(null);
  const dentro = !sessione.inCaricamento && sessione.autenticato;
  const traduzione = useTraduzione([navigazione, contenuto], lingua, {
    sorgente: "it", chiave: dentro ? "dentro" : "fuori",
  });

  if (sessione.inCaricamento) {
    return <p className={stili.attesa}>Verifica della sessione…</p>;
  }

  if (!sessione.autenticato) {
    return (
      <div className={stili.soglia}>
        <div className={stili.sogliaColonna}>
          <Logo altezza={96} decorativo />
          <h1 className={stili.sogliaTitolo}>
            TAROTS <em>chat</em> · Console
          </h1>
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
          <Logo altezza={42} decorativo />
          <span>
            TAROTS <em>chat</em> <small>· Console</small>
          </span>
        </Link>

        {amministratore && (
          <nav ref={navigazione} className={stili.navigazione}>
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

        <SceltaLinguaConsole className={stili.lingua} />

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

      <main ref={contenuto} className={stili.contenuto}>
        <AvvisoTraduzioneConsole stato={traduzione} className={stili.avvisoTraduzione} />
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
