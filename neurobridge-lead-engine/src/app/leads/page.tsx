import Link from "next/link";
import { Suspense } from "react";
import { UserPlus } from "lucide-react";
import { DashboardShell } from "@/components/layout/Sidebar";
import { LeadFiltersBar, LeadTable } from "@/components/leads/LeadTable";
import { getLeads } from "@/lib/data/repository";
import type { LeadCategory, LeadFilters, LeadStatus } from "@/lib/types";

interface PageProps {
  searchParams: Promise<{
    category?: string;
    status?: string;
    search?: string;
    overdue?: string;
  }>;
}

export default async function LeadsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const filters: LeadFilters = {
    category: (params.category as LeadCategory) ?? "all",
    status: (params.status as LeadStatus) ?? "all",
    search: params.search,
    overdue_only: params.overdue === "true",
  };

  const leads = await getLeads(filters);

  return (
    <DashboardShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="section-title">Lead Dashboard</h1>
          <p className="section-subtitle">{leads.length} leads · sorted by priority</p>
        </div>
        <Link href="/leads/new" className="btn-primary">
          <UserPlus className="h-4 w-4" />
          Add Lead
        </Link>
      </div>

      <div className="mb-4">
        <Suspense fallback={<div className="dashboard-card h-20 animate-pulse" />}>
          <LeadFiltersBar />
        </Suspense>
      </div>

      <LeadTable leads={leads} />
    </DashboardShell>
  );
}
