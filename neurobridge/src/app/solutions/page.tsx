import { ArrowRight, Check } from "lucide-react";
import { processSteps, solutions, solutionsPage } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { ProcessStep } from "@/components/ui/Cards";
import { CTASection, PageHero } from "@/components/ui/PageHero";
import { Container, Section, SectionHeader } from "@/components/ui/Section";

export const metadata = {
  title: "Solutions",
  description:
    "Four NeuroBridge pathways: expert advisory, IONM program development, the TMS Clinic Accelerator, and training with de-identified technical review.",
};

export default function SolutionsPage() {
  const { hero, methodology, differentiation } = solutionsPage;

  return (
    <>
      <PageHero
        eyebrow={hero.eyebrow}
        title={hero.title}
        description={hero.description}
        cta={{ label: "Email Brandon", href: "/contact" }}
      />

      <Section>
        <Container>
          <div className="grid gap-8 lg:grid-cols-2">
            {solutions.map((solution) => (
              <div
                key={solution.title}
                className="group relative overflow-hidden rounded-3xl border border-navy-900/5 bg-white p-8 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-teal-500/5 md:p-10"
              >
                <div
                  className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-gradient-to-br from-blue-500/10 to-teal-500/10 blur-2xl transition-opacity group-hover:opacity-150"
                  aria-hidden
                />
                <div className="relative">
                  <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-teal-500 text-white shadow-lg shadow-teal-500/20">
                    <solution.icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-display text-2xl font-bold text-navy-900">
                    {solution.title}
                  </h3>
                  <p className="mt-3 text-sm leading-relaxed text-navy-700/70">
                    {solution.description}
                  </p>
                  <ul className="mt-6 space-y-3">
                    {solution.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-teal-500" />
                        <span className="text-sm text-navy-700/80">
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      <Section dark className="relative overflow-hidden">
        <div
          className="pointer-events-none absolute inset-0 bg-gradient-to-br from-navy-900 via-navy-800 to-navy-950"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute bottom-0 left-0 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl"
          aria-hidden
        />
        <Container className="relative">
          <SectionHeader
            eyebrow={methodology.eyebrow}
            title={methodology.title}
            description={methodology.description}
            light
          />
          <div className="grid gap-12 md:grid-cols-3 md:gap-8">
            {processSteps.map((step, i) => (
              <ProcessStep key={step.title} {...step} index={i} />
            ))}
          </div>
          <div className="mt-14 text-center">
            <Button href="/contact" size="lg">
              Email Brandon
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </Container>
      </Section>

      <Section className="bg-surface-muted">
        <Container>
          <div className="mx-auto max-w-3xl text-center">
            <SectionHeader
              eyebrow={differentiation.eyebrow}
              title={differentiation.title}
              description={differentiation.description}
            />
          </div>
          <div className="mt-4 grid gap-6 sm:grid-cols-3">
            {differentiation.pillars.map((item) => (
              <div
                key={item.title}
                className="rounded-2xl border border-navy-900/5 bg-white p-7 text-center"
              >
                <h3 className="font-display text-lg font-bold text-navy-900">
                  {item.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-navy-700/65">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      <CTASection />
    </>
  );
}
