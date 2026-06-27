export type LeadCategory =
  | "surgeon"
  | "hospital"
  | "healthcare_executive"
  | "investor"
  | "university"
  | "government"
  | "trainee";

export type LeadStatus =
  | "new"
  | "researching"
  | "ready_to_contact"
  | "contacted"
  | "in_conversation"
  | "nurturing"
  | "qualified"
  | "not_a_fit"
  | "archived";

export type PipelineStage =
  | "researched"
  | "connected"
  | "message_sent"
  | "replied"
  | "discovery_call_booked"
  | "assessment_requested"
  | "proposal_sent"
  | "closed_won"
  | "closed_lost";

export type MessageAudience =
  | "surgeon"
  | "hospital_executive"
  | "healthcare_system_leader"
  | "investor"
  | "university_program_leader"
  | "government_healthcare_contact"
  | "neurophysiology_trainee";

export type DocumentCategory =
  | "capability_statement"
  | "service_description"
  | "case_study"
  | "outreach_template"
  | "proposal_section";

export type ContentDayTheme =
  | "clinical_operations"
  | "neurophysiology_education"
  | "case_study"
  | "healthcare_leadership"
  | "founder_perspective";

export interface ScoringFactors {
  decision_making_authority: number;
  ionm_relevance: number;
  hospital_system_size: number;
  geographic_opportunity: number;
  strategic_fit: number;
  urgency_signals: number;
  partnership_potential: number;
}

export interface Lead {
  id: string;
  full_name: string;
  title: string;
  organization: string;
  specialty: string;
  country_state: string;
  lead_category: LeadCategory;
  linkedin_url: string;
  public_email: string;
  website: string;
  notes: string;
  source: string;
  status: LeadStatus;
  priority_score: number;
  pipeline_stage: PipelineStage;
  scoring: ScoringFactors;
  next_follow_up_date: string | null;
  created_at: string;
  updated_at: string;
}

export type LeadInput = Omit<
  Lead,
  "id" | "priority_score" | "created_at" | "updated_at"
> & {
  priority_score?: number;
};

export interface MessageHistoryEntry {
  id: string;
  lead_id: string;
  channel: string;
  direction: "outbound" | "inbound";
  subject: string;
  body: string;
  sent_at: string;
  created_at: string;
}

export interface CallOutcome {
  id: string;
  lead_id: string;
  outcome: string;
  notes: string;
  call_date: string;
  created_at: string;
}

export interface ContentCalendarEntry {
  id: string;
  week_start: string;
  day_of_week: string;
  theme: ContentDayTheme;
  draft_title: string;
  draft_body: string;
  status: "draft" | "scheduled" | "published";
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  title: string;
  category: DocumentCategory;
  content: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface LeadFilters {
  category?: LeadCategory | "all";
  status?: LeadStatus | "all";
  pipeline_stage?: PipelineStage | "all";
  search?: string;
  overdue_only?: boolean;
}

export interface DataStore {
  leads: Lead[];
  message_history: MessageHistoryEntry[];
  call_outcomes: CallOutcome[];
  content_calendar: ContentCalendarEntry[];
  documents: Document[];
}
