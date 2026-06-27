import { notFound } from "next/navigation";
import { DashboardShell } from "@/components/layout/Sidebar";
import { LeadForm } from "@/components/leads/LeadForm";
import { getLead } from "@/lib/data/repository";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function EditLeadPage({ params }: PageProps) {
  const { id } = await params;
  const lead = await getLead(id);
  if (!lead) notFound();

  return (
    <DashboardShell>
      <div className="mb-6">
        <h1 className="section-title">Edit Lead</h1>
        <p className="section-subtitle">{lead.full_name}</p>
      </div>
      <LeadForm initial={lead} mode="edit" />
    </DashboardShell>
  );
}
