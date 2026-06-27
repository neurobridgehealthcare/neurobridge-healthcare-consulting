import { addDays, format, isBefore, parseISO, startOfDay } from "date-fns";
import { FOLLOW_UP_INTERVALS_DAYS } from "./constants";
import type { Lead, LeadStatus } from "./types";

export function calculateNextFollowUpDate(
  status: LeadStatus,
  fromDate: Date = new Date()
): string {
  const days = FOLLOW_UP_INTERVALS_DAYS[status] ?? 14;
  return format(addDays(fromDate, days), "yyyy-MM-dd");
}

export function isFollowUpOverdue(nextFollowUpDate: string | null): boolean {
  if (!nextFollowUpDate) return false;
  const today = startOfDay(new Date());
  const followUp = startOfDay(parseISO(nextFollowUpDate));
  return isBefore(followUp, today);
}

export function daysUntilFollowUp(nextFollowUpDate: string | null): number | null {
  if (!nextFollowUpDate) return null;
  const today = startOfDay(new Date());
  const followUp = startOfDay(parseISO(nextFollowUpDate));
  return Math.ceil((followUp.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

export function getOverdueLeads(leads: Lead[]): Lead[] {
  return leads.filter((lead) => isFollowUpOverdue(lead.next_follow_up_date));
}

export function formatFollowUpDate(date: string | null): string {
  if (!date) return "Not scheduled";
  const days = daysUntilFollowUp(date);
  if (days === null) return date;
  if (days < 0) return `${Math.abs(days)}d overdue`;
  if (days === 0) return "Due today";
  if (days === 1) return "Due tomorrow";
  return `In ${days} days`;
}
