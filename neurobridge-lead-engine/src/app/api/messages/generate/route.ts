import { NextRequest, NextResponse } from "next/server";
import { generateOutreachMessage } from "@/lib/openai";
import type { MessageAudience } from "@/lib/types";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const message = await generateOutreachMessage({
      audience: body.audience as MessageAudience,
      recipientName: body.recipientName,
      recipientTitle: body.recipientTitle,
      organization: body.organization,
      context: body.context,
      senderName: body.senderName,
    });
    return NextResponse.json({ message });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to generate message" },
      { status: 500 }
    );
  }
}
