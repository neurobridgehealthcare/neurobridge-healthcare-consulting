import { Clock, Mail, MessageSquare } from "lucide-react";
import { contactPage, siteConfig } from "@/lib/data";
import { ContactForm } from "@/components/ui/ContactForm";
import { Container, Section } from "@/components/ui/Section";
import { PageHeroBackground } from "@/components/ui/HeroBackground";

export const metadata = {
  title: "Schedule Consultation",
  description:
    "Schedule a consultation with NeuroBridge to discuss neurophysiology program development, clinical oversight, and IONM infrastructure planning.",
};

export default function ContactPage() {
  const { hero, sidebar, form } = contactPage;

  return (
    <>
      <section className="relative overflow-hidden bg-gradient-to-b from-surface via-white to-surface pt-32 pb-16 md:pt-40">
        <PageHeroBackground />
        <Container className="relative">
          <p className="animate-fade-up text-sm font-semibold uppercase tracking-widest text-teal-500">
            {hero.eyebrow}
          </p>
          <h1 className="animate-fade-up animation-delay-100 font-display mt-4 max-w-3xl text-4xl font-bold tracking-tight text-navy-900 sm:text-5xl">
            {hero.title}
          </h1>
          <p className="animate-fade-up animation-delay-200 mt-5 max-w-xl text-lg text-navy-700/70">
            {hero.description}
          </p>
        </Container>
      </section>

      <Section className="pt-0">
        <Container>
          <div className="grid gap-12 lg:grid-cols-5">
            <div className="lg:col-span-2">
              <div className="sticky top-28 space-y-6">
                <div className="rounded-2xl border border-navy-900/5 bg-white p-7">
                  <div className="flex items-start gap-4">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-teal-500/10 text-teal-600">
                      <MessageSquare className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-navy-900">
                        {sidebar.expect.title}
                      </h3>
                      <p className="mt-2 text-sm leading-relaxed text-navy-700/65">
                        {sidebar.expect.text}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-navy-900/5 bg-white p-7">
                  <div className="flex items-start gap-4">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500">
                      <Clock className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-navy-900">
                        {sidebar.response.title}
                      </h3>
                      <p className="mt-2 text-sm leading-relaxed text-navy-700/65">
                        {sidebar.response.text}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-navy-900/5 bg-white p-7">
                  <div className="flex items-start gap-4">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-navy-900/5 text-navy-700">
                      <Mail className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-navy-900">
                        {sidebar.direct.title}
                      </h3>
                      <p className="mt-2 text-sm text-navy-700/65">
                        {siteConfig.email}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl bg-gradient-to-br from-navy-900 to-navy-800 p-7 text-white">
                  <p className="text-xs font-semibold uppercase tracking-widest text-teal-400">
                    {sidebar.confidential.title}
                  </p>
                  <p className="mt-3 text-sm leading-relaxed text-white/65">
                    {sidebar.confidential.text}
                  </p>
                </div>
              </div>
            </div>

            <div className="lg:col-span-3">
              <div className="rounded-3xl border border-navy-900/5 bg-white p-8 shadow-sm md:p-10">
                <h2 className="font-display text-xl font-bold text-navy-900">
                  {form.title}
                </h2>
                <p className="mt-2 text-sm text-navy-700/65">
                  {form.description}
                </p>
                <div className="mt-8">
                  <ContactForm />
                </div>
              </div>
            </div>
          </div>
        </Container>
      </Section>
    </>
  );
}
