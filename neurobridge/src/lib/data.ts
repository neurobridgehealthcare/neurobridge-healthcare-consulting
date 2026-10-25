import type { LucideIcon } from "lucide-react";
import { productInterests } from "./products";
import {
  Activity,
  Award,
  BookOpen,
  Brain,
  Building2,
  ClipboardCheck,
  Cpu,
  Eye,
  FileSearch,
  FileText,
  GraduationCap,
  Headset,
  Hospital,
  LineChart,
  ListChecks,
  MessagesSquare,
  Microscope,
  Newspaper,
  ShieldCheck,
  Users,
} from "lucide-react";

export const siteConfig = {
  name: "NeuroBridge Healthcare Consulting",
  shortName: "NeuroBridge",
  url: "https://neurobridgehealthcare.com",
  tagline: "IONM consulting, program development, and related ventures",
  description:
    "Intraoperative neuromonitoring consulting for hospitals, surgery centers, and surgeon groups, from Brandon Garrison, CNIM, R. EP T. TMS planning support is also available. Not medical diagnosis or physician oversight.",
  email: "garrison839@gmail.com",
  phoneDisplay: "(678) 488-4288",
  phoneHref: "tel:+16784884288",
  location: "Macon, Georgia",
  disclaimer:
    "NeuroBridge Healthcare Consulting provides technical and operational consulting. It does not provide medical diagnosis, treatment recommendations, or physician oversight. Interpretation of neuromonitoring, and any physician-of-record role, belong to a licensed physician.",
};

export const navigation = [
  { label: "Home", href: "/" },
  { label: "Offerings", href: "/services" },
  { label: "Solutions", href: "/solutions" },
  { label: "About", href: "/about" },
  { label: "Ventures", href: "/ventures" },
  { label: "Contact", href: "/contact" },
];

export type Offering = {
  title: string;
  description: string;
  icon: LucideIcon;
  price: string;
  href?: string;
  details?: string[];
};

export const offeringGroups: {
  id: string;
  eyebrow: string;
  title: string;
  description: string;
  items: Offering[];
}[] = [
  {
    id: "expert-advisory",
    eyebrow: "Expert Advisory",
    title: "Expert calls and product reviews",
    description:
      "For expert networks, med-device and software companies, and investors who need a practicing technologist’s account of how intraoperative neuromonitoring actually runs.",
    items: [
      {
        title: "IONM expert consulting",
        description:
          "Advisory calls on operating-room workflow, coordination with surgery and anesthesia, in-house versus outsourced models, technologist staffing and training, equipment and software usability, and reimbursement pressure as seen from the field. Confidential information about a current or former employer is out of scope.",
        icon: MessagesSquare,
        price: "Starting at $150/hr",
        details: [
          "30–60 minute calls, with optional written notes",
          "Expert-network calls are typically quoted from $200/hr",
          "Not available for questions about an employer, its customers, or non-public information",
        ],
      },
      {
        title: "Device and software product reviews",
        description:
          "A walkthrough of a device or software workflow against a real case flow, with a written note of the main risks and follow-up time with the team building it.",
        icon: Cpu,
        price: "Starting at $750",
        details: [
          "Starter reviews start at $750. A standard review starts at $1,500",
          "Deeper reviews with a follow-up are scoped separately",
          "Vendor-neutral. Employer protocols, pricing, and methods are not reused",
        ],
      },
    ],
  },
  {
    id: "program-development",
    eyebrow: "IONM Program Development",
    title: "Hospital programs, including international work",
    description:
      "Build-out follows the paid IONM Program Feasibility Assessment when the report supports one. International work, including Caribbean programs, covers SOPs, equipment selection, workflow, training, and quality assurance.",
    items: [
      {
        title: "IONM program build-out",
        description:
          "For hospitals that have completed a feasibility assessment. Standard operating procedures, workflow, a training plan, vendor selection, a quality-assurance framework, and launch support.",
        icon: Building2,
        price: "Starting at $3,000/month",
        details: [
          "Typically $3,000–$5,000 per month, plus travel. Contact for scope",
          "Physician interpretation and oversight are not included",
          "Those roles stay with a licensed physician, not with NeuroBridge",
        ],
      },
    ],
  },
  {
    id: "training",
    eyebrow: "Training and Review",
    title: "SOPs, technical review, and CNIM tutoring",
    description:
      "Training materials, a technologist-level look at de-identified cases, and exam tutoring. Custom materials are written for the client and owned by the client.",
    items: [
      {
        title: "Training and SOP packages",
        description:
          "A module, an onboarding pack, or a competency checklist for an IONM team, hospital, or training program. Built from general professional knowledge, not from an employer’s materials.",
        icon: FileText,
        price: "Starting at $900",
        details: [
          "A single module starts at $900",
          "An onboarding pack is typically quoted from $2,500",
          "Custom and client-owned",
        ],
      },
      {
        title: "De-identified technical case review",
        description:
          "A technologist-level review of de-identified setup, montage, documentation, and alert-communication workflow against published guidelines. A scoped review can include de-identified signal data or model output.",
        icon: FileSearch,
        price: "Starting at $150/hr",
        details: [
          "Also offered at $500 per case packet",
          "Send no patient identifiers and no medical-record dumps",
          "Not a diagnosis, medical opinion, or standard-of-care opinion",
        ],
      },
      {
        title: "CNIM exam tutoring",
        description:
          "Tutoring for candidates preparing for the CNIM exam, including question review across a short series of sessions.",
        icon: GraduationCap,
        price: "Starting at $400",
        details: [
          "A five-session series starts at $400",
          "Teaching support only. No exam result is promised",
        ],
      },
    ],
  },
  {
    id: "team-support",
    eyebrow: "Secondary",
    title: "Support for IONM teams",
    description:
      "Part-time technical support for groups that already monitor. It sits behind program feasibility, training, and advisory work. Brandon is a CNIM and R. EP T.",
    items: [
      {
        title: "Remote Neurophysiology Support & Case Review",
        description:
          "Remote technical neurophysiology support for IONM teams: second-look case and data review, protocol and setup guidance, and backup technical support. Professional interpretation stays with the supervising physician.",
        icon: Headset,
        price: "Inquire",
        href: "/contact?interest=Remote%20Neurophysiology%20Support%20%26%20Case%20Review",
        details: [
          "Technical support, review, protocol and setup guidance, and backup for the team",
          "Second-look review of de-identified case material and data",
          "Professional interpretation stays with the supervising physician",
        ],
      },
      {
        title: "Fractional Clinical Lead for Small IONM Groups",
        description:
          "Part-time clinical leadership for small neuromonitoring groups: protocols, technologist training and onboarding, quality review, documentation standards, and audit readiness. Professional interpretation stays with the supervising physician.",
        icon: ListChecks,
        price: "Inquire",
        href: "/contact?interest=Fractional%20Clinical%20Lead%20for%20Small%20IONM%20Groups",
        details: [
          "Protocols, technologist training and onboarding, and documentation standards",
          "Quality review and audit readiness for a small group",
          "Professional interpretation stays with the supervising physician",
        ],
      },
    ],
  },
];

export const additionalOfferings: Offering[] = [
  offeringGroups[0].items[0],
  offeringGroups[0].items[1],
  offeringGroups[1].items[0],
  ...offeringGroups[2].items,
  ...offeringGroups[3].items,
];

export const audiences = [
  {
    title: "Hospitals and surgery centers",
    description:
      "Feasibility and build-out for a new or expanding intraoperative neuromonitoring service.",
    icon: Hospital,
  },
  {
    title: "Surgeon groups",
    description:
      "A written comparison of in-house neuromonitoring and an outside service, before a program is stood up.",
    icon: Users,
  },
  {
    title: "IONM teams and training programs",
    description:
      "SOP packages, onboarding materials, and de-identified technical review. Not medical opinions.",
    icon: BookOpen,
  },
  {
    title: "Expert networks and investors",
    description:
      "Practitioner insight on IONM workflow, staffing, and technology from the operating room.",
    icon: LineChart,
  },
  {
    title: "Med-device and software teams",
    description:
      "Workflow reviews from someone who runs the modalities the product is meant to support.",
    icon: Microscope,
  },
];

export const processSteps = [
  {
    step: "01",
    title: "Assess",
    description:
      "Review volume, case mix, staffing, equipment, and workflow. Feasibility comes before a build-out.",
    icon: ClipboardCheck,
  },
  {
    step: "02",
    title: "Build",
    description:
      "Write the SOPs, workflow, training plan, equipment shortlist, and quality checks the engagement calls for. Materials for a client are scoped to that client.",
    icon: FileText,
  },
  {
    step: "03",
    title: "Launch support",
    description:
      "Support training, technical review, and the first operating period. Physician interpretation stays with a licensed physician. NeuroBridge does not provide it.",
    icon: ShieldCheck,
  },
];

export const solutions = [
  {
    title: "New IONM program",
    description:
      "A feasibility assessment, then a build-out if the report supports standing the service up. For hospitals, surgery centers, and surgeon groups.",
    features: [
      "Remote feasibility at $1,500–$3,000",
      "SOPs, workflow, training, and QA",
      "Vendor-neutral equipment selection",
      "Physician oversight stays with a physician",
      "Case coverage in the room is not offered yet",
    ],
    icon: Hospital,
  },
  {
    title: "Expert advisory",
    description:
      "Calls and written reviews for expert networks, investors, and teams building IONM devices or software.",
    features: [
      "Expert calls starting at $150/hr",
      "Device and software reviews starting at $750",
      "Optional notes the buyer can keep",
      "No employer confidential information",
      "No diagnosis and no physician oversight",
    ],
    icon: MessagesSquare,
  },
  {
    title: "TMS Clinic Accelerator",
    description:
      "Launch support for psychiatry and behavioral-health practices adding TMS, starting with a feasibility assessment.",
    features: [
      "Feasibility starting at $1,500",
      "Equipment, workflow, staffing, and training",
      "Billing setup is part of the launch scope, not the feasibility fee",
      "Full launch package quoted only after a paid feasibility",
      "Based on launch planning, not on operating a clinic",
    ],
    icon: Brain,
  },
  {
    title: "Training and technical review",
    description:
      "SOP and onboarding packages, de-identified technical case review, and CNIM exam tutoring.",
    features: [
      "Training modules starting at $900",
      "De-identified review starting at $150/hr",
      "CNIM tutoring starting at $400",
      "Client-owned materials",
      "Technical review is not a medical opinion",
    ],
    icon: GraduationCap,
  },
];

export const ventures = [
  {
    id: "connectome",
    title: "Connectome.news",
    kicker: "Media and research arm",
    status: "Live",
    summary:
      "Connectome.news is a neuroscience discovery and news platform. It is NeuroBridge’s media and research arm, separate from client consulting.",
    href: "https://connectome.news",
    hrefLabel: "Visit connectome.news",
    points: [
      "Neuroscience discovery and news",
      "Editorial work is separate from consulting engagements",
      "No readership or sponsorship figures are claimed here",
    ],
    icon: Newspaper,
  },
  {
    id: "focus",
    title: "FOCUS",
    kicker: "Functional Ocular Control Unit System",
    status: "In development",
    summary:
      "FOCUS is a clinician-originated concept, at prototype stage, for intraoperative visual evoked potential stimulation under the eyelid during skull-base and orbital surgery. It is in development.",
    href: null,
    hrefLabel: null,
    points: [
      "Concept only. Not a product for sale",
      "No clinical performance, safety, or regulatory claims",
      "No prototype specifications are published here",
    ],
    icon: Eye,
  },
];

export const founder = {
  name: "Brandon Garrison, CNIM, R. EP T.",
  shortName: "Brandon Garrison",
  title: "Founder",
  credentials: [
    {
      abbr: "CNIM",
      full: "Certified in Neurophysiologic Intraoperative Monitoring (ABRET)",
    },
    {
      abbr: "R. EP T.",
      full: "Registered Evoked Potential Technologist (ABRET)",
    },
  ],
  bio: "Brandon Garrison, CNIM, R. EP T., is the founder of NeuroBridge Healthcare Consulting and a practicing surgical neurophysiologist. He is a technologist, not a physician. NeuroBridge is the umbrella for his consulting, training, and related ventures.",
  story: {
    eyebrow: "Career",
    title: "Operating-room practice, then a consulting practice",
    paragraphs: [
      "Brandon has worked in intraoperative neuromonitoring since August 2019. Confirmed roles are National Neuromonitoring Services (August 2019–December 2020), Neuro Protective Solutions (August 2021–February 28, 2023), Cleveland Clinic (March 8, 2023–January 2025), and Guardion Medical (February 2025–present).",
      "He is experienced in advanced and complex intraoperative neuromonitoring. Case work on his resume includes neuro and vascular procedures; spine, including spinal cord tumors and scoliosis; peripheral-nerve cases; ECoG; awake and asleep brain mapping; and DBS neurophysiology. Modalities include SSEP, MEP, EMG, and EEG. At National Neuromonitoring Services he supervised and trained other practitioners under real-time online physician supervision of the monitoring, and took part in performance reviews.",
      "Work at Lenox Hill Hospital was part of the Neuro Protective Solutions role. Lenox Hill is not a separate employer. Since February 2025 he has practiced IONM with Guardion Medical in Macon, Georgia. That employment is separate from NeuroBridge and is not an endorsement of this consulting practice.",
    ],
  },
  timeline: [
    {
      period: "February 2025 – present",
      organization: "Guardion Medical",
      role: "IONM Specialist",
      location: "Macon, Georgia",
      description:
        "Intraoperative neuromonitoring for brain, spine, and peripheral-nerve surgery, using SSEP, MEP, EMG, and EEG.",
      note: "Current employment, listed for career context only. Guardion Medical does not endorse NeuroBridge.",
    },
    {
      period: "March 8, 2023 – January 2025",
      organization: "Cleveland Clinic",
      role: "IONM Specialist",
      location: "Cleveland, Ohio",
      description:
        "Neurosurgical and orthopedic cases, including spinal cord tumors, scoliosis correction, microdiscectomy, and carpal tunnel release. Work included ECoG, awake and asleep brain mapping, and DBS neurophysiology, across multiple hospital systems.",
    },
    {
      period: "August 2021 – February 28, 2023",
      organization: "Neuro Protective Solutions",
      role: "CNIM IOM Surgical Neurotechnologist",
      location: "Hauppauge, New York",
      description:
        "Monitoring for a broad range of complex procedures, and working relationships with surgical teams.",
      note: "Includes work at Lenox Hill Hospital through Neuro Protective Solutions. Lenox Hill is not a separate employer.",
    },
    {
      period: "August 2019 – December 2020",
      organization: "National Neuromonitoring Services",
      role: "CNIM IOM Surgical Neurotechnologist",
      location: "Columbus, Ohio",
      description:
        "Acquired and monitored data under real-time online IONM physician supervision. Supervised and trained other practitioners and took part in performance reviews.",
    },
    {
      period: "2019",
      organization: "Baldwin Wallace University",
      role: "B.S. Neuroscience",
      location: "Berea, Ohio",
      description: "Bachelor of Science in Neuroscience, completed in 2019.",
    },
  ],
  specialties: [
    "Advanced and complex intraoperative neuromonitoring",
    "Neuro and vascular procedures",
    "Spine, including spinal cord tumors and scoliosis",
    "Peripheral nerve, including microdiscectomy and carpal tunnel release",
    "Electrocorticography (ECoG)",
    "Awake and asleep brain mapping",
    "DBS neurophysiology",
    "SSEP, MEP, EMG, and EEG",
  ],
  areasOfFocus: [
    {
      title: "Expert advisory",
      description:
        "Calls and product reviews for expert networks, med-device and software companies, and investors.",
    },
    {
      title: "IONM program development",
      description:
        "Feasibility and build-out for hospitals, including SOPs, equipment selection, workflow, training, and QA.",
    },
    {
      title: "TMS clinic launches",
      description:
        "Feasibility and launch planning for psychiatry and behavioral-health practices adding TMS.",
    },
    {
      title: "Training and SOPs",
      description:
        "Client-owned modules, onboarding packs, and competency checklists.",
    },
    {
      title: "Technical case review",
      description:
        "De-identified review of setup, documentation, and workflow. Not a medical opinion.",
    },
    {
      title: "CNIM tutoring",
      description:
        "Exam preparation for CNIM candidates. No result is promised.",
    },
  ],
  orientation: {
    eyebrow: "Scope",
    title: "Technical and operational consulting",
    statement:
      "NeuroBridge helps organizations with the workflow, the training, the documents, and the program design around intraoperative neuromonitoring and related services.",
    supporting:
      "It does not diagnose patients, interpret studies as a physician, or take a physician-of-record role. Those responsibilities stay with a licensed physician.",
  },
};

export const credibilityStrip = [
  { label: "CNIM and R. EP T.", icon: Award },
  { label: "IONM practice since 2019", icon: Activity },
  { label: "Program design and training", icon: FileText },
  { label: "Not physician oversight", icon: ShieldCheck },
];

export const problemSection = {
  eyebrow: "The work",
  title: "Where a technologist’s view is the missing piece",
  description:
    "Hospitals, device teams, and investors often need someone who has run the case, not only read about it. NeuroBridge is that consulting practice: technical and operational help, scoped in writing, without crossing into diagnosis or physician oversight.",
  painPoints: [
    "A hospital or surgery center is choosing in-house neuromonitoring or an outside service without a staffing and cost picture",
    "A program is planned before the workflow, staffing, and SOPs exist",
    "A device or software team needs the case flow checked by someone who monitors",
    "An investor or expert network needs field context without confidential information",
  ],
  callout:
    "Engagements are scoped before work starts. NeuroBridge does not provide medical diagnosis or physician oversight.",
};

export const whyNeuroBridge = [
  {
    title: "Dual ABRET certification",
    description:
      "CNIM (Certified in Neurophysiologic Intraoperative Monitoring) and R. EP T. (Registered Evoked Potential Technologist).",
    icon: Award,
  },
  {
    title: "Still in the operating room",
    description:
      "A practicing IONM technologist, experienced in advanced and complex intraoperative neuromonitoring, including brain, spine, vascular, and peripheral-nerve surgery.",
    icon: Activity,
  },
  {
    title: "Program documents, not slogans",
    description:
      "Feasibility reports, SOPs, training plans, equipment shortlists, and quality checks a hospital can actually use.",
    icon: ClipboardCheck,
  },
  {
    title: "Medtech and investor calls",
    description:
      "Workflow, usability, and staffing context for people building or evaluating IONM products and services.",
    icon: Cpu,
  },
  {
    title: "A hard scope line",
    description:
      "Technical and operational consulting only. No diagnosis, no treatment advice, and no physician oversight.",
    icon: ShieldCheck,
  },
];

export const homePage = {
  hero: {
    badge: "Brandon Garrison, CNIM, R. EP T. · Founder",
    headlineBefore: "Intraoperative neuromonitoring",
    headlineAccent: "for hospitals, surgery centers, and surgeons.",
    headlineAfter: "",
    subheadline:
      "Program feasibility and design from a CNIM, R. EP T. Start with a one-hour call, or request an IONM assessment.",
    disclaimer:
      "Technical and operational consulting only. Not medical diagnosis or physician oversight.",
  },
  coreServices: {
    eyebrow: "IONM",
    title: "Start with a call, or assess the program",
    description:
      "For hospitals, surgery centers, and surgeon groups. The call applies to IONM or TMS. The assessment below is the IONM engagement.",
  },
  whoWeServe: {
    eyebrow: "Who it’s for",
    title: "Hospitals, surgery centers, and the people around the case",
    description:
      "Surgeon groups and monitoring teams first. Expert networks and device teams are part of the same practice.",
  },
  approach: {
    eyebrow: "How an engagement runs",
    title: "Assess, build, then support the launch",
    description:
      "Feasibility or a defined call comes first. Build-out and full launch packages are separate scopes. Physician oversight is never part of the scope.",
  },
  expanded: {
    eyebrow: "Also offered",
    title: "Reviews, build-outs, training, and team support",
    description:
      "Expert calls, product reviews, program build-out, training packages, de-identified technical review, CNIM exam tutoring, and secondary support for IONM teams.",
  },
  ventures: {
    eyebrow: "Ventures",
    title: "Connectome.news and FOCUS",
    description:
      "NeuroBridge is also the home for a neuroscience news platform and an early device concept. Neither is a client result.",
  },
  whySection: {
    eyebrow: "Why NeuroBridge",
    title: "A practicing CNIM, consulting under his own name",
    description:
      "The firm is Brandon Garrison’s umbrella for consulting, training, and ventures. It is not a physician group and it does not speak for any employer.",
  },
};

export const servicesPage = {
  hero: {
    eyebrow: "Offerings",
    title: "IONM first",
    description:
      "Feasibility for hospitals, surgery centers, and surgeon groups. A 60-minute strategy call is the way to start. TMS consulting is further down.",
  },
  priceNote:
    "Figures are starting points from the current service catalog. A written scope confirms the fee before any work begins. Travel, when it is needed, is quoted separately.",
  engagement: {
    eyebrow: "Engagement",
    title: "Scoped before it starts",
    description:
      "Tell Brandon what you are building and the deadline. He will reply with a short scope. Nothing here is a standing offer to interpret studies or supervise a case as a physician.",
    points: [
      "Starting prices are public. The fee is confirmed in writing",
      "Feasibility before an IONM program build-out",
      "Remote by default. Travel is extra",
      "Vendor-neutral equipment guidance",
      "No patient data. Technical review uses de-identified material only",
      "Physician oversight is outside the engagement",
    ],
  },
};

export const solutionsPage = {
  hero: {
    eyebrow: "Solutions",
    title: "IONM is the main pathway",
    description:
      "A new neuromonitoring program, then expert advisory and training. TMS planning is a smaller pathway on the same page.",
  },
  methodology: {
    eyebrow: "Method",
    title: "From a question to a written scope",
    description:
      "The first step is an assessment or a defined call. Documents, training, and launch support follow only when that scope says they should.",
  },
  differentiation: {
    eyebrow: "Limits that stay in place",
    title: "What the work does not include",
    description:
      "NeuroBridge is a technologist’s consulting practice. The limits below are part of every pathway on this page.",
    pillars: [
      {
        title: "Not a physician service",
        desc: "No diagnosis, no treatment advice, and no remote interpretation or oversight in the physician-of-record sense.",
      },
      {
        title: "No employer material",
        desc: "Protocols, pricing, customer lists, and case data from any employer stay out of the work.",
      },
      {
        title: "No invented outcomes",
        desc: "There is no signed client engagement to publish. Caribbean program work is in development only.",
      },
    ],
  },
};

export const aboutPage = {
  hero: {
    eyebrow: "About",
    title: "Brandon Garrison, CNIM, R. EP T.",
    description:
      "Founder of NeuroBridge Healthcare Consulting. A practicing surgical neurophysiologist (technologist, not a physician) whose consulting, training, and ventures sit under this practice.",
    cta: { label: "Capability Statement", href: "/capability-statement" },
  },
  timeline: {
    eyebrow: "Experience",
    title: "Where he has practiced",
    description:
      "Lenox Hill Hospital is listed with Neuro Protective Solutions. It was not a separate employer.",
  },
  specialties: {
    eyebrow: "Case experience",
    title: "What the resume supports",
    description:
      "These are specialties and modalities from his resume. They describe case experience, not a promise about any future engagement.",
  },
  areasOfFocus: {
    eyebrow: "Consulting focus",
    title: "How that experience is used",
    description:
      "NeuroBridge applies this background to advisory calls, program design, TMS launch planning, training, and technical review.",
  },
  capabilityLink: {
    title: "Capability Statement",
    description:
      "A one-document summary of the practice, credentials, offerings, and scope limits, for administrators and anyone comparing consultants.",
    href: "/capability-statement",
  },
};

export const capabilityStatement = {
  title: "Capability Statement",
  subtitle: "NeuroBridge Healthcare Consulting",
  tagline: "Technical and operational consulting for IONM and related programs",
  issued: "2026",
  sections: {
    overview: {
      title: "Firm Overview",
      content:
        "NeuroBridge Healthcare Consulting is the professional practice of Brandon Garrison, CNIM, R. EP T. It is the umbrella for his expert consulting, IONM program development, TMS clinic launch support, training, de-identified technical review, and related ventures. The firm provides technical and operational consulting. It does not provide medical diagnosis or physician oversight.",
    },
    leadership: {
      title: "Founder",
      name: "Brandon Garrison, CNIM, R. EP T.",
      role: "Founder",
      bio: "Practicing IONM technologist since August 2019. B.S. Neuroscience, Baldwin Wallace University, 2019. Roles at National Neuromonitoring Services, Neuro Protective Solutions (including work at Lenox Hill Hospital), Cleveland Clinic, and Guardion Medical. Guardion Medical is a current employer and does not endorse NeuroBridge.",
    },
    capabilities: [
      "IONM expert calls for expert networks, medtech teams, and investors",
      "Device and software product reviews",
      "IONM program feasibility and build-out, including international and Caribbean programs",
      "SOPs, workflow design, training plans, and quality-assurance frameworks",
      "Vendor-neutral equipment selection",
      "TMS clinic feasibility and launch planning",
      "TMS startup ROI calculator",
      "60-minute strategy calls for TMS and neuromonitoring questions",
      "Training modules and onboarding packs",
      "De-identified technical case review",
      "CNIM exam tutoring",
    ],
    audiences: [
      "Expert networks, investors, and consultants",
      "Med-device and software companies",
      "Hospitals and surgical programs",
      "Psychiatry and behavioral-health practices",
      "IONM companies and training programs",
      "CNIM candidates",
    ],
    methodology: [
      {
        step: "Assess",
        detail: "Volume, case mix, staffing, equipment, workflow, or the product question at hand",
      },
      {
        step: "Build",
        detail: "SOPs, training, equipment shortlists, and other documents named in the scope",
      },
      {
        step: "Support",
        detail: "Launch support and technical review. Physician oversight is not included",
      },
    ],
    engagement: [
      "Starting prices are published. The fee is confirmed in a written scope",
      "Remote work by default. Travel is quoted separately",
      "No patient data",
      "No employer confidential material",
      "No medical diagnosis and no physician oversight",
    ],
    initiatives:
      "Connectome.news is the media and research arm (https://connectome.news). FOCUS, the Functional Ocular Control Unit System, is a prototype-stage concept in development, with no clinical or regulatory claims. A Jamaica and Cayman Islands program-development effort is in development and has no signed client. No client case studies are published.",
  },
};

export const venturesPage = {
  hero: {
    eyebrow: "Ventures",
    title: "Projects alongside the consulting practice",
    description:
      "Connectome.news and FOCUS sit under NeuroBridge. They are not client engagements, and this page does not report clinical or commercial results for them.",
  },
  note: "NeuroBridge does not publish client case studies. There is no signed client engagement to describe. Program development aimed at Jamaica and the Cayman Islands is in development only.",
};

export const contactPage = {
  hero: {
    eyebrow: "Contact",
    title: "Email Brandon",
    description:
      "The form opens a draft in your email app to garrison839@gmail.com. Nothing is delivered until you send that email. Do not include patient information.",
  },
  sidebar: {
    expect: {
      title: "What happens next",
      text: "You send the email. Brandon replies with a short scope or with a no, if the request is outside what NeuroBridge does. This is not a medical consultation.",
    },
    response: {
      title: "Timing",
      text: "He is in clinical practice, so a reply may wait until he is out of the operating room. The site does not promise a specific turnaround.",
    },
    direct: {
      title: "Direct",
    },
    confidential: {
      title: "What not to send",
      text: "Do not send patient names, medical record numbers, images, or identifiable case detail. Technical review, if you scope it later, uses de-identified material only.",
    },
  },
  form: {
    title: "Draft an email",
    description:
      "This does not submit to a server. It opens your email app with the message filled in. You still have to press send.",
    messagePlaceholder:
      "What you are building or deciding, who it is for, and any deadline. No patient information.",
  },
  interests: [
    ...productInterests,
    "IONM expert call",
    "Device or software product review",
    "IONM program feasibility or build-out",
    "TMS Clinic Accelerator",
    "Training or SOP package",
    "De-identified technical case review",
    "CNIM exam tutoring",
    "Remote Neurophysiology Support & Case Review",
    "Fractional Clinical Lead for Small IONM Groups",
    "Something else",
  ],
};

export const ctaSection = {
  eyebrow: "Next step",
  title: "Tell Brandon what you need scoped",
  description:
    "Email a short description of the call, product, program, or training question. He will reply with whether it fits and what it would cost.",
  primaryLabel: "Email Brandon",
};

export const footerCopy = {
  ctaTitle: "Start with an email",
  ctaText:
    "Describe the question and the deadline. The contact page opens a draft to Brandon. It is not sent until you send it.",
};

export const priceDisclaimer =
  "Starting prices are catalog ranges. They are not a quote until a scope is confirmed in writing.";
