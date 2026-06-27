"""
Father's Hand — 5-layer decision training simulator backend.

Training only. No live trading. No real orders. No profit promises.
"""

from __future__ import annotations

import csv
import json
import random
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
SCENARIOS_FILE = PROJECT_DIR / "fathers_hand_scenarios.csv"
REPLAY_LOG_FILE = PROJECT_DIR / "fathers_hand_replay_log.csv"
CHECKLIST_LOG_FILE = PROJECT_DIR / "fathers_hand_checklist_log.csv"
COACH_REPORT_FILE = PROJECT_DIR / "fathers_hand_coach_report.csv"
SKILL_HISTORY_FILE = PROJECT_DIR / "fathers_hand_skill_history.csv"
JOURNAL_FILE = PROJECT_DIR / "fathers_hand_journal.csv"
PROGRESS_FILE = PROJECT_DIR / "fathers_hand_progress.json"

SIM_DISCLAIMER = (
    "**Training only.** This is practice, not prediction. "
    "The goal is better decisions, not guaranteed profits. "
    "No trade is a valid answer. No live orders."
)

GradeLabel = Literal[
    "Excellent",
    "Good",
    "Risky",
    "Poor",
    "Best answer was No Trade",
]

ChoiceLabel = Literal["Long", "Short", "Watch", "No Trade"]

TRADER_LEVELS = [
    (0, "Beginner"),
    (30, "Developing"),
    (50, "Disciplined"),
    (70, "Consistent"),
    (85, "Elite-in-training"),
]

SCENARIO_COLUMNS = [
    "scenario_id",
    "market",
    "asset_class",
    "date",
    "session_type",
    "timeframe",
    "setup_type",
    "higher_timeframe_trend",
    "weekly_trend",
    "monthly_trend",
    "prior_day_high",
    "prior_day_low",
    "premarket_trend",
    "first_15m_candle",
    "vwap_status",
    "relative_strength",
    "or_quality",
    "volume_status",
    "market_regime",
    "support_resistance_context",
    "or_high",
    "or_low",
    "vwap_price",
    "outcome_resolution",
    "best_choice",
    "best_direction",
    "ideal_entry",
    "ideal_stop",
    "ideal_target",
    "outcome_1030",
    "outcome_1100",
    "outcome_1200",
    "outcome_close",
    "explanation",
    "difficulty",
    "tags",
    "synthetic_training_example",
    "checklist_trend",
    "checklist_vwap",
    "checklist_relative_strength",
    "checklist_or_quality",
    "checklist_volume",
    "checklist_risk_reward",
    "checklist_market_regime",
    "checklist_trade_or_pass",
]

REPLAY_LOG_COLUMNS = [
    "timestamp",
    "user_id",
    "scenario_id",
    "market",
    "date",
    "session_type",
    "user_choice",
    "best_choice",
    "correct_direction",
    "entry",
    "stop",
    "target",
    "target2",
    "risk_amount",
    "risk_percent",
    "confidence",
    "outcome_1030",
    "outcome_1100",
    "outcome_1200",
    "outcome_close",
    "trade_outcome",
    "grade",
    "score",
    "user_note",
]

CHECKLIST_LOG_COLUMNS = [
    "timestamp",
    "user_id",
    "scenario_id",
    "checklist_score_pct",
    "trend_answer",
    "trend_correct",
    "vwap_answer",
    "vwap_correct",
    "relative_strength_answer",
    "relative_strength_correct",
    "or_quality_answer",
    "or_quality_correct",
    "volume_answer",
    "volume_correct",
    "risk_reward_answer",
    "risk_reward_correct",
    "market_regime_answer",
    "market_regime_correct",
    "trade_or_pass_answer",
    "trade_or_pass_correct",
    "missed_items",
]

COACH_REPORT_COLUMNS = [
    "timestamp",
    "user_id",
    "top_weakness",
    "second_weakness",
    "strongest_skill",
    "coach_message",
    "recommended_drill",
    "next_training_focus",
]

SKILL_HISTORY_COLUMNS = [
    "timestamp",
    "user_id",
    "chart_reading",
    "market_context",
    "structure_reading",
    "pattern_recognition",
    "risk_management",
    "trade_selection",
    "trade_management",
    "discipline",
    "overall_trader_score",
    "trader_level",
]

CHECKLIST_ITEMS = [
    ("trend", "What is the higher-timeframe trend?", ["Up", "Down", "Sideways", "Unsure"]),
    ("vwap", "Where is price compared with VWAP?", ["Above", "Below", "Crossing", "Unsure"]),
    (
        "relative_strength",
        "Is the market showing strength or weakness?",
        ["Strength", "Weakness", "Neutral", "Unsure"],
    ),
    (
        "or_quality",
        "How clean is the opening range?",
        ["Clean", "Messy", "Too large", "Too small", "Unsure"],
    ),
    ("volume", "Is volume meaningful?", ["Strong", "Normal", "Weak", "Unsure"]),
    ("risk_reward", "Is there enough reward for the risk?", ["Yes", "No", "Unsure"]),
    (
        "market_regime",
        "What is the market regime?",
        ["Trending", "Choppy", "Reversing", "Unsure"],
    ),
    ("trade_or_pass", "What should you do?", ["Long", "Short", "Watch", "No Trade"]),
]

# Maps legacy CSV answer keys to neutral checklist vocabulary
LEGACY_CHECKLIST_ALIASES: Dict[str, Dict[str, str]] = {
    "trend": {
        "uptrend": "up",
        "downtrend": "down",
        "chop / range": "sideways",
        "chop/range": "sideways",
        "range": "sideways",
    },
    "vwap": {
        "above vwap": "above",
        "below vwap": "below",
        "crossing vwap": "crossing",
        "not available": "unsure",
    },
    "relative_strength": {
        "stronger than benchmark": "strength",
        "weaker than benchmark": "weakness",
        "not available": "unsure",
    },
    "or_quality": {
        "strong bullish or": "clean",
        "strong bearish or": "clean",
        "weak or": "too small",
        "large risky or": "too large",
        "choppy or": "messy",
    },
    "volume": {"not available": "unsure"},
    "risk_reward": {"good": "yes", "poor": "no", "unclear": "unsure"},
    "market_regime": {
        "trend day": "trending",
        "gap continuation": "trending",
        "chop": "choppy",
        "mean reversion": "reversing",
        "unknown": "unsure",
    },
    "trade_or_pass": {
        "trade": "long",
        "pass": "no trade",
    },
}

MISTAKE_CATEGORIES = [
    "trend_reading",
    "vwap_reading",
    "opening_range_quality",
    "risk_reward",
    "stop_placement",
    "target_placement",
    "overtrading",
    "no_trade_discipline",
    "confidence_mismatch",
    "volume_misread",
    "regime_misread",
    "undertrading",
    "poor_journal_reasoning",
]

MARKETS = [
    ("QQQ", "stock_etf"),
    ("SPY", "stock_etf"),
    ("NQ", "futures"),
    ("XAUUSD", "commodity"),
    ("EUR/USD", "forex"),
    ("GBP/USD", "forex"),
    ("GBP/JPY", "forex"),
    ("AUD/USD", "forex"),
    ("BTC/USD", "crypto"),
    ("ETH/USD", "crypto"),
]

SETUP_TYPES = [
    "ORB long",
    "ORB short",
    "trend day up",
    "trend day down",
    "VWAP reclaim",
    "VWAP rejection",
    "fakeout",
    "no-trade chop",
    "gap and go",
    "gap fill",
]


@dataclass
class FullScenario:
    scenario_id: str
    market: str
    asset_class: str
    date: str
    session_type: str
    timeframe: str
    setup_type: str
    higher_timeframe_trend: str
    weekly_trend: str
    monthly_trend: str
    prior_day_high: str
    prior_day_low: str
    premarket_trend: str
    first_15m_candle: str
    vwap_status: str
    relative_strength: str
    or_quality: str
    volume_status: str
    market_regime: str
    support_resistance_context: str
    best_choice: str
    best_direction: str
    ideal_entry: float
    ideal_stop: float
    ideal_target: float
    outcome_1030: str
    outcome_1100: str
    outcome_1200: str
    outcome_close: str
    explanation: str
    difficulty: str
    tags: str
    or_high: float = 0.0
    or_low: float = 0.0
    vwap_price: float = 0.0
    outcome_resolution: str = ""
    synthetic_training_example: bool = True
    checklist_trend: str = ""
    checklist_vwap: str = ""
    checklist_relative_strength: str = ""
    checklist_or_quality: str = ""
    checklist_volume: str = ""
    checklist_risk_reward: str = ""
    checklist_market_regime: str = ""
    checklist_trade_or_pass: str = ""

    def to_row(self) -> Dict[str, Any]:
        d = asdict(self)
        d["synthetic_training_example"] = str(d["synthetic_training_example"]).lower()
        return d

    @classmethod
    def from_row(cls, row: Any) -> "FullScenario":
        def _f(key: str, default: str = "") -> str:
            v = row.get(key, default)
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return default
            return str(v)

        def _float(key: str, default: float = 0.0) -> float:
            try:
                v = row.get(key, default)
                if v is None or (isinstance(v, float) and pd.isna(v)):
                    return default
                return float(v)
            except (TypeError, ValueError):
                return default

        syn = str(row.get("synthetic_training_example", "true")).lower() in ("true", "1", "yes")
        return cls(
            scenario_id=_f("scenario_id", "unknown"),
            market=_f("market"),
            asset_class=_f("asset_class"),
            date=_f("date"),
            session_type=_f("session_type"),
            timeframe=_f("timeframe", "15m OR"),
            setup_type=_f("setup_type"),
            higher_timeframe_trend=_f("higher_timeframe_trend"),
            weekly_trend=_f("weekly_trend"),
            monthly_trend=_f("monthly_trend"),
            prior_day_high=_f("prior_day_high"),
            prior_day_low=_f("prior_day_low"),
            premarket_trend=_f("premarket_trend"),
            first_15m_candle=_f("first_15m_candle"),
            vwap_status=_f("vwap_status"),
            relative_strength=_f("relative_strength"),
            or_quality=_f("or_quality"),
            volume_status=_f("volume_status"),
            market_regime=_f("market_regime"),
            support_resistance_context=_f("support_resistance_context"),
            or_high=_float("or_high"),
            or_low=_float("or_low"),
            vwap_price=_float("vwap_price"),
            outcome_resolution=_f("outcome_resolution"),
            best_choice=_f("best_choice"),
            best_direction=_f("best_direction"),
            ideal_entry=_float("ideal_entry"),
            ideal_stop=_float("ideal_stop"),
            ideal_target=_float("ideal_target"),
            outcome_1030=_f("outcome_1030"),
            outcome_1100=_f("outcome_1100"),
            outcome_1200=_f("outcome_1200"),
            outcome_close=_f("outcome_close"),
            explanation=_f("explanation"),
            difficulty=_f("difficulty", "beginner"),
            tags=_f("tags"),
            synthetic_training_example=syn,
            checklist_trend=_f("checklist_trend"),
            checklist_vwap=_f("checklist_vwap"),
            checklist_relative_strength=_f("checklist_relative_strength"),
            checklist_or_quality=_f("checklist_or_quality"),
            checklist_volume=_f("checklist_volume"),
            checklist_risk_reward=_f("checklist_risk_reward"),
            checklist_market_regime=_f("checklist_market_regime"),
            checklist_trade_or_pass=_f("checklist_trade_or_pass"),
        )

    def checklist_answer_key(self) -> Dict[str, str]:
        raw = {
            "trend": self.checklist_trend or self._infer_trend(),
            "vwap": self.checklist_vwap or self._normalize_vwap_key(),
            "relative_strength": self.checklist_relative_strength or self._infer_strength(),
            "or_quality": self.checklist_or_quality or self._infer_or_quality(),
            "volume": self.checklist_volume or self._normalize_volume_key(),
            "risk_reward": self.checklist_risk_reward or self._infer_risk_reward(),
            "market_regime": self.checklist_market_regime or self._infer_regime(),
            "trade_or_pass": self.checklist_trade_or_pass or self._infer_trade_or_pass(),
        }
        return {k: _canonical_checklist_answer(k, v) for k, v in raw.items()}

    def _normalize_vwap_key(self) -> str:
        v = self.vwap_status.lower()
        if "above" in v:
            return "Above"
        if "below" in v:
            return "Below"
        if "cross" in v:
            return "Crossing"
        return "Unsure"

    def _normalize_volume_key(self) -> str:
        v = self.volume_status.lower()
        if "strong" in v:
            return "Strong"
        if "weak" in v:
            return "Weak"
        if "normal" in v:
            return "Normal"
        return "Unsure"

    def _infer_trend(self) -> str:
        t = self.higher_timeframe_trend.lower()
        if "up" in t:
            return "Up"
        if "down" in t:
            return "Down"
        if "chop" in t or "range" in t or "side" in t:
            return "Sideways"
        return "Unsure"

    def _infer_risk_reward(self) -> str:
        if self.best_choice in ("No Trade", "Watch"):
            return "Unsure"
        if self.ideal_entry and self.ideal_stop and self.ideal_target:
            risk = abs(self.ideal_entry - self.ideal_stop)
            reward = abs(self.ideal_target - self.ideal_entry)
            if risk > 0 and reward / risk >= 2.0:
                return "Yes"
            return "No"
        return "Unsure"

    def _infer_trade_or_pass(self) -> str:
        if self.best_choice == "No Trade":
            return "No Trade"
        if self.best_choice == "Watch":
            return "Watch"
        if self.best_choice == "Long":
            return "Long"
        if self.best_choice == "Short":
            return "Short"
        return "Watch"

    def _infer_strength(self) -> str:
        rs = self.relative_strength.lower()
        if "strong" in rs:
            return "Strength"
        if "weak" in rs:
            return "Weakness"
        if "neutral" in rs:
            return "Neutral"
        return "Unsure"

    def _infer_or_quality(self) -> str:
        oq = self.or_quality.lower()
        if "choppy" in oq or "messy" in oq:
            return "Messy"
        if "large" in oq or "risky" in oq:
            return "Too large"
        if "weak" in oq or "small" in oq:
            return "Too small"
        if "strong" in oq or "clean" in oq:
            return "Clean"
        return "Unsure"

    def _infer_regime(self) -> str:
        r = self.market_regime.lower()
        if "chop" in r:
            return "Choppy"
        if "revers" in r or "mean" in r:
            return "Reversing"
        if "trend" in r or "gap" in r:
            return "Trending"
        return "Unsure"


@dataclass
class SkillScores:
    chart_reading: float = 0.0
    market_context: float = 0.0
    structure_reading: float = 0.0
    pattern_recognition: float = 0.0
    risk_management: float = 0.0
    trade_selection: float = 0.0
    trade_management: float = 0.0
    discipline: float = 0.0
    overall_trader_score: float = 0.0
    trader_level: str = "Beginner"


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------


def _ensure_csv(path: Path, columns: List[str]) -> None:
    if not path.is_file():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=columns).writeheader()


def _append_csv_row(path: Path, columns: List[str], row: Dict[str, Any]) -> None:
    _ensure_csv(path, columns)
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writerow({k: row.get(k, "") for k in columns})


def _load_csv_df(path: Path, columns: List[str]) -> pd.DataFrame:
    if not path.is_file():
        return pd.DataFrame(columns=columns)
    try:
        return pd.read_csv(path)
    except Exception:  # noqa: BLE001
        return pd.DataFrame(columns=columns)


def ensure_simulator_files() -> None:
    """Create starter data files if missing."""
    _ensure_csv(REPLAY_LOG_FILE, REPLAY_LOG_COLUMNS)
    _ensure_csv(CHECKLIST_LOG_FILE, CHECKLIST_LOG_COLUMNS)
    _ensure_csv(COACH_REPORT_FILE, COACH_REPORT_COLUMNS)
    _ensure_csv(SKILL_HISTORY_FILE, SKILL_HISTORY_COLUMNS)
    try:
        import fathers_hand_modules as _mod
        _mod.ensure_module_files()
    except ImportError:  # pragma: no cover
        pass
    ensure_scenario_library(250)


# ---------------------------------------------------------------------------
# Scenario library (Layer 5)
# ---------------------------------------------------------------------------


def _base_price(market: str) -> float:
    bases = {
        "QQQ": 480.0,
        "SPY": 520.0,
        "NQ": 18500.0,
        "XAUUSD": 2350.0,
        "EUR/USD": 1.085,
        "GBP/USD": 1.265,
        "GBP/JPY": 188.5,
        "AUD/USD": 0.655,
        "BTC/USD": 65000.0,
        "ETH/USD": 3400.0,
    }
    return bases.get(market, 100.0)


def _build_synthetic_scenario(
    idx: int,
    market: str,
    asset_class: str,
    setup_type: str,
    rng: Optional[random.Random] = None,
) -> FullScenario:
    """Build one realistic synthetic training scenario."""
    r = rng if rng is not None else random
    base = _base_price(market)
    tick = base * 0.002 if base > 100 else base * 0.001
    or_size = tick * r.uniform(3, 12)
    entry = round(base + r.uniform(-or_size, or_size), 4 if base < 10 else 2)
    stop = round(entry - or_size * 0.8, 4 if base < 10 else 2)
    target = round(entry + or_size * 1.6, 4 if base < 10 else 2)

    trends = ["Uptrend", "Downtrend", "Chop / Range"]
    weekly = r.choice(trends)
    monthly = r.choice(trends)
    htf = weekly if r.random() > 0.3 else monthly

    vwap_opts = ["Above VWAP", "Below VWAP", "Crossing VWAP"]
    vwap = r.choice(vwap_opts)
    rs_opts = ["Stronger than benchmark", "Weaker than benchmark", "Neutral"]
    rs = r.choice(rs_opts)
    vol_opts = ["Strong", "Normal", "Weak"]
    vol = r.choice(vol_opts)
    or_opts = ["Clean", "Messy", "Too large", "Too small"]
    or_q = r.choice(or_opts)
    regimes = ["Trending", "Choppy", "Reversing"]
    regime = r.choice(regimes)

    best_choice: ChoiceLabel = "No Trade"
    best_dir = "None"
    outcome_resolution = "no_trade_best"
    if setup_type == "ORB long" and htf == "Uptrend" and vwap == "Above VWAP":
        best_choice, best_dir = "Long", "Long"
        outcome_resolution = "target_first"
    elif setup_type == "ORB short" and htf == "Downtrend" and vwap == "Below VWAP":
        best_choice, best_dir = "Short", "Short"
        outcome_resolution = "target_first"
    elif setup_type in ("no-trade chop",) or regime == "Choppy":
        best_choice, best_dir = "No Trade", "None"
        outcome_resolution = "no_trade_best"
    elif setup_type == "fakeout":
        best_choice, best_dir = "No Trade", "None"
        outcome_resolution = "stop_first"
    elif setup_type == "trend day up" and htf == "Uptrend":
        best_choice, best_dir = "Long", "Long"
        outcome_resolution = "target_first"
    elif setup_type == "trend day down" and htf == "Downtrend":
        best_choice, best_dir = "Short", "Short"
        outcome_resolution = "target_first"
    elif setup_type == "VWAP reclaim" and vwap == "Above VWAP":
        best_choice, best_dir = "Long", "Long"
        outcome_resolution = "target_first"
    elif setup_type == "VWAP rejection" and vwap == "Below VWAP":
        best_choice, best_dir = "Short", "Short"
        outcome_resolution = "target_first"
    elif setup_type == "gap and go" and htf == "Uptrend":
        best_choice, best_dir = "Long", "Long"
        outcome_resolution = "target_first"
    elif setup_type == "gap fill" and regime == "Reversing":
        best_choice, best_dir = "Watch", "None"
        outcome_resolution = "neither"
    else:
        best_choice = r.choice(["Long", "Short", "Watch", "No Trade"])
        best_dir = best_choice if best_choice in ("Long", "Short") else "None"
        outcome_resolution = "target_first" if best_choice in ("Long", "Short") else "no_trade_best"

    if best_choice == "Short":
        stop = round(entry + or_size * 0.8, 4 if base < 10 else 2)
        target = round(entry - or_size * 1.6, 4 if base < 10 else 2)

    session = "US RTH" if asset_class in ("stock_etf", "futures", "commodity") else (
        "London/NY overlap" if asset_class == "forex" else "24h crypto"
    )
    yr = r.randint(2023, 2025)
    mo = r.randint(1, 12)
    dy = r.randint(1, 28)

    outcome_templates = {
        "Long": [
            "Price holds above OR high and pushes toward target.",
            "Trend continues; pullback finds support at VWAP.",
            "Afternoon drift higher; closes near highs.",
            "Closes above entry; trend day reward.",
        ],
        "Short": [
            "Breakdown continues below OR low.",
            "Lower highs form; sellers stay in control.",
            "Afternoon weakness; closes near lows.",
            "Closes below entry; short plan rewarded.",
        ],
        "No Trade": [
            "Price chops inside OR range.",
            "Fake breakout then reversal back to VWAP.",
            "Sideways lunch; no clean follow-through.",
            "Closes near open; sitting out was correct.",
        ],
        "Watch": [
            "Early move fades; no clean entry yet.",
            "Pullback holds; better entry came later.",
            "Mixed action; patience helped.",
            "Closes flat; watching was reasonable.",
        ],
    }
    outs = outcome_templates.get(best_choice, outcome_templates["No Trade"])

    trade_pass = best_choice if best_choice in ("Long", "Short", "Watch", "No Trade") else "Watch"
    rr = "Yes" if best_choice in ("Long", "Short") and abs(target - entry) >= abs(entry - stop) * 2 else (
        "No" if best_choice in ("Long", "Short") else "Unsure"
    )
    or_high = round(entry + or_size / 2, 4 if base < 10 else 2)
    or_low = round(entry - or_size / 2, 4 if base < 10 else 2)
    vwap_px = round(
        or_low + or_size * 0.35 if vwap == "Above VWAP" else (
            or_high - or_size * 0.35 if vwap == "Below VWAP" else (or_high + or_low) / 2
        ),
        4 if base < 10 else 2,
    )
    strength = "Strength" if rs == "Stronger than benchmark" else (
        "Weakness" if rs == "Weaker than benchmark" else "Neutral"
    )
    trend_key = "Up" if htf == "Uptrend" else ("Down" if htf == "Downtrend" else "Sideways")
    vwap_key = "Above" if vwap == "Above VWAP" else ("Below" if vwap == "Below VWAP" else "Crossing")

    return FullScenario(
        scenario_id=f"syn_{market.lower().replace('/', '')}_{idx:04d}",
        market=market,
        asset_class=asset_class,
        date=f"{yr}-{mo:02d}-{dy:02d}",
        session_type=session,
        timeframe="15m OR",
        setup_type=setup_type,
        higher_timeframe_trend=htf,
        weekly_trend=weekly,
        monthly_trend=monthly,
        prior_day_high=str(round(entry + or_size, 4 if base < 10 else 2)),
        prior_day_low=str(round(entry - or_size, 4 if base < 10 else 2)),
        premarket_trend=r.choice(["Higher", "Lower", "Flat", "N/A"]),
        first_15m_candle=r.choice(
            [
                "Bullish body, small upper wick",
                "Bearish body, long lower wick",
                "Doji, indecision",
                "Large range, closes mid-body",
                "Gap up hold",
                "Gap down hold",
            ]
        ),
        vwap_status=vwap,
        relative_strength=rs,
        or_quality=or_q,
        volume_status=vol,
        market_regime=regime,
        support_resistance_context=f"OR high {or_high} / OR low {or_low}",
        or_high=or_high,
        or_low=or_low,
        vwap_price=vwap_px,
        outcome_resolution=outcome_resolution,
        best_choice=best_choice,
        best_direction=best_dir,
        ideal_entry=entry,
        ideal_stop=stop,
        ideal_target=target,
        outcome_1030=outs[0],
        outcome_1100=outs[1],
        outcome_1200=outs[2],
        outcome_close=outs[3],
        explanation=(
            f"Synthetic {setup_type} on {market}. Best action: {best_choice}. "
            f"This is practice data, not a live signal."
        ),
        difficulty=r.choice(["beginner", "intermediate", "advanced"]),
        tags=f"{setup_type},{market},{regime}",
        synthetic_training_example=True,
        checklist_trend=trend_key,
        checklist_vwap=vwap_key,
        checklist_relative_strength=strength,
        checklist_or_quality=or_q,
        checklist_volume=vol,
        checklist_risk_reward=rr,
        checklist_market_regime=regime,
        checklist_trade_or_pass=trade_pass,
    )


def _starter_featured_scenarios() -> List[FullScenario]:
    """Hand-crafted starter scenarios covering key patterns."""
    return [
        FullScenario(
            scenario_id="feat_qqq_orb_long",
            market="QQQ",
            asset_class="stock_etf",
            date="2024-03-15",
            session_type="US RTH",
            timeframe="15m OR",
            setup_type="ORB long",
            higher_timeframe_trend="Uptrend",
            weekly_trend="Uptrend",
            monthly_trend="Uptrend",
            prior_day_high="445.80",
            prior_day_low="441.20",
            premarket_trend="Higher",
            first_15m_candle="Bullish body, closes near high of range",
            vwap_status="Above VWAP",
            relative_strength="Stronger than benchmark",
            or_quality="Strong bullish OR",
            volume_status="Strong",
            market_regime="Trend day",
            support_resistance_context="OR high 446.50 / OR low 444.90. Prior day high 445.80.",
            best_choice="Long",
            best_direction="Long",
            ideal_entry=446.55,
            ideal_stop=444.85,
            ideal_target=449.95,
            outcome_1030="Breakout holds above OR high. Price trends toward VWAP extension.",
            outcome_1100="Pullback to OR high holds as support. Buyers step back in.",
            outcome_1200="Steady push higher. Lunch drift stays above VWAP.",
            outcome_close="Closes near highs. Long plan rewarded.",
            explanation="Aligned ORB long: trend, VWAP, RS, and volume agree.",
            difficulty="beginner",
            tags="ORB long,QQQ,trend day",
            checklist_trend="Uptrend",
            checklist_vwap="Above VWAP",
            checklist_relative_strength="Stronger than benchmark",
            checklist_or_quality="Strong bullish OR",
            checklist_volume="Strong",
            checklist_risk_reward="Good",
            checklist_market_regime="Trend day",
            checklist_trade_or_pass="Trade",
        ),
        FullScenario(
            scenario_id="feat_spy_chop",
            market="SPY",
            asset_class="stock_etf",
            date="2024-06-10",
            session_type="US RTH",
            timeframe="15m OR",
            setup_type="no-trade chop",
            higher_timeframe_trend="Chop / Range",
            weekly_trend="Chop / Range",
            monthly_trend="Uptrend",
            prior_day_high="534.10",
            prior_day_low="531.50",
            premarket_trend="Flat",
            first_15m_candle="Small doji, price stuck mid-range",
            vwap_status="Crossing VWAP",
            relative_strength="Neutral",
            or_quality="Choppy OR",
            volume_status="Weak",
            market_regime="Chop",
            support_resistance_context="Tight OR inside prior day range. No clear break.",
            best_choice="No Trade",
            best_direction="None",
            ideal_entry=532.80,
            ideal_stop=532.20,
            ideal_target=533.40,
            outcome_1030="Price whipsaws across VWAP. No follow-through.",
            outcome_1100="Range tightens further. Breakout attempts fail.",
            outcome_1200="Lunch chop continues. Volume dries up.",
            outcome_close="Closes near open. No edge for directional trade.",
            explanation="Chop + weak volume + messy OR = best answer is No Trade.",
            difficulty="beginner",
            tags="no-trade chop,SPY,chop",
            checklist_trend="Chop / Range",
            checklist_vwap="Crossing VWAP",
            checklist_relative_strength="Neutral",
            checklist_or_quality="Choppy OR",
            checklist_volume="Weak",
            checklist_risk_reward="Poor",
            checklist_market_regime="Chop",
            checklist_trade_or_pass="Pass",
        ),
        FullScenario(
            scenario_id="feat_nq_trend",
            market="NQ",
            asset_class="futures",
            date="2024-09-22",
            session_type="US RTH",
            timeframe="15m OR",
            setup_type="trend day",
            higher_timeframe_trend="Uptrend",
            weekly_trend="Uptrend",
            monthly_trend="Uptrend",
            prior_day_high="18520",
            prior_day_low="18380",
            premarket_trend="Higher",
            first_15m_candle="Strong bullish candle, minimal upper wick",
            vwap_status="Above VWAP",
            relative_strength="Stronger than benchmark",
            or_quality="Strong bullish OR",
            volume_status="Strong",
            market_regime="Trend day",
            support_resistance_context="OR breakout above prior day high.",
            best_choice="Long",
            best_direction="Long",
            ideal_entry=18545.0,
            ideal_stop=18490.0,
            ideal_target=18655.0,
            outcome_1030="Trend continuation. NQ holds above OR and prior high.",
            outcome_1100="Small pullback finds buyers at VWAP.",
            outcome_1200="New session highs. Momentum steady.",
            outcome_close="Strong trend day close. Long rewarded.",
            explanation="Trend day continuation with confirmation across timeframes.",
            difficulty="intermediate",
            tags="trend day,NQ,trend day",
            checklist_trend="Uptrend",
            checklist_vwap="Above VWAP",
            checklist_relative_strength="Stronger than benchmark",
            checklist_or_quality="Strong bullish OR",
            checklist_volume="Strong",
            checklist_risk_reward="Good",
            checklist_market_regime="Trend day",
            checklist_trade_or_pass="Trade",
        ),
        FullScenario(
            scenario_id="feat_audusd_session",
            market="AUD/USD",
            asset_class="forex",
            date="2024-11-05",
            session_type="London/NY overlap",
            timeframe="15m OR",
            setup_type="ORB long",
            higher_timeframe_trend="Uptrend",
            weekly_trend="Uptrend",
            monthly_trend="Chop / Range",
            prior_day_high="0.6585",
            prior_day_low="0.6520",
            premarket_trend="Higher",
            first_15m_candle="Bullish London open candle",
            vwap_status="Above VWAP",
            relative_strength="Stronger than benchmark",
            or_quality="Strong bullish OR",
            volume_status="Strong",
            market_regime="Gap continuation",
            support_resistance_context="London/NY overlap breakout above Asian range high.",
            best_choice="Long",
            best_direction="Long",
            ideal_entry=0.6568,
            ideal_stop=0.6552,
            ideal_target=0.6592,
            outcome_1030="AUD pushes higher on dollar weakness during overlap.",
            outcome_1100="Pullback holds above OR high.",
            outcome_1200="Trend extends into NY afternoon.",
            outcome_close="Closes near session high.",
            explanation="Forex session overlap ORB with dollar context alignment.",
            difficulty="intermediate",
            tags="ORB long,AUD/USD,gap continuation",
            checklist_trend="Uptrend",
            checklist_vwap="Above VWAP",
            checklist_relative_strength="Stronger than benchmark",
            checklist_or_quality="Strong bullish OR",
            checklist_volume="Strong",
            checklist_risk_reward="Good",
            checklist_market_regime="Gap continuation",
            checklist_trade_or_pass="Trade",
        ),
        FullScenario(
            scenario_id="feat_btc_fakeout",
            market="BTC/USD",
            asset_class="crypto",
            date="2024-12-18",
            session_type="24h crypto",
            timeframe="15m OR",
            setup_type="fakeout",
            higher_timeframe_trend="Chop / Range",
            weekly_trend="Chop / Range",
            monthly_trend="Uptrend",
            prior_day_high="68000",
            prior_day_low="65500",
            premarket_trend="Flat",
            first_15m_candle="Large wick above OR high, closes back inside range",
            vwap_status="Below VWAP",
            relative_strength="Weaker than benchmark",
            or_quality="Large risky OR",
            volume_status="Normal",
            market_regime="Chop",
            support_resistance_context="Break above OR high failed quickly. Wick trap visible.",
            best_choice="No Trade",
            best_direction="None",
            ideal_entry=67200.0,
            ideal_stop=67800.0,
            ideal_target=66200.0,
            outcome_1030="Fakeout complete. Price falls back below OR high.",
            outcome_1100="Chop resumes around VWAP.",
            outcome_1200="Range tightens. No clean direction.",
            outcome_close="Closes mid-range. Avoiding the long trap was correct.",
            explanation="Breakout fakeout in chop — No Trade protects capital.",
            difficulty="beginner",
            tags="fakeout,BTC/USD,chop",
            checklist_trend="Chop / Range",
            checklist_vwap="Below VWAP",
            checklist_relative_strength="Weaker than benchmark",
            checklist_or_quality="Large risky OR",
            checklist_volume="Normal",
            checklist_risk_reward="Poor",
            checklist_market_regime="Chop",
            checklist_trade_or_pass="Pass",
        ),
    ]


def generate_starter_scenario_library(min_count: int = 250) -> Path:
    """
    Generate synthetic scenario library.
    Default: 75 QQQ, 75 SPY, 75 NQ, 25 mixed secondary markets.
    """
    targets = {
        "QQQ": 75,
        "SPY": 75,
        "NQ": 75,
    }
    mixed_markets = [m for m, _ in MARKETS if m not in targets]
    mixed_total = max(25, min_count - sum(targets.values()))

    scenarios: List[FullScenario] = []
    idx = 0
    asset_map = {m: ac for m, ac in MARKETS}

    for market, count in targets.items():
        setups = list(SETUP_TYPES)
        rng = random.Random(hash(market) % 10000)
        rng.shuffle(setups)
        for j in range(count):
            setup = setups[j % len(setups)]
            scenarios.append(
                _build_synthetic_scenario(idx, market, asset_map[market], setup, rng=rng)
            )
            idx += 1

    per_mixed = max(1, mixed_total // len(mixed_markets))
    for market in mixed_markets:
        setups = list(SETUP_TYPES)
        rng = random.Random(hash(market) % 9999)
        for j in range(per_mixed):
            setup = setups[j % len(setups)]
            scenarios.append(
                _build_synthetic_scenario(idx, market, asset_map[market], setup, rng=rng)
            )
            idx += 1

    while len(scenarios) < min_count:
        market, asset_class = random.choice(MARKETS)
        setup = random.choice(SETUP_TYPES)
        scenarios.append(_build_synthetic_scenario(idx, market, asset_class, setup))
        idx += 1

    with SCENARIOS_FILE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SCENARIO_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for s in scenarios:
            w.writerow(s.to_row())

    _generate_candle_library(scenarios)
    return SCENARIOS_FILE


def _generate_candle_library(scenarios: List[FullScenario]) -> None:
    """Write synthetic OHLCV candles for each scenario."""
    try:
        import fathers_hand_charts as fhc
    except ImportError:  # pragma: no cover
        return
    frames = [fhc.generate_session_candles(s) for s in scenarios]
    fhc.save_candles_batch(frames)


def ensure_scenario_library(min_count: int = 250) -> None:
    """Regenerate library if below minimum scenario count."""
    if not SCENARIOS_FILE.is_file():
        generate_starter_scenario_library(min_count)
        return
    try:
        count = sum(1 for _ in SCENARIOS_FILE.open(encoding="utf-8")) - 1
    except OSError:
        count = 0
    if count < min_count:
        generate_starter_scenario_library(min_count)


def load_scenarios(
    market: Optional[str] = None,
    setup_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 50,
) -> List[FullScenario]:
    """Load a preview sample. Full library is procedural — not stored in CSV."""
    try:
        import fathers_hand_scenario_engine as _eng
        _eng.ensure_registry()
        pool = _eng.sample_scenarios(market=market, setup_type=setup_type, limit=limit * 3)
    except ImportError:  # pragma: no cover
        ensure_simulator_files()
        pool = [FullScenario.from_row(row) for _, row in pd.read_csv(SCENARIOS_FILE).iterrows()]

    if difficulty:
        pool = [s for s in pool if s.difficulty.lower() == difficulty.lower()]
    if tags:
        pool = [s for s in pool if tags.lower() in s.tags.lower()]
    return pool[:limit]


def pick_scenario(
    scenarios: Optional[List[FullScenario]] = None,
    exclude_ids: Optional[List[str]] = None,
    market: Optional[str] = None,
) -> Optional[FullScenario]:
    if scenarios:
        pool = scenarios
        if exclude_ids:
            pool = [s for s in pool if s.scenario_id not in exclude_ids]
        return random.choice(pool) if pool else None
    try:
        import fathers_hand_scenario_engine as _eng
        return _eng.pick_scenario(market=market, exclude_ids=exclude_ids)
    except ImportError:  # pragma: no cover
        pool = load_scenarios(market=market)
        if exclude_ids:
            pool = [s for s in pool if s.scenario_id not in exclude_ids]
        return random.choice(pool) if pool else None


def scenario_library_stats() -> Dict[str, Any]:
    csv_count = 0
    if SCENARIOS_FILE.is_file():
        try:
            csv_count = sum(1 for _ in SCENARIOS_FILE.open(encoding="utf-8")) - 1
        except OSError:
            csv_count = 0
    try:
        import fathers_hand_scenario_engine as _eng
        _eng.ensure_registry()
        stats = _eng.library_stats()
        stats["csv_scenarios"] = csv_count
        return stats
    except ImportError:  # pragma: no cover
        return {"total": csv_count, "by_market": {}, "by_setup": {}, "synthetic": csv_count, "csv_scenarios": csv_count}


def strongest_weakest_skills(user_id: str = "default") -> Tuple[str, str]:
    scores = compute_skill_scores(user_id)
    skill_map = {
        "Chart Reading": scores.chart_reading,
        "Market Context": scores.market_context,
        "Risk Management": scores.risk_management,
        "Trade Selection": scores.trade_selection,
        "Discipline": scores.discipline,
        "Trade Management": scores.trade_management,
    }
    if not any(v > 0 for v in skill_map.values()):
        return "Building foundation", "Chart Reading"
    strongest = max(skill_map, key=skill_map.get)
    weakest = min(skill_map, key=skill_map.get)
    return strongest, weakest


def recommended_drill(user_id: str = "default") -> str:
    report = generate_coach_report(user_id)
    return report.get("recommended_drill", "Start a new chart replay in My Edge Mode.")


# ---------------------------------------------------------------------------
# Future expansion stubs (Layer 5)
# ---------------------------------------------------------------------------


def import_historical_ohlcv(csv_path: str | Path) -> pd.DataFrame:
    """
    Import historical OHLCV CSV for future scenario generation.
    Expected columns: date, open, high, low, close, volume (optional).
    """
    path = Path(csv_path)
    if not path.is_file():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:  # noqa: BLE001
        return pd.DataFrame()


def convert_historical_to_scenarios(
    ohlcv_df: pd.DataFrame,
    market: str,
    asset_class: str = "stock_etf",
) -> List[FullScenario]:
    """
    Placeholder: convert historical OHLCV rows into training scenarios.
    Full implementation will tag ORB windows, VWAP, and outcomes from real bars.
    """
    if ohlcv_df.empty or len(ohlcv_df) < 5:
        return []
    scenarios: List[FullScenario] = []
    for i in range(min(3, len(ohlcv_df) - 1)):
        row = ohlcv_df.iloc[i]
        close = float(row.get("close", 100))
        scenarios.append(
            FullScenario(
                scenario_id=f"hist_{market}_{i}",
                market=market,
                asset_class=asset_class,
                date=str(row.get("date", date.today().isoformat())),
                session_type="US RTH",
                timeframe="15m OR",
                setup_type="ORB long",
                higher_timeframe_trend="Unsure",
                weekly_trend="Unsure",
                monthly_trend="Unsure",
                prior_day_high=str(close * 1.01),
                prior_day_low=str(close * 0.99),
                premarket_trend="N/A",
                first_15m_candle="Imported from historical data",
                vwap_status="Not available",
                relative_strength="Not available",
                or_quality="Weak OR",
                volume_status="Not available",
                market_regime="Unknown",
                support_resistance_context="Generated from OHLCV import stub",
                best_choice="Watch",
                best_direction="None",
                ideal_entry=close,
                ideal_stop=close * 0.99,
                ideal_target=close * 1.02,
                outcome_1030="Historical conversion stub",
                outcome_1100="Historical conversion stub",
                outcome_1200="Historical conversion stub",
                outcome_close="Historical conversion stub",
                explanation="Placeholder scenario from imported OHLCV.",
                difficulty="intermediate",
                tags="historical_import",
                synthetic_training_example=False,
            )
        )
    return scenarios


def tag_orb_examples(scenarios: List[FullScenario]) -> List[FullScenario]:
    """Placeholder: auto-tag ORB setup quality from scenario metadata."""
    for s in scenarios:
        if "ORB" in s.setup_type.upper() or "orb" in s.tags.lower():
            if "Strong" not in s.or_quality:
                if s.volume_status == "Strong" and s.vwap_status == "Above VWAP":
                    s.or_quality = "Strong bullish OR"
                elif s.volume_status == "Strong" and s.vwap_status == "Below VWAP":
                    s.or_quality = "Strong bearish OR"
    return scenarios


# ---------------------------------------------------------------------------
# Layer 1: Replay engine grading
# ---------------------------------------------------------------------------


def validate_trade_plan(
    user_choice: str,
    entry: float,
    stop: float,
    target1: float,
    target2: float,
    risk_amount: float,
    risk_percent: float,
    reason: str,
    max_risk_dollars: float = 500.0,
) -> Tuple[bool, List[str], Dict[str, float]]:
    """
    Validate trade plan before submit.
    Returns ok, warnings, and risk metrics.
    """
    warnings: List[str] = []
    metrics: Dict[str, float] = {
        "risk_per_unit": 0.0,
        "reward_tp1": 0.0,
        "reward_risk_ratio": 0.0,
        "planned_r": 0.0,
    }
    user = user_choice.strip()

    if user in ("Watch", "No Trade"):
        if not reason.strip():
            warnings.append("Add a reason for watching or passing.")
        return len(warnings) == 0, warnings, metrics

    if user in ("Long", "Short"):
        if entry <= 0 or stop <= 0 or target1 <= 0:
            warnings.append("Entry, stop, and take profit 1 are required for trades.")
        if user == "Long":
            if stop >= entry:
                warnings.append("Stop must be below entry on a long.")
            if target1 <= entry:
                warnings.append("Take profit 1 must be above entry on a long.")
        if user == "Short":
            if stop <= entry:
                warnings.append("Stop must be above entry on a short.")
            if target1 >= entry:
                warnings.append("Take profit 1 must be below entry on a short.")
        if target2 > 0:
            if user == "Long" and target2 <= target1:
                warnings.append("Take profit 2 should be above take profit 1 on a long.")
            if user == "Short" and target2 >= target1:
                warnings.append("Take profit 2 should be below take profit 1 on a short.")

        risk_unit = abs(entry - stop) if entry > 0 and stop > 0 else 0.0
        reward_unit = abs(target1 - entry) if entry > 0 and target1 > 0 else 0.0
        rr = reward_unit / risk_unit if risk_unit > 0 else 0.0
        metrics["risk_per_unit"] = round(risk_unit, 4)
        metrics["reward_tp1"] = round(reward_unit, 4)
        metrics["reward_risk_ratio"] = round(rr, 2)
        metrics["planned_r"] = round(rr, 2)

        if risk_unit > 0 and rr < 2.0:
            warnings.append(f"Reward:risk is {rr:.1f}:1 — aim for at least 2:1.")
        if risk_amount > max_risk_dollars:
            warnings.append(
                f"Risk amount ${risk_amount:,.2f} exceeds max risk ${max_risk_dollars:,.2f}."
            )
        if risk_percent > 2.0:
            warnings.append(f"Risk percent {risk_percent:.1f}% is high for practice sizing.")
        if not reason.strip():
            warnings.append("Add a short reason for the trade.")

    return len(warnings) == 0, warnings, metrics


def grade_replay_decision(
    scenario: FullScenario,
    user_choice: str,
    entry: float,
    stop: float,
    target: float,
    confidence: int,
    target2: float = 0.0,
    trade_outcome: Optional[Dict[str, Any]] = None,
    checklist_pct: float = 0.0,
) -> Tuple[GradeLabel, int, bool, str, Dict[str, Any]]:
    """Grade user trade decision. Returns grade, score, correct_direction, feedback, breakdown."""
    best = scenario.best_choice.strip()
    user = user_choice.strip()
    correct_dir = _choices_match(user, best)

    score = 0
    notes: List[str] = []
    breakdown: Dict[str, Any] = {
        "market_read": 0,
        "checklist_quality": 0,
        "direction": 0,
        "entry_quality": 0,
        "stop_placement": 0,
        "target_placement": 0,
        "risk_reward": 0,
        "discipline": 0,
    }

    breakdown["checklist_quality"] = int(min(15, checklist_pct * 0.15))
    score += breakdown["checklist_quality"]

    if correct_dir:
        breakdown["direction"] = 20
        score += 20
        notes.append(f"Direction call matches best answer ({best}).")
    elif best == "No Trade" and user in ("Watch", "No Trade"):
        breakdown["direction"] = 12
        score += 12
        notes.append("Partial credit: you avoided a bad trade, but No Trade was best.")
    elif best == "Watch" and user == "No Trade":
        breakdown["direction"] = 10
        score += 10
        notes.append("Close — you passed when watching was acceptable.")
    else:
        notes.append(f"Best choice was **{best}**, not {user}.")

    breakdown["market_read"] = 10 if checklist_pct >= 75 else (5 if checklist_pct >= 50 else 0)
    score += breakdown["market_read"]

    if user in ("Long", "Short"):
        if entry > 0 and stop > 0 and target > 0:
            risk = abs(entry - stop)
            reward = abs(target - entry)
            ideal_risk = abs(scenario.ideal_entry - scenario.ideal_stop)
            ideal_reward = abs(scenario.ideal_target - scenario.ideal_entry)

            if risk > 0:
                r_mult = reward / risk
                if r_mult >= 2.0:
                    breakdown["risk_reward"] = 15
                    notes.append(f"Risk/reward looks solid (~{r_mult:.1f}R).")
                elif r_mult >= 1.5:
                    breakdown["risk_reward"] = 8
                    notes.append(f"Risk/reward is acceptable (~{r_mult:.1f}R).")
                else:
                    breakdown["risk_reward"] = 3
                    notes.append(f"Risk/reward is thin (~{r_mult:.1f}R).")
                score += breakdown["risk_reward"]

            if ideal_risk > 0:
                entry_delta = abs(entry - scenario.ideal_entry) / ideal_risk
                if entry_delta <= 0.5:
                    breakdown["entry_quality"] = 10
                    notes.append("Entry is close to the ideal zone.")
                elif entry_delta <= 1.0:
                    breakdown["entry_quality"] = 5
                else:
                    notes.append("You entered late or far from the ideal entry.")
                score += breakdown["entry_quality"]

                stop_delta = abs(stop - scenario.ideal_stop) / ideal_risk
                if stop_delta <= 0.5:
                    breakdown["stop_placement"] = 8
                elif stop_delta <= 1.0:
                    breakdown["stop_placement"] = 4
                else:
                    notes.append("Stop placement differs from the ideal plan.")
                score += breakdown["stop_placement"]

                tgt_delta = abs(target - scenario.ideal_target) / max(ideal_reward, ideal_risk)
                if tgt_delta <= 0.5:
                    breakdown["target_placement"] = 7
                elif tgt_delta <= 1.0:
                    breakdown["target_placement"] = 3
                else:
                    notes.append("Target placement could be improved.")
                score += breakdown["target_placement"]
        else:
            notes.append("Fill in entry, stop, and target for trades.")
    elif user in ("Watch", "No Trade") and best in ("Watch", "No Trade"):
        breakdown["discipline"] = 20
        score += 20
        notes.append("Good discipline — no forced trade.")
    elif user in ("Watch", "No Trade"):
        breakdown["discipline"] = 10
        score += 10

    if trade_outcome:
        result = trade_outcome.get("result", "")
        if best in ("No Trade", "Watch") and user in ("Long", "Short"):
            notes.append("You traded when the best answer was to stay out.")
        elif result == "stop_first" and correct_dir:
            notes.append("Direction was right, but your stop was hit first on this path.")
        elif result == "target_first" and correct_dir:
            notes.append("Your plan would have reached target 1 before stop.")
        elif result == "neither":
            notes.append("Neither stop nor target was hit in the simulated path.")

    if 1 <= confidence <= 10:
        if correct_dir and confidence >= 6:
            score += 10
            notes.append("Confidence matches a solid read.")
        elif not correct_dir and confidence >= 8:
            score -= 10
            notes.append("High confidence on a wrong call — review checklist.")
        elif correct_dir and confidence <= 4:
            score += 5
            notes.append("Humble confidence on a good call.")
        else:
            score += 5
    else:
        notes.append("Set confidence 1–10.")

    score = max(0, min(100, score))
    grade = _score_to_grade(score, best, user)
    feedback = " ".join(notes) + f" {scenario.explanation}"
    return grade, score, correct_dir, feedback, breakdown


def _choices_match(user: str, best: str) -> bool:
    return user.strip().lower() == best.strip().lower()


def _score_to_grade(score: int, best: str, user: str) -> GradeLabel:
    if best == "No Trade" and user != "No Trade" and user != "Watch":
        return "Best answer was No Trade"
    if best == "No Trade" and user == "Watch":
        return "Good"
    if score >= 85:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 45:
        return "Risky"
    return "Poor"


def save_replay_attempt(
    scenario: FullScenario,
    user_id: str,
    user_choice: str,
    entry: float,
    stop: float,
    target: float,
    confidence: int,
    grade: GradeLabel,
    score: int,
    correct_direction: bool,
    user_note: str,
    target2: float = 0.0,
    risk_amount: float = 0.0,
    risk_percent: float = 0.0,
    trade_outcome: str = "",
) -> Path:
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "scenario_id": scenario.scenario_id,
        "market": scenario.market,
        "date": scenario.date,
        "session_type": scenario.session_type,
        "user_choice": user_choice,
        "best_choice": scenario.best_choice,
        "correct_direction": str(correct_direction).lower(),
        "entry": entry,
        "stop": stop,
        "target": target,
        "target2": target2,
        "risk_amount": risk_amount,
        "risk_percent": risk_percent,
        "confidence": confidence,
        "outcome_1030": scenario.outcome_1030,
        "outcome_1100": scenario.outcome_1100,
        "outcome_1200": scenario.outcome_1200,
        "outcome_close": scenario.outcome_close,
        "trade_outcome": trade_outcome,
        "grade": grade,
        "score": score,
        "user_note": user_note,
    }
    _append_csv_row(REPLAY_LOG_FILE, REPLAY_LOG_COLUMNS, row)
    return REPLAY_LOG_FILE


# ---------------------------------------------------------------------------
# Layer 2: Checklist grading
# ---------------------------------------------------------------------------


def grade_checklist(
    scenario: FullScenario,
    answers: Dict[str, str],
) -> Tuple[float, List[Dict[str, str]]]:
    """
    Grade checklist answers against scenario key.
    Returns score_pct and list of missed items with explanations.
    """
    key = scenario.checklist_answer_key()
    results: List[Dict[str, str]] = []
    correct = 0
    total = len(CHECKLIST_ITEMS)

    explanations = {
        "trend": "Check the higher-timeframe trend before picking a direction.",
        "vwap": "VWAP tells you if buyers or sellers control the session so far.",
        "relative_strength": "Read whether the market is showing strength or weakness.",
        "or_quality": "A clean opening range is easier to trust than a messy one.",
        "volume": "Strong volume helps confirm real moves.",
        "risk_reward": "Only trade when reward is worth the risk (aim for 2:1 or better).",
        "market_regime": "Trending, choppy, and reversing days need different plans.",
        "trade_or_pass": "No Trade is a valid and often smart choice.",
    }

    for field_key, label, _options in CHECKLIST_ITEMS:
        expected = _canonical_checklist_answer(field_key, key.get(field_key, ""))
        user_ans = _canonical_checklist_answer(field_key, answers.get(field_key, ""))
        ok = _normalize_checklist_answer(user_ans) == _normalize_checklist_answer(expected)
        if ok:
            correct += 1
        else:
            results.append(
                {
                    "item": label,
                    "your_answer": user_ans,
                    "correct_answer": expected,
                    "explanation": explanations.get(field_key, "Review this item."),
                }
            )

    pct = round(100.0 * correct / total, 1) if total else 0.0
    return pct, results


def _normalize_checklist_answer(ans: str) -> str:
    return ans.strip().lower().replace(" / ", "/").replace("  ", " ")


def _canonical_checklist_answer(field_key: str, ans: str) -> str:
    """Normalize legacy and new checklist answers to current vocabulary."""
    norm = _normalize_checklist_answer(ans)
    aliases = LEGACY_CHECKLIST_ALIASES.get(field_key, {})
    if norm in aliases:
        mapped = aliases[norm]
        return mapped.title() if mapped in ("up", "down") else mapped.replace("no trade", "No Trade").title()
    if field_key == "trade_or_pass" and norm == "trade":
        return "Long"
    return ans.strip() if ans else "Unsure"


def save_checklist_attempt(
    scenario: FullScenario,
    user_id: str,
    answers: Dict[str, str],
    score_pct: float,
    missed: List[Dict[str, str]],
) -> Path:
    key = scenario.checklist_answer_key()
    row: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "scenario_id": scenario.scenario_id,
        "checklist_score_pct": score_pct,
        "missed_items": "; ".join(m["item"] for m in missed),
    }
    for field_key, _, _ in CHECKLIST_ITEMS:
        row[f"{field_key}_answer"] = answers.get(field_key, "")
        expected = key.get(field_key, "")
        user = answers.get(field_key, "")
        row[f"{field_key}_correct"] = str(
            _normalize_checklist_answer(user) == _normalize_checklist_answer(expected)
        ).lower()
    _append_csv_row(CHECKLIST_LOG_FILE, CHECKLIST_LOG_COLUMNS, row)
    return CHECKLIST_LOG_FILE


# ---------------------------------------------------------------------------
# Layer 3: Adaptive coach
# ---------------------------------------------------------------------------


def _count_checklist_errors(df: pd.DataFrame) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    field_map = {
        "trend": "trend_correct",
        "vwap": "vwap_correct",
        "relative_strength": "relative_strength_correct",
        "or_quality": "or_quality_correct",
        "volume": "volume_correct",
        "risk_reward": "risk_reward_correct",
        "market_regime": "market_regime_correct",
        "trade_or_pass": "trade_or_pass_correct",
    }
    mistake_map = {
        "trend": "trend_reading",
        "vwap": "vwap_reading",
        "relative_strength": "opening_range_quality",
        "or_quality": "opening_range_quality",
        "volume": "volume_misread",
        "risk_reward": "risk_reward",
        "market_regime": "regime_misread",
    }
    for _, row in df.iterrows():
        for field_key, col in field_map.items():
            val = str(row.get(col, "true")).lower()
            if val == "false":
                cat = mistake_map.get(field_key, "trend_misread")
                counts[cat] = counts.get(cat, 0) + 1
    return counts


def _count_replay_errors(df: pd.DataFrame) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    if df.empty:
        return counts
    for _, row in df.iterrows():
        if str(row.get("correct_direction", "false")).lower() != "true":
            user = str(row.get("user_choice", ""))
            best = str(row.get("best_choice", ""))
            if best == "No Trade" and user in ("Long", "Short"):
                counts["overtrading"] = counts.get("overtrading", 0) + 1
                counts["no_trade_discipline"] = counts.get("no_trade_discipline", 0) + 1
            elif best in ("Long", "Short") and user in ("No Trade", "Watch"):
                counts["undertrading"] = counts.get("undertrading", 0) + 1
            else:
                counts["trend_reading"] = counts.get("trend_reading", 0) + 1
        try:
            conf = int(row.get("confidence", 5))
            if conf >= 8 and str(row.get("grade", "")) in ("Poor", "Risky", "Best answer was No Trade"):
                counts["confidence_mismatch"] = counts.get("confidence_mismatch", 0) + 1
        except (TypeError, ValueError):
            pass
    return counts


COACH_MESSAGES = {
    "trend_reading": "You are repeatedly misreading the higher-timeframe trend.",
    "vwap_reading": "You often miss VWAP context — check above vs below before deciding.",
    "opening_range_quality": "Opening range quality is tripping you up — messy ORs need patience.",
    "risk_reward": "You are taking trades without enough reward for the risk.",
    "stop_placement": "Your stops are getting hit too often — review stop placement.",
    "target_placement": "Target placement needs work — aim for realistic reward zones.",
    "volume_misread": "Volume reads need work — weak volume breakouts often fail.",
    "regime_misread": "You are mixing up trending days and choppy days.",
    "overtrading": "You keep trading chop when No Trade was best.",
    "no_trade_discipline": "Good passes are available — practice sitting out messy setups.",
    "undertrading": "You are passing on valid setups — review when rules align.",
    "confidence_mismatch": "Your confidence is high on trades that grade poorly.",
    "poor_journal_reasoning": "Journal notes are short — write why you chose each action.",
}

COACH_DRILLS = {
    "trend_reading": "Drill: 10 scenarios — label trend before every trade plan.",
    "vwap_reading": "Drill: 5 VWAP reclaim and rejection chart replays.",
    "opening_range_quality": "Drill: Classify OR quality on 10 opening range charts.",
    "risk_reward": "Drill: Build 5 trade plans with 2:1 reward:risk minimum.",
    "stop_placement": "Drill: Mark ideal stop vs your stop on 5 replays.",
    "target_placement": "Drill: Practice TP1/TP2 placement on trend day scenarios.",
    "volume_misread": "Drill: Volume checklist focus on 10 scenarios.",
    "regime_misread": "Drill: Label regime first on 10 chop vs trending charts.",
    "overtrading": "Drill: Practice 10 no-trade chop scenarios.",
    "no_trade_discipline": "Drill: Pass on 5 messy OR scenarios in a row.",
    "undertrading": "Drill: Replay 5 clean ORB setups in My Edge Mode.",
    "confidence_mismatch": "Drill: Lower confidence until checklist score is above 75%.",
    "poor_journal_reasoning": "Drill: Write 3 journal entries with full setup reasoning.",
}


def generate_session_coaching(
    scenario: FullScenario,
    result: Dict[str, Any],
) -> str:
    """Plain-language coaching for a single simulation."""
    user = str(result.get("user_choice", ""))
    best = scenario.best_choice
    grade = str(result.get("grade", ""))
    breakdown = result.get("breakdown", {})
    trade_outcome = result.get("trade_outcome", {})
    missed = result.get("checklist_missed", [])

    if best == "No Trade" and user in ("No Trade", "Watch"):
        return "Good pass. The opening range was too messy or the edge was not clear enough to trade."
    if best == "No Trade" and user in ("Long", "Short"):
        return "You traded chop. Your best decision was no trade."
    if user == best and grade in ("Excellent", "Good"):
        if trade_outcome.get("result") == "stop_first":
            return "You were right on direction, but your stop was too tight."
        return "Solid read. Your plan matched the scenario's best decision."
    if user != best and breakdown.get("direction", 0) == 0:
        missed_fields = {m.get("item", "") for m in missed}
        if any("VWAP" in x for x in missed_fields):
            return "You identified the trend correctly but ignored VWAP."
        if any("opening range" in x.lower() or "OR" in x for x in missed_fields):
            return "Good pass instinct — the opening range was too messy."
    if breakdown.get("risk_reward", 0) < 8:
        return "You entered late. The reward was no longer worth the risk."
    if breakdown.get("stop_placement", 0) < 4:
        return "You were right on direction, but your stop was too tight."
    if grade == "Best answer was No Trade":
        return "You forced a trade when sitting out was the best answer."
    return str(result.get("feedback", "Review the chart and checklist, then try another scenario."))


def generate_coach_report(user_id: str = "default") -> Dict[str, Any]:
    ensure_simulator_files()
    checklist_df = _load_csv_df(CHECKLIST_LOG_FILE, CHECKLIST_LOG_COLUMNS)
    replay_df = _load_csv_df(REPLAY_LOG_FILE, REPLAY_LOG_COLUMNS)
    journal_df = _load_csv_df(JOURNAL_FILE, ["date", "module", "scenario", "notes"])

    if not checklist_df.empty and "user_id" in checklist_df.columns:
        checklist_df = checklist_df[checklist_df["user_id"].astype(str) == user_id]
    if not replay_df.empty and "user_id" in replay_df.columns:
        replay_df = replay_df[replay_df["user_id"].astype(str) == user_id]

    errors: Dict[str, int] = {}
    for d in (_count_checklist_errors(checklist_df), _count_replay_errors(replay_df)):
        for k, v in d.items():
            errors[k] = errors.get(k, 0) + v

    if not journal_df.empty:
        short_notes = journal_df["notes"].astype(str).str.len() < 30
        if short_notes.sum() >= 3:
            errors["poor_journal_reasoning"] = int(short_notes.sum())

    if not errors:
        report = {
            "top_weakness": "none_yet",
            "second_weakness": "none_yet",
            "strongest_skill": "building_foundation",
            "coach_message": "Keep practicing. Complete replay scenarios and fill the checklist each time.",
            "recommended_drill": "Start with 5 beginner scenarios in Replay Engine.",
            "next_training_focus": "Complete first 10 replay attempts with checklist.",
        }
    else:
        sorted_errs = sorted(errors.items(), key=lambda x: x[1], reverse=True)
        top = sorted_errs[0][0]
        second = sorted_errs[1][0] if len(sorted_errs) > 1 else "none"
        strengths = [k for k, v in sorted_errs if v == 0]
        strongest = strengths[0] if strengths else "discipline_improving"

        positives = []
        if replay_df.shape[0] > 0:
            no_trade_best = replay_df[replay_df["best_choice"].astype(str) == "No Trade"]
            if not no_trade_best.empty:
                passed = no_trade_best[
                    no_trade_best["user_choice"].astype(str).isin(["No Trade", "Watch"])
                ]
                if len(passed) / len(no_trade_best) >= 0.6:
                    positives.append("Your No Trade discipline is improving.")

        coach_msg = COACH_MESSAGES.get(top, f"Focus area: {top}.")
        if positives:
            coach_msg = positives[0] + " " + coach_msg

        report = {
            "top_weakness": top,
            "second_weakness": second,
            "strongest_skill": strongest,
            "coach_message": coach_msg,
            "recommended_drill": COACH_DRILLS.get(top, "Replay 5 random scenarios."),
            "next_training_focus": top.replace("_", " "),
        }

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        **report,
    }
    _append_csv_row(COACH_REPORT_FILE, COACH_REPORT_COLUMNS, row)
    return report


def load_coach_reports(user_id: str = "default") -> pd.DataFrame:
    df = _load_csv_df(COACH_REPORT_FILE, COACH_REPORT_COLUMNS)
    if df.empty:
        return df
    return df[df["user_id"].astype(str) == user_id].sort_values("timestamp", ascending=False)


# ---------------------------------------------------------------------------
# Layer 4: Skill rating
# ---------------------------------------------------------------------------


def compute_skill_scores(user_id: str = "default") -> SkillScores:
    ensure_simulator_files()
    checklist_df = _load_csv_df(CHECKLIST_LOG_FILE, CHECKLIST_LOG_COLUMNS)
    replay_df = _load_csv_df(REPLAY_LOG_FILE, REPLAY_LOG_COLUMNS)
    progress_data: Dict[str, Any] = {}
    if PROGRESS_FILE.is_file():
        try:
            progress_data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            progress_data = {}

    if not checklist_df.empty and "user_id" in checklist_df.columns:
        checklist_df = checklist_df[checklist_df["user_id"].astype(str) == user_id]
    if not replay_df.empty and "user_id" in replay_df.columns:
        replay_df = replay_df[replay_df["user_id"].astype(str) == user_id]

    mod_inputs: Dict[str, float] = {}
    try:
        import fathers_hand_modules as _mod
        mod_inputs = _mod.compute_module_skill_inputs(user_id)
    except ImportError:  # pragma: no cover
        pass

    chart_fields = [
        "trend_correct",
        "vwap_correct",
        "relative_strength_correct",
        "or_quality_correct",
        "market_regime_correct",
    ]
    chart_base = _accuracy_from_columns(checklist_df, chart_fields)
    chart_reading = chart_base
    if mod_inputs.get("futures_read", 0) > 0:
        chart_reading = 0.7 * chart_base + 0.3 * mod_inputs["futures_read"]

    market_context = mod_inputs.get("market_context", 0.0)
    if market_context == 0 and checklist_df.shape[0] > 0:
        market_context = _accuracy_from_columns(checklist_df, ["market_regime_correct"])

    structure_reading = mod_inputs.get("structure_reading", 0.0)
    if structure_reading == 0:
        structure_reading = _accuracy_from_columns(checklist_df, ["trend_correct"])

    risk_mgmt = _accuracy_from_columns(checklist_df, ["risk_reward_correct"])
    if not replay_df.empty:
        filled = replay_df[
            (replay_df["entry"].astype(float) > 0)
            & (replay_df["stop"].astype(float) > 0)
            & (replay_df["target"].astype(float) > 0)
        ]
        if not filled.empty:
            risk_mgmt = 0.6 * risk_mgmt + 0.4 * _pct_true(filled, "correct_direction")

    trade_selection = _pct_true(replay_df, "correct_direction") if not replay_df.empty else 0.0

    pattern_base = trade_selection
    if not checklist_df.empty:
        or_acc = _accuracy_from_columns(checklist_df, ["or_quality_correct"])
        regime_acc = _accuracy_from_columns(checklist_df, ["market_regime_correct"])
        pattern_base = 0.5 * trade_selection + 0.25 * or_acc + 0.25 * regime_acc
    pattern_drill = mod_inputs.get("pattern_drill", 0.0)
    pattern_recognition = pattern_base
    if pattern_drill > 0:
        pattern_recognition = 0.55 * pattern_base + 0.45 * pattern_drill

    trade_management = mod_inputs.get("trade_management", 0.0)
    trend_day = mod_inputs.get("trend_day", 0.0)
    if trend_day > 0 and trade_management > 0:
        trade_management = 0.6 * trade_management + 0.4 * trend_day
    elif trend_day > 0:
        trade_management = trend_day * 0.5

    discipline = 0.0
    disc_parts = 0
    if not replay_df.empty:
        no_trade_rows = replay_df[replay_df["best_choice"].astype(str) == "No Trade"]
        if not no_trade_rows.empty:
            passed = no_trade_rows[
                no_trade_rows["user_choice"].astype(str).isin(["No Trade", "Watch"])
            ]
            discipline += 100.0 * len(passed) / len(no_trade_rows)
            disc_parts += 1
        checklist_complete = (
            checklist_df["checklist_score_pct"].astype(float).mean()
            if not checklist_df.empty
            else 0
        )
        if checklist_complete > 0:
            discipline += float(checklist_complete)
            disc_parts += 1
    journal_entries = int(progress_data.get("journal_entries", 0))
    if journal_entries > 0:
        discipline += min(100.0, journal_entries * 10)
        disc_parts += 1
    if not replay_df.empty:
        low_conf_bad = replay_df[
            (replay_df["confidence"].astype(float) >= 8)
            & (replay_df["grade"].astype(str).isin(["Poor", "Risky"]))
        ]
        discipline += 80 if len(low_conf_bad) == 0 else max(20, 80 - len(low_conf_bad) * 10)
        disc_parts += 1
    discipline = discipline / disc_parts if disc_parts else 15.0

    attempts = len(replay_df) + len(checklist_df)
    if attempts < 3:
        baseline = 15.0
        for name in (
            "chart_reading", "market_context", "structure_reading", "pattern_recognition",
            "risk_mgmt", "trade_selection", "trade_management", "discipline",
        ):
            if name == "risk_mgmt":
                risk_mgmt = max(risk_mgmt, baseline)
            elif name == "chart_reading":
                chart_reading = max(chart_reading, baseline)
            elif name == "market_context":
                market_context = max(market_context, baseline)
            elif name == "structure_reading":
                structure_reading = max(structure_reading, baseline)
            elif name == "pattern_recognition":
                pattern_recognition = max(pattern_recognition, baseline)
            elif name == "trade_selection":
                trade_selection = max(trade_selection, baseline)
            elif name == "trade_management":
                trade_management = max(trade_management, baseline)
            elif name == "discipline":
                discipline = max(discipline, baseline)

    try:
        import fathers_hand_modules as _mod
        weights = _mod.MASTER_SKILL_WEIGHTS
    except ImportError:  # pragma: no cover
        weights = {
            "chart_reading": 0.14,
            "market_context": 0.12,
            "structure_reading": 0.12,
            "pattern_recognition": 0.12,
            "risk_management": 0.12,
            "trade_selection": 0.14,
            "trade_management": 0.12,
            "discipline": 0.12,
        }

    overall = round(
        weights["chart_reading"] * chart_reading
        + weights["market_context"] * market_context
        + weights["structure_reading"] * structure_reading
        + weights["pattern_recognition"] * pattern_recognition
        + weights["risk_management"] * risk_mgmt
        + weights["trade_selection"] * trade_selection
        + weights["trade_management"] * trade_management
        + weights["discipline"] * discipline,
        1,
    )
    level = trader_level_from_score(overall)

    return SkillScores(
        chart_reading=round(chart_reading, 1),
        market_context=round(market_context, 1),
        structure_reading=round(structure_reading, 1),
        pattern_recognition=round(pattern_recognition, 1),
        risk_management=round(risk_mgmt, 1),
        trade_selection=round(trade_selection, 1),
        trade_management=round(trade_management, 1),
        discipline=round(discipline, 1),
        overall_trader_score=overall,
        trader_level=level,
    )


def _accuracy_from_columns(df: pd.DataFrame, columns: List[str]) -> float:
    if df.empty:
        return 0.0
    total = 0
    correct = 0
    for col in columns:
        if col not in df.columns:
            continue
        for val in df[col]:
            total += 1
            if str(val).lower() == "true":
                correct += 1
    return 100.0 * correct / total if total else 0.0


def _pct_true(df: pd.DataFrame, col: str) -> float:
    if df.empty or col not in df.columns:
        return 0.0
    total = len(df)
    correct = sum(1 for v in df[col] if str(v).lower() == "true")
    return 100.0 * correct / total if total else 0.0


def trader_level_from_score(score: float) -> str:
    level = TRADER_LEVELS[0][1]
    for threshold, name in TRADER_LEVELS:
        if score >= threshold:
            level = name
    return level


def save_skill_history(user_id: str = "default") -> SkillScores:
    scores = compute_skill_scores(user_id)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "chart_reading": scores.chart_reading,
        "market_context": scores.market_context,
        "structure_reading": scores.structure_reading,
        "pattern_recognition": scores.pattern_recognition,
        "risk_management": scores.risk_management,
        "trade_selection": scores.trade_selection,
        "trade_management": scores.trade_management,
        "discipline": scores.discipline,
        "overall_trader_score": scores.overall_trader_score,
        "trader_level": scores.trader_level,
    }
    _append_csv_row(SKILL_HISTORY_FILE, SKILL_HISTORY_COLUMNS, row)
    return scores


def load_skill_history(user_id: str = "default") -> pd.DataFrame:
    df = _load_csv_df(SKILL_HISTORY_FILE, SKILL_HISTORY_COLUMNS)
    if df.empty:
        return df
    return df[df["user_id"].astype(str) == user_id].sort_values("timestamp", ascending=False)


def export_all_logs() -> Dict[str, str]:
    """Return paths to all log files for export."""
    ensure_simulator_files()
    paths = {
        "replay_log": str(REPLAY_LOG_FILE),
        "checklist_log": str(CHECKLIST_LOG_FILE),
        "coach_report": str(COACH_REPORT_FILE),
        "skill_history": str(SKILL_HISTORY_FILE),
        "scenarios": str(SCENARIOS_FILE),
        "candles": str(PROJECT_DIR / "fathers_hand_candles.csv"),
        "game_progress": str(PROJECT_DIR / "fathers_hand_game_progress.json"),
        "badges": str(PROJECT_DIR / "fathers_hand_badges.json"),
    }
    try:
        import fathers_hand_modules as _mod
        paths.update({
            "market_context_log": str(_mod.MARKET_CONTEXT_LOG),
            "futures_context_log": str(_mod.FUTURES_CONTEXT_LOG),
            "structure_log": str(_mod.STRUCTURE_LOG),
            "pattern_log": str(_mod.PATTERN_LOG),
            "trend_day_log": str(_mod.TREND_DAY_LOG),
            "trade_mgmt_log": str(_mod.TRADE_MGMT_LOG),
        })
    except ImportError:  # pragma: no cover
        pass
    return paths
