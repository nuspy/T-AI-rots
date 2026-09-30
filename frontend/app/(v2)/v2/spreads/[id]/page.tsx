import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { testiServer } from "@/v2/lib/meta";
import { SchedaStesa } from "@/v2/pagine/stese";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return { title: t.stese.meta_titolo };
}

export default async function PaginaStesa({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <Pagina>
      <SchedaStesa id={id} />
    </Pagina>
  );
}
