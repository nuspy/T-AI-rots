/* L'involucro di ogni pagina della v2: salto al contenuto, testata, contenuto, piede. Componente del server:
 * testata e piede sono del browser (lingua, sessione), il contenuto può restare del server. */

import { DimensioneTesto } from "@/v2/lib/testo";
import { BannerProva } from "./banner-prova";
import { Piede } from "./piede";
import { SaltaAlContenuto } from "./salta";
import { Testata } from "./testata";

export function Pagina({ children, classe = "page" }: { children: React.ReactNode; classe?: string }) {
  return (
    <>
      <SaltaAlContenuto />
      <Testata />
      {/* La prova gratuita (v9, Fase 2b): nel flusso, sotto la testata, mai sopra il contenuto. */}
      <BannerProva />
      {/* A− / A+ in alto a destra, sopra il primo contenuto: un'ancora alta zero, la pagina non si sposta. */}
      <div className="dimensione-testo-ancora"><DimensioneTesto /></div>
      <main id="main" className={classe}>{children}</main>
      <Piede />
    </>
  );
}
