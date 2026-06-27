import { NextRequest, NextResponse } from "next/server";
import { addMessageHistory, getMessageHistory } from "@/lib/data/repository";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(_request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const messages = await getMessageHistory(id);
  return NextResponse.json(messages);
}

export async function POST(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  try {
    const body = await request.json();
    const entry = await addMessageHistory({
      lead_id: id,
      channel: body.channel ?? "email",
      direction: body.direction ?? "outbound",
      subject: body.subject ?? "",
      body: body.body,
      sent_at: body.sent_at ?? new Date().toISOString(),
    });
    return NextResponse.json(entry, { status: 201 });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to log message" },
      { status: 500 }
    );
  }
}
