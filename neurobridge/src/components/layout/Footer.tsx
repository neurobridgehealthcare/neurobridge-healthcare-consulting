import Link from "next/link";
import { ArrowUpRight, Mail } from "lucide-react";
import { navigation, siteConfig, footerCopy } from "@/lib/data";
import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Section";

export function Footer() {
  const footerLinks = navigation.filter(
    (item) => item.label !== "Schedule Consultation"
  );

  return (
    <footer className="site-footer border-t border-navy-900/5 bg-navy-950 text-white">
      <Container className="py-16 md:py-20">
        <div className="grid gap-12 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <Link href="/" className="inline-flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-teal-500">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  className="h-5 w-5 text-white"
                  aria-hidden
                >
                  <path
                    d="M4 16 L12 8 L20 16"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div>
                <p className="font-display text-sm font-bold">NeuroBridge</p>
                <p className="text-[11px] text-white/50">Healthcare Consulting</p>
              </div>
            </Link>
            <p className="mt-6 max-w-md text-sm leading-relaxed text-white/60">
              {siteConfig.description}
            </p>
            <div className="mt-6 flex items-center gap-2 text-sm text-white/60">
              <Mail className="h-4 w-4 text-teal-400" />
              <span>{siteConfig.email}</span>
            </div>
          </div>

          <div className="lg:col-span-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-teal-400">
              Navigation
            </p>
            <ul className="mt-5 space-y-3">
              {footerLinks.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-white/60 transition-colors hover:text-white"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
              <li>
                <Link
                  href="/capability-statement"
                  className="text-sm text-white/60 transition-colors hover:text-white"
                >
                  Capability Statement
                </Link>
              </li>
            </ul>
          </div>

          <div className="lg:col-span-4">
            <p className="text-xs font-semibold uppercase tracking-widest text-teal-400">
              {footerCopy.ctaTitle}
            </p>
            <p className="mt-5 text-sm leading-relaxed text-white/60">
              {footerCopy.ctaText}
            </p>
            <Button href="/contact" className="mt-6">
              Schedule Consultation
              <ArrowUpRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-8 sm:flex-row">
          <p className="text-xs text-white/40">
            &copy; {new Date().getFullYear()} {siteConfig.name}. All rights
            reserved.
          </p>
          <p className="text-xs text-white/40">
            {siteConfig.tagline}
          </p>
        </div>
      </Container>
    </footer>
  );
}
