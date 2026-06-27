import type { ScoringFactors } from "./types";

const FACTOR_WEIGHTS: Record<keyof ScoringFactors, number> = {
  decision_making_authority: 0.2,
  ionm_relevance: 0.2,
  hospital_system_size: 0.15,
  geographic_opportunity: 0.1,
  strategic_fit: 0.15,
  urgency_signals: 0.1,
  partnership_potential: 0.1,
};

export function clampScore(value: number): number {
  return Math.max(0, Math.min(100, Math.round(value)));
}

export function calculatePriorityScore(scoring: ScoringFactors): number {
  let total = 0;
  for (const [key, weight] of Object.entries(FACTOR_WEIGHTS) as [keyof ScoringFactors, number][]) {
    total += (scoring[key] ?? 0) * weight;
  }
  return clampScore(total);
}

export function defaultScoring(): ScoringFactors {
  return {
    decision_making_authority: 50,
    ionm_relevance: 50,
    hospital_system_size: 50,
    geographic_opportunity: 50,
    strategic_fit: 50,
    urgency_signals: 30,
    partnership_potential: 40,
  };
}

export function scoringSummary(scoring: ScoringFactors): string {
  const score = calculatePriorityScore(scoring);
  const topFactors = (Object.entries(scoring) as [keyof ScoringFactors, number][])
    .sort(([, a], [, b]) => b - a)
    .slice(0, 2)
    .map(([key]) => key.replace(/_/g, " "))
    .join(", ");
  return `Priority ${score}/100 — strongest signals: ${topFactors}`;
}
