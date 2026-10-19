import { siteConfig } from "@/lib/data";
import { cn } from "@/lib/utils";

export function Disclaimer({
  className,
  light = false,
}: {
  className?: string;
  light?: boolean;
}) {
  return (
    <p
      className={cn(
        "text-xs leading-relaxed",
        light ? "text-white/55" : "text-navy-700/60",
        className
      )}
    >
      {siteConfig.disclaimer}
    </p>
  );
}
