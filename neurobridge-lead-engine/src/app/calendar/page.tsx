import { format, startOfWeek } from "date-fns";
import { DashboardShell } from "@/components/layout/Sidebar";
import { ContentCalendarView } from "@/components/calendar/ContentCalendarView";
import { getContentCalendar } from "@/lib/data/repository";

interface PageProps {
  searchParams: Promise<{ week?: string }>;
}

export default async function CalendarPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const weekStart =
    params.week ??
    format(startOfWeek(new Date(), { weekStartsOn: 1 }), "yyyy-MM-dd");

  const entries = await getContentCalendar(weekStart);

  return (
    <DashboardShell>
      <div className="mb-6">
        <h1 className="section-title">Content Calendar</h1>
        <p className="section-subtitle">
          Weekly LinkedIn draft schedule — generate, review, post manually
        </p>
      </div>
      <ContentCalendarView entries={entries} weekStart={weekStart} />
    </DashboardShell>
  );
}
