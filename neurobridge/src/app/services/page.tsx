import { ArrowRight, Check } from "lucide-react";
import {
  aTierServices,
  additionalServices,
  servicesPage,
  sTierServices,
} from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { ServiceCard } from "@/components/ui/Cards";
import { CTASection, PageHero } from "@/components/ui/PageHero";
import { Container, Section, SectionHeader } from "@/components/ui/Section";

export const metadata = {
  title: "Services",
  description:
    "Clinical oversight, quality assurance, and neurophysiology program development services for hospitals and healthcare systems.",
};

export default function ServicesPage() {
  const { hero, sTier, aTier, additional, engagement } = servicesPage;

  return (
    <>
      <PageHero
        eyebrow={hero.eyebrow}
        title={hero.title}
        description={hero.description}
        cta={{ label: "Schedule Consultation", href: "/contact" }}
      />

      <Section>
        <Container>
          <SectionHeader
            eyebrow={sTier.eyebrow}
            title={sTier.title}
            description={sTier.description}
            align="left"
          />
          <div className="grid gap-6 lg:grid-cols-3">
            {sTierServices.map((service) => (
              <ServiceCard key={service.title} {...service} tier="s" />
            ))}
          </div>
        </Container>
      </Section>

      <Section className="bg-surface-muted">
        <Container>
          <SectionHeader
            eyebrow={aTier.eyebrow}
            title={aTier.title}
            description={aTier.description}
            align="left"
          />
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {aTierServices.map((service) => (
              <ServiceCard key={service.title} {...service} />
            ))}
          </div>
        </Container>
      </Section>

      <Section>
        <Container>
          <SectionHeader
            eyebrow={additional.eyebrow}
            title={additional.title}
            description={additional.description}
            align="left"
          />
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {additionalServices.map((service) => (
              <ServiceCard key={service.title} {...service} />
            ))}
          </div>
        </Container>
      </Section>

      <Section className="bg-navy-900">
        <Container>
          <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-teal-400">
                {engagement.eyebrow}
              </p>
              <h2 className="mt-4 font-display text-3xl font-bold text-white sm:text-4xl">
                {engagement.title}
              </h2>
              <p className="mt-5 text-lg leading-relaxed text-white/65">
                {engagement.description}
              </p>
              <Button href="/contact" className="mt-8">
                Schedule a Consultation
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-4">
              {engagement.points.map((item) => (
                <div
                  key={item}
                  className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/5 p-4"
                >
                  <Check className="mt-0.5 h-5 w-5 shrink-0 text-teal-400" />
                  <p className="text-sm text-white/75">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </Container>
      </Section>

      <CTASection />
    </>
  );
}
