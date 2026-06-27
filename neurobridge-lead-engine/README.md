# NeuroBridge Lead Engine

Private CRM and business-development dashboard for **NeuroBridge Healthcare Consulting**.

## Features

- **Lead Dashboard** — Filterable table by category, status, priority, and follow-up date
- **Add Lead Form** — Full contact capture with weighted scoring (0–100)
- **Lead Scoring** — Seven-factor model: authority, IONM relevance, system size, geography, strategic fit, urgency, partnership potential
- **Message Generator** — AI-assisted outreach drafts for manual email/LinkedIn sending
- **Content Calendar** — Weekly LinkedIn draft schedule (Mon–Fri themes)
- **Follow-Up Tracker** — Auto-calculated follow-up dates, overdue alerts, message and call history
- **Consultation Pipeline** — Kanban-style stages from researched through closed
- **Document Library** — Capability statements, templates, case studies, proposal sections

## Compliance

This app supports **manual, compliant outreach only**. It does not automate LinkedIn scraping, connection requests, messaging, or engagement.

## Tech Stack

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS 4
- Supabase (optional)
- OpenAI API (optional)

## Getting Started

```bash
cd neurobridge-lead-engine
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Data Storage

Without Supabase credentials, the app uses a local JSON file at `data/store.json` with seed data. For production, configure Supabase and run `supabase/schema.sql` in the SQL editor.

### OpenAI

Set `OPENAI_API_KEY` in `.env.local` to enable AI message and content generation. Without it, sensible fallback templates are used.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

## Design

Premium healthcare consulting aesthetic — dark navy, white, teal, and electric blue. Executive, modern, no startup flash.
