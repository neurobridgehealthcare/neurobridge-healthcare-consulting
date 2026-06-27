"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ScoringPanel } from "./ScoringPanel";
import { calculatePriorityScore } from "@/lib/scoring";
import { defaultScoring } from "@/lib/scoring";
import {
  LEAD_CATEGORIES,
  LEAD_STATUSES,
  PIPELINE_STAGES,
} from "@/lib/constants";
import type { Lead, LeadInput } from "@/lib/types";

interface LeadFormProps {
  initial?: Lead;
  mode?: "create" | "edit";
}

export function LeadForm({ initial, mode = "create" }: LeadFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    full_name: initial?.full_name ?? "",
    title: initial?.title ?? "",
    organization: initial?.organization ?? "",
    specialty: initial?.specialty ?? "",
    country_state: initial?.country_state ?? "",
    lead_category: initial?.lead_category ?? "surgeon" as LeadInput["lead_category"],
    linkedin_url: initial?.linkedin_url ?? "",
    public_email: initial?.public_email ?? "",
    website: initial?.website ?? "",
    notes: initial?.notes ?? "",
    source: initial?.source ?? "",
    status: initial?.status ?? "new" as LeadInput["status"],
    pipeline_stage: initial?.pipeline_stage ?? "researched" as LeadInput["pipeline_stage"],
    next_follow_up_date: initial?.next_follow_up_date ?? "",
  });

  const [scoring, setScoring] = useState(initial?.scoring ?? defaultScoring());

  function updateField<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const payload: LeadInput = {
      ...form,
      scoring,
      priority_score: calculatePriorityScore(scoring),
      next_follow_up_date: form.next_follow_up_date || null,
    };

    try {
      const url = mode === "edit" && initial ? `/api/leads/${initial.id}` : "/api/leads";
      const method = mode === "edit" ? "PATCH" : "POST";
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error ?? "Failed to save lead");
      }
      const lead = (await res.json()) as Lead;
      router.push(`/leads/${lead.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-3">
      <div className="space-y-5 lg:col-span-2">
        <div className="dashboard-card p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-white">Contact Information</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="dashboard-label">Full Name *</label>
              <input
                required
                className="dashboard-input"
                value={form.full_name}
                onChange={(e) => updateField("full_name", e.target.value)}
              />
            </div>
            <div>
              <label className="dashboard-label">Title</label>
              <input
                className="dashboard-input"
                value={form.title}
                onChange={(e) => updateField("title", e.target.value)}
              />
            </div>
            <div>
              <label className="dashboard-label">Organization</label>
              <input
                className="dashboard-input"
                value={form.organization}
                onChange={(e) => updateField("organization", e.target.value)}
              />
            </div>
            <div>
              <label className="dashboard-label">Specialty</label>
              <input
                className="dashboard-input"
                value={form.specialty}
                onChange={(e) => updateField("specialty", e.target.value)}
              />
            </div>
            <div>
              <label className="dashboard-label">Country / State</label>
              <input
                className="dashboard-input"
                value={form.country_state}
                onChange={(e) => updateField("country_state", e.target.value)}
              />
            </div>
            <div>
              <label className="dashboard-label">Lead Category</label>
              <select
                className="dashboard-select"
                value={form.lead_category}
                onChange={(e) => updateField("lead_category", e.target.value as LeadInput["lead_category"])}
              >
                {LEAD_CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="dashboard-label">LinkedIn URL</label>
              <input
                type="url"
                className="dashboard-input"
                placeholder="https://linkedin.com/in/..."
                value={form.linkedin_url}
                onChange={(e) => updateField("linkedin_url", e.target.value)}
              />
            </div>
            <div>
              <label className="dashboard-label">Public Email</label>
              <input
                type="email"
                className="dashboard-input"
                value={form.public_email}
                onChange={(e) => updateField("public_email", e.target.value)}
              />
            </div>
            <div>
              <label className="dashboard-label">Website</label>
              <input
                type="url"
                className="dashboard-input"
                value={form.website}
                onChange={(e) => updateField("website", e.target.value)}
              />
            </div>
            <div>
              <label className="dashboard-label">Source</label>
              <input
                className="dashboard-input"
                placeholder="Conference, referral, research..."
                value={form.source}
                onChange={(e) => updateField("source", e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="dashboard-card p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-white">Status & Pipeline</h3>
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="dashboard-label">Status</label>
              <select
                className="dashboard-select"
                value={form.status}
                onChange={(e) => updateField("status", e.target.value as LeadInput["status"])}
              >
                {LEAD_STATUSES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="dashboard-label">Pipeline Stage</label>
              <select
                className="dashboard-select"
                value={form.pipeline_stage}
                onChange={(e) => updateField("pipeline_stage", e.target.value as LeadInput["pipeline_stage"])}
              >
                {PIPELINE_STAGES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="dashboard-label">Next Follow-Up</label>
              <input
                type="date"
                className="dashboard-input"
                value={form.next_follow_up_date}
                onChange={(e) => updateField("next_follow_up_date", e.target.value)}
              />
            </div>
          </div>
          <div className="mt-4">
            <label className="dashboard-label">Notes</label>
            <textarea
              rows={4}
              className="dashboard-input resize-none"
              value={form.notes}
              onChange={(e) => updateField("notes", e.target.value)}
            />
          </div>
        </div>

        {error && (
          <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </p>
        )}

        <div className="flex gap-3">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Saving..." : mode === "edit" ? "Update Lead" : "Create Lead"}
          </button>
          <button type="button" onClick={() => router.back()} className="btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      <div>
        <ScoringPanel scoring={scoring} onChange={setScoring} />
      </div>
    </form>
  );
}
