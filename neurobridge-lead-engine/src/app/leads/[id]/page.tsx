import Link from "next/link";
import { notFound } from "next/navigation";
import { ExternalLink, Pencil } from "lucide-react";
import { DashboardShell } from "@/components/layout/Sidebar";
import { FollowUpTracker } from "@/components/leads/FollowUpTracker";
import { ScoringPanel } from "@/components/leads/ScoringPanel";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  getLead,
  getMessageHistory,
  getCallOutcomes,
} from "@/lib/data/repository";
import { getCategoryLabel, getPipelineLabel } from "@/lib/constants";
import { formatFollowUpDate, isFollowUpOverdue } from "@/lib/follow-up";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function LeadDetailPage({ params }: PageProps) {
  const { id } = await params;
  const [lead, messages, calls] = await Promise.all([
    getLead(id),
    getMessageHistory(id),
    getCallOutcomes(id),
  ]);

  if (!lead) notFound();

  const overdue = isFollowUpOverdue(lead.next_follow_up_date);

  return (
    <DashboardShell>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-teal-400">
            {getCategoryLabel(lead.lead_category)}
          </p>
          <h1 className="section-title">{lead.full_name}</h1>
          <p className="section-subtitle">
            {lead.title}{lead.organization ? ` · ${lead.organization}` : ""}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <PriorityBadge score={lead.priority_score} />
          <Link href={`/leads/${id}/edit`} className="btn-secondary">
            <Pencil className="h-4 w-4" />
            Edit
          </Link>
        </div>
      </div>

      <div className="mb-6 flex flex-wrap gap-2">
        <StatusBadge status={lead.status} />
        <span className="badge bg-navy-700 text-slate-300">{getPipelineLabel(lead.pipeline_stage)}</span>
        <span
          className={`badge ${overdue ? "bg-amber-500/20 text-amber-300" : "bg-navy-700 text-slate-400"}`}
        >
          Follow-up: {formatFollowUpDate(lead.next_follow_up_date)}
        </span>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-5 lg:col-span-2">
          <div className="dashboard-card p-5">
            <h3 className="mb-4 font-display text-sm font-semibold text-white">Contact Details</h3>
            <dl className="grid gap-3 sm:grid-cols-2 text-sm">
              <DetailItem label="Specialty" value={lead.specialty} />
              <DetailItem label="Location" value={lead.country_state} />
              <DetailItem label="Email" value={lead.public_email} />
              <DetailItem label="Source" value={lead.source} />
              <DetailItem label="Website" value={lead.website} link />
              <DetailItem label="LinkedIn" value={lead.linkedin_url} link />
            </dl>
            {lead.notes && (
              <div className="mt-4 border-t border-white/8 pt-4">
                <p className="dashboard-label">Notes</p>
                <p className="text-sm leading-relaxed text-slate-300">{lead.notes}</p>
              </div>
            )}
          </div>

          <FollowUpTracker leadId={id} messages={messages} calls={calls} />
        </div>

        <ScoringPanel scoring={lead.scoring} readOnly />
      </div>
    </DashboardShell>
  );
}

function DetailItem({
  label,
  value,
  link,
}: {
  label: string;
  value: string;
  link?: boolean;
}) {
  if (!value) return null;
  return (
    <div>
      <dt className="text-xs text-slate-500">{label}</dt>
      <dd className="mt-0.5 text-slate-200">
        {link ? (
          <a
            href={value.startsWith("http") ? value : `https://${value}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-teal-400 hover:text-teal-300"
          >
            {value.replace(/^https?:\/\//, "")}
            <ExternalLink className="h-3 w-3" />
          </a>
        ) : (
          value
        )}
      </dd>
    </div>
  );
}
