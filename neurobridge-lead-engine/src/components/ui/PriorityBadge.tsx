import { getPriorityBg, getPriorityColor } from "@/lib/constants";

export function PriorityBadge({ score }: { score: number }) {
  return (
    <span
      className={`badge border ${getPriorityBg(score)} ${getPriorityColor(score)} font-semibold tabular-nums`}
    >
      {score}
    </span>
  );
}

export function ScoreBar({ score }: { score: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-navy-700">
        <div
          className="h-full rounded-full bg-gradient-to-r from-teal-500 to-blue-400 transition-all"
          style={{ width: `${score}%` }}
        />
      </div>
      <PriorityBadge score={score} />
    </div>
  );
}
