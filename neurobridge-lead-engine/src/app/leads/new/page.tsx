import { DashboardShell } from "@/components/layout/Sidebar";
import { LeadForm } from "@/components/leads/LeadForm";

export default function NewLeadPage() {
  return (
    <DashboardShell>
      <div className="mb-6">
        <h1 className="section-title">Add Lead</h1>
        <p className="section-subtitle">Capture a new prospect with scoring and follow-up scheduling</p>
      </div>
      <LeadForm mode="create" />
    </DashboardShell>
  );
}
