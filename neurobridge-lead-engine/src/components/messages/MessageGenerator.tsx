"use client";

import { useState } from "react";
import { Sparkles, Copy, Check } from "lucide-react";
import { MESSAGE_AUDIENCES } from "@/lib/constants";
import type { MessageAudience } from "@/lib/types";

export function MessageGenerator() {
  const [audience, setAudience] = useState<MessageAudience>("surgeon");
  const [recipientName, setRecipientName] = useState("");
  const [recipientTitle, setRecipientTitle] = useState("");
  const [organization, setOrganization] = useState("");
  const [context, setContext] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  async function generate() {
    setLoading(true);
    try {
      const res = await fetch("/api/messages/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          audience,
          recipientName,
          recipientTitle,
          organization,
          context,
        }),
      });
      const data = await res.json();
      setMessage(data.message ?? "");
    } finally {
      setLoading(false);
    }
  }

  async function copyMessage() {
    await navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="dashboard-card space-y-4 p-5">
        <div>
          <h3 className="font-display text-sm font-semibold text-white">Outreach Context</h3>
          <p className="text-xs text-slate-500">
            Generate drafts for manual email or LinkedIn outreach. Nothing is sent automatically.
          </p>
        </div>

        <div>
          <label className="dashboard-label">Audience Type</label>
          <select
            className="dashboard-select"
            value={audience}
            onChange={(e) => setAudience(e.target.value as MessageAudience)}
          >
            {MESSAGE_AUDIENCES.map((a) => (
              <option key={a.value} value={a.value}>{a.label}</option>
            ))}
          </select>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="dashboard-label">Recipient Name</label>
            <input
              className="dashboard-input"
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
            />
          </div>
          <div>
            <label className="dashboard-label">Title</label>
            <input
              className="dashboard-input"
              value={recipientTitle}
              onChange={(e) => setRecipientTitle(e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="dashboard-label">Organization</label>
          <input
            className="dashboard-input"
            value={organization}
            onChange={(e) => setOrganization(e.target.value)}
          />
        </div>

        <div>
          <label className="dashboard-label">Additional Context</label>
          <textarea
            rows={3}
            className="dashboard-input resize-none"
            placeholder="Why you're reaching out, shared connection, recent news..."
            value={context}
            onChange={(e) => setContext(e.target.value)}
          />
        </div>

        <button onClick={generate} disabled={loading} className="btn-primary">
          <Sparkles className="h-4 w-4" />
          {loading ? "Generating..." : "Generate Message"}
        </button>
      </div>

      <div className="dashboard-card flex flex-col p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-display text-sm font-semibold text-white">Draft Message</h3>
          {message && (
            <button onClick={copyMessage} className="btn-ghost text-xs">
              {copied ? <Check className="h-3.5 w-3.5 text-teal-400" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </button>
          )}
        </div>
        {message ? (
          <pre className="flex-1 whitespace-pre-wrap rounded-lg border border-white/5 bg-navy-800/40 p-4 text-sm leading-relaxed text-slate-300">
            {message}
          </pre>
        ) : (
          <div className="flex flex-1 items-center justify-center rounded-lg border border-dashed border-white/10 p-8 text-center text-sm text-slate-500">
            Your generated outreach draft will appear here. Copy and send manually.
          </div>
        )}
      </div>
    </div>
  );
}
