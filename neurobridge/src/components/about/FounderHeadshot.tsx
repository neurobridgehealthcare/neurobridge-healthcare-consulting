import { User } from "lucide-react";
import { cn } from "@/lib/utils";

type FounderHeadshotProps = {
  className?: string;
  size?: "md" | "lg";
};

export function FounderHeadshot({ className, size = "lg" }: FounderHeadshotProps) {
  const sizeClasses = {
    md: "aspect-[4/5] max-w-xs",
    lg: "aspect-[4/5] w-full max-w-md",
  };

  return (
    <div className={cn("relative", sizeClasses[size], className)}>
      <div
        className="absolute -inset-1 rounded-2xl bg-gradient-to-br from-blue-500/20 via-transparent to-teal-500/20 blur-sm"
        aria-hidden
      />
      <div className="relative flex h-full flex-col overflow-hidden rounded-2xl border border-navy-900/8 bg-gradient-to-br from-surface-muted via-white to-surface-muted shadow-xl shadow-navy-900/5">
        <div className="relative flex flex-1 flex-col items-center justify-center bg-gradient-to-b from-navy-900/5 to-navy-900/10 p-8">
          <div className="flex h-28 w-28 items-center justify-center rounded-full border-2 border-white/80 bg-gradient-to-br from-navy-800 to-navy-900 shadow-lg md:h-36 md:w-36">
            <User className="h-14 w-14 text-white/30 md:h-16 md:w-16" strokeWidth={1.25} />
          </div>
          <div className="mt-6 text-center">
            <p className="text-[10px] font-semibold uppercase tracking-[0.25em] text-navy-700/40">
              Professional Headshot
            </p>
            <p className="mt-1 text-xs text-navy-700/30">Placeholder</p>
          </div>
        </div>
        <div className="border-t border-navy-900/5 bg-white px-6 py-4">
          <p className="text-center text-xs font-medium text-navy-700/50">
            Image to be provided
          </p>
        </div>
      </div>
    </div>
  );
}
