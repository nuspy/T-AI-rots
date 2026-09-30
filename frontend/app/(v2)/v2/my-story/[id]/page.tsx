import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { testiServer } from "@/v2/lib/meta";
import { DettaglioLettura } from "@/v2/pagine/lettura-dettaglio";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return { title: t.storia.meta_titolo };
}

export default async function PaginaLettura({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <Pagina>
      <DettaglioLettura id={id} />
    </Pagina>
  );
}
