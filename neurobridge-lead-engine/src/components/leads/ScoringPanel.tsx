"use client";

import { calculatePriorityScore } from "@/lib/scoring";
import { SCORING_LABELS } from "@/lib/constants";
import type { ScoringFactors } from "@/lib/types";
import { PriorityBadge } from "@/components/ui/PriorityBadge";

interface ScoringPanelProps {
  scoring: ScoringFactors;
  onChange?: (scoring: ScoringFactors) => void;
  readOnly?: boolean;
}

export function ScoringPanel({ scoring, onChange, readOnly }: ScoringPanelProps) {
  const total = calculatePriorityScore(scoring);

  function updateFactor(key: keyof ScoringFactors, value: number) {
    onChange?.({ ...scoring, [key]: value });
  }

  return (
    <div className="dashboard-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="font-display text-sm font-semibold text-white">Lead Scoring</h3>
          <p className="text-xs text-slate-500">Weighted score 0–100 across seven factors</p>
        </div>
        <PriorityBadge score={total} />
      </div>

      <div className="space-y-4">
        {SCORING_LABELS.map(({ key, label, description }) => (
          <div key={key}>
            <div className="mb-1.5 flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-200">{label}</p>
                <p className="text-[11px] text-slate-500">{description}</p>
              </div>
              <span className="text-sm font-medium tabular-nums text-teal-400">
                {scoring[key]}
              </span>
            </div>
            {!readOnly && (
              <input
                type="range"
                min={0}
                max={100}
                value={scoring[key]}
                onChange={(e) => updateFactor(key, Number(e.target.value))}
                className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-navy-700 accent-teal-500"
              />
            )}
            {readOnly && (
              <div className="h-1.5 overflow-hidden rounded-full bg-navy-700">
                <div
                  className="h-full rounded-full bg-teal-500/70"
                  style={{ width: `${scoring[key]}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
