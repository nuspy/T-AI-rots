"use client";

import { useLingua } from "@/v2/lib/lingua";

export function SaltaAlContenuto() {
  const { t } = useLingua();
  return <a className="skip" href="#main">{t.comune.salta}</a>;
}
