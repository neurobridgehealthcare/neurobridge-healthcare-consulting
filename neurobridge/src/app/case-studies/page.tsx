import { Clock, MapPin } from "lucide-react";
import { caseStudies, caseStudiesPage } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { CTASection, PageHero } from "@/components/ui/PageHero";
import { Container, Section, SectionHeader } from "@/components/ui/Section";

export const metadata = {
  title: "Case Studies",
  description:
    "NeuroBridge program development initiatives in neurophysiology infrastructure for hospitals and healthcare systems.",
};

export default function CaseStudiesPage() {
  const { hero, cta } = caseStudiesPage;

  return (
    <>
      <PageHero
        eyebrow={hero.eyebrow}
        title={hero.title}
        description={hero.description}
      />

      <Section>
        <Container>
          <div className="space-y-8">
            {caseStudies.map((study) => (
              <article
                key={study.title}
                className="group relative overflow-hidden rounded-3xl border border-navy-900/5 bg-white shadow-sm transition-all duration-300 hover:shadow-lg hover:shadow-teal-500/5"
              >
                <div className="grid lg:grid-cols-5">
                  <div className="relative flex items-center justify-center bg-gradient-to-br from-navy-900 via-navy-800 to-navy-900 p-10 lg:col-span-2">
                    <div
                      className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(20,184,166,0.15),transparent_60%)]"
                      aria-hidden
                    />
                    <svg
                      viewBox="0 0 200 200"
                      className="relative h-40 w-40"
                      aria-hidden
                    >
                      <circle
                        cx="100"
                        cy="100"
                        r="80"
                        fill="none"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="1"
                      />
                      <circle
                        cx="100"
                        cy="100"
                        r="60"
                        fill="none"
                        stroke="rgba(255,255,255,0.08)"
                        strokeWidth="1"
                      />
                      <circle
                        cx="100"
                        cy="100"
                        r="40"
                        fill="none"
                        stroke="rgba(255,255,255,0.06)"
                        strokeWidth="1"
                      />
                      <path
                        d="M60 120 Q100 60, 140 100"
                        fill="none"
                        stroke="#14b8a6"
                        strokeWidth="2"
                        opacity="0.8"
                      />
                      <circle cx="100" cy="85" r="5" fill="#0ea5e9" />
                      <circle cx="140" cy="100" r="4" fill="#14b8a6" opacity="0.7" />
                      <circle cx="60" cy="120" r="4" fill="#0ea5e9" opacity="0.7" />
                    </svg>
                  </div>

                  <div className="p-8 md:p-10 lg:col-span-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-700">
                        <Clock className="h-3.5 w-3.5" />
                        {study.status}
                      </span>
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-teal-500/10 px-3 py-1 text-xs font-semibold text-teal-700">
                        <MapPin className="h-3.5 w-3.5" />
                        {study.region}
                      </span>
                    </div>

                    <h2 className="mt-5 font-display text-2xl font-bold text-navy-900 md:text-3xl">
                      {study.title}
                    </h2>
                    <p className="mt-4 text-base leading-relaxed text-navy-700/70">
                      {study.summary}
                    </p>

                    <div className="mt-8">
                      <p className="text-xs font-semibold uppercase tracking-widest text-navy-700/50">
                        Scope of Work
                      </p>
                      <ul className="mt-4 grid gap-3 sm:grid-cols-2">
                        {study.highlights.map((highlight) => (
                          <li
                            key={highlight}
                            className="flex items-start gap-2 text-sm text-navy-700/80"
                          >
                            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-500" />
                            {highlight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </Container>
      </Section>

      <Section className="bg-surface-muted">
        <Container>
          <div className="mx-auto max-w-2xl text-center">
            <SectionHeader
              eyebrow={cta.eyebrow}
              title={cta.title}
              description={cta.description}
            />
            <Button href="/contact" size="lg">
              Schedule a Consultation
            </Button>
          </div>
        </Container>
      </Section>

      <CTASection />
    </>
  );
}
