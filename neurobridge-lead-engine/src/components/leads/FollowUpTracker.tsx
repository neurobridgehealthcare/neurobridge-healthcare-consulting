"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Phone, Mail, Plus } from "lucide-react";
import type { CallOutcome, MessageHistoryEntry } from "@/lib/types";

interface FollowUpTrackerProps {
  leadId: string;
  messages: MessageHistoryEntry[];
  calls: CallOutcome[];
}

export function FollowUpTracker({ leadId, messages, calls }: FollowUpTrackerProps) {
  const router = useRouter();
  const [tab, setTab] = useState<"messages" | "calls">("messages");
  const [loading, setLoading] = useState(false);

  const [msgForm, setMsgForm] = useState({
    channel: "email",
    direction: "outbound" as const,
    subject: "",
    body: "",
  });

  const [callForm, setCallForm] = useState({
    outcome: "",
    notes: "",
  });

  async function addMessage(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    await fetch(`/api/leads/${leadId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(msgForm),
    });
    setMsgForm({ channel: "email", direction: "outbound", subject: "", body: "" });
    setLoading(false);
    router.refresh();
  }

  async function addCall(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    await fetch(`/api/leads/${leadId}/calls`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(callForm),
    });
    setCallForm({ outcome: "", notes: "" });
    setLoading(false);
    router.refresh();
  }

  return (
    <div className="dashboard-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-display text-sm font-semibold text-white">Follow-Up Tracker</h3>
        <div className="flex rounded-lg border border-white/10 p-0.5">
          <button
            type="button"
            onClick={() => setTab("messages")}
            className={`rounded-md px-3 py-1 text-xs ${tab === "messages" ? "bg-teal-500/20 text-teal-400" : "text-slate-400"}`}
          >
            Messages
          </button>
          <button
            type="button"
            onClick={() => setTab("calls")}
            className={`rounded-md px-3 py-1 text-xs ${tab === "calls" ? "bg-teal-500/20 text-teal-400" : "text-slate-400"}`}
          >
            Calls
          </button>
        </div>
      </div>

      {tab === "messages" ? (
        <>
          <div className="mb-4 max-h-64 space-y-3 overflow-y-auto scrollbar-thin">
            {messages.length === 0 ? (
              <p className="text-xs text-slate-500">No messages logged yet.</p>
            ) : (
              messages.map((m) => (
                <div key={m.id} className="rounded-lg border border-white/5 bg-navy-800/40 p-3">
                  <div className="mb-1 flex items-center gap-2 text-xs text-slate-500">
                    <Mail className="h-3 w-3" />
                    {m.channel} · {m.direction} · {new Date(m.sent_at).toLocaleDateString()}
                  </div>
                  {m.subject && <p className="text-sm font-medium text-slate-200">{m.subject}</p>}
                  <p className="mt-1 whitespace-pre-wrap text-xs text-slate-400">{m.body}</p>
                </div>
              ))
            )}
          </div>
          <form onSubmit={addMessage} className="space-y-3 border-t border-white/8 pt-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="dashboard-label">Channel</label>
                <select
                  className="dashboard-select"
                  value={msgForm.channel}
                  onChange={(e) => setMsgForm({ ...msgForm, channel: e.target.value })}
                >
                  <option value="email">Email</option>
                  <option value="linkedin">LinkedIn (manual)</option>
                  <option value="phone">Phone</option>
                </select>
              </div>
              <div>
                <label className="dashboard-label">Subject</label>
                <input
                  className="dashboard-input"
                  value={msgForm.subject}
                  onChange={(e) => setMsgForm({ ...msgForm, subject: e.target.value })}
                />
              </div>
            </div>
            <div>
              <label className="dashboard-label">Message</label>
              <textarea
                required
                rows={3}
                className="dashboard-input resize-none"
                value={msgForm.body}
                onChange={(e) => setMsgForm({ ...msgForm, body: e.target.value })}
              />
            </div>
            <button type="submit" disabled={loading} className="btn-secondary text-xs">
              <Plus className="h-3.5 w-3.5" />
              Log Message
            </button>
          </form>
        </>
      ) : (
        <>
          <div className="mb-4 max-h-64 space-y-3 overflow-y-auto scrollbar-thin">
            {calls.length === 0 ? (
              <p className="text-xs text-slate-500">No call outcomes logged yet.</p>
            ) : (
              calls.map((c) => (
                <div key={c.id} className="rounded-lg border border-white/5 bg-navy-800/40 p-3">
                  <div className="mb-1 flex items-center gap-2 text-xs text-slate-500">
                    <Phone className="h-3 w-3" />
                    {new Date(c.call_date).toLocaleDateString()}
                  </div>
                  <p className="text-sm font-medium text-slate-200">{c.outcome}</p>
                  {c.notes && <p className="mt-1 text-xs text-slate-400">{c.notes}</p>}
                </div>
              ))
            )}
          </div>
          <form onSubmit={addCall} className="space-y-3 border-t border-white/8 pt-4">
            <div>
              <label className="dashboard-label">Outcome</label>
              <input
                required
                className="dashboard-input"
                placeholder="Voicemail, connected, no answer..."
                value={callForm.outcome}
                onChange={(e) => setCallForm({ ...callForm, outcome: e.target.value })}
              />
            </div>
            <div>
              <label className="dashboard-label">Notes</label>
              <textarea
                rows={2}
                className="dashboard-input resize-none"
                value={callForm.notes}
                onChange={(e) => setCallForm({ ...callForm, notes: e.target.value })}
              />
            </div>
            <button type="submit" disabled={loading} className="btn-secondary text-xs">
              <Plus className="h-3.5 w-3.5" />
              Log Call
            </button>
          </form>
        </>
      )}
    </div>
  );
}
