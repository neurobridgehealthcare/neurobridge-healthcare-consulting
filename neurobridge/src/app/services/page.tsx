import { ArrowRight, Check } from "lucide-react";
import { offeringGroups, servicesPage } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { ServiceCard } from "@/components/ui/Cards";
import { CTASection, PageHero } from "@/components/ui/PageHero";
import { Container, Section, SectionHeader } from "@/components/ui/Section";

export const metadata = {
  title: "Offerings",
  description:
    "IONM expert calls, device and software reviews, hospital program development, TMS Clinic Accelerator, training, de-identified technical review, and CNIM tutoring. Starting prices listed.",
};

export default function ServicesPage() {
  const { hero, priceNote, engagement } = servicesPage;

  return (
    <>
      <PageHero
        eyebrow={hero.eyebrow}
        title={hero.title}
        description={hero.description}
        cta={{ label: "Email Brandon", href: "/contact" }}
      />

      {offeringGroups.map((group, index) => (
        <Section
          key={group.id}
          id={group.id}
          className={`scroll-mt-28 ${index % 2 === 1 ? "bg-surface-muted" : ""}`}
        >
          <Container>
            <SectionHeader
              eyebrow={group.eyebrow}
              title={group.title}
              description={group.description}
              align="left"
            />
            <div
              className={
                group.items.length === 1
                  ? "grid gap-6 lg:max-w-xl"
                  : group.items.length === 2
                    ? "grid gap-6 lg:grid-cols-2"
                    : "grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
              }
            >
              {group.items.map((service) => (
                <ServiceCard key={service.title} {...service} />
              ))}
            </div>
          </Container>
        </Section>
      ))}

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
              <p className="mt-4 text-sm leading-relaxed text-white/50">
                {priceNote}
              </p>
              <Button href="/contact" className="mt-8">
                Email Brandon
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
