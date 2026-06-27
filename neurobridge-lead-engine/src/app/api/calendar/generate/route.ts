import { NextRequest, NextResponse } from "next/server";
import { generateContentDraft } from "@/lib/openai";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const draft = await generateContentDraft(body.theme, body.dayLabel);
    return NextResponse.json(draft);
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to generate draft" },
      { status: 500 }
    );
  }
}
