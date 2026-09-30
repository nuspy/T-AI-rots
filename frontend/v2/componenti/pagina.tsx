/* L'involucro di ogni pagina della v2: salto al contenuto, testata, contenuto, piede. Componente del server:
 * testata e piede sono del browser (lingua, sessione), il contenuto può restare del server. */

import { Piede } from "./piede";
import { SaltaAlContenuto } from "./salta";
import { Testata } from "./testata";

export function Pagina({ children, classe = "page" }: { children: React.ReactNode; classe?: string }) {
  return (
    <>
      <SaltaAlContenuto />
      <Testata />
      <main id="main" className={classe}>{children}</main>
      <Piede />
    </>
  );
}
