import Link from "next/link";
import { format } from "date-fns";
import { Users, AlertTriangle, GitBranch, TrendingUp, ArrowRight } from "lucide-react";
import { DashboardShell } from "@/components/layout/Sidebar";
import { StatCard } from "@/components/ui/StatCard";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { getDashboardStats, getLeads } from "@/lib/data/repository";
import { getCategoryLabel } from "@/lib/constants";
import { formatFollowUpDate, isFollowUpOverdue } from "@/lib/follow-up";

export default async function HomePage() {
  const [stats, leads] = await Promise.all([getDashboardStats(), getLeads()]);
  const overdueLeads = leads.filter((l) => isFollowUpOverdue(l.next_follow_up_date));
  const topLeads = leads.slice(0, 5);

  return (
    <DashboardShell>
      <div className="mb-8">
        <h1 className="section-title">Overview</h1>
        <p className="section-subtitle">
          {format(new Date(), "EEEE, MMMM d, yyyy")} — NeuroBridge business development
        </p>
      </div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Leads" value={stats.totalLeads} icon={Users} accent="blue" />
        <StatCard
          label="Overdue Follow-Ups"
          value={stats.overdueFollowUps}
          icon={AlertTriangle}
          accent="amber"
          subtext="Requires attention"
        />
        <StatCard label="Active Pipeline" value={stats.pipelineActive} icon={GitBranch} accent="purple" />
        <StatCard
          label="Avg Priority Score"
          value={stats.avgPriorityScore}
          icon={TrendingUp}
          accent="teal"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="dashboard-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-sm font-semibold text-white">Overdue Follow-Ups</h2>
            <Link href="/leads?overdue=true" className="text-xs text-teal-400 hover:text-teal-300">
              View all
            </Link>
          </div>
          {overdueLeads.length === 0 ? (
            <p className="text-sm text-slate-500">No overdue follow-ups. You're on track.</p>
          ) : (
            <div className="space-y-3">
              {overdueLeads.slice(0, 5).map((lead) => (
                <Link
                  key={lead.id}
                  href={`/leads/${lead.id}`}
                  className="flex items-center justify-between rounded-lg border border-amber-500/20 bg-amber-500/5 px-4 py-3 transition hover:border-amber-500/40"
                >
                  <div>
                    <p className="text-sm font-medium text-white">{lead.full_name}</p>
                    <p className="text-xs text-slate-500">{lead.organization}</p>
                  </div>
                  <span className="text-xs text-amber-400">
                    {formatFollowUpDate(lead.next_follow_up_date)}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="dashboard-card p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-sm font-semibold text-white">Top Priority Leads</h2>
            <Link href="/leads" className="flex items-center gap-1 text-xs text-teal-400 hover:text-teal-300">
              All leads <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="space-y-3">
            {topLeads.map((lead) => (
              <Link
                key={lead.id}
                href={`/leads/${lead.id}`}
                className="flex items-center justify-between rounded-lg border border-white/5 px-4 py-3 transition hover:border-white/15"
              >
                <div>
                  <p className="text-sm font-medium text-white">{lead.full_name}</p>
                  <p className="text-xs text-slate-500">
                    {getCategoryLabel(lead.lead_category)} · {lead.organization}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={lead.status} />
                  <PriorityBadge score={lead.priority_score} />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </DashboardShell>
  );
}
