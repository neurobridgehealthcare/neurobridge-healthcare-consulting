import Link from "next/link";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import {
  additionalOfferings,
  audiences,
  featuredOfferings,
  homePage,
  processSteps,
  ventures,
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
  const { hero, coreServices, whoWeServe, approach, expanded, ventures: venturesCopy } =
    homePage;

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
              {hero.headlineBefore}{" "}
              <span className="gradient-text">{hero.headlineAccent}</span>{" "}
              {hero.headlineAfter}
            </h1>
            <p className="animate-fade-up animation-delay-200 mx-auto mt-7 max-w-2xl text-lg leading-relaxed text-navy-700/70 md:text-xl">
              {hero.subheadline}
            </p>
            <p className="animate-fade-up animation-delay-200 mx-auto mt-4 max-w-2xl text-sm font-medium text-navy-700/70">
              {hero.disclaimer}
            </p>
            <div className="animate-fade-up animation-delay-300 mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button href="/contact" size="lg">
                Email Brandon
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button href="/services" variant="outline" size="lg">
                View Offerings
              </Button>
            </div>
          </div>
        </Container>
      </section>

      <CredibilityStrip />

      <ProblemSection />

      <WhyNeuroBridgeSection />

      <Section id="offerings" className="scroll-mt-28 bg-white">
        <Container>
          <SectionHeader
            eyebrow={coreServices.eyebrow}
            title={coreServices.title}
            description={coreServices.description}
          />
          <div className="grid gap-6 md:grid-cols-3">
            {featuredOfferings.map((service) => (
              <ServiceCard
                key={service.title}
                title={service.title}
                description={service.description}
                icon={service.icon}
                price={service.price}
                tier="s"
              />
            ))}
          </div>
          <div className="mt-12 text-center">
            <Button href="/services" variant="outline">
              View All Offerings
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
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
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
              View Pathways
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </Container>
      </Section>

      <Section id="ventures" className="scroll-mt-28">
        <Container>
          <SectionHeader
            eyebrow={venturesCopy.eyebrow}
            title={venturesCopy.title}
            description={venturesCopy.description}
          />
          <div className="grid gap-6 md:grid-cols-2">
            {ventures.map((venture) => (
              <article
                key={venture.id}
                className="rounded-3xl border border-navy-900/5 bg-white p-8 shadow-sm"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/10 to-teal-500/10 text-teal-600">
                    <venture.icon className="h-5 w-5" />
                  </div>
                  <span
                    className={
                      venture.status === "In development"
                        ? "rounded-full bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-700"
                        : "rounded-full bg-teal-500/10 px-3 py-1 text-xs font-semibold text-teal-700"
                    }
                  >
                    {venture.status}
                  </span>
                </div>
                <h3 className="mt-6 font-display text-2xl font-bold text-navy-900">
                  {venture.title}
                </h3>
                <p className="mt-1 text-sm font-medium text-navy-700/60">
                  {venture.kicker}
                </p>
                <p className="mt-4 text-sm leading-relaxed text-navy-700/75">
                  {venture.summary}
                </p>
                <div className="mt-6">
                  {venture.href ? (
                    <a
                      href={venture.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-sm font-semibold text-teal-700 hover:text-teal-600"
                    >
                      {venture.hrefLabel}
                      <ArrowUpRight className="h-4 w-4" />
                    </a>
                  ) : (
                    <Link
                      href="/ventures#focus"
                      className="inline-flex items-center gap-2 text-sm font-semibold text-teal-700 hover:text-teal-600"
                    >
                      Read the scope limits
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  )}
                </div>
              </article>
            ))}
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
            {additionalOfferings.map((service) => (
              <ServiceCard
                key={service.title}
                title={service.title}
                description={service.description}
                icon={service.icon}
                price={service.price}
              />
            ))}
          </div>
          <div className="mt-10 text-center">
            <Link
              href="/services"
              className="inline-flex items-center gap-2 text-sm font-semibold text-teal-600 transition-colors hover:text-teal-500"
            >
              See scope and starting prices
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </Container>
      </Section>

      <CTASection />
    </>
  );
}
