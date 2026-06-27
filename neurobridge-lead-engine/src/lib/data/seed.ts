import { calculateNextFollowUpDate } from "../follow-up";
import { calculatePriorityScore, defaultScoring } from "../scoring";
import type { DataStore, Lead, LeadStatus } from "../types";

function now(): string {
  return new Date().toISOString();
}

function id(): string {
  return crypto.randomUUID();
}

export function seedData(): DataStore {
  const scoring1 = {
    decision_making_authority: 85,
    ionm_relevance: 90,
    hospital_system_size: 75,
    geographic_opportunity: 70,
    strategic_fit: 88,
    urgency_signals: 60,
    partnership_potential: 80,
  };

  const scoring2 = {
    decision_making_authority: 70,
    ionm_relevance: 65,
    hospital_system_size: 90,
    geographic_opportunity: 55,
    strategic_fit: 72,
    urgency_signals: 45,
    partnership_potential: 65,
  };

  const scoring3 = {
    decision_making_authority: 60,
    ionm_relevance: 95,
    hospital_system_size: 40,
    geographic_opportunity: 80,
    strategic_fit: 70,
    urgency_signals: 30,
    partnership_potential: 50,
  };

  const leads: Lead[] = [
    {
      id: "lead-001",
      full_name: "Dr. Sarah Chen",
      title: "Chief of Neurosurgery",
      organization: "Pacific Northwest Medical Center",
      specialty: "Spine & Complex Neurosurgery",
      country_state: "Washington, USA",
      lead_category: "surgeon",
      linkedin_url: "https://linkedin.com/in/example",
      public_email: "s.chen@pnwmc.org",
      website: "https://pnwmc.org/neurosurgery",
      notes: "Expanding spine program. Previously worked with external IONM vendor — potential quality concerns mentioned in public lecture.",
      source: "Conference networking",
      status: "ready_to_contact",
      priority_score: calculatePriorityScore(scoring1),
      pipeline_stage: "researched",
      scoring: scoring1,
      next_follow_up_date: calculateNextFollowUpDate("ready_to_contact"),
      created_at: now(),
      updated_at: now(),
    },
    {
      id: "lead-002",
      full_name: "Michael Torres",
      title: "VP, Perioperative Services",
      organization: "Heartland Health System",
      specialty: "Perioperative Operations",
      country_state: "Ohio, USA",
      lead_category: "healthcare_executive",
      linkedin_url: "",
      public_email: "mtorres@heartlandhealth.org",
      website: "https://heartlandhealth.org",
      notes: "System-wide OR efficiency initiative. Neuro service line is a stated priority for 2025.",
      source: "LinkedIn research",
      status: "contacted",
      priority_score: calculatePriorityScore(scoring2),
      pipeline_stage: "message_sent",
      scoring: scoring2,
      next_follow_up_date: "2025-06-15",
      created_at: now(),
      updated_at: now(),
    },
    {
      id: "lead-003",
      full_name: "Dr. Amara Okonkwo",
      title: "Program Director, CNIM Training",
      organization: "State University School of Health Sciences",
      specialty: "Neurophysiology Education",
      country_state: "Georgia, USA",
      lead_category: "university",
      linkedin_url: "",
      public_email: "a.okonkwo@stateu.edu",
      website: "https://stateu.edu/neurophysiology",
      notes: "Seeking clinical partnership for trainee rotations. Good long-term pipeline opportunity.",
      source: "Professional referral",
      status: "in_conversation",
      priority_score: calculatePriorityScore(scoring3),
      pipeline_stage: "replied",
      scoring: scoring3,
      next_follow_up_date: calculateNextFollowUpDate("in_conversation"),
      created_at: now(),
      updated_at: now(),
    },
  ];

  return {
    leads,
    message_history: [
      {
        id: id(),
        lead_id: "lead-002",
        channel: "email",
        direction: "outbound",
        subject: "Perioperative neuro monitoring — brief introduction",
        body: "Hi Michael,\n\nI came across Heartland's perioperative services initiative and wanted to introduce NeuroBridge Healthcare Consulting. We support health systems on IONM program design, quality oversight, and operational alignment.\n\nIf useful, I'd welcome a brief conversation about your neuro service line priorities.\n\nBest,\nNeuroBridge",
        sent_at: "2025-06-10T14:00:00.000Z",
        created_at: now(),
      },
    ],
    call_outcomes: [],
    content_calendar: [],
    documents: [
      {
        id: id(),
        title: "NeuroBridge Capability Statement",
        category: "capability_statement",
        content: "NeuroBridge Healthcare Consulting provides advisory services in intraoperative neurophysiological monitoring (IONM), neurosurgical program development, and perioperative quality systems.\n\nCore capabilities:\n• IONM program assessment and optimization\n• Clinical operations and workflow design\n• Quality metrics and compliance frameworks\n• Leadership advisory for neuro service lines\n• Education and trainee program development",
        tags: ["capability", "overview"],
        created_at: now(),
        updated_at: now(),
      },
      {
        id: id(),
        title: "IONM Program Assessment — Service Description",
        category: "service_description",
        content: "A structured assessment of existing IONM operations covering clinical protocols, staffing models, technology utilization, documentation quality, and surgeon collaboration patterns. Deliverables include a findings report and prioritized improvement roadmap.",
        tags: ["ionm", "assessment"],
        created_at: now(),
        updated_at: now(),
      },
      {
        id: id(),
        title: "Regional Health System — Case Study Summary",
        category: "case_study",
        content: "A multi-hospital system engaged NeuroBridge to evaluate IONM coverage consistency across neurosurgical sites. The engagement identified protocol variation, improved case-to-technologist ratios, and established a unified quality dashboard — reducing signal-related delays by 22% over six months.",
        tags: ["case-study", "quality"],
        created_at: now(),
        updated_at: now(),
      },
    ],
  };
}

export function createEmptyLead(status: LeadStatus = "new"): Omit<Lead, "id" | "created_at" | "updated_at" | "priority_score"> {
  const scoring = defaultScoring();
  return {
    full_name: "",
    title: "",
    organization: "",
    specialty: "",
    country_state: "",
    lead_category: "surgeon",
    linkedin_url: "",
    public_email: "",
    website: "",
    notes: "",
    source: "",
    status,
    pipeline_stage: "researched",
    scoring,
    next_follow_up_date: calculateNextFollowUpDate(status),
  };
}
