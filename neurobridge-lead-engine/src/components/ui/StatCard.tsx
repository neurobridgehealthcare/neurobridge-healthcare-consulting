import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  accent?: "teal" | "blue" | "amber" | "purple";
  subtext?: string;
}

const accentMap = {
  teal: "from-teal-500/20 to-teal-500/5 text-teal-400",
  blue: "from-blue-500/20 to-blue-500/5 text-blue-400",
  amber: "from-amber-500/20 to-amber-500/5 text-amber-400",
  purple: "from-purple-500/20 to-purple-500/5 text-purple-400",
};

export function StatCard({ label, value, icon: Icon, accent = "teal", subtext }: StatCardProps) {
  return (
    <div className="dashboard-card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
          <p className="mt-2 font-display text-3xl font-semibold tabular-nums text-white">{value}</p>
          {subtext && <p className="mt-1 text-xs text-slate-500">{subtext}</p>}
        </div>
        <div className={`rounded-lg bg-gradient-to-br p-2.5 ${accentMap[accent]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
