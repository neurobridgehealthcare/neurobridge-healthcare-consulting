"use client";

import { useState } from "react";
import { CheckCircle, Send } from "lucide-react";
import { contactPage } from "@/lib/data";
import { Button } from "@/components/ui/Button";

export function ContactForm() {
  const [submitted, setSubmitted] = useState(false);
  const { form } = contactPage;

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="flex flex-col items-center rounded-2xl border border-teal-500/20 bg-teal-500/5 p-12 text-center">
        <CheckCircle className="h-12 w-12 text-teal-500" />
        <h3 className="mt-4 font-display text-xl font-bold text-navy-900">
          {form.successTitle}
        </h3>
        <p className="mt-2 max-w-md text-sm text-navy-700/70">
          {form.successMessage}
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid gap-6 sm:grid-cols-2">
        <div>
          <label htmlFor="name" className="mb-2 block text-sm font-medium text-navy-900">
            Name
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
            placeholder="Full name"
          />
        </div>
        <div>
          <label htmlFor="organization" className="mb-2 block text-sm font-medium text-navy-900">
            Organization
          </label>
          <input
            id="organization"
            name="organization"
            type="text"
            required
            className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
            placeholder="Hospital, health system, or institution"
          />
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div>
          <label htmlFor="role" className="mb-2 block text-sm font-medium text-navy-900">
            Role
          </label>
          <input
            id="role"
            name="role"
            type="text"
            required
            className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
            placeholder="Title or department"
          />
        </div>
        <div>
          <label htmlFor="email" className="mb-2 block text-sm font-medium text-navy-900">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
            placeholder="you@organization.com"
          />
        </div>
      </div>

      <div>
        <label htmlFor="country" className="mb-2 block text-sm font-medium text-navy-900">
          Country
        </label>
        <input
          id="country"
          name="country"
          type="text"
          required
          className="w-full rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
          placeholder="Country or region"
        />
      </div>

      <div>
        <label htmlFor="message" className="mb-2 block text-sm font-medium text-navy-900">
          What are you looking to build or improve?
        </label>
        <textarea
          id="message"
          name="message"
          required
          rows={5}
          className="w-full resize-none rounded-xl border border-navy-900/10 bg-white px-4 py-3 text-sm text-navy-900 outline-none transition-colors focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20"
          placeholder={form.messagePlaceholder}
        />
      </div>

      <Button type="submit" size="lg" className="w-full sm:w-auto">
        Request Consultation
        <Send className="h-4 w-4" />
      </Button>
    </form>
  );
}
