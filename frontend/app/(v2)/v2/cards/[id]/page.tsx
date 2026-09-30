import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { testiServer } from "@/v2/lib/meta";
import { SchedaCarta } from "@/v2/pagine/carte";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return { title: t.carte.meta_titolo };
}

export default async function PaginaCarta({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <Pagina>
      <SchedaCarta id={id} />
    </Pagina>
  );
}
