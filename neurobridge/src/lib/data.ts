import type { LucideIcon } from "lucide-react";
import {
  Activity,
  Award,
  BookOpen,
  ClipboardCheck,
  Cpu,
  FileText,
  Globe,
  GraduationCap,
  Handshake,
  Hospital,
  Layers,
  LineChart,
  Microscope,
  Monitor,
  Network,
  Scan,
  ShieldCheck,
  Stethoscope,
  Target,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";

export const siteConfig = {
  name: "NeuroBridge Healthcare Consulting",
  shortName: "NeuroBridge",
  tagline: "Neurophysiology Program Development & Clinical Operations",
  description:
    "NeuroBridge partners with hospitals, surgeons, and healthcare systems to develop, implement, and sustain intraoperative neuromonitoring and neurophysiology programs — through clinical oversight, quality assurance, training pathways, and operational infrastructure.",
  email: "contact@neurobridgehealth.com",
};

export const navigation = [
  { label: "Home", href: "/" },
  { label: "Services", href: "/services" },
  { label: "Solutions", href: "/solutions" },
  { label: "About", href: "/about" },
  { label: "Case Studies", href: "/case-studies" },
  { label: "Schedule Consultation", href: "/contact" },
];

export type Service = {
  title: string;
  description: string;
  icon: LucideIcon;
};

export const sTierServices: Service[] = [
  {
    title: "Remote Neurophysiology Oversight",
    description:
      "Clinical oversight for intraoperative neuromonitoring programs — supporting protocol adherence, case review, and coordination with surgical teams in real time.",
    icon: Monitor,
  },
  {
    title: "Quality Assurance & Clinical Auditing",
    description:
      "Structured QA programs, case audits, and performance review to maintain clinical standards, identify gaps, and support continuous improvement.",
    icon: ShieldCheck,
  },
  {
    title: "Intraoperative Neuromonitoring Program Development",
    description:
      "Program design from feasibility assessment through clinical launch — including workflow architecture, staffing models, governance structure, and implementation planning.",
    icon: Activity,
  },
];

export const aTierServices: Service[] = [
  {
    title: "Standard Operating Procedure Development",
    description:
      "Institution-specific SOPs developed against surgical volume, case mix, and clinical requirements — forming the foundation of consistent IONM delivery.",
    icon: FileText,
  },
  {
    title: "Clinical Operations Consulting",
    description:
      "Operational planning for case scheduling, workflow integration, equipment utilization, and coordination across surgical and support departments.",
    icon: Layers,
  },
  {
    title: "Personnel Development & Training Programs",
    description:
      "Defined training pathways for neurophysiology technologists — from structured onboarding through progressive clinical competency.",
    icon: Users,
  },
  {
    title: "CNIM Preparation Programs",
    description:
      "Targeted preparation for CNIM certification candidates, including clinical case review, competency assessment, and examination readiness support.",
    icon: Award,
  },
  {
    title: "Equipment Selection & Implementation Planning",
    description:
      "Vendor-neutral guidance on IONM equipment evaluation, procurement planning, and integration into existing clinical and operational workflows.",
    icon: Cpu,
  },
  {
    title: "Competency Benchmark Development",
    description:
      "Competency frameworks and assessment criteria aligned with institutional standards, case complexity, and program maturity.",
    icon: Target,
  },
];

export const additionalServices: Service[] = [
  {
    title: "Hospital Program Assessments",
    description:
      "Structured assessment of existing or planned neurophysiology programs — evaluating clinical readiness, operational gaps, and implementation priorities.",
    icon: Hospital,
  },
  {
    title: "Physician Partnership Development",
    description:
      "Support for aligning IONM services with surgeon practices and surgical service lines — establishing clinical expectations and operational coordination.",
    icon: Handshake,
  },
  {
    title: "Service Line Expansion Planning",
    description:
      "Planning for IONM coverage across additional surgical specialties, procedural types, or institutional locations.",
    icon: TrendingUp,
  },
  {
    title: "Educational Curriculum Development",
    description:
      "Curriculum design for neurophysiology education, continuing professional development, and institutional training programs.",
    icon: BookOpen,
  },
  {
    title: "Healthcare Startup Consulting",
    description:
      "Advisory for investors and organizations entering neurophysiology markets — covering operational planning, infrastructure requirements, and implementation feasibility.",
    icon: Zap,
  },
];

export const audiences = [
  {
    title: "Hospitals",
    description:
      "Program development and clinical infrastructure for institutions building or strengthening IONM services.",
    icon: Hospital,
  },
  {
    title: "Spine Surgeons",
    description:
      "Clinical oversight and program support aligned with spine surgical volume, case complexity, and service line requirements.",
    icon: Scan,
  },
  {
    title: "Neurosurgeons",
    description:
      "Neurophysiology infrastructure for skull base, tumor, cranial nerve, and vascular neurosurgical procedures.",
    icon: Microscope,
  },
  {
    title: "Neurophysiology Trainees",
    description:
      "Structured clinical development, CNIM preparation, and competency-based training pathways.",
    icon: GraduationCap,
  },
  {
    title: "Universities",
    description:
      "Academic program design, curriculum development, and clinical training infrastructure for neurophysiology education.",
    icon: BookOpen,
  },
  {
    title: "Healthcare Investors",
    description:
      "Operational due diligence, market assessment, and infrastructure planning for neurophysiology ventures and service line investments.",
    icon: LineChart,
  },
  {
    title: "Government Healthcare Systems",
    description:
      "Regional and national IONM infrastructure development for public healthcare systems and emerging market health ministries.",
    icon: Globe,
  },
  {
    title: "Existing Neurophysiology Organizations",
    description:
      "Quality assurance review, operational assessment, and clinical governance improvement for established IONM providers.",
    icon: Network,
  },
];

export const processSteps = [
  {
    step: "01",
    title: "Assess",
    description:
      "Review surgical volume, staffing capacity, equipment, clinical workflow, and program readiness against institutional objectives.",
    icon: ClipboardCheck,
  },
  {
    step: "02",
    title: "Build",
    description:
      "Develop SOPs, training pathways, equipment plans, competency standards, and the operational structure required for clinical launch.",
    icon: Layers,
  },
  {
    step: "03",
    title: "Support",
    description:
      "Provide ongoing clinical oversight, QA review, continuing education, and long-term guidance as the program matures.",
    icon: Stethoscope,
  },
];

export const solutions = [
  {
    title: "New Program Launch",
    description:
      "Structured program development for hospitals initiating intraoperative neuromonitoring services — from feasibility analysis through first clinical cases.",
    features: [
      "Feasibility assessment and business case support",
      "Equipment evaluation and procurement planning",
      "Staff recruitment and training pathway design",
      "SOP and clinical protocol development",
      "Surgeon and department engagement planning",
    ],
    icon: Zap,
  },
  {
    title: "Program Optimization",
    description:
      "Clinical and operational review for established IONM programs seeking to improve quality, consistency, and service line performance.",
    features: [
      "Clinical audit and QA program review",
      "Workflow and case flow assessment",
      "Competency benchmarking and gap analysis",
      "Technology and equipment evaluation",
      "Personnel development planning",
    ],
    icon: TrendingUp,
  },
  {
    title: "Regional Infrastructure",
    description:
      "Multi-site and system-level neurophysiology infrastructure for healthcare networks, government systems, and emerging market regions.",
    features: [
      "Regional service model and coverage planning",
      "Training academy and workforce development",
      "Centralized quality assurance framework",
      "Equipment standardization across sites",
      "Sustainable staffing and oversight models",
    ],
    icon: Globe,
  },
  {
    title: "Surgeon Partnership",
    description:
      "Clinical and operational support aligned with individual surgeon practices and high-volume neurosurgical or spine programs.",
    features: [
      "Procedure-specific monitoring protocols",
      "Case workflow and scheduling coordination",
      "Remote clinical oversight support",
      "Performance review and case documentation",
      "Continuing education for clinical teams",
    ],
    icon: Handshake,
  },
];

export const caseStudies = [
  {
    title: "Jamaica & Cayman Islands Neurophysiology Development Initiative",
    status: "In Development" as const,
    region: "Caribbean",
    summary:
      "A physician-supported initiative to establish sustainable intraoperative neuromonitoring services — including equipment planning, personnel training, SOP development, quality assurance frameworks, and clinical oversight infrastructure.",
    highlights: [
      "Regional IONM infrastructure and service planning",
      "Personnel training and competency pathway development",
      "Clinical protocol and SOP development",
      "Equipment selection and implementation support",
      "Ongoing clinical oversight framework",
    ],
  },
];

export const founder = {
  name: "Brandon Garrison, CNIM",
  shortName: "Brandon Garrison",
  title: "Founder & Principal Consultant",
  credentials: [
    {
      abbr: "CNIM",
      full: "Certified in Neurophysiologic Intraoperative Monitoring",
    },
    {
      abbr: "R.EPT",
      full: "Registered Electrophysiology Technologist",
    },
  ],
  bio: "Brandon Garrison is a CNIM-certified surgical neurophysiologist with experience in intraoperative neuromonitoring, neurophysiology education, clinical operations, and program development. His clinical background includes high-acuity neurosurgical and spine environments — including Cleveland Clinic and Lenox Hill Hospital — with experience in complex spine, skull base, tumor, and cranial nerve monitoring procedures.",
  story: {
    eyebrow: "Founder Story",
    title: "Clinical Practice to Program Infrastructure",
    paragraphs: [
      "Brandon Garrison built his career in intraoperative neuromonitoring across high-acuity neurosurgical and spine environments — including Cleveland Clinic and Lenox Hill Hospital. His clinical work spans complex spine, skull base, tumor, and cranial nerve monitoring procedures, with direct responsibility for real-time neuromonitoring support in demanding surgical settings.",
      "Through that clinical foundation, he developed expertise beyond the operating room: neurophysiology education, clinical operations, competency development, and the structural requirements that allow IONM programs to function reliably within hospital systems.",
      "NeuroBridge Healthcare Consulting was established to apply that experience at the institutional level — helping hospitals, surgeons, and healthcare systems develop the clinical oversight, quality assurance, training pathways, and operational infrastructure required for sustainable neurophysiology services.",
    ],
  },
  timeline: [
    {
      period: "Clinical Practice",
      organization: "Cleveland Clinic",
      role: "Surgical Neurophysiologist",
      description:
        "Intraoperative neuromonitoring in a high-acuity academic medical center — supporting complex neurosurgical and spine procedures across a major institutional environment.",
    },
    {
      period: "Clinical Practice",
      organization: "Lenox Hill Hospital",
      role: "Surgical Neurophysiologist",
      description:
        "IONM support for neurosurgical and spine surgical service lines — including skull base, tumor, cranial nerve, and complex spine monitoring cases.",
    },
    {
      period: "Program Development",
      organization: "Neurophysiology Education & Operations",
      role: "Clinical Operations & Training",
      description:
        "Development of training pathways, clinical competency frameworks, and operational support structures for neurophysiology teams and program staff.",
    },
    {
      period: "Present",
      organization: "NeuroBridge Healthcare Consulting",
      role: "Founder & Principal Consultant",
      description:
        "Advisory and program development for hospitals, surgeons, healthcare systems, and emerging market regions — including current infrastructure initiatives in Jamaica and the Cayman Islands.",
    },
  ],
  areasOfFocus: [
    {
      title: "Program Development",
      description:
        "Feasibility assessment, implementation planning, and clinical launch support for new and expanding IONM programs.",
    },
    {
      title: "Clinical Oversight",
      description:
        "Remote neuromonitoring oversight, protocol adherence, and real-time clinical coordination with surgical teams.",
    },
    {
      title: "Quality Assurance",
      description:
        "Structured QA programs, case audits, and performance review to maintain clinical standards and support improvement.",
    },
    {
      title: "Training Pathways",
      description:
        "Technologist development, CNIM preparation support, and continuing education for neurophysiology personnel.",
    },
    {
      title: "SOP & Protocol Development",
      description:
        "Institution-specific standard operating procedures and clinical protocols aligned with surgical volume and case mix.",
    },
    {
      title: "Global Healthcare Systems",
      description:
        "Neurophysiology infrastructure development for emerging market health systems and multi-site regional programs.",
    },
  ],
  vision: {
    eyebrow: "Vision",
    title: "Sustainable Neurophysiology Infrastructure",
    statement:
      "NeuroBridge exists to help institutions build neurophysiology programs that perform reliably in clinical practice — not only at launch, but over time. That requires defined clinical oversight, quality assurance systems, training infrastructure, and operational frameworks that hospitals and surgeons can depend on.",
    supporting:
      "Our work is oriented toward long-term program sustainability — supporting hospitals, surgical service lines, and healthcare systems as they develop, implement, and maintain intraoperative neuromonitoring services at scale.",
  },
  highlights: [
    {
      title: "Clinical Background",
      text: "CNIM-certified surgical neurophysiologist with experience across complex spine, skull base, tumor, and cranial nerve monitoring procedures.",
    },
    {
      title: "Institutional Experience",
      text: "Clinical experience in high-acuity neurosurgical and spine environments, including Cleveland Clinic and Lenox Hill Hospital.",
    },
    {
      title: "Program Development",
      text: "Background in neurophysiology education, clinical operations, and IONM program infrastructure development for hospitals and healthcare systems.",
    },
  ],
};

export const developmentNote =
  "NeuroBridge is currently supporting neurophysiology infrastructure development initiatives, with an initial focus on Jamaica and the Cayman Islands.";

export const credibilityStrip = [
  { label: "CNIM-Certified Clinical Leadership", icon: Award },
  { label: "Neurophysiology Program Development", icon: Layers },
  { label: "IONM Training & Clinical Oversight", icon: Monitor },
  { label: "Global Healthcare Systems Advisory", icon: Globe },
];

export const problemSection = {
  eyebrow: "The Challenge",
  title: "The Problem We Solve",
  description:
    "Many hospitals and surgical teams recognize the clinical value of intraoperative neuromonitoring but lack the infrastructure to implement it safely and at scale. NeuroBridge helps institutions move from intent to execution — by developing the clinical, operational, educational, and quality systems that reliable neurophysiology services require.",
  painPoints: [
    "No defined clinical protocols or standard operating procedures",
    "Insufficient training pathways and competency standards",
    "No structured quality assurance or audit framework",
    "No implementation plan from feasibility to clinical operations",
  ],
  callout:
    "NeuroBridge addresses the gap between clinical intent and the infrastructure required for sustainable IONM delivery.",
};

export const whyNeuroBridge = [
  {
    title: "Clinical Expertise",
    description:
      "CNIM-certified leadership with direct experience in high-acuity neurosurgical and spine monitoring environments.",
    icon: Stethoscope,
  },
  {
    title: "Training Infrastructure",
    description:
      "Defined training pathways for technologist development, CNIM preparation, and continuing clinical education.",
    icon: GraduationCap,
  },
  {
    title: "SOP & QA Development",
    description:
      "Institution-specific protocols, competency frameworks, and quality assurance programs built for clinical consistency.",
    icon: ShieldCheck,
  },
  {
    title: "Remote Oversight Capability",
    description:
      "Clinical oversight and QA review for programs that require expert guidance without full on-site staffing.",
    icon: Monitor,
  },
  {
    title: "Global Implementation Experience",
    description:
      "Program development experience across domestic institutions and emerging market healthcare systems.",
    icon: Globe,
  },
];

export const homePage = {
  hero: {
    badge: "Neurophysiology Program Development & Clinical Operations",
    headlineAccent: "Neurophysiology Programs",
    subheadline:
      "NeuroBridge develops and supports intraoperative neuromonitoring and neurophysiology programs for hospitals and surgical service lines — spanning clinical oversight, quality assurance, training pathway design, SOP development, and the operational infrastructure required for sustainable IONM services.",
  },
  coreServices: {
    eyebrow: "Core Services",
    title: "Clinical Infrastructure for IONM Programs",
    description:
      "Remote oversight, quality assurance, and program development services — structured to support hospitals and surgeons at every stage of neurophysiology service delivery.",
  },
  whoWeServe: {
    eyebrow: "Who We Serve",
    title: "Institutions Across the Healthcare Landscape",
    description:
      "Hospitals, surgeons, academic centers, investors, and government healthcare systems — at every stage of neurophysiology program development.",
  },
  approach: {
    eyebrow: "Our Approach",
    title: "From Concept to Clinical Operations",
    description:
      "A defined three-phase methodology for assessing readiness, building infrastructure, and supporting sustainable clinical operations.",
  },
  expanded: {
    eyebrow: "Expanded Capabilities",
    title: "Operational & Strategic Support",
    description:
      "Additional consulting across clinical operations, personnel development, physician partnerships, and service line planning.",
  },
  whySection: {
    eyebrow: "Why NeuroBridge",
    title: "Built for Institutional Requirements",
    description:
      "NeuroBridge works with hospitals and healthcare systems that need defined clinical systems, structured training pathways, and operational frameworks — not general guidance alone.",
  },
};

export const servicesPage = {
  hero: {
    eyebrow: "Services",
    title: "Neurophysiology Consulting Services",
    description:
      "Structured consulting across clinical oversight, quality assurance, program development, and operational infrastructure — scoped to the maturity and objectives of each institution.",
  },
  sTier: {
    eyebrow: "Core Services",
    title: "Clinical & Program Infrastructure",
    description:
      "Foundational services that establish clinical governance, quality standards, and the structural basis for sustainable IONM program delivery.",
  },
  aTier: {
    eyebrow: "Operational Services",
    title: "Development & Operational Support",
    description:
      "Consulting to strengthen clinical operations, personnel development, equipment planning, and day-to-day program infrastructure.",
  },
  additional: {
    eyebrow: "Advisory Services",
    title: "Assessment & Strategic Consulting",
    description:
      "Targeted advisory for program assessments, physician partnerships, service line expansion, and neurophysiology market entry.",
  },
  engagement: {
    eyebrow: "Engagement Model",
    title: "Scoped to Your Program",
    description:
      "Each engagement begins with an assessment of surgical volume, institutional objectives, and current infrastructure. Services are defined against specific clinical and operational outcomes.",
    points: [
      "Engagements scoped individually — no public pricing",
      "Advisory, development, and ongoing oversight models available",
      "Remote and on-site support options",
      "Vendor-neutral equipment and technology guidance",
      "Long-term clinical partnership orientation",
    ],
  },
};

export const solutionsPage = {
  hero: {
    eyebrow: "Solutions",
    title: "Program Pathways by Stage and Scale",
    description:
      "Structured solutions for new program launches, established program optimization, regional infrastructure development, and surgeon-aligned clinical support.",
  },
  methodology: {
    eyebrow: "Methodology",
    title: "From Concept to Clinical Operations",
    description:
      "A three-phase approach — assess readiness, build infrastructure, and provide ongoing clinical support — designed for sustainable program implementation.",
  },
  differentiation: {
    eyebrow: "Our Approach",
    title: "Infrastructure, Not General Advice",
    description:
      "NeuroBridge engagements produce defined clinical systems — SOPs, training pathways, QA frameworks, and operational structures — built for institutions that require implementable infrastructure.",
    pillars: [
      {
        title: "Clinical Credibility",
        desc: "CNIM-certified leadership with direct experience in high-acuity hospital neurophysiology environments.",
      },
      {
        title: "Operational Depth",
        desc: "SOPs, training pathways, QA frameworks, and competency standards — developed for clinical use, not presentation.",
      },
      {
        title: "Global Experience",
        desc: "Program development across domestic healthcare systems and emerging market regions.",
      },
    ],
  },
};

export const aboutPage = {
  hero: {
    eyebrow: "About",
    title: "Leadership in Neurophysiology Program Development",
    description:
      "NeuroBridge Healthcare Consulting is led by Brandon Garrison, CNIM — a surgical neurophysiologist with institutional experience in intraoperative neuromonitoring, clinical operations, and program infrastructure development for hospitals and healthcare systems.",
    cta: { label: "Capability Statement", href: "/capability-statement" },
  },
  founderStory: {
    eyebrow: "Founder Story",
    title: "Clinical Practice to Program Infrastructure",
  },
  timeline: {
    eyebrow: "Clinical Experience",
    title: "Institutional Background",
    description:
      "A clinical career in high-acuity hospital environments — extended into neurophysiology education, operational development, and institutional consulting.",
  },
  areasOfFocus: {
    eyebrow: "Areas of Focus",
    title: "Where Clinical Experience Meets Institutional Need",
    description:
      "NeuroBridge engagements are structured around the clinical and operational domains required to build and sustain reliable IONM programs.",
  },
  vision: {
    eyebrow: "Vision",
    title: "Sustainable Neurophysiology Infrastructure",
  },
  capabilityLink: {
    title: "Capability Statement",
    description:
      "A formal overview of NeuroBridge services, leadership credentials, and engagement model — prepared for hospital administrators and healthcare executives.",
    href: "/capability-statement",
  },
};

export const capabilityStatement = {
  title: "Capability Statement",
  subtitle: "NeuroBridge Healthcare Consulting",
  tagline: "Neurophysiology Program Development & Clinical Operations",
  issued: "2025",
  sections: {
    overview: {
      title: "Firm Overview",
      content:
        "NeuroBridge Healthcare Consulting is a healthcare operations and neurophysiology development firm. We partner with hospitals, surgeons, healthcare systems, universities, investors, and government health organizations to develop, implement, and sustain intraoperative neuromonitoring and neurophysiology programs — through clinical oversight, quality assurance, training pathway design, SOP development, and operational infrastructure.",
    },
    leadership: {
      title: "Leadership",
      name: "Brandon Garrison, CNIM",
      role: "Founder & Principal Consultant",
      bio: "CNIM-certified surgical neurophysiologist with clinical experience in high-acuity neurosurgical and spine environments, including Cleveland Clinic and Lenox Hill Hospital. Background in intraoperative neuromonitoring, neurophysiology education, clinical operations, and IONM program development.",
    },
    capabilities: [
      "Remote neurophysiology oversight",
      "Quality assurance and clinical auditing",
      "IONM program development and implementation",
      "Standard operating procedure development",
      "Clinical operations consulting",
      "Personnel development and training programs",
      "CNIM preparation programs",
      "Equipment selection and implementation planning",
      "Competency benchmark development",
      "Hospital program assessments",
      "Physician partnership development",
      "Regional and emerging market infrastructure planning",
    ],
    audiences: [
      "Hospitals and health systems",
      "Spine surgeons and neurosurgeons",
      "Neurophysiology trainees and educators",
      "Universities and academic medical centers",
      "Healthcare investors",
      "Government healthcare systems",
      "Existing neurophysiology organizations",
    ],
    methodology: [
      { step: "Assess", detail: "Surgical volume, staffing, equipment, workflow, and program readiness" },
      { step: "Build", detail: "SOPs, training pathways, equipment plans, competency standards, operational structure" },
      { step: "Support", detail: "Remote oversight, QA review, continuing education, long-term clinical guidance" },
    ],
    engagement: [
      "Engagements scoped individually to institutional objectives",
      "Advisory, development, and ongoing oversight models",
      "Remote and on-site support available",
      "Vendor-neutral equipment and technology guidance",
      "Confidential consultation process",
    ],
  },
};

export const caseStudiesPage = {
  hero: {
    eyebrow: "Case Studies",
    title: "Program Development Initiatives",
    description:
      "Active and developing neurophysiology infrastructure projects — illustrating how NeuroBridge supports hospitals and healthcare systems in building sustainable IONM programs.",
  },
  cta: {
    eyebrow: "Partner With Us",
    title: "Discuss Your Program Development Needs",
    description:
      "NeuroBridge works with hospitals, healthcare systems, and investors on neurophysiology infrastructure development. Contact us to discuss your institution's objectives.",
  },
};

export const contactPage = {
  hero: {
    eyebrow: "Contact",
    title: "Schedule a Consultation",
    description:
      "Share your program objectives and institutional context. We will review your inquiry and schedule a consultation to discuss clinical infrastructure, implementation planning, and next steps.",
  },
  sidebar: {
    expect: {
      title: "What to Expect",
      text: "A structured conversation about your surgical volume, current infrastructure, and program objectives. Each engagement is scoped individually — there is no public pricing.",
    },
    response: {
      title: "Response Time",
      text: "Consultation requests are reviewed within one to two business days. We respond with proposed next steps.",
    },
    direct: {
      title: "Direct Contact",
    },
    confidential: {
      title: "Confidential",
      text: "All inquiries are handled confidentially. We recognize the sensitivity of healthcare program development and institutional planning.",
    },
  },
  form: {
    title: "Request a Consultation",
    description: "Provide your details and program context below.",
    successTitle: "Consultation Request Received",
    successMessage:
      "Thank you for your inquiry. We will review your submission and respond within one to two business days.",
    messagePlaceholder:
      "Describe the program you are building or improving — including surgical volume, current infrastructure, and primary objectives.",
  },
};

export const ctaSection = {
  eyebrow: "Next Step",
  title: "Ready to Build or Strengthen a Neurophysiology Program?",
  description:
    "Schedule a consultation to discuss your goals, current infrastructure, and next steps.",
  primaryLabel: "Schedule Consultation",
};

export const footerCopy = {
  ctaTitle: "Begin a Conversation",
  ctaText:
    "Discuss your neurophysiology program objectives with our team. Consultations are scoped to your institution's clinical and operational requirements.",
};
