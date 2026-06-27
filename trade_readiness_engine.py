"""
Trade Readiness Simulator — backend engine.

Training only. No live trading. No real orders. No profit promises.
"""

from __future__ import annotations

import csv
import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
SCENARIOS_FILE = PROJECT_DIR / "trade_readiness_scenarios.csv"
JOURNAL_FILE = PROJECT_DIR / "trade_readiness_journal.csv"
PROGRESS_FILE = PROJECT_DIR / "trade_readiness_progress.json"

DISCLAIMER = (
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

TRADER_LEVELS = [
    (0, "Beginner"),
    (30, "Developing"),
    (50, "Disciplined"),
    (70, "Consistent"),
    (85, "Elite-in-training"),
]

MARKETS = [
    "QQQ",
    "SPY",
    "NVDA",
    "TSLA",
    "AAPL",
    "AUD/USD",
    "EUR/USD",
    "GBP/USD",
    "BTC/USD",
    "ETH/USD",
]

SCENARIO_COLUMNS = [
    "scenario_id",
    "market",
    "date",
    "time",
    "weekly_trend",
    "monthly_trend",
    "opening_15m_candle",
    "vwap_status",
    "volume_rvol",
    "support_resistance",
    "market_condition_summary",
    "best_choice",
    "ideal_entry",
    "ideal_stop",
    "ideal_target",
    "outcome_1030",
    "outcome_1100",
    "outcome_1200",
    "outcome_close",
    "explanation",
    "checklist_trend",
    "checklist_vwap",
    "checklist_volume",
    "checklist_regime",
    "checklist_relative_strength",
]

JOURNAL_COLUMNS = [
    "timestamp",
    "scenario_id",
    "market",
    "trade_choice",
    "entry",
    "stop",
    "target",
    "confidence",
    "notes",
    "grade",
    "score",
    "simulated_pnl",
    "simulated_r",
    "account_balance_after",
    "checklist_completion_pct",
]

CHECKLIST_ITEMS = [
    ("market", "What market am I trading?", None),
    ("trend", "What is the higher-timeframe trend?", ["Uptrend", "Downtrend", "Chop / Range", "Unsure"]),
    ("vwap", "Is price above or below VWAP?", ["Above VWAP", "Below VWAP", "Crossing VWAP", "Not sure"]),
    ("opening_candle", "What did the opening 15-minute candle show?", None),
    ("volume", "Is volume strong?", ["Yes — strong", "Normal", "No — weak", "Not sure"]),
    ("regime", "Is the market trending or chopping?", ["Trending", "Chopping", "Mixed", "Not sure"]),
    ("relative_strength", "Is there relative strength or weakness?", ["Stronger", "Weaker", "Neutral", "Not sure"]),
    ("entry_plan", "Where is the entry?", None),
    ("stop_plan", "Where is the stop?", None),
    ("target_plan", "Where is the target?", None),
    ("risk_reward", "Is the reward worth the risk?", ["Yes", "No", "Unclear"]),
    ("final_decision", "Should I trade, watch, or pass?", ["Trade (Long/Short)", "Watch", "Pass (No Trade)"]),
]


@dataclass
class TradeScenario:
    scenario_id: str
    market: str
    date: str
    time: str
    weekly_trend: str
    monthly_trend: str
    opening_15m_candle: str
    vwap_status: str
    volume_rvol: str
    support_resistance: str
    market_condition_summary: str
    best_choice: str
    ideal_entry: float
    ideal_stop: float
    ideal_target: float
    outcome_1030: str
    outcome_1100: str
    outcome_1200: str
    outcome_close: str
    explanation: str
    checklist_trend: str = ""
    checklist_vwap: str = ""
    checklist_volume: str = ""
    checklist_regime: str = ""
    checklist_relative_strength: str = ""

    def to_row(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "TradeScenario":
        def _s(k: str, d: str = "") -> str:
            v = row.get(k, d)
            return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)

        def _f(k: str, d: float = 0.0) -> float:
            try:
                v = row.get(k, d)
                return float(v) if v not in (None, "") and not pd.isna(v) else d
            except (TypeError, ValueError):
                return d

        return cls(
            scenario_id=_s("scenario_id"),
            market=_s("market"),
            date=_s("date"),
            time=_s("time"),
            weekly_trend=_s("weekly_trend"),
            monthly_trend=_s("monthly_trend"),
            opening_15m_candle=_s("opening_15m_candle"),
            vwap_status=_s("vwap_status"),
            volume_rvol=_s("volume_rvol"),
            support_resistance=_s("support_resistance"),
            market_condition_summary=_s("market_condition_summary"),
            best_choice=_s("best_choice"),
            ideal_entry=_f("ideal_entry"),
            ideal_stop=_f("ideal_stop"),
            ideal_target=_f("ideal_target"),
            outcome_1030=_s("outcome_1030"),
            outcome_1100=_s("outcome_1100"),
            outcome_1200=_s("outcome_1200"),
            outcome_close=_s("outcome_close"),
            explanation=_s("explanation"),
            checklist_trend=_s("checklist_trend"),
            checklist_vwap=_s("checklist_vwap"),
            checklist_volume=_s("checklist_volume"),
            checklist_regime=_s("checklist_regime"),
            checklist_relative_strength=_s("checklist_relative_strength"),
        )


@dataclass
class ProgressState:
    starting_balance: float = 10_000.0
    account_balance: float = 10_000.0
    risk_per_trade_pct: float = 1.0
    total_trades: int = 0
    wins: int = 0
    total_r: float = 0.0
    best_trade_r: float = 0.0
    worst_trade_r: float = 0.0
    discipline_score: float = 0.0
    checklist_completion_total: float = 0.0
    checklist_attempts: int = 0
    completed_scenarios: List[str] = None  # type: ignore[assignment]
    last_activity: str = ""

    def __post_init__(self) -> None:
        if self.completed_scenarios is None:
            self.completed_scenarios = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressState":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        if "completed_scenarios" not in filtered:
            filtered["completed_scenarios"] = []
        return cls(**filtered)


def _starter_scenarios() -> List[TradeScenario]:
    return [
        TradeScenario(
            scenario_id="tr_qqq_orb_long",
            market="QQQ",
            date="2024-04-12",
            time="09:45 ET",
            weekly_trend="Uptrend",
            monthly_trend="Uptrend",
            opening_15m_candle="Bullish body, closes near high. OR high broken with intent.",
            vwap_status="Above VWAP",
            volume_rvol="RVOL 1.9 — strong",
            support_resistance="OR high 438.20 / OR low 436.50. Prior week high 437.80.",
            market_condition_summary="Trend day setup. QQQ leading SPY. Clean ORB long context.",
            best_choice="Long",
            ideal_entry=438.25,
            ideal_stop=436.45,
            ideal_target=441.85,
            outcome_1030="Holds above OR high. Steady push toward target zone.",
            outcome_1100="Small pullback to VWAP holds. Buyers return.",
            outcome_1200="Trend continues into lunch.",
            outcome_close="Closes near highs. Long plan worked.",
            explanation="Classic QQQ ORB long with trend, VWAP, and volume aligned.",
            checklist_trend="Uptrend",
            checklist_vwap="Above VWAP",
            checklist_volume="Yes — strong",
            checklist_regime="Trending",
            checklist_relative_strength="Stronger",
        ),
        TradeScenario(
            scenario_id="tr_spy_chop",
            market="SPY",
            date="2024-07-08",
            time="09:50 ET",
            weekly_trend="Chop / Range",
            monthly_trend="Uptrend",
            opening_15m_candle="Tiny body doji. Price stuck in middle of OR.",
            vwap_status="Crossing VWAP",
            volume_rvol="RVOL 0.6 — weak",
            support_resistance="Tight range. No break of OR high or low.",
            market_condition_summary="Chop day. Low volume. No clear edge.",
            best_choice="No Trade",
            ideal_entry=556.0,
            ideal_stop=555.5,
            ideal_target=556.5,
            outcome_1030="Whipsaw around VWAP. No follow-through.",
            outcome_1100="Range tightens. Break attempts fail.",
            outcome_1200="Flat lunch session.",
            outcome_close="Closes near open. Sitting out was smart.",
            explanation="SPY chop/no-trade — weak volume and messy OR mean pass.",
            checklist_trend="Chop / Range",
            checklist_vwap="Crossing VWAP",
            checklist_volume="No — weak",
            checklist_regime="Chopping",
            checklist_relative_strength="Neutral",
        ),
        TradeScenario(
            scenario_id="tr_nvda_trend",
            market="NVDA",
            date="2024-08-20",
            time="09:48 ET",
            weekly_trend="Uptrend",
            monthly_trend="Uptrend",
            opening_15m_candle="Strong bullish candle. Minimal upper wick.",
            vwap_status="Above VWAP",
            volume_rvol="RVOL 2.2 — very strong",
            support_resistance="OR high 128.50 cleared. Prior day high 127.90.",
            market_condition_summary="Trend continuation. NVDA leading semis.",
            best_choice="Long",
            ideal_entry=128.60,
            ideal_stop=127.20,
            ideal_target=131.40,
            outcome_1030="Momentum continues. New session highs.",
            outcome_1100="Brief pause at VWAP. Trend resumes.",
            outcome_1200="Steady grind higher.",
            outcome_close="Strong trend day close.",
            explanation="NVDA trend continuation — high RVOL and clean OR.",
            checklist_trend="Uptrend",
            checklist_vwap="Above VWAP",
            checklist_volume="Yes — strong",
            checklist_regime="Trending",
            checklist_relative_strength="Stronger",
        ),
        TradeScenario(
            scenario_id="tr_audusd_london",
            market="AUD/USD",
            date="2024-10-15",
            time="08:30 London",
            weekly_trend="Uptrend",
            monthly_trend="Chop / Range",
            opening_15m_candle="Bullish London open candle breaking Asian high.",
            vwap_status="Above VWAP",
            volume_rvol="Volume rising into London/NY overlap",
            support_resistance="Asian range high 0.6540. Support at 0.6525.",
            market_condition_summary="London/NY session momentum long setup on AUD.",
            best_choice="Long",
            ideal_entry=0.6545,
            ideal_stop=0.6528,
            ideal_target=0.6578,
            outcome_1030="AUD pushes higher as dollar softens.",
            outcome_1100="Pullback holds above breakout.",
            outcome_1200="Overlap volume supports trend.",
            outcome_close="Closes near session high.",
            explanation="AUD/USD London/NY session ORB long.",
            checklist_trend="Uptrend",
            checklist_vwap="Above VWAP",
            checklist_volume="Yes — strong",
            checklist_regime="Trending",
            checklist_relative_strength="Stronger",
        ),
        TradeScenario(
            scenario_id="tr_btc_fakeout",
            market="BTC/USD",
            date="2024-11-28",
            time="00:15 UTC",
            weekly_trend="Chop / Range",
            monthly_trend="Uptrend",
            opening_15m_candle="Long upper wick above OR high. Closes back inside range.",
            vwap_status="Below VWAP",
            volume_rvol="RVOL 1.1 — normal, not confirming breakout",
            support_resistance="Fake break above 97,200. Resistance at prior week high.",
            market_condition_summary="Breakout fakeout in chop. Trap for early longs.",
            best_choice="No Trade",
            ideal_entry=97200.0,
            ideal_stop=97800.0,
            ideal_target=95800.0,
            outcome_1030="Reversal complete. Price back below OR high.",
            outcome_1100="Chop around VWAP.",
            outcome_1200="Range tightens.",
            outcome_close="Mid-range close. Avoiding long was correct.",
            explanation="BTC breakout fakeout — No Trade protects practice account.",
            checklist_trend="Chop / Range",
            checklist_vwap="Below VWAP",
            checklist_volume="Normal",
            checklist_regime="Chopping",
            checklist_relative_strength="Weaker",
        ),
    ]


def ensure_files() -> None:
    if not SCENARIOS_FILE.is_file():
        with SCENARIOS_FILE.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=SCENARIO_COLUMNS)
            w.writeheader()
            for s in _starter_scenarios():
                w.writerow(s.to_row())
    if not JOURNAL_FILE.is_file():
        with JOURNAL_FILE.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=JOURNAL_COLUMNS).writeheader()
    if not PROGRESS_FILE.is_file():
        save_progress(ProgressState())


def load_scenarios() -> List[TradeScenario]:
    ensure_files()
    try:
        df = pd.read_csv(SCENARIOS_FILE)
        return [TradeScenario.from_row(r) for _, r in df.iterrows()]
    except Exception:  # noqa: BLE001
        ensure_files()
        df = pd.read_csv(SCENARIOS_FILE)
        return [TradeScenario.from_row(r) for _, r in df.iterrows()]


def pick_scenario(exclude: Optional[List[str]] = None) -> Optional[TradeScenario]:
    pool = load_scenarios()
    if exclude:
        pool = [s for s in pool if s.scenario_id not in exclude]
    return random.choice(pool) if pool else None


def load_progress() -> ProgressState:
    ensure_files()
    if not PROGRESS_FILE.is_file():
        return ProgressState()
    try:
        return ProgressState.from_dict(json.loads(PROGRESS_FILE.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, TypeError):
        return ProgressState()


def save_progress(state: ProgressState) -> None:
    state.last_activity = datetime.now(timezone.utc).isoformat()
    PROGRESS_FILE.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")


def win_rate(state: ProgressState) -> float:
    if state.total_trades == 0:
        return 0.0
    return 100.0 * state.wins / state.total_trades


def average_r(state: ProgressState) -> float:
    if state.total_trades == 0:
        return 0.0
    return state.total_r / state.total_trades


def checklist_completion_score(state: ProgressState) -> float:
    if state.checklist_attempts == 0:
        return 0.0
    return state.checklist_completion_total / state.checklist_attempts


def trader_level(score: float) -> str:
    label = TRADER_LEVELS[0][1]
    for threshold, name in TRADER_LEVELS:
        if score >= threshold:
            label = name
    return label


def overall_trader_score(state: ProgressState) -> float:
    wr = win_rate(state)
    avg = average_r(state)
    disc = state.discipline_score
    chk = checklist_completion_score(state)
    raw = 0.25 * wr + 0.25 * min(100, max(0, avg * 40)) + 0.25 * disc + 0.25 * chk
    if state.total_trades < 3:
        raw = max(raw, 10.0)
    return round(min(100.0, raw), 1)


def grade_checklist_answers(
    scenario: TradeScenario,
    answers: Dict[str, str],
    trade_choice: str,
    entry: float,
    stop: float,
    target: float,
) -> Tuple[float, List[str]]:
    """Score checklist completion (items user should have considered)."""
    gradable = {
        "trend": scenario.checklist_trend,
        "vwap": scenario.checklist_vwap,
        "volume": scenario.checklist_volume,
        "regime": scenario.checklist_regime,
        "relative_strength": scenario.checklist_relative_strength,
    }
    correct = 0
    total = len(gradable)
    missed: List[str] = []

    norm_map = {
        "Yes — strong": "yes — strong",
        "No — weak": "no — weak",
        "Trending": "trending",
        "Chopping": "chopping",
    }

    for key, expected in gradable.items():
        user = answers.get(key, "")
        eu = norm_map.get(expected, expected).lower()
        uu = norm_map.get(user, user).lower()
        if eu and uu and (eu in uu or uu in eu or eu == uu):
            correct += 1
        elif expected:
            missed.append(f"{key}: expected {expected}, got {user or 'blank'}")

    if trade_choice in ("Long", "Short") and entry > 0 and stop > 0 and target > 0:
        correct += 1
        total += 1
    elif trade_choice in ("Watch", "No Trade"):
        correct += 1
        total += 1
    else:
        missed.append("Entry/stop/target or pass decision incomplete")
        total += 1

    pct = round(100.0 * correct / total, 1) if total else 0.0
    return pct, missed


def grade_trade_decision(
    scenario: TradeScenario,
    trade_choice: str,
    entry: float,
    stop: float,
    target: float,
    confidence: int,
) -> Tuple[GradeLabel, int, str]:
    best = scenario.best_choice
    user = trade_choice
    score = 0
    notes: List[str] = []

    if user.strip().lower() == best.strip().lower():
        score += 50
        notes.append(f"Correct choice: {best}.")
    elif best == "No Trade" and user in ("Watch", "No Trade"):
        score += 35
        notes.append("Good discipline — No Trade was the best answer.")
    elif best == "Watch" and user == "No Trade":
        score += 30
        notes.append("Close — passing was acceptable.")
    else:
        notes.append(f"Best answer was {best}, not {user}.")

    if user in ("Long", "Short"):
        if entry and stop and target:
            risk = abs(entry - stop)
            reward = abs(target - entry)
            if risk > 0:
                r_mult = reward / risk
                if r_mult >= 1.5:
                    score += 25
                    notes.append(f"Solid R plan (~{r_mult:.1f}R).")
                else:
                    score += 10
                    notes.append(f"R plan is thin (~{r_mult:.1f}R).")
        else:
            notes.append("Add entry, stop, and target.")
    elif best in ("No Trade", "Watch"):
        score += 25

    if 1 <= confidence <= 10:
        if score >= 50 and confidence >= 5:
            score += 15
        elif score < 40 and confidence >= 8:
            score -= 5
            notes.append("Confidence was high for a weak setup.")
        else:
            score += 10

    score = max(0, min(100, score))
    if best == "No Trade" and user in ("Long", "Short"):
        grade: GradeLabel = "Best answer was No Trade"
    elif score >= 85:
        grade = "Excellent"
    elif score >= 65:
        grade = "Good"
    elif score >= 45:
        grade = "Risky"
    else:
        grade = "Poor"

    return grade, score, " ".join(notes) + " " + scenario.explanation


def simulate_pnl(
    scenario: TradeScenario,
    trade_choice: str,
    entry: float,
    stop: float,
    target: float,
    account_balance: float,
    risk_pct: float,
) -> Tuple[float, float]:
    """
    Simulate P/L and R for paper trade.
    Uses outcome_close hint to determine win/loss for directional trades.
    """
    if trade_choice in ("Watch", "No Trade"):
        return 0.0, 0.0

    max_risk = account_balance * (risk_pct / 100.0)
    risk_per_unit = abs(entry - stop) if entry and stop else 0.0
    if risk_per_unit <= 0:
        return 0.0, 0.0

    units = max_risk / risk_per_unit
    close_text = scenario.outcome_close.lower()
    won = False
    if trade_choice == "Long":
        won = any(w in close_text for w in ("long", "high", "rewarded", "worked", "higher", "up"))
        if scenario.best_choice == "Long":
            won = True
        elif scenario.best_choice in ("No Trade", "Watch"):
            won = False
    elif trade_choice == "Short":
        won = any(w in close_text for w in ("short", "low", "rewarded", "lower", "down"))
        if scenario.best_choice == "Short":
            won = True
        elif scenario.best_choice in ("No Trade", "Watch"):
            won = False

    if won:
        reward_per_unit = abs(target - entry) if target else risk_per_unit * 2
        pnl = units * reward_per_unit
        r_mult = reward_per_unit / risk_per_unit
    else:
        pnl = -max_risk
        r_mult = -1.0

    return round(pnl, 2), round(r_mult, 2)


def save_trade_attempt(
    scenario: TradeScenario,
    trade_choice: str,
    entry: float,
    stop: float,
    target: float,
    confidence: int,
    notes: str,
    grade: GradeLabel,
    score: int,
    simulated_pnl: float,
    simulated_r: float,
    account_balance_after: float,
    checklist_pct: float,
) -> None:
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_id": scenario.scenario_id,
        "market": scenario.market,
        "trade_choice": trade_choice,
        "entry": entry,
        "stop": stop,
        "target": target,
        "confidence": confidence,
        "notes": notes,
        "grade": grade,
        "score": score,
        "simulated_pnl": simulated_pnl,
        "simulated_r": simulated_r,
        "account_balance_after": account_balance_after,
        "checklist_completion_pct": checklist_pct,
    }
    with JOURNAL_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=JOURNAL_COLUMNS, extrasaction="ignore")
        w.writerow(row)


def record_attempt(
    state: ProgressState,
    scenario: TradeScenario,
    trade_choice: str,
    entry: float,
    stop: float,
    target: float,
    confidence: int,
    notes: str,
    grade: GradeLabel,
    score: int,
    checklist_pct: float,
) -> ProgressState:
    pnl, r_mult = simulate_pnl(
        scenario, trade_choice, entry, stop, target, state.account_balance, state.risk_per_trade_pct
    )
    state.account_balance = round(state.account_balance + pnl, 2)
    state.total_trades += 1
    if pnl > 0:
        state.wins += 1
    state.total_r += r_mult
    state.best_trade_r = max(state.best_trade_r, r_mult)
    state.worst_trade_r = min(state.worst_trade_r, r_mult)

    if trade_choice in ("No Trade", "Watch") and scenario.best_choice in ("No Trade", "Watch"):
        state.discipline_score = min(100.0, state.discipline_score + 5)
    elif trade_choice == scenario.best_choice:
        state.discipline_score = min(100.0, state.discipline_score + 3)
    else:
        state.discipline_score = max(0.0, state.discipline_score - 2)

    state.checklist_completion_total += checklist_pct
    state.checklist_attempts += 1
    if scenario.scenario_id not in state.completed_scenarios:
        state.completed_scenarios.append(scenario.scenario_id)

    save_trade_attempt(
        scenario,
        trade_choice,
        entry,
        stop,
        target,
        confidence,
        notes,
        grade,
        score,
        pnl,
        r_mult,
        state.account_balance,
        checklist_pct,
    )
    save_progress(state)
    return state


def load_journal() -> pd.DataFrame:
    ensure_files()
    if not JOURNAL_FILE.is_file():
        return pd.DataFrame(columns=JOURNAL_COLUMNS)
    try:
        return pd.read_csv(JOURNAL_FILE)
    except Exception:  # noqa: BLE001
        return pd.DataFrame(columns=JOURNAL_COLUMNS)
