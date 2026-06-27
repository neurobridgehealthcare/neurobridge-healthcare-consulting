"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Search, AlertCircle } from "lucide-react";
import { LEAD_CATEGORIES, LEAD_STATUSES, getCategoryLabel } from "@/lib/constants";
import { formatFollowUpDate, isFollowUpOverdue } from "@/lib/follow-up";
import type { Lead, LeadCategory, LeadStatus } from "@/lib/types";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";

interface LeadTableProps {
  leads: Lead[];
}

export function LeadFiltersBar() {
  const router = useRouter();
  const params = useSearchParams();

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (value === "all") next.delete(key);
    else next.set(key, value);
    router.push(`/leads?${next.toString()}`);
  }

  return (
    <div className="dashboard-card flex flex-wrap items-end gap-3 p-4">
      <div className="min-w-[180px] flex-1">
        <label className="dashboard-label">Search</label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            className="dashboard-input pl-9"
            placeholder="Name, organization..."
            defaultValue={params.get("search") ?? ""}
            onChange={(e) => {
              const val = e.target.value;
              clearTimeout((window as unknown as { _searchTimer?: ReturnType<typeof setTimeout> })._searchTimer);
              (window as unknown as { _searchTimer?: ReturnType<typeof setTimeout> })._searchTimer = setTimeout(
                () => updateFilter("search", val || "all"),
                300
              );
            }}
          />
        </div>
      </div>
      <div>
        <label className="dashboard-label">Category</label>
        <select
          className="dashboard-select min-w-[160px]"
          value={params.get("category") ?? "all"}
          onChange={(e) => updateFilter("category", e.target.value)}
        >
          <option value="all">All Categories</option>
          {LEAD_CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>{c.label}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="dashboard-label">Status</label>
        <select
          className="dashboard-select min-w-[160px]"
          value={params.get("status") ?? "all"}
          onChange={(e) => updateFilter("status", e.target.value)}
        >
          <option value="all">All Statuses</option>
          {LEAD_STATUSES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </div>
      <div className="flex items-center pb-1">
        <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-400">
          <input
            type="checkbox"
            className="rounded border-white/20 bg-navy-800 accent-teal-500"
            checked={params.get("overdue") === "true"}
            onChange={(e) => updateFilter("overdue", e.target.checked ? "true" : "all")}
          />
          Overdue only
        </label>
      </div>
    </div>
  );
}

export function LeadTable({ leads }: LeadTableProps) {
  if (leads.length === 0) {
    return (
      <div className="dashboard-card flex flex-col items-center justify-center py-16 text-center">
        <p className="text-slate-400">No leads match your filters.</p>
        <Link href="/leads/new" className="btn-primary mt-4">
          Add your first lead
        </Link>
      </div>
    );
  }

  return (
    <div className="dashboard-card overflow-hidden">
      <div className="overflow-x-auto scrollbar-thin">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-white/8 text-xs uppercase tracking-wider text-slate-500">
              <th className="px-4 py-3 font-medium">Lead</th>
              <th className="px-4 py-3 font-medium">Category</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Priority</th>
              <th className="px-4 py-3 font-medium">Follow-Up</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {leads.map((lead) => {
              const overdue = isFollowUpOverdue(lead.next_follow_up_date);
              return (
                <tr key={lead.id} className="transition hover:bg-white/[0.02]">
                  <td className="px-4 py-3">
                    <Link href={`/leads/${lead.id}`} className="group">
                      <p className="font-medium text-white group-hover:text-teal-400">
                        {lead.full_name}
                      </p>
                      <p className="text-xs text-slate-500">
                        {lead.title}{lead.organization ? ` · ${lead.organization}` : ""}
                      </p>
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-slate-400">
                    {getCategoryLabel(lead.lead_category as LeadCategory)}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={lead.status as LeadStatus} />
                  </td>
                  <td className="px-4 py-3">
                    <PriorityBadge score={lead.priority_score} />
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center gap-1 text-xs ${
                        overdue ? "text-amber-400" : "text-slate-400"
                      }`}
                    >
                      {overdue && <AlertCircle className="h-3.5 w-3.5" />}
                      {formatFollowUpDate(lead.next_follow_up_date)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
