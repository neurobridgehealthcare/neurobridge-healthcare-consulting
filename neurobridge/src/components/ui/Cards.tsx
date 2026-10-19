import type { LucideIcon } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

type ServiceCardProps = {
  title: string;
  description: string;
  icon: LucideIcon;
  price?: string;
  href?: string;
  details?: string[];
  tier?: "s" | "a" | "additional";
  className?: string;
};

export function ServiceCard({
  title,
  description,
  icon: Icon,
  price,
  href,
  details,
  tier,
  className,
}: ServiceCardProps) {
  return (
    <div
      className={cn(
        "group relative flex flex-col rounded-2xl border border-navy-900/5 bg-white p-7 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-teal-500/20 hover:shadow-lg hover:shadow-teal-500/5",
        className
      )}
    >
      {tier === "s" && (
        <span className="absolute right-5 top-5 rounded-full bg-gradient-to-r from-blue-500/10 to-teal-500/10 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-teal-600">
          Start here
        </span>
      )}
      <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/10 to-teal-500/10 text-teal-600 transition-colors group-hover:from-blue-500 group-hover:to-teal-500 group-hover:text-white">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="font-display text-lg font-bold text-navy-900">{title}</h3>
      <p className="mt-3 flex-1 text-sm leading-relaxed text-navy-700/70">
        {description}
      </p>
      {price && href && (
        <Link
          href={href}
          className="mt-4 inline-flex text-sm font-semibold text-teal-700 hover:text-teal-600"
        >
          {price}
        </Link>
      )}
      {price && !href && (
        <p className="mt-4 text-sm font-semibold text-teal-700">{price}</p>
      )}
      {details && details.length > 0 && (
        <ul className="mt-4 space-y-2">
          {details.map((detail) => (
            <li
              key={detail}
              className="flex items-start gap-2 text-sm text-navy-700/75"
            >
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-teal-500" />
              {detail}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function AudienceCard({
  title,
  description,
  icon: Icon,
}: {
  title: string;
  description: string;
  icon: LucideIcon;
}) {
  return (
    <div className="glass group rounded-2xl p-6 transition-all duration-300 hover:shadow-lg hover:shadow-teal-500/5">
      <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-navy-900/5 text-teal-600 transition-colors group-hover:bg-gradient-to-br group-hover:from-blue-500 group-hover:to-teal-500 group-hover:text-white">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="font-display text-base font-bold text-navy-900">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-navy-700/65">{description}</p>
    </div>
  );
}

export function ProcessStep({
  step,
  title,
  description,
  icon: Icon,
  index,
}: {
  step: string;
  title: string;
  description: string;
  icon: LucideIcon;
  index: number;
}) {
  return (
    <div className="relative flex flex-col items-center text-center">
      {index < 2 && (
        <div
          className="absolute left-[calc(50%+48px)] top-12 hidden h-px w-[calc(100%-96px)] bg-gradient-to-r from-teal-500/40 to-blue-500/40 md:block"
          aria-hidden
        />
      )}
      <div className="relative mb-6 flex h-24 w-24 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-teal-500 shadow-lg shadow-teal-500/20">
        <Icon className="h-8 w-8 text-white" />
        <span className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-navy-900 text-xs font-bold text-white">
          {step}
        </span>
      </div>
      <h3 className="font-display text-xl font-bold text-white">{title}</h3>
      <p className="mt-3 max-w-xs text-sm leading-relaxed text-white/65">
        {description}
      </p>
    </div>
  );
}
