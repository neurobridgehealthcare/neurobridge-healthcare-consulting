"use client";

import Link from "next/link";
import { getCategoryLabel, getPipelineLabel } from "@/lib/constants";
import type { Lead, PipelineStage } from "@/lib/types";
import { PriorityBadge } from "@/components/ui/PriorityBadge";

interface PipelineBoardProps {
  leads: Lead[];
}

const ACTIVE_STAGES: PipelineStage[] = [
  "researched",
  "connected",
  "message_sent",
  "replied",
  "discovery_call_booked",
  "assessment_requested",
  "proposal_sent",
];

export function PipelineBoard({ leads }: PipelineBoardProps) {
  const closedWon = leads.filter((l) => l.pipeline_stage === "closed_won");
  const closedLost = leads.filter((l) => l.pipeline_stage === "closed_lost");

  return (
    <div>
      <div className="mb-6 overflow-x-auto pb-2 scrollbar-thin">
        <div className="flex min-w-max gap-3">
          {ACTIVE_STAGES.map((stage) => {
            const stageLeads = leads.filter((l) => l.pipeline_stage === stage);
            return (
              <div key={stage} className="w-56 shrink-0">
                <div className="mb-2 flex items-center justify-between px-1">
                  <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                    {getPipelineLabel(stage)}
                  </p>
                  <span className="rounded-full bg-navy-800 px-2 py-0.5 text-[10px] tabular-nums text-slate-400">
                    {stageLeads.length}
                  </span>
                </div>
                <div className="min-h-[200px] space-y-2 rounded-xl border border-white/8 bg-navy-900/50 p-2">
                  {stageLeads.map((lead) => (
                    <Link
                      key={lead.id}
                      href={`/leads/${lead.id}`}
                      className="block rounded-lg border border-white/5 bg-navy-800/60 p-3 transition hover:border-teal-500/30"
                    >
                      <p className="text-sm font-medium text-white">{lead.full_name}</p>
                      <p className="mt-0.5 truncate text-[11px] text-slate-500">{lead.organization}</p>
                      <div className="mt-2 flex items-center justify-between">
                        <span className="text-[10px] text-slate-500">
                          {getCategoryLabel(lead.lead_category)}
                        </span>
                        <PriorityBadge score={lead.priority_score} />
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <ClosedColumn title="Closed Won" leads={closedWon} accent="text-emerald-400" />
        <ClosedColumn title="Closed Lost" leads={closedLost} accent="text-slate-400" />
      </div>
    </div>
  );
}

function ClosedColumn({
  title,
  leads,
  accent,
}: {
  title: string;
  leads: Lead[];
  accent: string;
}) {
  return (
    <div className="dashboard-card p-4">
      <p className={`mb-3 text-xs font-medium uppercase tracking-wider ${accent}`}>
        {title} ({leads.length})
      </p>
      <div className="space-y-2">
        {leads.length === 0 ? (
          <p className="text-xs text-slate-500">None</p>
        ) : (
          leads.map((lead) => (
            <Link
              key={lead.id}
              href={`/leads/${lead.id}`}
              className="block rounded-lg border border-white/5 px-3 py-2 text-sm text-slate-300 hover:border-white/15"
            >
              {lead.full_name} · {lead.organization}
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
