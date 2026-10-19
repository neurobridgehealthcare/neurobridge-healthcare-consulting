import { CheckCircle2 } from "lucide-react";
import {
  credibilityStrip,
  homePage,
  problemSection,
  whyNeuroBridge,
} from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Container, Section, SectionHeader } from "@/components/ui/Section";

export function CredibilityStrip() {
  return (
    <div className="relative border-y border-white/10 bg-navy-950">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-navy-950 via-navy-900 to-navy-950" aria-hidden />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(20,184,166,0.08),transparent_70%)]" aria-hidden />
      <Container className="relative">
        <div className="grid grid-cols-1 divide-y divide-white/10 sm:grid-cols-2 sm:divide-x sm:divide-y-0 lg:grid-cols-4">
          {credibilityStrip.map((item, i) => (
            <div
              key={item.label}
              className="group flex items-center gap-4 px-2 py-6 sm:justify-center sm:px-6 lg:py-8 animate-fade-up"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500/20 to-teal-500/20 text-teal-400 ring-1 ring-white/10 transition-all duration-300 group-hover:from-blue-500/30 group-hover:to-teal-500/30">
                <item.icon className="h-4 w-4" />
              </div>
              <p className="text-sm font-semibold leading-snug tracking-wide text-white/90">
                {item.label}
              </p>
            </div>
          ))}
        </div>
      </Container>
    </div>
  );
}

export function ProblemSection() {
  return (
    <Section className="relative overflow-hidden bg-white">
      <div className="pointer-events-none absolute -left-32 top-1/2 h-96 w-96 -translate-y-1/2 rounded-full bg-blue-500/5 blur-3xl" aria-hidden />
      <Container>
        <div className="grid items-center gap-14 lg:grid-cols-2 lg:gap-20">
          <div>
            <SectionHeader
              eyebrow={problemSection.eyebrow}
              title={problemSection.title}
              description={problemSection.description}
              align="left"
            />
            <Button href="/contact" className="mt-2">
              Email Brandon
            </Button>
          </div>

          <div className="relative">
            <div className="absolute -inset-1 rounded-3xl bg-gradient-to-br from-blue-500/20 via-transparent to-teal-500/20 blur-sm" aria-hidden />
            <div className="relative overflow-hidden rounded-3xl border border-navy-900/5 bg-gradient-to-br from-navy-900 via-navy-800 to-navy-900 p-8 md:p-10">
              <div className="pointer-events-none absolute right-0 top-0 h-48 w-48 rounded-full bg-teal-500/10 blur-3xl" aria-hidden />
              <p className="text-xs font-semibold uppercase tracking-widest text-teal-400">
                Infrastructure Gaps
              </p>
              <ul className="mt-6 space-y-4">
                {problemSection.painPoints.map((point) => (
                  <li key={point} className="flex items-start gap-3">
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-teal-500/15">
                      <CheckCircle2 className="h-3 w-3 text-teal-400" />
                    </span>
                    <span className="text-sm leading-relaxed text-white/75">
                      {point}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="mt-8 rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-medium text-white/90">
                  {problemSection.callout}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </Section>
  );
}

export function WhyNeuroBridgeSection() {
  return (
    <Section className="bg-surface-muted">
      <Container>
        <SectionHeader
          eyebrow={homePage.whySection.eyebrow}
          title={homePage.whySection.title}
          description={homePage.whySection.description}
        />
        <div className="space-y-5">
          <div className="grid gap-5 md:grid-cols-3">
            {whyNeuroBridge.slice(0, 3).map((item, i) => (
              <WhyCard key={item.title} item={item} index={i} />
            ))}
          </div>
          <div className="mx-auto grid max-w-4xl gap-5 md:grid-cols-2">
            {whyNeuroBridge.slice(3).map((item, i) => (
              <WhyCard key={item.title} item={item} index={i + 3} />
            ))}
          </div>
        </div>
      </Container>
    </Section>
  );
}

function WhyCard({
  item,
  index,
}: {
  item: (typeof whyNeuroBridge)[number];
  index: number;
}) {
  return (
    <div
      className="group relative overflow-hidden rounded-2xl border border-navy-900/5 bg-white p-7 shadow-sm transition-all duration-500 hover:-translate-y-1 hover:border-teal-500/20 hover:shadow-xl hover:shadow-teal-500/5"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div
        className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-gradient-to-br from-blue-500/10 to-teal-500/10 opacity-0 blur-2xl transition-opacity duration-500 group-hover:opacity-100"
        aria-hidden
      />
      <div className="relative">
        <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-navy-900 to-navy-800 text-teal-400 shadow-lg shadow-navy-900/10 transition-all duration-300 group-hover:from-blue-500 group-hover:to-teal-500 group-hover:text-white">
          <item.icon className="h-5 w-5" />
        </div>
        <h3 className="font-display text-lg font-bold text-navy-900">
          {item.title}
        </h3>
        <p className="mt-3 text-sm leading-relaxed text-navy-700/70">
          {item.description}
        </p>
      </div>
    </div>
  );
}
