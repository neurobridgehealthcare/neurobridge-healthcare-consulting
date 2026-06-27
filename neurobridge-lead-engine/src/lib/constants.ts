import type {
  ContentDayTheme,
  DocumentCategory,
  LeadCategory,
  LeadStatus,
  MessageAudience,
  PipelineStage,
} from "./types";

export const APP_NAME = "NeuroBridge Lead Engine";
export const APP_TAGLINE = "Private CRM & Business Development";

export const LEAD_CATEGORIES: { value: LeadCategory; label: string }[] = [
  { value: "surgeon", label: "Surgeon" },
  { value: "hospital", label: "Hospital" },
  { value: "healthcare_executive", label: "Healthcare Executive" },
  { value: "investor", label: "Investor" },
  { value: "university", label: "University" },
  { value: "government", label: "Government" },
  { value: "trainee", label: "Trainee" },
];

export const LEAD_STATUSES: { value: LeadStatus; label: string; color: string }[] = [
  { value: "new", label: "New", color: "bg-blue-500/20 text-blue-300" },
  { value: "researching", label: "Researching", color: "bg-slate-500/20 text-slate-300" },
  { value: "ready_to_contact", label: "Ready to Contact", color: "bg-teal-500/20 text-teal-300" },
  { value: "contacted", label: "Contacted", color: "bg-indigo-500/20 text-indigo-300" },
  { value: "in_conversation", label: "In Conversation", color: "bg-purple-500/20 text-purple-300" },
  { value: "nurturing", label: "Nurturing", color: "bg-amber-500/20 text-amber-300" },
  { value: "qualified", label: "Qualified", color: "bg-emerald-500/20 text-emerald-300" },
  { value: "not_a_fit", label: "Not a Fit", color: "bg-red-500/20 text-red-300" },
  { value: "archived", label: "Archived", color: "bg-gray-500/20 text-gray-400" },
];

export const PIPELINE_STAGES: { value: PipelineStage; label: string; order: number }[] = [
  { value: "researched", label: "Researched", order: 0 },
  { value: "connected", label: "Connected", order: 1 },
  { value: "message_sent", label: "Message Sent", order: 2 },
  { value: "replied", label: "Replied", order: 3 },
  { value: "discovery_call_booked", label: "Discovery Call Booked", order: 4 },
  { value: "assessment_requested", label: "Assessment Requested", order: 5 },
  { value: "proposal_sent", label: "Proposal Sent", order: 6 },
  { value: "closed_won", label: "Closed Won", order: 7 },
  { value: "closed_lost", label: "Closed Lost", order: 8 },
];

export const MESSAGE_AUDIENCES: { value: MessageAudience; label: string }[] = [
  { value: "surgeon", label: "Surgeon" },
  { value: "hospital_executive", label: "Hospital Executive" },
  { value: "healthcare_system_leader", label: "Healthcare System Leader" },
  { value: "investor", label: "Investor" },
  { value: "university_program_leader", label: "University Program Leader" },
  { value: "government_healthcare_contact", label: "Government Healthcare Contact" },
  { value: "neurophysiology_trainee", label: "Neurophysiology Trainee" },
];

export const CONTENT_CALENDAR_SCHEDULE: {
  day: string;
  theme: ContentDayTheme;
  label: string;
}[] = [
  { day: "Monday", theme: "clinical_operations", label: "Clinical Operations Insight" },
  { day: "Tuesday", theme: "neurophysiology_education", label: "Neurophysiology Education" },
  { day: "Wednesday", theme: "case_study", label: "Case Study / Program Development" },
  { day: "Thursday", theme: "healthcare_leadership", label: "Healthcare Leadership & Quality" },
  { day: "Friday", theme: "founder_perspective", label: "Founder Perspective" },
];

export const DOCUMENT_CATEGORIES: { value: DocumentCategory; label: string }[] = [
  { value: "capability_statement", label: "Capability Statement" },
  { value: "service_description", label: "Service Description" },
  { value: "case_study", label: "Case Study Summary" },
  { value: "outreach_template", label: "Outreach Template" },
  { value: "proposal_section", label: "Proposal Section" },
];

export const SCORING_LABELS: { key: keyof import("./types").ScoringFactors; label: string; description: string }[] = [
  { key: "decision_making_authority", label: "Decision-Making Authority", description: "Budget influence and program ownership" },
  { key: "ionm_relevance", label: "IONM / Neurophysiology Relevance", description: "Direct connection to intraoperative monitoring" },
  { key: "hospital_system_size", label: "Hospital / System Size", description: "Volume, complexity, and strategic scale" },
  { key: "geographic_opportunity", label: "Geographic Opportunity", description: "Market access and regional fit" },
  { key: "strategic_fit", label: "Strategic Fit", description: "Alignment with NeuroBridge service lines" },
  { key: "urgency_signals", label: "Urgency Signals", description: "Active hiring, RFPs, quality issues, or transitions" },
  { key: "partnership_potential", label: "Partnership Potential", description: "Long-term advisory or program development opportunity" },
];

export const FOLLOW_UP_INTERVALS_DAYS: Record<LeadStatus, number> = {
  new: 14,
  researching: 10,
  ready_to_contact: 7,
  contacted: 7,
  in_conversation: 5,
  nurturing: 21,
  qualified: 3,
  not_a_fit: 90,
  archived: 365,
};

export function getCategoryLabel(category: LeadCategory): string {
  return LEAD_CATEGORIES.find((c) => c.value === category)?.label ?? category;
}

export function getStatusLabel(status: LeadStatus): string {
  return LEAD_STATUSES.find((s) => s.value === status)?.label ?? status;
}

export function getStatusColor(status: LeadStatus): string {
  return LEAD_STATUSES.find((s) => s.value === status)?.color ?? "bg-gray-500/20 text-gray-400";
}

export function getPipelineLabel(stage: PipelineStage): string {
  return PIPELINE_STAGES.find((s) => s.value === stage)?.label ?? stage;
}

export function getPriorityColor(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-teal-400";
  if (score >= 40) return "text-amber-400";
  return "text-slate-400";
}

export function getPriorityBg(score: number): string {
  if (score >= 80) return "bg-emerald-500/15 border-emerald-500/30";
  if (score >= 60) return "bg-teal-500/15 border-teal-500/30";
  if (score >= 40) return "bg-amber-500/15 border-amber-500/30";
  return "bg-slate-500/15 border-slate-500/30";
}
