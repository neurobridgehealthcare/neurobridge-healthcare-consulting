import { NextRequest, NextResponse } from "next/server";
import { saveContentCalendarEntry } from "@/lib/data/repository";
import type { ContentCalendarEntry } from "@/lib/types";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const entry = await saveContentCalendarEntry(body as Omit<ContentCalendarEntry, "created_at" | "updated_at">);
    return NextResponse.json(entry);
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to save entry" },
      { status: 500 }
    );
  }
}
