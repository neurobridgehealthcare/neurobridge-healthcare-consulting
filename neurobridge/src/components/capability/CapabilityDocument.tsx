import Link from "next/link";
import {
  capabilityStatement,
  founder,
  siteConfig,
} from "@/lib/data";
import { CredentialBadgeRow } from "@/components/about/CredentialBadge";
import { BrandLogo } from "@/components/brand/BrandLogo";

export function CapabilityDocument() {
  const { sections } = capabilityStatement;

  return (
    <article className="capability-document mx-auto max-w-[816px] bg-white shadow-2xl shadow-navy-900/10 print:max-w-none print:shadow-none">
      {/* Cover */}
      <header className="border-b-4 border-navy-900 px-10 py-14 md:px-14 md:py-16 print:px-12 print:py-12">
        <div className="flex items-start justify-between gap-8">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-teal-600">
              {capabilityStatement.title}
            </p>
            <h1 className="mt-3 font-display text-3xl font-bold tracking-tight text-navy-900 md:text-4xl">
              {capabilityStatement.subtitle}
            </h1>
            <p className="mt-2 text-sm font-medium text-navy-700/70">
              {capabilityStatement.tagline}
            </p>
          </div>
          <div className="hidden shrink-0 text-right sm:block">
            <BrandLogo variant="mark" alt="" className="h-14 w-14" />
          </div>
        </div>
        <div className="mt-10 flex flex-wrap gap-6 border-t border-navy-900/10 pt-8 text-xs text-navy-700/60">
          <div>
            <p className="font-semibold uppercase tracking-wider text-navy-900/50">Document</p>
            <p className="mt-1">Capability Statement</p>
          </div>
          <div>
            <p className="font-semibold uppercase tracking-wider text-navy-900/50">Issued</p>
            <p className="mt-1">{capabilityStatement.issued}</p>
          </div>
          <div>
            <p className="font-semibold uppercase tracking-wider text-navy-900/50">Contact</p>
            <p className="mt-1">{siteConfig.email}</p>
          </div>
        </div>
      </header>

      {/* Firm Overview */}
      <section className="border-b border-navy-900/8 px-10 py-10 md:px-14 print:break-inside-avoid">
        <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-navy-900">
          {sections.overview.title}
        </h2>
        <p className="mt-4 text-sm leading-[1.75] text-navy-800/85">
          {sections.overview.content}
        </p>
      </section>

      {/* Leadership */}
      <section className="border-b border-navy-900/8 px-10 py-10 md:px-14 print:break-inside-avoid">
        <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-navy-900">
          {sections.leadership.title}
        </h2>
        <div className="mt-6 grid gap-8 md:grid-cols-[1fr_auto] md:items-start">
          <div>
            <h3 className="font-display text-lg font-bold text-navy-900">
              {sections.leadership.name}
            </h3>
            <p className="mt-1 text-sm font-medium text-teal-700">
              {sections.leadership.role}
            </p>
            <p className="mt-4 text-sm leading-[1.75] text-navy-800/85">
              {sections.leadership.bio}
            </p>
          </div>
          <CredentialBadgeRow credentials={founder.credentials} variant="document" />
        </div>
      </section>

      {/* Core Capabilities */}
      <section className="border-b border-navy-900/8 px-10 py-10 md:px-14 print:break-inside-avoid">
        <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-navy-900">
          Core Capabilities
        </h2>
        <ul className="mt-5 columns-1 gap-x-10 text-sm text-navy-800/85 sm:columns-2">
          {sections.capabilities.map((item) => (
            <li key={item} className="mb-2.5 flex items-start gap-2 break-inside-avoid">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-teal-500" />
              {item}
            </li>
          ))}
        </ul>
      </section>

      {/* Who We Serve */}
      <section className="border-b border-navy-900/8 px-10 py-10 md:px-14 print:break-inside-avoid">
        <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-navy-900">
          Client Profile
        </h2>
        <ul className="mt-5 grid gap-2 sm:grid-cols-2">
          {sections.audiences.map((item) => (
            <li key={item} className="flex items-center gap-2 text-sm text-navy-800/85">
              <span className="h-1 w-1 rounded-full bg-teal-500" />
              {item}
            </li>
          ))}
        </ul>
      </section>

      {/* Methodology */}
      <section className="border-b border-navy-900/8 px-10 py-10 md:px-14 print:break-inside-avoid">
        <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-navy-900">
          Implementation Methodology
        </h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {sections.methodology.map((item, i) => (
            <div key={item.step} className="rounded-lg border border-navy-900/10 bg-surface-muted/50 p-4">
              <p className="font-display text-2xl font-bold text-teal-600/80">
                0{i + 1}
              </p>
              <h3 className="mt-1 font-display text-sm font-bold text-navy-900">
                {item.step}
              </h3>
              <p className="mt-2 text-xs leading-relaxed text-navy-700/70">
                {item.detail}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Current Initiatives */}
      <section className="border-b border-navy-900/8 px-10 py-10 md:px-14 print:break-inside-avoid">
        <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-navy-900">
          Current Initiatives
        </h2>
        <p className="mt-4 text-sm leading-[1.75] text-navy-800/85">
          {capabilityStatement.sections.initiatives}
        </p>
      </section>

      {/* Engagement */}
      <section className="border-b border-navy-900/8 px-10 py-10 md:px-14 print:break-inside-avoid">
        <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-navy-900">
          Engagement Model
        </h2>
        <ul className="mt-5 space-y-2">
          {sections.engagement.map((item) => (
            <li key={item} className="flex items-start gap-2 text-sm text-navy-800/85">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-teal-500" />
              {item}
            </li>
          ))}
        </ul>
      </section>

      {/* Footer */}
      <footer className="bg-navy-900 px-10 py-10 text-white md:px-14 print:break-inside-avoid">
        <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
          <div>
            <p className="font-display text-lg font-bold">{siteConfig.shortName}</p>
            <p className="mt-1 text-xs text-white/50">{siteConfig.tagline}</p>
            <p className="mt-4 text-sm text-white/70">{siteConfig.email}</p>
          </div>
          <div className="max-w-sm text-left text-xs leading-relaxed text-white/55 sm:text-right">
            <p>{siteConfig.disclaimer}</p>
            <Link href="/contact" className="mt-3 inline-block text-teal-400 print:hidden">
              Email Brandon →
            </Link>
          </div>
        </div>
      </footer>
    </article>
  );
}
