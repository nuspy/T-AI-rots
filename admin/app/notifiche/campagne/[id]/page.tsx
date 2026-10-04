"use client";

import { useParams } from "next/navigation";
import { EditorCampagna } from "../../editor";

export default function PaginaCampagna() {
  const { id } = useParams<{ id: string }>();
  /* La chiave rimonta l'editor passando da una campagna all'altra: lo stato del modulo non sopravvive al cambio. */
  return <EditorCampagna key={id} id={id === "nuova" ? null : Number(id)} />;
}
