"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, Trash2, FileText } from "lucide-react";
import { DOCUMENT_CATEGORIES } from "@/lib/constants";
import type { Document, DocumentCategory } from "@/lib/types";

interface DocumentLibraryProps {
  documents: Document[];
}

export function DocumentLibrary({ documents: initial }: DocumentLibraryProps) {
  const router = useRouter();
  const [documents, setDocuments] = useState(initial);
  const [selected, setSelected] = useState<Document | null>(initial[0] ?? null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    category: "capability_statement" as DocumentCategory,
    content: "",
    tags: "",
  });

  async function saveDocument(e: React.FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/documents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
      }),
    });
    const doc = (await res.json()) as Document;
    setDocuments((prev) => [...prev, doc]);
    setSelected(doc);
    setShowForm(false);
    setForm({ title: "", category: "capability_statement", content: "", tags: "" });
    router.refresh();
  }

  async function deleteDocument(id: string) {
    await fetch(`/api/documents/${id}`, { method: "DELETE" });
    setDocuments((prev) => prev.filter((d) => d.id !== id));
    setSelected(null);
    router.refresh();
  }

  const categoryLabel = (cat: DocumentCategory) =>
    DOCUMENT_CATEGORIES.find((c) => c.value === cat)?.label ?? cat;

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="space-y-3 lg:col-span-1">
        <button onClick={() => setShowForm(!showForm)} className="btn-primary w-full">
          <Plus className="h-4 w-4" />
          Add Document
        </button>

        {showForm && (
          <form onSubmit={saveDocument} className="dashboard-card space-y-3 p-4">
            <input
              required
              className="dashboard-input"
              placeholder="Title"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            <select
              className="dashboard-select"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value as DocumentCategory })}
            >
              {DOCUMENT_CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
            <textarea
              required
              rows={4}
              className="dashboard-input resize-none"
              placeholder="Content"
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
            />
            <input
              className="dashboard-input"
              placeholder="Tags (comma-separated)"
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
            />
            <button type="submit" className="btn-secondary w-full text-xs">Save</button>
          </form>
        )}

        <div className="dashboard-card divide-y divide-white/5 overflow-hidden">
          {documents.map((doc) => (
            <button
              key={doc.id}
              onClick={() => setSelected(doc)}
              className={`flex w-full items-start gap-3 px-4 py-3 text-left transition ${
                selected?.id === doc.id ? "bg-teal-500/10" : "hover:bg-white/[0.02]"
              }`}
            >
              <FileText className="mt-0.5 h-4 w-4 shrink-0 text-teal-400" />
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-white">{doc.title}</p>
                <p className="text-[11px] text-slate-500">{categoryLabel(doc.category)}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="dashboard-card lg:col-span-2">
        {selected ? (
          <div className="p-6">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-teal-400">
                  {categoryLabel(selected.category)}
                </p>
                <h2 className="font-display text-xl font-semibold text-white">{selected.title}</h2>
                {selected.tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {selected.tags.map((tag) => (
                      <span key={tag} className="badge bg-navy-700 text-slate-400">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={() => deleteDocument(selected.id)}
                className="btn-ghost text-red-400 hover:text-red-300"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
            <div className="whitespace-pre-wrap rounded-lg border border-white/5 bg-navy-800/40 p-5 text-sm leading-relaxed text-slate-300">
              {selected.content}
            </div>
          </div>
        ) : (
          <div className="flex h-64 items-center justify-center text-sm text-slate-500">
            Select a document to view
          </div>
        )}
      </div>
    </div>
  );
}
