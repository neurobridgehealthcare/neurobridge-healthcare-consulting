import { DashboardShell } from "@/components/layout/Sidebar";
import { MessageGenerator } from "@/components/messages/MessageGenerator";

export default function MessagesPage() {
  return (
    <DashboardShell>
      <div className="mb-6">
        <h1 className="section-title">Message Generator</h1>
        <p className="section-subtitle">
          AI-assisted outreach drafts for manual, compliant sending
        </p>
      </div>
      <MessageGenerator />
    </DashboardShell>
  );
}
