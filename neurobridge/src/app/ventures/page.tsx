import { ArrowUpRight } from "lucide-react";
import { ventures, venturesPage } from "@/lib/data";
import { CTASection, PageHero } from "@/components/ui/PageHero";
import { Disclaimer } from "@/components/ui/Disclaimer";
import { Container, Section } from "@/components/ui/Section";

export const metadata = {
  title: "Ventures",
  description:
    "Connectome.news, NeuroBridge’s neuroscience news platform, and FOCUS, a prototype-stage concept for intraoperative visual evoked potential stimulation. FOCUS is in development, with no clinical claims.",
};

export default function VenturesPage() {
  const { hero, note } = venturesPage;

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
          <p className="mb-10 max-w-3xl rounded-2xl border border-amber-500/20 bg-amber-500/5 px-5 py-4 text-sm leading-relaxed text-navy-800">
            {note}
          </p>
          <div className="space-y-8">
            {ventures.map((venture) => (
              <article
                key={venture.id}
                id={venture.id}
                className="scroll-mt-28 overflow-hidden rounded-3xl border border-navy-900/5 bg-white shadow-sm"
              >
                <div className="grid lg:grid-cols-5">
                  <div className="relative flex flex-col justify-between bg-gradient-to-br from-navy-900 via-navy-800 to-navy-900 p-10 text-white lg:col-span-2">
                    <div>
                      <venture.icon className="h-8 w-8 text-teal-300" />
                      <p className="mt-8 text-xs font-semibold uppercase tracking-[0.2em] text-teal-300">
                        {venture.status}
                      </p>
                      <h2 className="mt-3 font-display text-3xl font-bold">
                        {venture.title}
                      </h2>
                      <p className="mt-2 text-sm text-white/65">{venture.kicker}</p>
                    </div>
                  </div>
                  <div className="p-8 md:p-10 lg:col-span-3">
                    <p className="text-base leading-relaxed text-navy-700/75">
                      {venture.summary}
                    </p>
                    <ul className="mt-6 space-y-3">
                      {venture.points.map((point) => (
                        <li
                          key={point}
                          className="flex items-start gap-2 text-sm text-navy-800/85"
                        >
                          <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-500" />
                          {point}
                        </li>
                      ))}
                    </ul>
                    {venture.href && venture.hrefLabel && (
                      <a
                        href={venture.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-8 inline-flex items-center gap-2 text-sm font-semibold text-teal-700 hover:text-teal-600"
                      >
                        {venture.hrefLabel}
                        <ArrowUpRight className="h-4 w-4" />
                      </a>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
          <Disclaimer className="mt-10 max-w-3xl" />
        </Container>
      </Section>

      <CTASection showSecondary={false} />
    </>
  );
}
