import { NextRequest, NextResponse } from "next/server";
import { addCallOutcome, getCallOutcomes } from "@/lib/data/repository";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(_request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  const calls = await getCallOutcomes(id);
  return NextResponse.json(calls);
}

export async function POST(request: NextRequest, { params }: RouteParams) {
  const { id } = await params;
  try {
    const body = await request.json();
    const entry = await addCallOutcome({
      lead_id: id,
      outcome: body.outcome,
      notes: body.notes ?? "",
      call_date: body.call_date ?? new Date().toISOString(),
    });
    return NextResponse.json(entry, { status: 201 });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to log call" },
      { status: 500 }
    );
  }
}
