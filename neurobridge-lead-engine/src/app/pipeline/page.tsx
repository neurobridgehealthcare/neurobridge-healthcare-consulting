import { DashboardShell } from "@/components/layout/Sidebar";
import { PipelineBoard } from "@/components/pipeline/PipelineBoard";
import { getLeads } from "@/lib/data/repository";

export default async function PipelinePage() {
  const leads = await getLeads();

  return (
    <DashboardShell>
      <div className="mb-6">
        <h1 className="section-title">Consultation Pipeline</h1>
        <p className="section-subtitle">
          Track prospects from research through proposal and close
        </p>
      </div>
      <PipelineBoard leads={leads} />
    </DashboardShell>
  );
}
