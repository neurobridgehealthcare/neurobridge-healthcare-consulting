import { ArrowUpRight, FileText } from "lucide-react";
import { aboutPage } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Section";

export function CapabilityStatementLink() {
  const { capabilityLink } = aboutPage;

  return (
    <section className="border-t border-navy-900/5 bg-surface-muted py-16 md:py-20">
      <Container>
        <div className="flex flex-col items-start justify-between gap-8 rounded-2xl border border-navy-900/5 bg-white p-8 md:flex-row md:items-center md:p-10">
          <div className="flex items-start gap-5">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-navy-900 text-teal-400">
              <FileText className="h-5 w-5" />
            </div>
            <div className="max-w-xl">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-500">
                For Administrators & Executives
              </p>
              <h2 className="mt-2 font-display text-xl font-bold text-navy-900 md:text-2xl">
                {capabilityLink.title}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-navy-700/65">
                {capabilityLink.description}
              </p>
            </div>
          </div>
          <Button href={capabilityLink.href} variant="secondary" className="shrink-0">
            View & Download
            <ArrowUpRight className="h-4 w-4" />
          </Button>
        </div>
      </Container>
    </section>
  );
}
