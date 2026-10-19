import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { capabilityStatement } from "@/lib/data";
import { CapabilityDocument } from "@/components/capability/CapabilityDocument";
import { PrintCapabilityButton } from "@/components/capability/PrintCapabilityButton";
import { Container } from "@/components/ui/Section";

export const metadata = {
  title: "Capability Statement",
  description:
    "Capability statement for NeuroBridge Healthcare Consulting: Brandon Garrison, CNIM, R. EP T., offerings, and the limit that this is technical consulting, not physician oversight.",
};

export default function CapabilityStatementPage() {
  return (
    <div className="capability-page min-h-screen bg-navy-900/5 pt-28 pb-20 print:bg-white print:pt-0 print:pb-0">
      {/* Toolbar — hidden when printing */}
      <div className="sticky top-[4.5rem] z-40 border-b border-navy-900/5 bg-white/90 backdrop-blur-md print:hidden">
        <Container className="flex items-center justify-between py-4">
          <Link
            href="/about"
            className="inline-flex items-center gap-2 text-sm font-medium text-navy-700/70 transition-colors hover:text-navy-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to About
          </Link>
          <div className="flex items-center gap-4">
            <p className="hidden text-xs text-navy-700/50 sm:block">
              Use &ldquo;Save as PDF&rdquo; to download for institutional review
            </p>
            <PrintCapabilityButton />
          </div>
        </Container>
      </div>

      <Container className="mt-8 print:mt-0 print:max-w-none print:px-0">
        <div className="mb-6 text-center print:hidden">
          <p className="section-eyebrow text-teal-600">
            {capabilityStatement.title}
          </p>
          <h1 className="mt-2 font-display text-2xl font-bold text-navy-900 md:text-3xl">
            {capabilityStatement.subtitle}
          </h1>
        </div>
        <CapabilityDocument />
      </Container>
    </div>
  );
}
