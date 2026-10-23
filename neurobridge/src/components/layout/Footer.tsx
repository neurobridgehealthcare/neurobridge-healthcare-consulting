import Link from "next/link";
import { ArrowUpRight, Mail } from "lucide-react";
import { navigation, siteConfig, footerCopy } from "@/lib/data";
import { BrandLogo } from "@/components/brand/BrandLogo";
import { Button } from "@/components/ui/Button";
import { Disclaimer } from "@/components/ui/Disclaimer";
import { Container } from "@/components/ui/Section";

export function Footer() {
  const footerLinks = navigation.filter((item) => item.href !== "/contact");

  return (
    <footer className="site-footer border-t border-navy-900/5 bg-navy-950 text-white">
      <Container className="py-16 md:py-20">
        <div className="grid gap-12 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <Link href="/" className="inline-flex rounded-lg bg-white p-2">
              <BrandLogo className="h-10 w-auto sm:h-12" />
            </Link>
            <p className="mt-6 max-w-md text-sm leading-relaxed text-white/60">
              {siteConfig.description}
            </p>
            <div className="mt-6 flex items-center gap-2 text-sm text-white/60">
              <Mail className="h-4 w-4 text-teal-400" />
              <a
                href={`mailto:${siteConfig.email}`}
                className="hover:text-white"
              >
                {siteConfig.email}
              </a>
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
              Email Brandon
              <ArrowUpRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="mt-14 border-t border-white/10 pt-8">
          <Disclaimer light />
          <div className="mt-6 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
            <p className="text-xs text-white/40">
              &copy; {new Date().getFullYear()} {siteConfig.name}. All rights
              reserved.
            </p>
            <p className="text-xs text-white/40">{siteConfig.tagline}</p>
          </div>
        </div>
      </Container>
    </footer>
  );
}
