/* Google Ads: le impostazioni di AdSense e, a parte, gli appunti sul profilo pagamenti. */

import { SchedeGoogle } from "../schede";

export default function LayoutGoogle({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SchedeGoogle />
      {children}
    </>
  );
}
