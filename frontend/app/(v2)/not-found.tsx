/* La pagina che non esiste, dentro la v2: testata, piede e voce della v2. */

import { Pagina } from "@/v2/componenti/pagina";
import { NonTrovataV2 } from "@/v2/pagine/errori";

export default function NonTrovata() {
  return (
    <Pagina>
      <NonTrovataV2 />
    </Pagina>
  );
}
