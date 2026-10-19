import { ArrowUpRight } from "lucide-react";
import { aboutPage, founder } from "@/lib/data";
import { CapabilityStatementLink } from "@/components/about/CapabilityStatementLink";
import { CredentialBadgeRow } from "@/components/about/CredentialBadge";
import { ExperienceTimeline } from "@/components/about/ExperienceTimeline";
import { Button } from "@/components/ui/Button";
import { CTASection } from "@/components/ui/PageHero";
import { PageHeroBackground } from "@/components/ui/HeroBackground";
import { Container, Section, SectionHeader } from "@/components/ui/Section";

export const metadata = {
  title: "About",
  description:
    "Brandon Garrison, CNIM, R. EP T., founder of NeuroBridge. IONM roles from 2019, B.S. Neuroscience from Baldwin Wallace, and the scope of his consulting practice.",
};

export default function AboutPage() {
  const { hero, timeline, specialties, areasOfFocus } = aboutPage;
  const { story, areasOfFocus: focusAreas, orientation, specialties: specialtyList } =
    founder;

  return (
    <>
      <section className="relative overflow-hidden bg-gradient-to-b from-surface via-white to-surface pt-32 pb-16 md:pt-40 md:pb-20">
        <PageHeroBackground />
        <Container className="relative">
          <div className="max-w-3xl">
            <p className="animate-fade-up section-eyebrow text-teal-500">
              {hero.eyebrow}
            </p>
            <h1 className="animate-fade-up animation-delay-100 font-display mt-4 text-4xl font-bold leading-[1.1] tracking-tight text-navy-900 sm:text-5xl lg:text-[3.25rem]">
              {hero.title}
            </h1>
            <p className="animate-fade-up animation-delay-100 mt-3 text-base font-semibold text-teal-700">
              Founder, NeuroBridge Healthcare Consulting
            </p>
            <p className="animate-fade-up animation-delay-200 mt-6 text-lg leading-relaxed text-navy-700/70">
              {hero.description}
            </p>
            <div className="animate-fade-up animation-delay-200 mt-8">
              <CredentialBadgeRow credentials={founder.credentials} />
            </div>
            <div className="animate-fade-up animation-delay-300 mt-8 flex flex-wrap gap-4">
              <Button href="/contact" size="lg">
                Email Brandon
                <ArrowUpRight className="h-4 w-4" />
              </Button>
              <Button href={hero.cta.href} variant="outline" size="lg">
                {hero.cta.label}
              </Button>
            </div>
          </div>
        </Container>
      </section>

      <Section className="bg-white">
        <Container>
          <div className="grid items-start gap-14 lg:grid-cols-12 lg:gap-16">
            <div className="lg:col-span-5">
              <div className="sticky top-28 rounded-2xl border border-navy-900/5 bg-surface-muted p-6">
                <p className="font-display text-lg font-bold text-navy-900">
                  {founder.name}
                </p>
                <p className="mt-1 text-sm text-navy-700/65">{founder.title}</p>
                <p className="mt-4 text-sm leading-relaxed text-navy-700/75">
                  {founder.bio}
                </p>
                <dl className="mt-6 space-y-3 text-sm">
                  <div>
                    <dt className="font-semibold text-navy-900">Education</dt>
                    <dd className="mt-1 text-navy-700/70">
                      B.S. Neuroscience, Baldwin Wallace University, 2019
                    </dd>
                  </div>
                  <div>
                    <dt className="font-semibold text-navy-900">Based in</dt>
                    <dd className="mt-1 text-navy-700/70">Macon, Georgia</dd>
                  </div>
                </dl>
              </div>
            </div>
            <div className="lg:col-span-7">
              <SectionHeader
                eyebrow={story.eyebrow}
                title={story.title}
                align="left"
              />
              <div className="space-y-5">
                {story.paragraphs.map((paragraph) => (
                  <p
                    key={paragraph.slice(0, 48)}
                    className="text-base leading-[1.8] text-navy-700/75 md:text-lg"
                  >
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </Container>
      </Section>

      <Section className="bg-surface-muted">
        <Container>
          <SectionHeader
            eyebrow={timeline.eyebrow}
            title={timeline.title}
            description={timeline.description}
          />
          <div className="mt-4">
            <ExperienceTimeline />
          </div>
        </Container>
      </Section>

      <Section className="bg-white">
        <Container>
          <SectionHeader
            eyebrow={specialties.eyebrow}
            title={specialties.title}
            description={specialties.description}
          />
          <ul className="grid gap-4 sm:grid-cols-2">
            {specialtyList.map((item) => (
              <li
                key={item}
                className="rounded-2xl border border-navy-900/5 bg-surface-muted px-5 py-4 text-sm leading-relaxed text-navy-800"
              >
                {item}
              </li>
            ))}
          </ul>
        </Container>
      </Section>

      <Section className="bg-surface-muted">
        <Container>
          <SectionHeader
            eyebrow={areasOfFocus.eyebrow}
            title={areasOfFocus.title}
            description={areasOfFocus.description}
          />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {focusAreas.map((area, i) => (
              <div
                key={area.title}
                className="group rounded-2xl border border-navy-900/5 bg-white p-7 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-teal-500/15 hover:shadow-lg hover:shadow-teal-500/5"
              >
                <span className="font-display text-3xl font-bold text-teal-500/20 transition-colors group-hover:text-teal-500/35">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <h3 className="mt-3 font-display text-lg font-bold text-navy-900">
                  {area.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-navy-700/65">
                  {area.description}
                </p>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      <Section dark className="relative overflow-hidden">
        <div
          className="pointer-events-none absolute inset-0 bg-gradient-to-br from-navy-950 via-navy-900 to-navy-950"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute right-0 top-0 h-[480px] w-[480px] rounded-full bg-teal-500/8 blur-3xl"
          aria-hidden
        />
        <Container className="relative">
          <div className="mx-auto max-w-3xl text-center">
            <p className="section-eyebrow text-teal-400">
              {orientation.eyebrow}
            </p>
            <h2 className="mt-4 font-display text-3xl font-bold text-white sm:text-4xl lg:text-5xl">
              {orientation.title}
            </h2>
            <p className="mt-8 text-xl leading-relaxed text-white/75 md:text-2xl md:leading-relaxed">
              {orientation.statement}
            </p>
            <p className="mt-8 text-base leading-relaxed text-white/55">
              {orientation.supporting}
            </p>
          </div>
        </Container>
      </Section>

      <CapabilityStatementLink />

      <CTASection />
    </>
  );
}
