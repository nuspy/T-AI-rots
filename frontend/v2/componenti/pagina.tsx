/* L'involucro di ogni pagina della v2: salto al contenuto, testata, contenuto, piede. Componente del server:
 * testata e piede sono del browser (lingua, sessione), il contenuto può restare del server. */

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
      <main id="main" className={classe}>{children}</main>
      <Piede />
    </>
  );
}
