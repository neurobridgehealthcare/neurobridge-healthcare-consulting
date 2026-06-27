import { founder } from "@/lib/data";

export function ExperienceTimeline() {
  return (
    <div className="relative mx-auto max-w-3xl">
      <div
        className="absolute bottom-0 left-[19px] top-2 w-px bg-gradient-to-b from-teal-500/50 via-teal-500/20 to-transparent"
        aria-hidden
      />

      <div className="space-y-8">
        {founder.timeline.map((item) => (
          <div key={`${item.organization}-${item.role}`} className="relative pl-14">
            <div
              className="absolute left-0 top-6 z-10 flex h-10 w-10 items-center justify-center rounded-full border-2 border-white bg-navy-900 shadow-lg"
              aria-hidden
            >
              <span className="h-2.5 w-2.5 rounded-full bg-teal-400" />
            </div>

            <div className="rounded-2xl border border-navy-900/5 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.15em] text-teal-600">
                {item.period}
              </p>
              <h3 className="mt-2 font-display text-lg font-bold text-navy-900">
                {item.organization}
              </h3>
              <p className="mt-1 text-sm font-medium text-navy-700/80">{item.role}</p>
              <p className="mt-3 text-sm leading-relaxed text-navy-700/65">
                {item.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
