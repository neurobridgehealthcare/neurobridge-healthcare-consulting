import { NextRequest, NextResponse } from "next/server";
import { getDocuments, saveDocument } from "@/lib/data/repository";
import type { Document } from "@/lib/types";

export async function GET() {
  const documents = await getDocuments();
  return NextResponse.json(documents);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const doc = await saveDocument(body as Omit<Document, "created_at" | "updated_at">);
    return NextResponse.json(doc, { status: 201 });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to save document" },
      { status: 500 }
    );
  }
}
