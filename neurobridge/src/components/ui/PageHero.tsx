import { ArrowUpRight } from "lucide-react";
import { ctaSection } from "@/lib/data";
import { Container } from "@/components/ui/Section";
import { Button } from "@/components/ui/Button";
import { PageHeroBackground } from "@/components/ui/HeroBackground";

type PageHeroProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  cta?: { label: string; href: string };
};

export function PageHero({ eyebrow, title, description, cta }: PageHeroProps) {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-surface via-white to-surface pt-32 pb-16 md:pt-40 md:pb-20">
      <PageHeroBackground />
      <Container className="relative">
        {eyebrow && (
          <p className="animate-fade-up mb-4 text-sm font-semibold uppercase tracking-widest text-teal-500">
            {eyebrow}
          </p>
        )}
        <h1 className="animate-fade-up animation-delay-100 font-display max-w-4xl text-4xl font-bold tracking-tight text-navy-900 sm:text-5xl lg:text-6xl">
          {title}
        </h1>
        {description && (
          <p className="animate-fade-up animation-delay-200 mt-6 max-w-2xl text-lg leading-relaxed text-navy-700/70">
            {description}
          </p>
        )}
        {cta && (
          <div className="animate-fade-up animation-delay-300 mt-8">
            <Button href={cta.href}>
              {cta.label}
              <ArrowUpRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </Container>
    </section>
  );
}

export function CTASection({
  title = ctaSection.title,
  description = ctaSection.description,
  primaryLabel = ctaSection.primaryLabel,
  primaryHref = "/contact",
  showSecondary = true,
}: {
  title?: string;
  description?: string;
  primaryLabel?: string;
  primaryHref?: string;
  showSecondary?: boolean;
} = {}) {
  return (
    <section className="section-padding bg-gradient-to-br from-navy-950 via-navy-900 to-navy-950">
      <Container>
        <div className="relative overflow-hidden rounded-[2rem] border border-white/10">
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-teal-500/10" aria-hidden />
          <div className="pointer-events-none absolute -right-32 -top-32 h-80 w-80 rounded-full bg-teal-500/15 blur-3xl animate-pulse-glow" aria-hidden />
          <div className="pointer-events-none absolute -bottom-32 -left-32 h-80 w-80 rounded-full bg-blue-500/15 blur-3xl animate-pulse-glow animation-delay-200" aria-hidden />

          <div className="relative grid gap-10 p-10 md:grid-cols-5 md:items-center md:p-16 lg:p-20">
            <div className="md:col-span-3">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-400">
                {ctaSection.eyebrow}
              </p>
              <h2 className="mt-4 font-display text-3xl font-bold leading-tight text-white sm:text-4xl lg:text-[2.75rem]">
                {title}
              </h2>
              <p className="mt-5 max-w-xl text-lg leading-relaxed text-white/60">
                {description}
              </p>
            </div>
            <div className="flex flex-col gap-4 md:col-span-2 md:items-end">
              <Button href={primaryHref} size="lg" className="w-full md:w-auto">
                {primaryLabel}
                <ArrowUpRight className="h-4 w-4" />
              </Button>
              {showSecondary && (
                <Button
                  href="/services"
                  variant="outline"
                  size="lg"
                  className="w-full border-white/20 text-white hover:border-teal-400/50 hover:bg-white/5 md:w-auto"
                >
                  View Services
                </Button>
              )}
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
