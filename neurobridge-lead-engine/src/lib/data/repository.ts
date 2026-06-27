import { isSupabaseConfigured, createSupabaseServerClient } from "../supabase/client";
import { readLocalStore, updateLocalStore } from "./local-store";
import { calculateNextFollowUpDate } from "../follow-up";
import { calculatePriorityScore, defaultScoring } from "../scoring";
import type {
  CallOutcome,
  ContentCalendarEntry,
  DataStore,
  Document,
  Lead,
  LeadFilters,
  LeadInput,
  MessageHistoryEntry,
  ScoringFactors,
} from "../types";

function now(): string {
  return new Date().toISOString();
}

function applyLeadFilters(leads: Lead[], filters?: LeadFilters): Lead[] {
  let result = [...leads];
  if (filters?.category && filters.category !== "all") {
    result = result.filter((l) => l.lead_category === filters.category);
  }
  if (filters?.status && filters.status !== "all") {
    result = result.filter((l) => l.status === filters.status);
  }
  if (filters?.pipeline_stage && filters.pipeline_stage !== "all") {
    result = result.filter((l) => l.pipeline_stage === filters.pipeline_stage);
  }
  if (filters?.search) {
    const q = filters.search.toLowerCase();
    result = result.filter(
      (l) =>
        l.full_name.toLowerCase().includes(q) ||
        l.organization.toLowerCase().includes(q) ||
        l.title.toLowerCase().includes(q)
    );
  }
  if (filters?.overdue_only) {
    const today = new Date().toISOString().slice(0, 10);
    result = result.filter(
      (l) => l.next_follow_up_date && l.next_follow_up_date < today
    );
  }
  return result.sort((a, b) => b.priority_score - a.priority_score);
}

function mapLeadRow(row: Record<string, unknown>): Lead {
  return {
    id: row.id as string,
    full_name: row.full_name as string,
    title: (row.title as string) ?? "",
    organization: (row.organization as string) ?? "",
    specialty: (row.specialty as string) ?? "",
    country_state: (row.country_state as string) ?? "",
    lead_category: row.lead_category as Lead["lead_category"],
    linkedin_url: (row.linkedin_url as string) ?? "",
    public_email: (row.public_email as string) ?? "",
    website: (row.website as string) ?? "",
    notes: (row.notes as string) ?? "",
    source: (row.source as string) ?? "",
    status: row.status as Lead["status"],
    priority_score: row.priority_score as number,
    pipeline_stage: row.pipeline_stage as Lead["pipeline_stage"],
    scoring: row.scoring as ScoringFactors,
    next_follow_up_date: (row.next_follow_up_date as string) ?? null,
    created_at: row.created_at as string,
    updated_at: row.updated_at as string,
  };
}

function leadToRow(lead: Partial<LeadInput> & { scoring?: ScoringFactors; priority_score?: number }) {
  const scoring = lead.scoring ?? defaultScoring();
  const priority_score = lead.priority_score ?? calculatePriorityScore(scoring);
  return {
    ...lead,
    scoring,
    priority_score,
    updated_at: now(),
  };
}

// ─── Leads ───────────────────────────────────────────────────────────────────

export async function getLeads(filters?: LeadFilters): Promise<Lead[]> {
  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      let query = supabase.from("leads").select("*").order("priority_score", { ascending: false });
      if (filters?.category && filters.category !== "all") {
        query = query.eq("lead_category", filters.category);
      }
      if (filters?.status && filters.status !== "all") {
        query = query.eq("status", filters.status);
      }
      if (filters?.pipeline_stage && filters.pipeline_stage !== "all") {
        query = query.eq("pipeline_stage", filters.pipeline_stage);
      }
      const { data, error } = await query;
      if (error) throw error;
      let leads = (data ?? []).map(mapLeadRow);
      if (filters?.search || filters?.overdue_only) {
        leads = applyLeadFilters(leads, filters);
      }
      return leads;
    } catch {
      // fall through to local
    }
  }
  const store = await readLocalStore();
  return applyLeadFilters(store.leads, filters);
}

export async function getLead(id: string): Promise<Lead | null> {
  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase.from("leads").select("*").eq("id", id).single();
      if (error) throw error;
      return data ? mapLeadRow(data) : null;
    } catch {
      // fall through
    }
  }
  const store = await readLocalStore();
  return store.leads.find((l) => l.id === id) ?? null;
}

export async function createLead(input: LeadInput): Promise<Lead> {
  const scoring = input.scoring ?? defaultScoring();
  const priority_score = input.priority_score ?? calculatePriorityScore(scoring);
  const next_follow_up_date =
    input.next_follow_up_date ?? calculateNextFollowUpDate(input.status);
  const lead: Lead = {
    ...input,
    id: crypto.randomUUID(),
    scoring,
    priority_score,
    next_follow_up_date,
    created_at: now(),
    updated_at: now(),
  };

  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase.from("leads").insert(lead).select().single();
      if (error) throw error;
      return mapLeadRow(data);
    } catch {
      // fall through
    }
  }

  await updateLocalStore((store) => ({
    ...store,
    leads: [...store.leads, lead],
  }));
  return lead;
}

export async function updateLead(id: string, updates: Partial<LeadInput>): Promise<Lead | null> {
  const existing = await getLead(id);
  if (!existing) return null;

  const scoring = updates.scoring ?? existing.scoring;
  const priority_score = updates.priority_score ?? calculatePriorityScore(scoring);
  const status = updates.status ?? existing.status;
  const next_follow_up_date =
    updates.next_follow_up_date ??
    (updates.status ? calculateNextFollowUpDate(status) : existing.next_follow_up_date);

  const updated: Lead = {
    ...existing,
    ...updates,
    scoring,
    priority_score,
    next_follow_up_date,
    updated_at: now(),
  };

  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase
        .from("leads")
        .update(leadToRow(updated))
        .eq("id", id)
        .select()
        .single();
      if (error) throw error;
      return mapLeadRow(data);
    } catch {
      // fall through
    }
  }

  await updateLocalStore((store) => ({
    ...store,
    leads: store.leads.map((l) => (l.id === id ? updated : l)),
  }));
  return updated;
}

export async function deleteLead(id: string): Promise<boolean> {
  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { error } = await supabase.from("leads").delete().eq("id", id);
      if (error) throw error;
      return true;
    } catch {
      // fall through
    }
  }
  await updateLocalStore((store) => ({
    ...store,
    leads: store.leads.filter((l) => l.id !== id),
    message_history: store.message_history.filter((m) => m.lead_id !== id),
    call_outcomes: store.call_outcomes.filter((c) => c.lead_id !== id),
  }));
  return true;
}

// ─── Message History ─────────────────────────────────────────────────────────

export async function getMessageHistory(leadId: string): Promise<MessageHistoryEntry[]> {
  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase
        .from("message_history")
        .select("*")
        .eq("lead_id", leadId)
        .order("sent_at", { ascending: false });
      if (error) throw error;
      return (data ?? []) as MessageHistoryEntry[];
    } catch {
      // fall through
    }
  }
  const store = await readLocalStore();
  return store.message_history.filter((m) => m.lead_id === leadId);
}

export async function addMessageHistory(
  entry: Omit<MessageHistoryEntry, "id" | "created_at">
): Promise<MessageHistoryEntry> {
  const record: MessageHistoryEntry = {
    ...entry,
    id: crypto.randomUUID(),
    created_at: now(),
  };

  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase
        .from("message_history")
        .insert(record)
        .select()
        .single();
      if (error) throw error;
      return data as MessageHistoryEntry;
    } catch {
      // fall through
    }
  }

  await updateLocalStore((store) => ({
    ...store,
    message_history: [...store.message_history, record],
  }));
  return record;
}

// ─── Call Outcomes ───────────────────────────────────────────────────────────

export async function getCallOutcomes(leadId: string): Promise<CallOutcome[]> {
  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase
        .from("call_outcomes")
        .select("*")
        .eq("lead_id", leadId)
        .order("call_date", { ascending: false });
      if (error) throw error;
      return (data ?? []) as CallOutcome[];
    } catch {
      // fall through
    }
  }
  const store = await readLocalStore();
  return store.call_outcomes.filter((c) => c.lead_id === leadId);
}

export async function addCallOutcome(
  entry: Omit<CallOutcome, "id" | "created_at">
): Promise<CallOutcome> {
  const record: CallOutcome = {
    ...entry,
    id: crypto.randomUUID(),
    created_at: now(),
  };

  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase
        .from("call_outcomes")
        .insert(record)
        .select()
        .single();
      if (error) throw error;
      return data as CallOutcome;
    } catch {
      // fall through
    }
  }

  await updateLocalStore((store) => ({
    ...store,
    call_outcomes: [...store.call_outcomes, record],
  }));
  return record;
}

// ─── Content Calendar ────────────────────────────────────────────────────────

export async function getContentCalendar(weekStart?: string): Promise<ContentCalendarEntry[]> {
  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      let query = supabase.from("content_calendar").select("*").order("day_of_week");
      if (weekStart) query = query.eq("week_start", weekStart);
      const { data, error } = await query;
      if (error) throw error;
      return (data ?? []) as ContentCalendarEntry[];
    } catch {
      // fall through
    }
  }
  const store = await readLocalStore();
  if (!weekStart) return store.content_calendar;
  return store.content_calendar.filter((c) => c.week_start === weekStart);
}

export async function saveContentCalendarEntry(
  entry: Omit<ContentCalendarEntry, "id" | "created_at" | "updated_at"> & { id?: string }
): Promise<ContentCalendarEntry> {
  const record: ContentCalendarEntry = {
    ...entry,
    id: entry.id ?? crypto.randomUUID(),
    created_at: now(),
    updated_at: now(),
  };

  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase
        .from("content_calendar")
        .upsert(record)
        .select()
        .single();
      if (error) throw error;
      return data as ContentCalendarEntry;
    } catch {
      // fall through
    }
  }

  await updateLocalStore((store) => {
    const existing = store.content_calendar.findIndex((c) => c.id === record.id);
    const content_calendar =
      existing >= 0
        ? store.content_calendar.map((c, i) => (i === existing ? { ...record, created_at: c.created_at, updated_at: now() } : c))
        : [...store.content_calendar, record];
    return { ...store, content_calendar };
  });
  return record;
}

// ─── Documents ───────────────────────────────────────────────────────────────

export async function getDocuments(): Promise<Document[]> {
  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase.from("documents").select("*").order("title");
      if (error) throw error;
      return (data ?? []) as Document[];
    } catch {
      // fall through
    }
  }
  const store = await readLocalStore();
  return store.documents;
}

export async function saveDocument(
  doc: Omit<Document, "id" | "created_at" | "updated_at"> & { id?: string }
): Promise<Document> {
  const record: Document = {
    ...doc,
    id: doc.id ?? crypto.randomUUID(),
    created_at: now(),
    updated_at: now(),
  };

  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { data, error } = await supabase.from("documents").upsert(record).select().single();
      if (error) throw error;
      return data as Document;
    } catch {
      // fall through
    }
  }

  await updateLocalStore((store) => {
    const existing = store.documents.findIndex((d) => d.id === record.id);
    const documents =
      existing >= 0
        ? store.documents.map((d, i) =>
            i === existing ? { ...record, created_at: d.created_at, updated_at: now() } : d
          )
        : [...store.documents, record];
    return { ...store, documents };
  });
  return record;
}

export async function deleteDocument(id: string): Promise<boolean> {
  if (isSupabaseConfigured()) {
    try {
      const supabase = createSupabaseServerClient();
      const { error } = await supabase.from("documents").delete().eq("id", id);
      if (error) throw error;
      return true;
    } catch {
      // fall through
    }
  }
  await updateLocalStore((store) => ({
    ...store,
    documents: store.documents.filter((d) => d.id !== id),
  }));
  return true;
}

export async function getDashboardStats(): Promise<{
  totalLeads: number;
  overdueFollowUps: number;
  pipelineActive: number;
  avgPriorityScore: number;
}> {
  const store = isSupabaseConfigured()
    ? { leads: await getLeads() }
    : await readLocalStore();
  const leads = store.leads;
  const today = new Date().toISOString().slice(0, 10);
  const overdueFollowUps = leads.filter(
    (l) => l.next_follow_up_date && l.next_follow_up_date < today
  ).length;
  const pipelineActive = leads.filter(
    (l) => !["closed_won", "closed_lost", "archived"].includes(l.pipeline_stage) &&
           l.status !== "archived"
  ).length;
  const avgPriorityScore =
    leads.length > 0
      ? Math.round(leads.reduce((sum, l) => sum + l.priority_score, 0) / leads.length)
      : 0;
  return { totalLeads: leads.length, overdueFollowUps, pipelineActive, avgPriorityScore };
}

export type { DataStore };
