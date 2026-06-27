import Link from "next/link";
import { ArrowRight } from "lucide-react";
import {
  aTierServices,
  additionalServices,
  audiences,
  developmentNote,
  homePage,
  processSteps,
  sTierServices,
} from "@/lib/data";
import {
  CredibilityStrip,
  ProblemSection,
  WhyNeuroBridgeSection,
} from "@/components/home/HomeSections";
import { Button } from "@/components/ui/Button";
import { HeroBackground } from "@/components/ui/HeroBackground";
import {
  AudienceCard,
  ProcessStep,
  ServiceCard,
} from "@/components/ui/Cards";
import { CTASection } from "@/components/ui/PageHero";
import { Container, Section, SectionHeader } from "@/components/ui/Section";

export default function HomePage() {
  const { hero, coreServices, whoWeServe, approach, expanded } = homePage;

  return (
    <>
      <section className="relative overflow-hidden bg-gradient-to-b from-surface via-white to-white pt-32 pb-16 md:pt-40 md:pb-20">
        <HeroBackground />
        <Container className="relative">
          <div className="mx-auto max-w-4xl text-center lg:max-w-5xl">
            <div className="animate-fade-up mb-6 inline-flex items-center gap-2 rounded-full border border-teal-500/20 bg-teal-500/5 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.15em] text-teal-600">
              <span className="h-1.5 w-1.5 rounded-full bg-teal-500" />
              {hero.badge}
            </div>
            <h1 className="animate-fade-up animation-delay-100 font-display text-4xl font-bold leading-[1.08] tracking-tight text-navy-900 sm:text-5xl lg:text-6xl xl:text-[3.75rem]">
              Building{" "}
              <span className="gradient-text">{hero.headlineAccent}</span> for
              Hospitals, Surgeons, and Healthcare Systems.
            </h1>
            <p className="animate-fade-up animation-delay-200 mx-auto mt-7 max-w-2xl text-lg leading-relaxed text-navy-700/70 md:text-xl">
              {hero.subheadline}
            </p>
            <div className="animate-fade-up animation-delay-300 mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button href="/contact" size="lg">
                Schedule Consultation
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button href="/services" variant="outline" size="lg">
                View Services
              </Button>
            </div>
          </div>
        </Container>
      </section>

      <CredibilityStrip />

      <ProblemSection />

      <WhyNeuroBridgeSection />

      <Section className="bg-white">
        <Container>
          <SectionHeader
            eyebrow={coreServices.eyebrow}
            title={coreServices.title}
            description={coreServices.description}
          />
          <div className="grid gap-6 md:grid-cols-3">
            {sTierServices.map((service) => (
              <ServiceCard key={service.title} {...service} tier="s" />
            ))}
          </div>
          <div className="mt-12 text-center">
            <Button href="/services" variant="outline">
              View All Services
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </Container>
      </Section>

      <Section className="bg-surface-muted">
        <Container>
          <SectionHeader
            eyebrow={whoWeServe.eyebrow}
            title={whoWeServe.title}
            description={whoWeServe.description}
          />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {audiences.map((audience) => (
              <AudienceCard key={audience.title} {...audience} />
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
          className="pointer-events-none absolute right-0 top-0 h-[500px] w-[500px] rounded-full bg-teal-500/8 blur-3xl"
          aria-hidden
        />
        <Container className="relative">
          <SectionHeader
            eyebrow={approach.eyebrow}
            title={approach.title}
            description={approach.description}
            light
          />
          <div className="grid gap-12 md:grid-cols-3 md:gap-8">
            {processSteps.map((step, i) => (
              <ProcessStep key={step.title} {...step} index={i} />
            ))}
          </div>
          <div className="mt-16 text-center">
            <Button
              href="/solutions"
              size="lg"
              variant="outline"
              className="border-white/20 text-white hover:border-teal-400/50 hover:bg-white/5"
            >
              View Program Pathways
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </Container>
      </Section>

      <Section>
        <Container>
          <div className="relative overflow-hidden rounded-[2rem] border border-teal-500/15 bg-gradient-to-br from-blue-500/5 via-white to-teal-500/5 p-8 md:p-12">
            <div
              className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-teal-500/10 blur-2xl"
              aria-hidden
            />
            <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
              <div className="max-w-2xl">
                <p className="text-xs font-semibold uppercase tracking-[0.15em] text-teal-500">
                  Current Initiatives
                </p>
                <p className="mt-3 text-lg leading-relaxed text-navy-700/80">
                  {developmentNote}
                </p>
              </div>
              <Button
                href="/case-studies"
                variant="secondary"
                className="shrink-0"
              >
                View Initiatives
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Container>
      </Section>

      <Section className="bg-white">
        <Container>
          <SectionHeader
            eyebrow={expanded.eyebrow}
            title={expanded.title}
            description={expanded.description}
          />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {[
              ...aTierServices.slice(0, 3),
              ...additionalServices.slice(0, 3),
            ].map((service) => (
              <ServiceCard key={service.title} {...service} />
            ))}
          </div>
          <div className="mt-10 text-center">
            <Link
              href="/solutions"
              className="inline-flex items-center gap-2 text-sm font-semibold text-teal-600 transition-colors hover:text-teal-500"
            >
              Review program pathways
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </Container>
      </Section>

      <CTASection />
    </>
  );
}
