/* Le pagine analytics (v8) condividono le schede. `Suspense` perché le pagine leggono il periodo
 * dall'indirizzo (`useSearchParams`), che nella build statica va dentro un confine di attesa. */

import { Suspense } from "react";
import { Schede } from "./comuni";

export default function LayoutAnalytics({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={null}>
      <Schede />
      {children}
    </Suspense>
  );
}
