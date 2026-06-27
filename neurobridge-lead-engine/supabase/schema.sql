-- NeuroBridge Lead Engine — Supabase Schema
-- Run this in the Supabase SQL editor to enable cloud persistence.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  full_name TEXT NOT NULL,
  title TEXT DEFAULT '',
  organization TEXT DEFAULT '',
  specialty TEXT DEFAULT '',
  country_state TEXT DEFAULT '',
  lead_category TEXT NOT NULL,
  linkedin_url TEXT DEFAULT '',
  public_email TEXT DEFAULT '',
  website TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  source TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'new',
  priority_score INTEGER NOT NULL DEFAULT 0,
  pipeline_stage TEXT NOT NULL DEFAULT 'researched',
  scoring JSONB NOT NULL DEFAULT '{}',
  next_follow_up_date DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS message_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  channel TEXT DEFAULT 'email',
  direction TEXT NOT NULL DEFAULT 'outbound',
  subject TEXT DEFAULT '',
  body TEXT NOT NULL,
  sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS call_outcomes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  outcome TEXT NOT NULL,
  notes TEXT DEFAULT '',
  call_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS content_calendar (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start DATE NOT NULL,
  day_of_week TEXT NOT NULL,
  theme TEXT NOT NULL,
  draft_title TEXT DEFAULT '',
  draft_body TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (week_start, day_of_week)
);

CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  content TEXT NOT NULL DEFAULT '',
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_category ON leads(lead_category);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_pipeline ON leads(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_leads_follow_up ON leads(next_follow_up_date);
CREATE INDEX IF NOT EXISTS idx_message_history_lead ON message_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_call_outcomes_lead ON call_outcomes(lead_id);

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Private app: restrict to authenticated users (configure auth as needed)
CREATE POLICY "Authenticated full access on leads" ON leads
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated full access on message_history" ON message_history
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated full access on call_outcomes" ON call_outcomes
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated full access on content_calendar" ON content_calendar
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated full access on documents" ON documents
  FOR ALL USING (auth.role() = 'authenticated');
