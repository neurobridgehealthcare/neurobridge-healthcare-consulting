import { NextRequest, NextResponse } from "next/server";
import { createLead, getLeads } from "@/lib/data/repository";
import type { LeadFilters, LeadInput } from "@/lib/types";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const filters: LeadFilters = {
    category: (searchParams.get("category") as LeadFilters["category"]) ?? "all",
    status: (searchParams.get("status") as LeadFilters["status"]) ?? "all",
    search: searchParams.get("search") ?? undefined,
    overdue_only: searchParams.get("overdue") === "true",
  };
  const leads = await getLeads(filters);
  return NextResponse.json(leads);
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as LeadInput;
    if (!body.full_name?.trim()) {
      return NextResponse.json({ error: "Full name is required" }, { status: 400 });
    }
    const lead = await createLead(body);
    return NextResponse.json(lead, { status: 201 });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to create lead" },
      { status: 500 }
    );
  }
}
