"""
Stage 3E / 3F — Live trade scoring and rule-based blocking.

Combines environment score (Stage 3D) with setup quality. Research / paper only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from risk import Direction

TRADE_LABEL_AVOID = "AVOID"
TRADE_LABEL_WATCH = "WATCH"
TRADE_LABEL_ALLOWED = "TRADE ALLOWED"
TRADE_LABEL_HIGH = "HIGH CONVICTION"
BLOCK_DECISION = "NO TRADE"
ALLOW_DECISION = "TRADE ALLOWED"


@dataclass
class TradeBlockThresholds:
    min_environment_score: float = 45.0
    min_trade_score: float = 60.0
    min_rvol: float = 1.0
    max_or_size: float = 8.0


@dataclass
class LiveTradeScoreInput:
    environment_score: float = 50.0
    environment_label: str = "NEUTRAL"
    vwap_aligned: bool = False
    spy_confirmed: bool = False
    volume_confirmed: bool = False
    session_rvol: Optional[float] = None
    or_candle_quality: Optional[str] = None
    relative_strength: Optional[str] = None
    time_bucket: Optional[str] = None
    stop_distance: float = 0.0
    or_size: float = 0.0
    direction: Direction = "None"
    r_multiple: float = 0.0


@dataclass
class LiveTradeScoreResult:
    trade_score: float = 0.0
    label: str = TRADE_LABEL_AVOID
    reasons: List[str] = field(default_factory=list)
    risk_warnings: List[str] = field(default_factory=list)
    blocked: bool = True
    block_decision: str = BLOCK_DECISION
    component_scores: Dict[str, float] = field(default_factory=dict)


def _or_quality_points(quality: Optional[str]) -> float:
    if not quality:
        return 3.0
    q = quality.lower()
    if "strong_body" in q and "bullish" in q:
        return 10.0
    if "strong_body" in q and "bearish" in q:
        return 10.0
    if "moderate_body" in q:
        return 7.0
    if "weak_body" in q:
        return 3.0
    if q in ("bullish", "bearish"):
        return 6.0
    return 4.0


def _relative_strength_points(strength: Optional[str]) -> float:
    if not strength:
        return 4.0
    s = strength.lower()
    if "stronger" in s:
        return 10.0
    if "weaker" in s:
        return 3.0
    return 5.0


def _time_bucket_points(bucket: Optional[str]) -> float:
    if not bucket:
        return 4.0
    scores = {
        "9:45-10:00": 10.0,
        "10:00-10:30": 9.0,
        "10:30-11:00": 7.0,
        "11:00-12:00": 5.0,
        "9:30-9:45": 6.0,
    }
    return scores.get(bucket, 3.0)


def _stop_or_points(stop_distance: float, or_size: float) -> float:
    if or_size <= 0 or stop_distance <= 0:
        return 3.0
    ratio = stop_distance / or_size
    if 0.5 <= ratio <= 1.25:
        return 8.0
    if ratio < 0.5:
        return 4.0
    if ratio <= 1.5:
        return 6.0
    return 3.0


def compute_live_trade_score(inp: LiveTradeScoreInput) -> LiveTradeScoreResult:
    """Rule-based trade score 0–100 from environment + setup factors."""
    reasons: List[str] = []
    warnings: List[str] = []
    components: Dict[str, float] = {}

    env_pts = max(0.0, min(25.0, inp.environment_score * 0.25))
    components["environment"] = round(env_pts, 1)
    reasons.append(f"Environment score {inp.environment_score:.0f} ({inp.environment_label}) → {env_pts:.0f}/25")

    vwap_pts = 12.0 if inp.vwap_aligned else 0.0
    components["vwap"] = vwap_pts
    reasons.append(f"VWAP {'aligned' if inp.vwap_aligned else 'not aligned'} → {vwap_pts:.0f}/12")

    spy_pts = 12.0 if inp.spy_confirmed else 0.0
    components["spy"] = spy_pts
    reasons.append(f"SPY {'confirmed' if inp.spy_confirmed else 'not confirmed'} → {spy_pts:.0f}/12")

    vol_pts = 0.0
    if inp.volume_confirmed:
        vol_pts = 8.0
        if inp.session_rvol is not None and inp.session_rvol >= 1.5:
            vol_pts = 11.0
        elif inp.session_rvol is not None and inp.session_rvol >= 1.25:
            vol_pts = 10.0
    components["volume_rvol"] = vol_pts
    rvol_note = f" (RVOL {inp.session_rvol:.2f})" if inp.session_rvol is not None else ""
    reasons.append(f"Volume/RVOL{' confirmed' if inp.volume_confirmed else ' not confirmed'}{rvol_note} → {vol_pts:.0f}/11")

    or_pts = _or_quality_points(inp.or_candle_quality)
    components["or_quality"] = or_pts
    reasons.append(f"OR quality `{inp.or_candle_quality or 'unknown'}` → {or_pts:.0f}/10")

    rs_pts = _relative_strength_points(inp.relative_strength)
    components["relative_strength"] = rs_pts
    reasons.append(f"QQQ vs SPY `{inp.relative_strength or 'unknown'}` → {rs_pts:.0f}/10")

    tb_pts = _time_bucket_points(inp.time_bucket)
    components["time_bucket"] = tb_pts
    reasons.append(f"Entry bucket `{inp.time_bucket or 'unknown'}` → {tb_pts:.0f}/10")

    so_pts = _stop_or_points(inp.stop_distance, inp.or_size)
    components["stop_or"] = so_pts
    reasons.append(f"Stop/OR geometry → {so_pts:.0f}/8")

    raw = env_pts + vwap_pts + spy_pts + vol_pts + or_pts + rs_pts + tb_pts + so_pts
    trade_score = round(max(0.0, min(100.0, raw)), 1)

    if inp.direction == "None":
        warnings.append("Direction is None — cannot score a live entry.")
    if inp.r_multiple < 1.5:
        warnings.append(f"R multiple {inp.r_multiple:.2f} is below 1.5.")
    if inp.environment_label == "AVOID":
        warnings.append("Stage 3D environment label is AVOID.")
    if inp.or_size > 0 and inp.stop_distance > inp.or_size * 1.5:
        warnings.append("Stop distance is wide relative to OR size.")

    label = TRADE_LABEL_AVOID
    if trade_score >= 80 and inp.environment_score >= 55 and not warnings:
        label = TRADE_LABEL_HIGH
    elif trade_score >= 68:
        label = TRADE_LABEL_ALLOWED
    elif trade_score >= 50:
        label = TRADE_LABEL_WATCH

    return LiveTradeScoreResult(
        trade_score=trade_score,
        label=label,
        reasons=reasons,
        risk_warnings=warnings,
        blocked=True,
        block_decision=BLOCK_DECISION,
        component_scores=components,
    )


def apply_trade_blocking(
    score_result: LiveTradeScoreResult,
    inp: LiveTradeScoreInput,
    thresholds: TradeBlockThresholds,
) -> LiveTradeScoreResult:
    """Stage 3F — apply threshold gates; does not send orders."""
    block_reasons: List[str] = list(score_result.risk_warnings)

    if inp.environment_score < thresholds.min_environment_score:
        block_reasons.append(
            f"Environment score {inp.environment_score:.1f} < minimum {thresholds.min_environment_score:.1f}"
        )
    if score_result.trade_score < thresholds.min_trade_score:
        block_reasons.append(
            f"Trade score {score_result.trade_score:.1f} < minimum {thresholds.min_trade_score:.1f}"
        )
    if thresholds.min_rvol > 0:
        if inp.session_rvol is not None and inp.session_rvol < thresholds.min_rvol:
            block_reasons.append(
                f"RVOL {inp.session_rvol:.2f} < minimum {thresholds.min_rvol:.2f}"
            )
        elif inp.session_rvol is None:
            score_result.risk_warnings = list(score_result.risk_warnings)
            score_result.risk_warnings.append(
                f"RVOL not available — enable override or use Live/backtest RVOL (min {thresholds.min_rvol:.2f})."
            )
    if inp.or_size > thresholds.max_or_size:
        block_reasons.append(f"OR size {inp.or_size:.2f} > maximum {thresholds.max_or_size:.2f}")
    if inp.direction == "None":
        block_reasons.append("Direction must be Long or Short.")
    if inp.r_multiple < 1.5:
        block_reasons.append("R multiple below 1.5.")

    blocked = len(block_reasons) > 0
    if blocked:
        score_result.blocked = True
        score_result.block_decision = BLOCK_DECISION
        score_result.label = TRADE_LABEL_AVOID
        score_result.risk_warnings = block_reasons
    else:
        score_result.blocked = False
        score_result.block_decision = ALLOW_DECISION
        if score_result.label == TRADE_LABEL_AVOID and score_result.trade_score >= thresholds.min_trade_score:
            score_result.label = TRADE_LABEL_ALLOWED

    return score_result


def build_score_input_from_context(
    *,
    environment_score: float,
    environment_label: str,
    vwap_aligned: bool,
    spy_confirmed: bool,
    volume_confirmed: bool,
    session_rvol: Optional[float],
    or_candle_quality: Optional[str],
    relative_strength: Optional[str],
    time_bucket: Optional[str],
    entry: float,
    stop: float,
    or_size: float,
    direction: Direction,
    r_multiple: float,
) -> LiveTradeScoreInput:
    stop_dist = abs(entry - stop) if direction != "None" else 0.0
    return LiveTradeScoreInput(
        environment_score=environment_score,
        environment_label=environment_label,
        vwap_aligned=vwap_aligned,
        spy_confirmed=spy_confirmed,
        volume_confirmed=volume_confirmed,
        session_rvol=session_rvol,
        or_candle_quality=or_candle_quality,
        relative_strength=relative_strength,
        time_bucket=time_bucket,
        stop_distance=stop_dist,
        or_size=or_size,
        direction=direction,
        r_multiple=r_multiple,
    )
