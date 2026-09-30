import type { Metadata } from "next";
import { Pagina } from "@/v2/componenti/pagina";
import { testiServer } from "@/v2/lib/meta";
import { SchedaMazzo } from "@/v2/pagine/mazzi";

export async function generateMetadata(): Promise<Metadata> {
  const t = await testiServer();
  return { title: t.mazzi.meta_titolo };
}

export default async function PaginaMazzo({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return (
    <Pagina>
      <SchedaMazzo slug={slug} />
    </Pagina>
  );
}
