"use client";

import { useState } from "react";
import { format, startOfWeek, addWeeks, subWeeks } from "date-fns";
import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { CONTENT_CALENDAR_SCHEDULE } from "@/lib/constants";
import type { ContentCalendarEntry } from "@/lib/types";

interface ContentCalendarViewProps {
  entries: ContentCalendarEntry[];
  weekStart: string;
}

export function ContentCalendarView({ entries, weekStart }: ContentCalendarViewProps) {
  const [localEntries, setLocalEntries] = useState(entries);
  const [generating, setGenerating] = useState<string | null>(null);

  const weekDate = new Date(weekStart + "T00:00:00");

  function navigateWeek(delta: number) {
    const next = delta > 0 ? addWeeks(weekDate, 1) : subWeeks(weekDate, 1);
    window.location.href = `/calendar?week=${format(startOfWeek(next, { weekStartsOn: 1 }), "yyyy-MM-dd")}`;
  }

  function getEntry(day: string): ContentCalendarEntry | undefined {
    return localEntries.find((e) => e.day_of_week === day);
  }

  async function generateDraft(day: string, theme: string) {
    setGenerating(day);
    try {
      const res = await fetch("/api/calendar/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme, dayLabel: day, weekStart }),
      });
      const draft = await res.json();

      const saveRes = await fetch("/api/calendar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: getEntry(day)?.id,
          week_start: weekStart,
          day_of_week: day,
          theme,
          draft_title: draft.title,
          draft_body: draft.body,
          status: "draft",
        }),
      });
      const saved = await saveRes.json();
      setLocalEntries((prev) => {
        const idx = prev.findIndex((e) => e.day_of_week === day);
        if (idx >= 0) {
          const next = [...prev];
          next[idx] = saved;
          return next;
        }
        return [...prev, saved];
      });
    } finally {
      setGenerating(null);
    }
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">Week of</p>
          <p className="font-display text-lg font-semibold text-white">
            {format(weekDate, "MMMM d, yyyy")}
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => navigateWeek(-1)} className="btn-secondary px-3">
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button onClick={() => navigateWeek(1)} className="btn-secondary px-3">
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="grid gap-4">
        {CONTENT_CALENDAR_SCHEDULE.map(({ day, theme, label }) => {
          const entry = getEntry(day);
          return (
            <div key={day} className="dashboard-card p-5">
              <div className="mb-3 flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-teal-400">{day}</p>
                  <h3 className="font-display text-sm font-semibold text-white">{label}</h3>
                </div>
                <button
                  onClick={() => generateDraft(day, theme)}
                  disabled={generating === day}
                  className="btn-secondary shrink-0 text-xs"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  {generating === day ? "Generating..." : entry ? "Regenerate" : "Generate Draft"}
                </button>
              </div>
              {entry ? (
                <div>
                  <p className="mb-2 text-sm font-medium text-slate-200">{entry.draft_title}</p>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-400">
                    {entry.draft_body}
                  </p>
                </div>
              ) : (
                <p className="text-sm text-slate-500">No draft yet for this day.</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
