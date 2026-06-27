"""
Father's Hand — extended training modules (Layers 0, 1.5, 2.5, 3.5, 4.5, 5.5).

Training only. No live trading. No real orders.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import pandas as pd

if TYPE_CHECKING:
    from fathers_hand_simulator import FullScenario

PROJECT_DIR = Path(__file__).resolve().parent

MARKET_CONTEXT_LOG = PROJECT_DIR / "fathers_hand_market_context_log.csv"
FUTURES_CONTEXT_LOG = PROJECT_DIR / "fathers_hand_futures_context_log.csv"
STRUCTURE_LOG = PROJECT_DIR / "fathers_hand_structure_log.csv"
PATTERN_LOG = PROJECT_DIR / "fathers_hand_pattern_log.csv"
TREND_DAY_LOG = PROJECT_DIR / "fathers_hand_trend_day_log.csv"
TRADE_MGMT_LOG = PROJECT_DIR / "fathers_hand_trade_mgmt_log.csv"

MARKET_ENVIRONMENT_OPTIONS = [
    "Trend Up",
    "Trend Down",
    "Range",
    "Chop",
    "Reversal",
    "Gap and Go",
    "Gap Fill",
    "Neutral",
]

FUTURES_STRENGTH_OPTIONS = ["Strong", "Neutral", "Weak"]
MARKET_BIAS_OPTIONS = ["Bullish", "Bearish", "Neutral"]

STRUCTURE_OPTIONS = [
    "Higher High",
    "Higher Low",
    "Lower High",
    "Lower Low",
    "Range",
]

PATTERN_OPTIONS = [
    "Flag",
    "Pennant",
    "Triangle",
    "Ascending Triangle",
    "Descending Triangle",
    "Double Top",
    "Double Bottom",
    "Head and Shoulders",
    "Support Break",
    "Resistance Break",
]

TREND_DAY_ANSWERS = ["Yes — trend day forming", "No — not a trend day", "Too early to tell"]
TRADE_MGMT_OPTIONS = ["Hold", "Scale Out", "Add", "Exit"]

MASTER_SKILL_WEIGHTS = {
    "chart_reading": 0.14,
    "market_context": 0.12,
    "structure_reading": 0.12,
    "pattern_recognition": 0.12,
    "risk_management": 0.12,
    "trade_selection": 0.14,
    "trade_management": 0.12,
    "discipline": 0.12,
}

MARKET_CONTEXT_COLUMNS = [
    "timestamp", "user_id", "scenario_id", "market", "user_answer", "correct_answer",
    "correct", "score", "market_context_score",
]
FUTURES_CONTEXT_COLUMNS = [
    "timestamp", "user_id", "scenario_id", "nq_answer", "es_answer", "bias_answer",
    "nq_correct", "es_correct", "bias_correct", "score", "futures_read_score",
]
STRUCTURE_COLUMNS = [
    "timestamp", "user_id", "scenario_id", "user_answer", "correct_answer",
    "correct", "score", "structure_score",
]
PATTERN_COLUMNS = [
    "timestamp", "user_id", "drill_id", "user_answer", "correct_answer",
    "correct", "score", "pattern_recognition_score",
]
TREND_DAY_COLUMNS = [
    "timestamp", "user_id", "scenario_id", "user_answer", "correct_answer",
    "or_break_quality", "pullback_depth", "vwap_retention", "relative_strength",
    "volume_persistence", "correct", "score", "trend_day_score",
]
TRADE_MGMT_COLUMNS = [
    "timestamp", "user_id", "scenario_id", "user_answer", "correct_answer",
    "replay_stage", "correct", "score", "trade_management_score",
]


@dataclass
class PatternDrill:
    drill_id: str
    title: str
    description: str
    correct_pattern: str
    hint: str


PATTERN_DRILLS: List[PatternDrill] = [
    PatternDrill("pat_01", "Tight consolidation", "Price drifts up in a small parallel channel after a sharp rally. Volume declines inside the channel.", "Flag", "A brief pause after a strong move."),
    PatternDrill("pat_02", "Symmetrical squeeze", "Highs get lower and lows get higher. Price coils toward a tip.", "Triangle", "Converging highs and lows."),
    PatternDrill("pat_03", "Flat top, rising lows", "Buyers keep lifting lows but sellers hold a flat ceiling.", "Ascending Triangle", "Flat resistance with rising support."),
    PatternDrill("pat_04", "Flat bottom, falling highs", "Sellers keep pressing highs lower while buyers defend one level.", "Descending Triangle", "Flat support with falling resistance."),
    PatternDrill("pat_05", "Two peaks", "Price rallies twice to nearly the same high and fails both times.", "Double Top", "Two similar highs often mean resistance."),
    PatternDrill("pat_06", "Two valleys", "Price dips twice to nearly the same low and bounces both times.", "Double Bottom", "Two similar lows often mean support."),
    PatternDrill("pat_07", "Three peaks", "A higher middle peak with two lower shoulders on each side.", "Head and Shoulders", "Classic reversal shape."),
    PatternDrill("pat_08", "Support failure", "Price breaks below a level that held multiple times. No quick reclaim.", "Support Break", "Support becomes resistance."),
    PatternDrill("pat_09", "Resistance clearance", "Price pushes through a ceiling that blocked earlier attempts. Holds above.", "Resistance Break", "Breakout through resistance."),
    PatternDrill("pat_10", "Small coil", "Very tight range after a fast move. Looks like a tiny symmetrical triangle.", "Pennant", "Short consolidation after momentum."),
]


def _ensure_csv(path: Path, columns: List[str]) -> None:
    if not path.is_file():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=columns).writeheader()


def _append_row(path: Path, columns: List[str], row: Dict[str, Any]) -> None:
    _ensure_csv(path, columns)
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writerow({k: row.get(k, "") for k in columns})


def _load_df(path: Path, columns: List[str]) -> pd.DataFrame:
    if not path.is_file():
        return pd.DataFrame(columns=columns)
    try:
        return pd.read_csv(path)
    except Exception:  # noqa: BLE001
        return pd.DataFrame(columns=columns)


def ensure_module_files() -> None:
    for path, cols in [
        (MARKET_CONTEXT_LOG, MARKET_CONTEXT_COLUMNS),
        (FUTURES_CONTEXT_LOG, FUTURES_CONTEXT_COLUMNS),
        (STRUCTURE_LOG, STRUCTURE_COLUMNS),
        (PATTERN_LOG, PATTERN_COLUMNS),
        (TREND_DAY_LOG, TREND_DAY_COLUMNS),
        (TRADE_MGMT_LOG, TRADE_MGMT_COLUMNS),
    ]:
        _ensure_csv(path, cols)


def _norm(s: str) -> str:
    return s.strip().lower()


# ---------------------------------------------------------------------------
# Answer key inference from scenarios
# ---------------------------------------------------------------------------


def infer_market_environment(scenario: "FullScenario") -> str:
    regime = _norm(scenario.market_regime)
    setup = _norm(scenario.setup_type)
    trend = _norm(scenario.higher_timeframe_trend)
    if "gap" in setup or regime == "gap continuation":
        return "Gap and Go"
    if setup in ("mean reversion",) or "fill" in setup:
        return "Gap Fill"
    if setup in ("fakeout", "vwap rejection", "liquidity sweep"):
        return "Reversal"
    if regime == "chop" or setup == "no-trade chop":
        return "Chop"
    if "range" in trend or regime == "mean reversion":
        return "Range"
    if trend == "uptrend" and regime == "trend day":
        return "Trend Up"
    if trend == "downtrend" and regime == "trend day":
        return "Trend Down"
    if trend == "uptrend":
        return "Trend Up"
    if trend == "downtrend":
        return "Trend Down"
    return "Neutral"


def infer_nq_strength(scenario: "FullScenario") -> str:
    rs = _norm(scenario.relative_strength)
    mkt = scenario.market.upper()
    if mkt in ("NQ", "QQQ"):
        if "strong" in rs:
            return "Strong"
        if "weak" in rs:
            return "Weak"
    if scenario.higher_timeframe_trend == "Uptrend" and scenario.vwap_status == "Above VWAP":
        return "Strong"
    if scenario.higher_timeframe_trend == "Downtrend" and scenario.vwap_status == "Below VWAP":
        return "Weak"
    return "Neutral"


def infer_es_strength(scenario: "FullScenario") -> str:
    mkt = scenario.market.upper()
    if mkt == "SPY":
        rs = _norm(scenario.relative_strength)
        if "strong" in rs:
            return "Strong"
        if "weak" in rs:
            return "Weak"
    if scenario.higher_timeframe_trend == "Uptrend":
        return "Strong"
    if scenario.higher_timeframe_trend == "Downtrend":
        return "Weak"
    return "Neutral"


def infer_market_bias(scenario: "FullScenario") -> str:
    t = scenario.higher_timeframe_trend
    if t == "Uptrend":
        return "Bullish"
    if t == "Downtrend":
        return "Bearish"
    return "Neutral"


def infer_market_structure(scenario: "FullScenario") -> str:
    trend = scenario.higher_timeframe_trend
    regime = _norm(scenario.market_regime)
    candle = _norm(scenario.first_15m_candle)
    if regime in ("chop", "mean reversion") or trend == "Chop / Range":
        return "Range"
    if trend == "Uptrend":
        return "Higher High" if "high" in candle or "bull" in candle else "Higher Low"
    if trend == "Downtrend":
        return "Lower Low" if "low" in candle or "bear" in candle else "Lower High"
    return "Range"


def infer_pattern_for_scenario(scenario: "FullScenario") -> str:
    setup = _norm(scenario.setup_type)
    tags = _norm(scenario.tags)
    mapping = {
        "orb long": "Resistance Break",
        "orb short": "Support Break",
        "fakeout": "Double Top",
        "trend day": "Flag",
        "vwap reclaim": "Ascending Triangle",
        "vwap rejection": "Descending Triangle",
        "liquidity sweep": "Head and Shoulders",
        "gap continuation": "Resistance Break",
        "mean reversion": "Double Bottom",
        "no-trade chop": "Triangle",
    }
    for key, pat in mapping.items():
        if key in setup or key.replace(" ", "") in tags.replace(" ", ""):
            return pat
    idx = sum(ord(c) for c in scenario.scenario_id) % len(PATTERN_OPTIONS)
    return PATTERN_OPTIONS[idx]


def infer_trend_day_answer(scenario: "FullScenario") -> str:
    if _norm(scenario.market_regime) == "trend day":
        return "Yes — trend day forming"
    if scenario.market_regime == "Chop":
        return "No — not a trend day"
    return "Too early to tell"


def infer_trade_management(scenario: "FullScenario", stage: str = "1100") -> str:
    """Best management action after entry based on scenario context."""
    if scenario.best_choice in ("No Trade", "Watch"):
        return "Exit"
    regime = _norm(scenario.market_regime)
    setup = _norm(scenario.setup_type)
    if setup in ("fakeout", "mean reversion", "no-trade chop"):
        return "Exit"
    if regime == "trend day" and scenario.best_choice in ("Long", "Short"):
        if stage == "1030":
            return "Hold"
        if stage == "1200":
            return "Scale Out"
        return "Hold"
    if regime == "chop":
        return "Exit"
    return "Hold"


def trend_day_factor_key(scenario: "FullScenario") -> Dict[str, str]:
    or_q = _norm(scenario.or_quality)
    vol = _norm(scenario.volume_status)
    vwap = scenario.vwap_status
    rs = scenario.relative_strength
    return {
        "or_break_quality": "Strong" if "strong" in or_q else ("Weak" if "weak" in or_q or "choppy" in or_q else "Mixed"),
        "pullback_depth": "Shallow" if scenario.best_choice in ("Long", "Short") else "Deep",
        "vwap_retention": "Holding" if vwap in ("Above VWAP", "Below VWAP") else "Lost",
        "relative_strength": rs if rs else "Neutral",
        "volume_persistence": "Strong" if "strong" in vol else ("Weak" if "weak" in vol else "Normal"),
    }


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------


def grade_market_environment(scenario: "FullScenario", user_answer: str) -> Tuple[bool, int, str]:
    correct_answer = infer_market_environment(scenario)
    ok = _norm(user_answer) == _norm(correct_answer)
    score = 100 if ok else (50 if _partial_day_type_match(user_answer, correct_answer) else 0)
    feedback = (
        f"Correct — this day type is **{correct_answer}**."
        if ok
        else f"Answer key: **{correct_answer}**. You chose {user_answer}. Read trend, gap, and chop clues."
    )
    return ok, score, feedback


def _partial_day_type_match(user: str, correct: str) -> bool:
    pairs = [
        ({"trend up", "gap and go"}, "bullish"),
        ({"trend down", "reversal"}, "bearish"),
        ({"chop", "range", "neutral"}, "sideways"),
    ]
    u = _norm(user)
    c = _norm(correct)
    for group, _ in pairs:
        if u in group and c in group:
            return True
    return False


def grade_futures_context(
    scenario: "FullScenario",
    nq_answer: str,
    es_answer: str,
    bias_answer: str,
) -> Tuple[int, Dict[str, bool], str]:
    nq_ok = _norm(nq_answer) == _norm(infer_nq_strength(scenario))
    es_ok = _norm(es_answer) == _norm(infer_es_strength(scenario))
    bias_ok = _norm(bias_answer) == _norm(infer_market_bias(scenario))
    score = round(100.0 * (int(nq_ok) + int(es_ok) + int(bias_ok)) / 3)
    feedback = (
        f"NQ: {'✓' if nq_ok else infer_nq_strength(scenario)} · "
        f"ES: {'✓' if es_ok else infer_es_strength(scenario)} · "
        f"Bias: {'✓' if bias_ok else infer_market_bias(scenario)}"
    )
    return score, {"nq": nq_ok, "es": es_ok, "bias": bias_ok}, feedback


def grade_market_structure(scenario: "FullScenario", user_answer: str) -> Tuple[bool, int, str]:
    correct = infer_market_structure(scenario)
    # Stabilize: use deterministic pick from scenario id
    trend = scenario.higher_timeframe_trend
    regime = _norm(scenario.market_regime)
    if regime in ("chop", "mean reversion") or trend == "Chop / Range":
        correct = "Range"
    elif trend == "Uptrend":
        correct = "Higher High" if "high" in _norm(scenario.first_15m_candle) else "Higher Low"
    elif trend == "Downtrend":
        correct = "Lower Low" if "low" in _norm(scenario.first_15m_candle) else "Lower High"
    ok = _norm(user_answer) == _norm(correct)
    score = 100 if ok else (40 if user_answer == "Range" and correct != "Range" else 0)
    return ok, score, f"Structure read: **{correct}**. {scenario.support_resistance_context[:80]}"


def pick_pattern_drill() -> PatternDrill:
    return random.choice(PATTERN_DRILLS)  # noqa: S311


def grade_pattern(drill: PatternDrill, user_answer: str) -> Tuple[bool, int, str]:
    ok = _norm(user_answer) == _norm(drill.correct_pattern)
    score = 100 if ok else 0
    feedback = drill.hint if ok else f"Correct pattern: **{drill.correct_pattern}**. {drill.hint}"
    return ok, score, feedback


def grade_trend_day(scenario: "FullScenario", user_answer: str) -> Tuple[bool, int, str, Dict[str, str]]:
    correct = infer_trend_day_answer(scenario)
    ok = _norm(user_answer) == _norm(correct)
    partial = (
        ok
        or (_norm(correct).startswith("yes") and "yes" in _norm(user_answer))
        or (_norm(correct).startswith("no") and "no" in _norm(user_answer))
    )
    score = 100 if ok else (60 if partial else 0)
    factors = trend_day_factor_key(scenario)
    feedback = (
        f"Trend day call: **{correct}**. "
        f"OR: {factors['or_break_quality']} · VWAP: {factors['vwap_retention']} · "
        f"Volume: {factors['volume_persistence']}"
    )
    return ok, score, feedback, factors


def grade_trade_management(
    scenario: "FullScenario",
    user_answer: str,
    stage: str = "1100",
) -> Tuple[bool, int, str]:
    correct = infer_trade_management(scenario, stage)
    ok = _norm(user_answer) == _norm(correct)
    score = 100 if ok else (50 if user_answer in ("Hold", "Scale Out") and correct in ("Hold", "Scale Out") else 0)
    feedback = (
        f"At {stage}, best action was **{correct}**. "
        f"{scenario.outcome_1100 if stage == '1100' else scenario.outcome_1030}"
    )
    return ok, score, feedback


# ---------------------------------------------------------------------------
# Save logs
# ---------------------------------------------------------------------------


def save_market_context(
    scenario: "FullScenario", user_id: str, user_answer: str, ok: bool, score: int,
) -> None:
    correct = infer_market_environment(scenario)
    _append_row(MARKET_CONTEXT_LOG, MARKET_CONTEXT_COLUMNS, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "scenario_id": scenario.scenario_id,
        "market": scenario.market,
        "user_answer": user_answer,
        "correct_answer": correct,
        "correct": str(ok).lower(),
        "score": score,
        "market_context_score": score,
    })


def save_futures_context(
    scenario: "FullScenario", user_id: str,
    nq: str, es: str, bias: str, score: int, flags: Dict[str, bool],
) -> None:
    _append_row(FUTURES_CONTEXT_LOG, FUTURES_CONTEXT_COLUMNS, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "scenario_id": scenario.scenario_id,
        "nq_answer": nq,
        "es_answer": es,
        "bias_answer": bias,
        "nq_correct": str(flags.get("nq", False)).lower(),
        "es_correct": str(flags.get("es", False)).lower(),
        "bias_correct": str(flags.get("bias", False)).lower(),
        "score": score,
        "futures_read_score": score,
    })


def save_structure(
    scenario: "FullScenario", user_id: str, user_answer: str, ok: bool, score: int,
) -> None:
    trend = scenario.higher_timeframe_trend
    regime = _norm(scenario.market_regime)
    if regime in ("chop", "mean reversion") or trend == "Chop / Range":
        correct = "Range"
    elif trend == "Uptrend":
        correct = "Higher High" if "high" in _norm(scenario.first_15m_candle) else "Higher Low"
    elif trend == "Downtrend":
        correct = "Lower Low" if "low" in _norm(scenario.first_15m_candle) else "Lower High"
    else:
        correct = "Range"
    _append_row(STRUCTURE_LOG, STRUCTURE_COLUMNS, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "scenario_id": scenario.scenario_id,
        "user_answer": user_answer,
        "correct_answer": correct,
        "correct": str(ok).lower(),
        "score": score,
        "structure_score": score,
    })


def save_pattern(drill: PatternDrill, user_id: str, user_answer: str, ok: bool, score: int) -> None:
    _append_row(PATTERN_LOG, PATTERN_COLUMNS, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "drill_id": drill.drill_id,
        "user_answer": user_answer,
        "correct_answer": drill.correct_pattern,
        "correct": str(ok).lower(),
        "score": score,
        "pattern_recognition_score": score,
    })


def save_trend_day(
    scenario: "FullScenario", user_id: str, user_answer: str,
    ok: bool, score: int, factors: Dict[str, str],
) -> None:
    _append_row(TREND_DAY_LOG, TREND_DAY_COLUMNS, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "scenario_id": scenario.scenario_id,
        "user_answer": user_answer,
        "correct_answer": infer_trend_day_answer(scenario),
        "or_break_quality": factors.get("or_break_quality", ""),
        "pullback_depth": factors.get("pullback_depth", ""),
        "vwap_retention": factors.get("vwap_retention", ""),
        "relative_strength": factors.get("relative_strength", ""),
        "volume_persistence": factors.get("volume_persistence", ""),
        "correct": str(ok).lower(),
        "score": score,
        "trend_day_score": score,
    })


def save_trade_management(
    scenario: "FullScenario", user_id: str, user_answer: str,
    ok: bool, score: int, stage: str = "1100",
) -> None:
    _append_row(TRADE_MGMT_LOG, TRADE_MGMT_COLUMNS, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "scenario_id": scenario.scenario_id,
        "user_answer": user_answer,
        "correct_answer": infer_trade_management(scenario, stage),
        "replay_stage": stage,
        "correct": str(ok).lower(),
        "score": score,
        "trade_management_score": score,
    })


# ---------------------------------------------------------------------------
# Aggregate scores for master skills
# ---------------------------------------------------------------------------


def _avg_score_col(df: pd.DataFrame, col: str = "score") -> float:
    if df.empty or col not in df.columns:
        return 0.0
    try:
        return float(df[col].astype(float).mean())
    except (TypeError, ValueError):
        return 0.0


def _pct_correct(df: pd.DataFrame) -> float:
    if df.empty or "correct" not in df.columns:
        return 0.0
    total = len(df)
    correct = sum(1 for v in df["correct"] if str(v).lower() == "true")
    return 100.0 * correct / total if total else 0.0


def compute_module_skill_inputs(user_id: str = "default") -> Dict[str, float]:
    """Average scores from module logs for master skill blending."""
    ensure_module_files()
    mc = _load_df(MARKET_CONTEXT_LOG, MARKET_CONTEXT_COLUMNS)
    fc = _load_df(FUTURES_CONTEXT_LOG, FUTURES_CONTEXT_COLUMNS)
    st_df = _load_df(STRUCTURE_LOG, STRUCTURE_COLUMNS)
    pat = _load_df(PATTERN_LOG, PATTERN_COLUMNS)
    td = _load_df(TREND_DAY_LOG, TREND_DAY_COLUMNS)
    tm = _load_df(TRADE_MGMT_LOG, TRADE_MGMT_COLUMNS)

    def _user_df(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "user_id" not in df.columns:
            return df
        return df[df["user_id"].astype(str) == user_id]

    mc, fc, st_df, pat, td, tm = (
        _user_df(mc), _user_df(fc), _user_df(st_df), _user_df(pat), _user_df(td), _user_df(tm),
    )

    return {
        "market_context": _avg_score_col(mc) or _pct_correct(mc),
        "futures_read": _avg_score_col(fc) or _pct_correct(fc),
        "structure_reading": _avg_score_col(st_df) or _pct_correct(st_df),
        "pattern_drill": _avg_score_col(pat) or _pct_correct(pat),
        "trend_day": _avg_score_col(td) or _pct_correct(td),
        "trade_management": _avg_score_col(tm) or _pct_correct(tm),
    }
