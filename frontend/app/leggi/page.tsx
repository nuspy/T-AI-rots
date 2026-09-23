"use client";

import { Suspense } from "react";
import { Involucro } from "../componenti/testata";
import { Lettura } from "./lettura";

export default function PaginaLettura() {
  return (
    <Involucro larga>
      {/* `useSearchParams` pretende un confine di sospensione in Next 16. */}
      <Suspense fallback={null}>
        <Lettura />
      </Suspense>
    </Involucro>
  );
}
