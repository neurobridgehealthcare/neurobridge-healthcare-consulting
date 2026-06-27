"""
Stage 3D — Adaptive Environment Filter Engine.

Rule-based scoring from Stage 3C research tables. Classifies conditions as
FAVORABLE / NEUTRAL / AVOID using historical expectancy, profit factor, and
robustness — not predictive modeling.

Research only. Not for live trading.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from environment_engine import (
    EnvironmentMarketBundle,
    EnvironmentResearchResult,
    SessionEnvironmentFeatures,
    compute_session_environment_features,
    load_environment_bundle_for_session,
)

PROJECT_DIR = Path(__file__).resolve().parent
ADAPTIVE_RULES_FILE = PROJECT_DIR / "adaptive_environment_rules.json"
ENVIRONMENT_SCORES_FILE = PROJECT_DIR / "environment_scores.csv"

MIN_SAMPLE_SIZE = 8
WEIGHT_CAP = 0.22
FAVORABLE_THRESHOLD = 62.0
AVOID_THRESHOLD = 38.0

DIMENSION_KEYS = (
    "time_bucket",
    "regime",
    "premarket_trend",
    "or_candle_quality",
    "relative_strength",
)

DIMENSION_TO_TABLE = {
    "time_bucket": "by_time_bucket",
    "regime": "by_regime",
    "premarket_trend": "by_premarket_trend",
    "or_candle_quality": "by_or_candle",
    "relative_strength": "by_relative_strength",
}


@dataclass
class BucketScore:
    dimension: str
    bucket: str
    total_trades: int
    win_rate: float
    expectancy: float
    profit_factor: float
    robustness_score: float
    bucket_score: float
    environment_label: str
    weight: float = WEIGHT_CAP


@dataclass
class AdaptiveEnvironmentRules:
    bucket_scores: Dict[str, Dict[str, BucketScore]] = field(default_factory=dict)
    min_sample_size: int = MIN_SAMPLE_SIZE
    favorable_threshold: float = FAVORABLE_THRESHOLD
    avoid_threshold: float = AVOID_THRESHOLD
    source_trades: int = 0
    built_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_sample_size": self.min_sample_size,
            "favorable_threshold": self.favorable_threshold,
            "avoid_threshold": self.avoid_threshold,
            "source_trades": self.source_trades,
            "built_at": self.built_at,
            "bucket_scores": {
                dim: {b: asdict(sc) for b, sc in buckets.items()}
                for dim, buckets in self.bucket_scores.items()
            },
        }


@dataclass
class EnvironmentAssessment:
    environment_score: float
    environment_label: str
    confidence: float
    historical_expectancy: float
    historical_win_rate: float
    recommendation: str
    tags: Dict[str, Optional[str]] = field(default_factory=dict)
    dimension_contributions: Dict[str, float] = field(default_factory=dict)
    session_features: Optional[SessionEnvironmentFeatures] = None
    warnings: List[str] = field(default_factory=list)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _label_from_bucket_score(normalized: float) -> str:
    if normalized >= 0.35:
        return "FAVORABLE"
    if normalized <= -0.35:
        return "AVOID"
    return "NEUTRAL"


def compute_bucket_score(
    expectancy: float,
    profit_factor: float,
    robustness_score: float,
    total_trades: int,
) -> Optional[float]:
    """Normalized bucket score in [-1, 1]; None if sample too small."""
    if total_trades < MIN_SAMPLE_SIZE:
        return None

    exp_part = _clamp(expectancy / 120.0, -1.0, 1.0) * 0.35
    pf_part = _clamp((profit_factor - 1.0) / 1.5, -1.0, 1.0) * 0.35
    rob_part = _clamp(robustness_score / 60.0, -1.0, 1.0) * 0.30
    score = exp_part + pf_part + rob_part

    if profit_factor < 1.15:
        score -= 0.25
    if expectancy < 0:
        score -= 0.20
    if robustness_score < 0:
        score -= 0.15

    return _clamp(score, -1.0, 1.0)


def build_adaptive_rules(
    research: EnvironmentResearchResult,
) -> AdaptiveEnvironmentRules:
    """Build rule tables from Stage 3C summary rows."""
    rules = AdaptiveEnvironmentRules(
        source_trades=len(research.trades),
        built_at=datetime.now().isoformat(timespec="seconds"),
    )

    score_rows: List[Dict[str, Any]] = []

    for dim in DIMENSION_KEYS:
        table_attr = DIMENSION_TO_TABLE[dim]
        rows: List[Dict[str, Any]] = getattr(research, table_attr, [])
        rules.bucket_scores[dim] = {}
        for row in rows:
            bucket = str(row.get("bucket", "unknown"))
            n = int(row.get("total_trades", 0))
            exp = float(row.get("expectancy", 0))
            pf = float(row.get("profit_factor", 0))
            rob = float(row.get("robustness_score", 0))
            wr = float(row.get("win_rate", 0))
            norm = compute_bucket_score(exp, pf, rob, n)
            if norm is None:
                continue
            label = _label_from_bucket_score(norm)
            bs = BucketScore(
                dimension=dim,
                bucket=bucket,
                total_trades=n,
                win_rate=wr,
                expectancy=exp,
                profit_factor=pf,
                robustness_score=rob,
                bucket_score=round(norm, 4),
                environment_label=label,
                weight=WEIGHT_CAP,
            )
            rules.bucket_scores.setdefault(dim, {})[bucket] = bs
            score_rows.append(
                {
                    "dimension": dim,
                    "bucket": bucket,
                    "total_trades": n,
                    "win_rate": round(wr, 4),
                    "expectancy": round(exp, 2),
                    "profit_factor": round(pf, 4),
                    "robustness_score": round(rob, 2),
                    "bucket_score": round(norm, 4),
                    "environment_label": label,
                    "included_in_rules": True,
                }
            )

    write_environment_scores_csv(score_rows)
    write_adaptive_rules_json(rules)
    return rules


def assess_environment(
    tags: Dict[str, Optional[str]],
    rules: AdaptiveEnvironmentRules,
    *,
    session_features: Optional[SessionEnvironmentFeatures] = None,
) -> EnvironmentAssessment:
    """Score current tags against historical bucket research."""
    warnings: List[str] = list(session_features.warnings) if session_features else []
    contributions: Dict[str, float] = {}
    confidences: List[float] = []
    expectancies: List[float] = []
    win_rates: List[float] = []
    weights_used = 0.0
    weighted_sum = 0.0

    tag_to_dim = {
        "time_bucket": tags.get("time_bucket"),
        "regime": tags.get("regime"),
        "premarket_trend": tags.get("premarket_trend"),
        "or_candle_quality": tags.get("or_candle_quality"),
        "relative_strength": tags.get("relative_strength"),
    }

    for dim, bucket in tag_to_dim.items():
        if not bucket:
            continue
        dim_rules = rules.bucket_scores.get(dim, {})
        bs = dim_rules.get(bucket)
        if bs is None:
            continue
        w = min(WEIGHT_CAP, bs.weight)
        contributions[dim] = round(bs.bucket_score * w, 4)
        weighted_sum += bs.bucket_score * w
        weights_used += w
        confidences.append(min(1.0, bs.total_trades / 30.0))
        expectancies.append(bs.expectancy)
        win_rates.append(bs.win_rate)

    if weights_used <= 0:
        return EnvironmentAssessment(
            environment_score=50.0,
            environment_label="NEUTRAL",
            confidence=0.0,
            historical_expectancy=0.0,
            historical_win_rate=0.0,
            recommendation="Insufficient historical sample for these tags — use standard risk controls.",
            tags=tags,
            dimension_contributions=contributions,
            session_features=session_features,
            warnings=warnings,
        )

    normalized = weighted_sum / weights_used
    environment_score = round((normalized + 1.0) * 50.0, 2)
    environment_score = _clamp(environment_score, 0.0, 100.0)

    if environment_score >= rules.favorable_threshold:
        label = "FAVORABLE"
        recommendation = (
            "Historical research supports QQQ ORB setups in this environment profile."
        )
    elif environment_score <= rules.avoid_threshold:
        label = "AVOID"
        recommendation = (
            "Historical research shows weak QQQ ORB results in this environment profile — "
            "consider skipping or reducing size."
        )
    else:
        label = "NEUTRAL"
        recommendation = (
            "Mixed historical results for this environment profile — apply standard filters and risk limits."
        )

    confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
    hist_exp = round(sum(expectancies) / len(expectancies), 2) if expectancies else 0.0
    hist_wr = round(sum(win_rates) / len(win_rates), 4) if win_rates else 0.0

    return EnvironmentAssessment(
        environment_score=environment_score,
        environment_label=label,
        confidence=confidence,
        historical_expectancy=hist_exp,
        historical_win_rate=hist_wr,
        recommendation=recommendation,
        tags=tags,
        dimension_contributions=contributions,
        session_features=session_features,
        warnings=warnings,
    )


def assess_session(
    bundle: EnvironmentMarketBundle,
    session_date: date,
    entry_tm: Optional[time],
    rules: AdaptiveEnvironmentRules,
) -> EnvironmentAssessment:
    """Calculate real session features, then score against adaptive rules."""
    features = compute_session_environment_features(bundle, session_date, entry_tm)
    tags = features.tags_for_scoring()
    return assess_environment(tags, rules, session_features=features)


def assess_entry(
    bundle: EnvironmentMarketBundle,
    session_date: date,
    entry_tm: Optional[time],
    rules: AdaptiveEnvironmentRules,
) -> EnvironmentAssessment:
    return assess_session(bundle, session_date, entry_tm, rules)


def is_favorable_entry(
    bundle: EnvironmentMarketBundle,
    session_date: date,
    entry_tm: Optional[time],
    rules: AdaptiveEnvironmentRules,
) -> bool:
    """True only when assessment label is FAVORABLE (Stage 3A optional filter)."""
    try:
        assessment = assess_session(bundle, session_date, entry_tm, rules)
        return assessment.environment_label == "FAVORABLE"
    except Exception:  # noqa: BLE001
        return False


def write_environment_scores_csv(
    rows: List[Dict[str, Any]],
    path: Path = ENVIRONMENT_SCORES_FILE,
) -> Path:
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    keys: set[str] = set()
    for row in rows:
        keys.update(row.keys())
    preferred = [
        "dimension",
        "bucket",
        "total_trades",
        "win_rate",
        "expectancy",
        "profit_factor",
        "robustness_score",
        "bucket_score",
        "environment_label",
        "included_in_rules",
    ]
    fieldnames = [k for k in preferred if k in keys] + sorted(k for k in keys if k not in preferred)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})
    return path


def write_adaptive_rules_json(
    rules: AdaptiveEnvironmentRules,
    path: Path = ADAPTIVE_RULES_FILE,
) -> Path:
    payload = {
        "warning": (
            "Rule-based research summary from past QQQ ORB trades. "
            "Not a forecast of future results. Do not auto-trade."
        ),
        **rules.to_dict(),
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


def load_adaptive_rules_from_disk(
    path: Path = ADAPTIVE_RULES_FILE,
) -> Optional[AdaptiveEnvironmentRules]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        rules = AdaptiveEnvironmentRules(
            min_sample_size=int(data.get("min_sample_size", MIN_SAMPLE_SIZE)),
            favorable_threshold=float(data.get("favorable_threshold", FAVORABLE_THRESHOLD)),
            avoid_threshold=float(data.get("avoid_threshold", AVOID_THRESHOLD)),
            source_trades=int(data.get("source_trades", 0)),
            built_at=str(data.get("built_at", "")),
        )
        raw = data.get("bucket_scores", {})
        for dim, buckets in raw.items():
            rules.bucket_scores[dim] = {}
            for bucket, sc in buckets.items():
                rules.bucket_scores[dim][bucket] = BucketScore(**sc)
        return rules
    except Exception:  # noqa: BLE001
        return None
