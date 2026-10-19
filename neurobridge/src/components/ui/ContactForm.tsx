"use client";

import { useMemo, useState } from "react";
import { Copy, Mail, Send } from "lucide-react";
import { Button } from "@/components/ui/Button";

type ContactFormProps = {
  email: string;
  interests: string[];
  messagePlaceholder: string;
};

type Draft = {
  subject: string;
  body: string;
  href: string;
};

function buildDraft(
  email: string,
  fields: {
    name: string;
    organization: string;
    role: string;
    replyTo: string;
    interest: string;
    message: string;
  }
): Draft {
  const subject = `NeuroBridge inquiry: ${fields.interest} — ${fields.name}`;
  const body = [
    `Name: ${fields.name}`,
    `Organization: ${fields.organization}`,
    `Role: ${fields.role}`,
    `Reply-to: ${fields.replyTo}`,
    `Interest: ${fields.interest}`,
    "",
    fields.message,
    "",
    "Sent from the NeuroBridge website. This draft is not delivered until you send it.",
  ].join("\n");

  const href = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  return { subject, body, href };
}

export function ContactForm({
  email,
  interests,
  messagePlaceholder,
}: ContactFormProps) {
  const [draft, setDraft] = useState<Draft | null>(null);
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);

  const emptyMailto = useMemo(
    () =>
      `mailto:${email}?subject=${encodeURIComponent("NeuroBridge consultation")}`,
    [email]
  );

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    const next = buildDraft(email, {
      name: String(data.get("name") || "").trim(),
      organization: String(data.get("organization") || "").trim(),
      role: String(data.get("role") || "").trim(),
      replyTo: String(data.get("email") || "").trim(),
      interest: String(data.get("interest") || "").trim(),
      message: String(data.get("message") || "").trim(),
    });
    setDraft(next);
    setCopied(false);
    setCopyError(false);
    const link = document.createElement("a");
    link.href = next.href;
    link.rel = "noopener";
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  async function copyDraft() {
    if (!draft) return;
    const text = `To: ${email}\nSubject: ${draft.subject}\n\n${draft.body}`;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setCopyError(false);
    } catch {
      setCopied(false);
      setCopyError(true);
    }
  }

  return (
    <div className="space-y-8">
      <form
        action={`mailto:${email}`}
        method="POST"
        encType="text/plain"
        onSubmit={handleSubmit}
        className="space-y-6"
      >
        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <label
              htmlFor="name"
              className="mb-2 block text-sm font-medium text-navy-900"
            >
              Name
            </label>
            <input
              id="name"
              name="name"
              type="text"
              required
              autoComplete="name"
              className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
              placeholder="Full name"
            />
          </div>
          <div>
            <label
              htmlFor="organization"
              className="mb-2 block text-sm font-medium text-navy-900"
            >
              Organization
            </label>
            <input
              id="organization"
              name="organization"
              type="text"
              required
              autoComplete="organization"
              className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
              placeholder="Hospital, company, or practice"
            />
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          <div>
            <label
              htmlFor="role"
              className="mb-2 block text-sm font-medium text-navy-900"
            >
              Role
            </label>
            <input
              id="role"
              name="role"
              type="text"
              required
              autoComplete="organization-title"
              className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
              placeholder="Title or department"
            />
          </div>
          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-navy-900"
            >
              Your email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
              placeholder="you@organization.com"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="interest"
            className="mb-2 block text-sm font-medium text-navy-900"
          >
            What do you need?
          </label>
          <select
            id="interest"
            name="interest"
            required
            defaultValue=""
            className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
          >
            <option value="" disabled>
              Select an offering
            </option>
            {interests.map((interest) => (
              <option key={interest} value={interest}>
                {interest}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="message"
            className="mb-2 block text-sm font-medium text-navy-900"
          >
            Message
          </label>
          <textarea
            id="message"
            name="message"
            required
            rows={5}
            className="w-full resize-y rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
            placeholder={messagePlaceholder}
          />
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button type="submit" size="lg" className="w-full sm:w-auto">
            Open email draft
            <Send className="h-4 w-4" />
          </Button>
          <a
            href={emptyMailto}
            className="inline-flex items-center justify-center gap-2 text-sm font-semibold text-teal-700 hover:text-teal-600"
          >
            <Mail className="h-4 w-4" />
            Or email {email} directly
          </a>
        </div>
      </form>

      {draft && (
        <div
          role="status"
          aria-live="polite"
          className="rounded-2xl border border-teal-500/20 bg-teal-500/5 p-6"
        >
          <h3 className="font-display text-lg font-bold text-navy-900">
            Draft opened in your email app
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-navy-700/75">
            This message has not been delivered. Send it from your email app
            to reach Brandon at {email}. If no app opened, copy the draft
            below and send it yourself.
          </p>
          <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-navy-700/50">
            To
          </p>
          <p className="mt-1 text-sm text-navy-900">{email}</p>
          <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-navy-700/50">
            Subject
          </p>
          <p className="mt-1 text-sm text-navy-900">{draft.subject}</p>
          <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-navy-700/50">
            Message
          </p>
          <pre className="mt-2 whitespace-pre-wrap rounded-xl bg-white p-4 text-sm leading-relaxed text-navy-800">
            {draft.body}
          </pre>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <a
              href={draft.href}
              className="inline-flex items-center justify-center gap-2 rounded-full bg-navy-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-navy-800"
            >
              <Mail className="h-4 w-4" />
              Open draft again
            </a>
            <button
              type="button"
              onClick={copyDraft}
              className="inline-flex items-center justify-center gap-2 rounded-full border border-navy-900/15 px-5 py-2.5 text-sm font-semibold text-navy-900 hover:border-teal-500/40"
            >
              <Copy className="h-4 w-4" />
              {copied ? "Copied" : "Copy draft"}
            </button>
          </div>
          {copyError && (
            <p className="mt-3 text-sm text-navy-700/70">
              Copy is unavailable in this browser. Select the message above
              and copy it manually.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
