import { NextResponse } from "next/server";
import { deleteDocument } from "@/lib/data/repository";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function DELETE(_request: Request, { params }: RouteParams) {
  const { id } = await params;
  await deleteDocument(id);
  return NextResponse.json({ success: true });
}
