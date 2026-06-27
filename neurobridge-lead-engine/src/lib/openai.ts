import OpenAI from "openai";
import type { MessageAudience } from "./types";
import { CONTENT_CALENDAR_SCHEDULE } from "./constants";

function getOpenAIClient(): OpenAI | null {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return null;
  return new OpenAI({ apiKey });
}

const AUDIENCE_CONTEXT: Record<MessageAudience, string> = {
  surgeon: "a neurosurgeon or spine surgeon who may influence IONM protocols and vendor relationships",
  hospital_executive: "a hospital executive responsible for perioperative services or neuro service line operations",
  healthcare_system_leader: "a health system leader overseeing multiple hospitals and standardized clinical programs",
  investor: "an investor or private equity operator evaluating healthcare services or neuro-related businesses",
  university_program_leader: "a university program director or academic leader in neurophysiology or CNIM training",
  government_healthcare_contact: "a government or public health official involved in healthcare quality or program oversight",
  neurophysiology_trainee: "a neurophysiology trainee or early-career CNIM professional exploring career development",
};

export interface GenerateMessageParams {
  audience: MessageAudience;
  recipientName?: string;
  recipientTitle?: string;
  organization?: string;
  context?: string;
  senderName?: string;
}

export async function generateOutreachMessage(
  params: GenerateMessageParams
): Promise<string> {
  const client = getOpenAIClient();
  const audienceDesc = AUDIENCE_CONTEXT[params.audience];

  const prompt = `Write a personalized outreach message for ${audienceDesc}.

Recipient: ${params.recipientName ?? "there"}${params.recipientTitle ? `, ${params.recipientTitle}` : ""}${params.organization ? ` at ${params.organization}` : ""}
Additional context: ${params.context ?? "General introduction to NeuroBridge Healthcare Consulting"}
Sender: ${params.senderName ?? "NeuroBridge Healthcare Consulting"}

Rules:
- Professional and brief (under 150 words)
- Not spammy, no exaggerated claims
- Human-written feel, not templated
- Clear reason for outreach related to IONM, neurophysiology, or neuro service line consulting
- Soft call-to-action (e.g., brief conversation, sharing a resource)
- Do NOT mention automation, scraping, or mass outreach
- Do NOT claim guaranteed outcomes
- Format as plain text suitable for email or LinkedIn message (manual send only)`;

  if (!client) {
    return fallbackMessage(params);
  }

  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "You write concise, professional healthcare consulting outreach. NeuroBridge specializes in IONM program advisory, neurophysiology operations, and neuro service line consulting.",
      },
      { role: "user", content: prompt },
    ],
    temperature: 0.7,
    max_tokens: 400,
  });

  return response.choices[0]?.message?.content?.trim() ?? fallbackMessage(params);
}

function fallbackMessage(params: GenerateMessageParams): string {
  const name = params.recipientName ?? "there";
  return `Hi ${name},

I came across your work${params.organization ? ` at ${params.organization}` : ""} and wanted to briefly introduce NeuroBridge Healthcare Consulting. We advise hospitals and neuro programs on IONM operations, quality oversight, and perioperative workflow design.

${params.context ? `${params.context}\n\n` : ""}If a short conversation would be useful, I'd welcome the chance to connect at your convenience.

Best regards,
${params.senderName ?? "NeuroBridge Healthcare Consulting"}`;
}

export async function generateContentDraft(
  theme: string,
  dayLabel: string
): Promise<{ title: string; body: string }> {
  const client = getOpenAIClient();
  const scheduleItem = CONTENT_CALENDAR_SCHEDULE.find((s) => s.theme === theme);

  const prompt = `Write a LinkedIn post draft for NeuroBridge Healthcare Consulting.

Day: ${dayLabel}
Theme: ${scheduleItem?.label ?? theme}

Rules:
- Professional healthcare consulting tone
- 150-250 words
- Insightful, not promotional
- No exaggerated claims or hype
- Include a thoughtful opening hook
- End with a reflective question or soft engagement prompt
- Focus on IONM, neurophysiology, neuro service lines, or healthcare operations as appropriate
- Return JSON: {"title": "short headline", "body": "full post text"}`;

  if (!client) {
    return fallbackContentDraft(dayLabel, scheduleItem?.label ?? theme);
  }

  const response = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content: "You create LinkedIn content for a healthcare consulting founder. Return valid JSON only.",
      },
      { role: "user", content: prompt },
    ],
    temperature: 0.75,
    max_tokens: 600,
    response_format: { type: "json_object" },
  });

  const raw = response.choices[0]?.message?.content ?? "{}";
  try {
    const parsed = JSON.parse(raw) as { title?: string; body?: string };
    return {
      title: parsed.title ?? `${dayLabel} Insight`,
      body: parsed.body ?? fallbackContentDraft(dayLabel, scheduleItem?.label ?? theme).body,
    };
  } catch {
    return fallbackContentDraft(dayLabel, scheduleItem?.label ?? theme);
  }
}

function fallbackContentDraft(day: string, theme: string): { title: string; body: string } {
  return {
    title: `${day}: ${theme}`,
    body: `Consistent IONM programs aren't built on technology alone — they're built on clear protocols, accountable workflows, and surgeon-aligned communication.\n\nIn our advisory work, the highest-performing neuro service lines share one trait: they treat intraoperative monitoring as a clinical partnership, not a vendor transaction.\n\nWhat's one operational change that improved your OR neuro monitoring workflow?`,
  };
}

export function isOpenAIConfigured(): boolean {
  return Boolean(process.env.OPENAI_API_KEY);
}
