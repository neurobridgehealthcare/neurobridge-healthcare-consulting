import { DashboardShell } from "@/components/layout/Sidebar";
import { DocumentLibrary } from "@/components/documents/DocumentLibrary";
import { getDocuments } from "@/lib/data/repository";

export default async function DocumentsPage() {
  const documents = await getDocuments();

  return (
    <DashboardShell>
      <div className="mb-6">
        <h1 className="section-title">Document Library</h1>
        <p className="section-subtitle">
          Reusable capability statements, templates, and proposal sections
        </p>
      </div>
      <DocumentLibrary documents={documents} />
    </DashboardShell>
  );
}
