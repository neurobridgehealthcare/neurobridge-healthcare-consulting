"""
Father's Hand — Day Trading Training OS.

Private beginner-friendly education and practice simulator.
NOT live trading. NOT financial advice.
"""

from __future__ import annotations

import csv
import json
import random
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd

import risk

PROJECT_DIR = Path(__file__).resolve().parent
TRAINING_LOG_FILE = PROJECT_DIR / "fathers_hand_training_log.csv"
JOURNAL_FILE = PROJECT_DIR / "fathers_hand_journal.csv"
PROGRESS_FILE = PROJECT_DIR / "fathers_hand_progress.json"
ENV_TRADES_FILE = PROJECT_DIR / "environment_trades.csv"
BACKTEST_TRADES_FILE = PROJECT_DIR / "backtest_trades.csv"

DISCLAIMER = (
    "**Training only.** This is a learning simulator. "
    "No live trading. No real orders. No profit promises. "
    "Past examples do not guarantee future results."
)

QuizType = Literal["multiple_choice", "true_false", "short_answer", "classify"]
GradeLabel = Literal["Correct", "Partially correct", "Incorrect"]

LOG_COLUMNS = [
    "timestamp_utc",
    "setup_date",
    "direction",
    "question_id",
    "question_text",
    "user_answer",
    "correct_answer",
    "is_correct",
    "explanation",
    "setup_pnl",
    "setup_r",
]

JOURNAL_COLUMNS = [
    "date",
    "module",
    "scenario",
    "user_answer",
    "correct_answer",
    "score",
    "notes",
    "lesson_learned",
]

SKILL_LABELS = [
    (0, "Beginner"),
    (30, "Developing"),
    (50, "Disciplined"),
    (70, "Consistent"),
    (85, "Elite-in-training"),
]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class QuizQuestion:
    question_id: str
    prompt: str
    quiz_type: QuizType
    options: List[str] = field(default_factory=list)
    correct_index: int = 0
    correct_answer: str = ""
    explanation: str = ""
    acceptable_answers: List[str] = field(default_factory=list)


@dataclass
class LessonModule:
    module_id: int
    title: str
    summary: str
    lessons: List[str]
    quiz: List[QuizQuestion] = field(default_factory=list)
    has_journal: bool = False
    has_simulator: bool = False


@dataclass
class TrainingSetup:
    setup_id: str
    date: str
    direction: str
    regime: str
    relative_strength: str
    or_candle_type: str
    or_body_percent: Optional[float]
    or_candle_quality: str
    pnl: Optional[float]
    r_multiple: Optional[float]
    recommended_action: str
    explanation: str


@dataclass
class TrainingQuestion:
    question_id: str
    prompt: str
    options: List[str]
    correct_index: int
    explanation: str


@dataclass
class TrainingQuiz:
    setup: TrainingSetup
    questions: List[TrainingQuestion] = field(default_factory=list)


@dataclass
class ReplayScenario:
    scenario_id: str
    ticker: str
    time: str
    trend: str
    vwap_status: str
    spy_status: str
    volume_rvol: str
    or_high: float
    or_low: float
    environment_label: str
    tradeable: bool
    direction: str
    risk_dollars: float
    invalidation: str
    explanation: str
    source: str = "sample"


@dataclass
class PaperTradeScenario:
    scenario_id: str
    title: str
    setup_text: str
    correct_choice: str
    explanation: str


@dataclass
class ProgressState:
    completed_modules: List[int] = field(default_factory=list)
    quiz_attempts: int = 0
    quiz_correct: int = 0
    replay_attempts: int = 0
    replay_correct: int = 0
    replay_partial: int = 0
    risk_calc_attempts: int = 0
    risk_calc_correct: int = 0
    no_trade_discipline_correct: int = 0
    no_trade_discipline_total: int = 0
    journal_entries: int = 0
    simulated_trades_logged: int = 0
    current_lesson_level: int = 1
    last_activity: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressState":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})


# ---------------------------------------------------------------------------
# Learning modules (simple language, ~5th grade reading level)
# ---------------------------------------------------------------------------


def _mc(
    qid: str,
    prompt: str,
    options: List[str],
    correct_index: int,
    explanation: str,
) -> QuizQuestion:
    return QuizQuestion(
        question_id=qid,
        prompt=prompt,
        quiz_type="multiple_choice",
        options=options,
        correct_index=correct_index,
        correct_answer=options[correct_index],
        explanation=explanation,
    )


def _tf(qid: str, prompt: str, correct: bool, explanation: str) -> QuizQuestion:
    return QuizQuestion(
        question_id=qid,
        prompt=prompt,
        quiz_type="true_false",
        options=["True", "False"],
        correct_index=0 if correct else 1,
        correct_answer="True" if correct else "False",
        explanation=explanation,
    )


def build_learning_modules() -> List[LessonModule]:
    return [
        LessonModule(
            module_id=1,
            title="What is day trading?",
            summary="Learn what buying, selling, long, short, risk, and reward mean.",
            lessons=[
                "**Day trading** means you buy or sell within the same day. You do not hold overnight.",
                "**Buying (long)** means you think price will go up. You buy low and try to sell higher.",
                "**Selling (short)** means you think price will go down. You sell high and try to buy back lower.",
                "**Risk** is how much money you could lose if you are wrong.",
                "**Reward** is how much money you could make if you are right.",
                "Good traders plan risk first. They do not chase random moves.",
            ],
            quiz=[
                _mc(
                    "m1_q1",
                    "What does going LONG mean?",
                    ["You think price will go up", "You think price will go down", "You hold for a year", "You never use a stop"],
                    0,
                    "Long means you buy because you expect price to rise.",
                ),
                _mc(
                    "m1_q2",
                    "What is risk?",
                    ["Money you might lose", "Money you already made", "A chart color", "A stock ticker"],
                    0,
                    "Risk is the dollars you could lose on a trade.",
                ),
                _tf(
                    "m1_q3",
                    "Day traders usually close trades before the market day ends.",
                    True,
                    "Day trading means same-day entries and exits.",
                ),
            ],
        ),
        LessonModule(
            module_id=2,
            title="Candles and charts",
            summary="Read candle body, wick, open, high, low, and close.",
            lessons=[
                "A **candle** shows price movement for one time period (like 1 minute or 5 minutes).",
                "**Open** is where price started. **Close** is where price ended.",
                "**High** is the top price. **Low** is the bottom price.",
                "The **body** is the thick part between open and close.",
                "The **wick** (or shadow) is the thin line above or below the body.",
                "A green (or white) candle often means close was above open. Red (or black) often means close was below open.",
            ],
            quiz=[
                _mc(
                    "m2_q1",
                    "What does the candle BODY show?",
                    ["Open and close", "Only the high", "Only volume", "The whole year"],
                    0,
                    "The body connects open and close.",
                ),
                _mc(
                    "m2_q2",
                    "What does the WICK show?",
                    ["High and low range", "Your account balance", "The dividend", "The ticker name"],
                    0,
                    "Wicks show how far price moved above and below the body.",
                ),
                _mc(
                    "m2_q3",
                    "If close is above open, the candle is often:",
                    ["Bullish (up)", "Bearish (down)", "Empty", "Illegal"],
                    0,
                    "Close above open often paints a bullish candle.",
                ),
            ],
        ),
        LessonModule(
            module_id=3,
            title="Trend vs chop",
            summary="Spot uptrend, downtrend, consolidation, and fakeouts.",
            lessons=[
                "**Uptrend**: price makes higher lows and higher highs. Buyers are in control.",
                "**Downtrend**: price makes lower highs and lower lows. Sellers are in control.",
                "**Consolidation (chop)**: price moves sideways in a range. Direction is unclear.",
                "**Fakeout**: price breaks a level then quickly reverses. It tricks traders who jump too early.",
                "In chop, breakouts fail more often. Patience matters.",
            ],
            quiz=[
                QuizQuestion(
                    question_id="m3_q1",
                    prompt="Price keeps making higher highs and higher lows. This is:",
                    quiz_type="classify",
                    options=["Uptrend", "Downtrend", "Chop", "Fakeout"],
                    correct_index=0,
                    correct_answer="Uptrend",
                    explanation="Higher highs and higher lows define an uptrend.",
                ),
                QuizQuestion(
                    question_id="m3_q2",
                    prompt="Price breaks above resistance then falls back inside the range. This is:",
                    quiz_type="classify",
                    options=["Uptrend", "Downtrend", "Chop", "Fakeout"],
                    correct_index=3,
                    correct_answer="Fakeout",
                    explanation="A quick break and reverse is a fakeout.",
                ),
                QuizQuestion(
                    question_id="m3_q3",
                    prompt="Price bounces between the same support and resistance for an hour. This is:",
                    quiz_type="classify",
                    options=["Uptrend", "Downtrend", "Chop", "Fakeout"],
                    correct_index=2,
                    correct_answer="Chop",
                    explanation="Sideways range action is chop or consolidation.",
                ),
            ],
        ),
        LessonModule(
            module_id=4,
            title="VWAP",
            summary="Volume-weighted average price — who is stronger, buyers or sellers?",
            lessons=[
                "**VWAP** is the average price weighted by volume since the session started.",
                "Think of it as the fair price zone for today.",
                "Price **above VWAP** often means buyers are stronger right now.",
                "Price **below VWAP** often means sellers are stronger right now.",
                "VWAP is a guide, not a magic line. Use it with trend and volume.",
            ],
            quiz=[
                _mc(
                    "m4_q1",
                    "Price is above VWAP. Who is often stronger?",
                    ["Buyers", "Sellers", "Nobody", "Only robots"],
                    0,
                    "Above VWAP often favors buyers.",
                ),
                _mc(
                    "m4_q2",
                    "VWAP is calculated using:",
                    ["Price and volume", "Only yesterday's close", "News headlines", "Random numbers"],
                    0,
                    "VWAP weights price by how much traded at each level.",
                ),
                _tf(
                    "m4_q3",
                    "VWAP alone guarantees a winning trade.",
                    False,
                    "VWAP is one tool. You still need risk control and context.",
                ),
            ],
        ),
        LessonModule(
            module_id=5,
            title="Opening Range Breakout (ORB)",
            summary="First 15 minutes, OR high, OR low, breakout, and breakdown.",
            lessons=[
                "The **opening range (OR)** is often the first **15 minutes** after the market opens.",
                "**OR high** is the highest price in that window.",
                "**OR low** is the lowest price in that window.",
                "A **breakout** happens when price pushes above OR high (possible long idea).",
                "A **breakdown** happens when price pushes below OR low (possible short idea).",
                "Wait for a clear break with volume. Do not guess early.",
            ],
            quiz=[
                _mc(
                    "m5_q1",
                    "ORB often uses the first:",
                    ["15 minutes", "15 days", "15 weeks", "15 seconds"],
                    0,
                    "The classic OR window is the first 15 minutes.",
                ),
                _mc(
                    "m5_q2",
                    "Price moves above OR high. This is called:",
                    ["Breakout", "Breakdown", "Dividend", "Split"],
                    0,
                    "Above OR high is a breakout.",
                ),
                _mc(
                    "m5_q3",
                    "Price moves below OR low. This is called:",
                    ["Breakout", "Breakdown", "IPO", "Merger"],
                    1,
                    "Below OR low is a breakdown.",
                ),
            ],
        ),
        LessonModule(
            module_id=6,
            title="Volume and RVOL",
            summary="Normal volume vs unusual volume and why it matters.",
            lessons=[
                "**Volume** is how many shares traded in a time period.",
                "**Normal volume** is typical for that stock at that time of day.",
                "**Unusual volume** means more shares than usual are trading.",
                "**RVOL** (relative volume) compares today to a normal day. RVOL above 1.0 means busier than usual.",
                "Strong moves with strong volume are often more trustworthy than weak volume pops.",
            ],
            quiz=[
                _mc(
                    "m6_q1",
                    "RVOL of 2.0 means:",
                    ["About twice normal volume", "Half normal volume", "No volume", "Market is closed"],
                    0,
                    "RVOL compares today to a typical day.",
                ),
                _tf(
                    "m6_q2",
                    "A breakout with very low volume is often weaker than one with high volume.",
                    True,
                    "Volume helps confirm real participation.",
                ),
                _mc(
                    "m6_q3",
                    "Volume tells you:",
                    ["How many shares traded", "Your tax rate", "The CEO's name", "Next year's earnings"],
                    0,
                    "Volume counts shares traded.",
                ),
            ],
        ),
        LessonModule(
            module_id=7,
            title="Risk management",
            summary="Stop loss, target, R multiple, and position size.",
            lessons=[
                "A **stop loss** is where you exit if you are wrong. It caps loss.",
                "A **target** is where you plan to take profit if you are right.",
                "**R multiple** = reward per share ÷ risk per share. A 2R target means reward is twice the risk.",
                "**Position size** = how many shares you buy. Size comes from account risk ÷ risk per share.",
                "Never risk more than your plan. Small, steady risk beats big gambles.",
            ],
            quiz=[
                _mc(
                    "m7_q1",
                    "If you risk $1 to make $2, your R multiple is:",
                    ["2R", "0.5R", "10R", "0R"],
                    0,
                    "Reward ÷ risk = 2 ÷ 1 = 2R.",
                ),
                _tf(
                    "m7_q2",
                    "Position size should match your planned dollar risk.",
                    True,
                    "Size shares so a stop hit loses about your planned risk.",
                ),
                QuizQuestion(
                    question_id="m7_q3",
                    prompt="In your own words: Why use a stop loss? (Short answer)",
                    quiz_type="short_answer",
                    correct_answer="limit loss",
                    acceptable_answers=["limit loss", "cap loss", "protect", "control risk", "stop out"],
                    explanation="A stop helps you exit when wrong so one trade cannot ruin your account.",
                ),
            ],
        ),
        LessonModule(
            module_id=8,
            title="Trade decision checklist",
            summary="Trend, VWAP, SPY, RVOL, OR quality, risk/reward, and no-trade rules.",
            lessons=[
                "Before any trade, run a simple checklist:",
                "1. **Trend** — Is the market trending or chopping?",
                "2. **VWAP** — Is price on the right side for your direction?",
                "3. **SPY confirmation** — Does the broad market agree?",
                "4. **RVOL** — Is volume strong enough?",
                "5. **OR quality** — Is the opening range candle clean or messy?",
                "6. **Risk/reward** — Is your R at least 1.5R to 2R?",
                "7. **No-trade rules** — Skip chop, weak volume, bad R, or unclear SPY.",
                "Missing several items? **Watch** or **No Trade** is often the smart choice.",
            ],
            quiz=[
                _mc(
                    "m8_q1",
                    "QQQ is above VWAP but SPY is below VWAP. You should:",
                    ["Be careful — confirmation is mixed", "Ignore SPY always", "Double size", "Never use stops"],
                    0,
                    "Mixed confirmation lowers odds. Patience helps.",
                ),
                _mc(
                    "m8_q2",
                    "Chop + weak RVOL + messy OR usually means:",
                    ["No Trade or Watch", "Must trade now", "Remove stop loss", "Add random size"],
                    0,
                    "Low-quality setups are for practice, not forcing trades.",
                ),
                _tf(
                    "m8_q3",
                    "A good checklist helps you skip bad trades.",
                    True,
                    "Discipline and pattern recognition beat guessing.",
                ),
            ],
        ),
        LessonModule(
            module_id=9,
            title="Paper trading simulator",
            summary="Choose Long, Short, Watch, or No Trade on sample setups.",
            lessons=[
                "You will see a setup description. Pick the best action.",
                "**Long** — bullish plan with rules met.",
                "**Short** — bearish plan with rules met.",
                "**Watch** — interesting but not ready.",
                "**No Trade** — rules fail or risk is unclear.",
                "There is no live money here. This builds decision habits.",
            ],
            has_simulator=True,
            quiz=[],
        ),
        LessonModule(
            module_id=10,
            title="Review and journal",
            summary="Write why you traded, the setup, risk, and rule-following.",
            lessons=[
                "After each practice session, answer four questions:",
                "1. **Why did I take this?** (or why did I skip?)",
                "2. **What was the setup?** (trend, VWAP, OR, volume)",
                "3. **What was the risk?** (stop, size, R)",
                "4. **Did I follow my rules?** (honest yes or no)",
                "Journaling turns mistakes into lessons. Review weekly.",
            ],
            has_journal=True,
            quiz=[],
        ),
    ]


PAPER_SCENARIOS: List[PaperTradeScenario] = [
    PaperTradeScenario(
        scenario_id="sim_1",
        title="Clean OR breakout",
        setup_text=(
            "QQQ uptrend. Price breaks OR high with RVOL 1.8. "
            "Above VWAP. SPY also above VWAP. OR candle bullish with strong body. "
            "2R plan with clear stop below OR low."
        ),
        correct_choice="Long",
        explanation="Trend, VWAP, SPY, volume, and OR align for a long idea.",
    ),
    PaperTradeScenario(
        scenario_id="sim_2",
        title="Chop fakeout",
        setup_text=(
            "Sideways chop for 45 minutes. Price pokes above OR high on weak RVOL 0.6. "
            "SPY flat. Wick-heavy OR candle."
        ),
        correct_choice="No Trade",
        explanation="Chop + weak volume + poor OR = skip.",
    ),
    PaperTradeScenario(
        scenario_id="sim_3",
        title="Breakdown with confirmation",
        setup_text=(
            "QQQ downtrend. Breaks OR low. Below VWAP. SPY below VWAP. "
            "RVOL 1.5. Bearish OR body. Stop above OR high. Target 2R."
        ),
        correct_choice="Short",
        explanation="Bearish context with confirmation supports a short plan.",
    ),
    PaperTradeScenario(
        scenario_id="sim_4",
        title="Almost ready",
        setup_text=(
            "Breakout above OR high. Good RVOL. But SPY still below VWAP and price wicks back to OR high."
        ),
        correct_choice="Watch",
        explanation="Some pieces are good but confirmation is not complete.",
    ),
]

SAMPLE_REPLAY_SCENARIOS: List[ReplayScenario] = [
    ReplayScenario(
        scenario_id="sample_1",
        ticker="QQQ",
        time="09:52 ET",
        trend="Uptrend",
        vwap_status="Above VWAP",
        spy_status="SPY above VWAP",
        volume_rvol="RVOL 1.9",
        or_high=450.25,
        or_low=448.90,
        environment_label="Trend Up",
        tradeable=True,
        direction="Long",
        risk_dollars=100.0,
        invalidation="Close back below OR high or VWAP",
        explanation="Aligned breakout with volume.",
    ),
    ReplayScenario(
        scenario_id="sample_2",
        ticker="QQQ",
        time="10:05 ET",
        trend="Chop",
        vwap_status="Crossing VWAP",
        spy_status="SPY flat",
        volume_rvol="RVOL 0.7",
        or_high=451.00,
        or_low=450.50,
        environment_label="Chop",
        tradeable=False,
        direction="No Trade",
        risk_dollars=0.0,
        invalidation="N/A — skip",
        explanation="Small OR, low RVOL, no clear trend.",
    ),
    ReplayScenario(
        scenario_id="sample_3",
        ticker="QQQ",
        time="09:48 ET",
        trend="Downtrend",
        vwap_status="Below VWAP",
        spy_status="SPY below VWAP",
        volume_rvol="RVOL 2.1",
        or_high=445.10,
        or_low=443.20,
        environment_label="Trend Down",
        tradeable=True,
        direction="Short",
        risk_dollars=75.0,
        invalidation="Close back above OR low",
        explanation="Breakdown with bearish confirmation.",
    ),
]


# ---------------------------------------------------------------------------
# Progress persistence
# ---------------------------------------------------------------------------


def load_progress() -> ProgressState:
    if not PROGRESS_FILE.is_file():
        return ProgressState()
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return ProgressState.from_dict(data)
    except (json.JSONDecodeError, TypeError):
        return ProgressState()


def save_progress(state: ProgressState) -> None:
    state.last_activity = datetime.now(timezone.utc).isoformat()
    PROGRESS_FILE.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")


def mark_module_complete(state: ProgressState, module_id: int) -> ProgressState:
    if module_id not in state.completed_modules:
        state.completed_modules.append(module_id)
        state.completed_modules.sort()
    state.current_lesson_level = min(10, max(state.completed_modules, default=0) + 1)
    save_progress(state)
    return state


# ---------------------------------------------------------------------------
# Quiz engine
# ---------------------------------------------------------------------------


def grade_quiz_question(question: QuizQuestion, user_answer: str) -> Tuple[bool, str]:
    """Grade one quiz question. Returns (is_correct, feedback)."""
    if question.quiz_type == "multiple_choice" or question.quiz_type == "classify":
        try:
            idx = question.options.index(user_answer)
        except ValueError:
            return False, f"Pick one option. Correct: **{question.correct_answer}**. {question.explanation}"
        ok = idx == question.correct_index
        if ok:
            return True, question.explanation
        return False, f"Correct answer: **{question.correct_answer}**. {question.explanation}"

    if question.quiz_type == "true_false":
        ok = user_answer.strip().lower() == question.correct_answer.lower()
        if ok:
            return True, question.explanation
        return False, f"Correct answer: **{question.correct_answer}**. {question.explanation}"

    if question.quiz_type == "short_answer":
        text = user_answer.strip().lower()
        if len(text) < 3:
            return False, "Please write at least a few words."
        checks = [question.correct_answer.lower(), *[a.lower() for a in question.acceptable_answers]]
        ok = any(c in text for c in checks if c)
        if ok:
            return True, question.explanation
        return False, (
            f"Your note is saved for review. Key idea: {question.explanation}"
        )

    return False, "Unknown question type."


def record_quiz_result(
    state: ProgressState,
    correct_count: int,
    total: int,
    module_id: int,
    module_title: str,
) -> ProgressState:
    state.quiz_attempts += total
    state.quiz_correct += correct_count
    if correct_count == total and total > 0:
        state = mark_module_complete(state, module_id)
    save_progress(state)
    return state


# ---------------------------------------------------------------------------
# Replay trainer
# ---------------------------------------------------------------------------


def _or_quality_label(candle_type: str, body_pct: Optional[float]) -> str:
    ct = (candle_type or "neutral").lower()
    body = body_pct if body_pct is not None else 0.0
    if body >= 35 and ct in ("bullish", "bearish"):
        return "good"
    if body < 20:
        return "bad"
    return "mixed"


def _action_from_trade(pnl: Optional[float], r: Optional[float], regime: str) -> str:
    reg = (regime or "").lower()
    if reg in ("chop", "mean reversion") and (pnl is not None and pnl < 0):
        return "avoid"
    if pnl is not None and pnl > 0 and r is not None and r >= 1.0:
        return "trade"
    if pnl is not None and pnl <= 0:
        return "avoid"
    return "watch"


def load_training_setups() -> List[TrainingSetup]:
    """Load setups from environment_trades.csv, else backtest_trades.csv."""
    path = ENV_TRADES_FILE if ENV_TRADES_FILE.is_file() else BACKTEST_TRADES_FILE
    if not path.is_file():
        return []
    try:
        df = pd.read_csv(path)
    except Exception:  # noqa: BLE001
        return []

    setups: List[TrainingSetup] = []
    for i, row in df.iterrows():
        regime = str(row.get("regime", "") or "unknown")
        rs = str(row.get("qqq_vs_spy_strength", row.get("relative_strength", "")) or "unknown")
        candle = str(row.get("or_candle_type", "") or "neutral")
        body_raw = row.get("or_body_percent")
        try:
            body = float(body_raw) if body_raw not in ("", None) and not pd.isna(body_raw) else None
        except (TypeError, ValueError):
            body = None
        quality = _or_quality_label(candle, body)
        pnl_raw = row.get("pnl")
        r_raw = row.get("r_multiple")
        try:
            pnl = float(pnl_raw) if pnl_raw not in ("", None) and not pd.isna(pnl_raw) else None
        except (TypeError, ValueError):
            pnl = None
        try:
            r_mult = float(r_raw) if r_raw not in ("", None) and not pd.isna(r_raw) else None
        except (TypeError, ValueError):
            r_mult = None
        action = _action_from_trade(pnl, r_mult, regime)
        exp = (
            f"Historical result: P/L ${pnl:.2f}, R {r_mult:.2f}."
            if pnl is not None and r_mult is not None
            else "Historical context from past backtest row."
        )
        setups.append(
            TrainingSetup(
                setup_id=f"{row.get('date', i)}_{row.get('direction', 'X')}_{i}",
                date=str(row.get("date", "")),
                direction=str(row.get("direction", "")),
                regime=regime,
                relative_strength=rs,
                or_candle_type=candle,
                or_body_percent=body,
                or_candle_quality=quality,
                pnl=pnl,
                r_multiple=r_mult,
                recommended_action=action,
                explanation=exp,
            )
        )
    return setups


def _row_to_replay(row: Any, idx: int) -> ReplayScenario:
    regime = str(row.get("regime", "") or "unknown")
    direction = str(row.get("direction", "") or "None")
    or_size = row.get("OR_size")
    entry = row.get("entry")
    try:
        or_sz = float(or_size) if or_size not in ("", None) and not pd.isna(or_size) else 2.0
    except (TypeError, ValueError):
        or_sz = 2.0
    try:
        ent = float(entry) if entry not in ("", None) and not pd.isna(entry) else 450.0
    except (TypeError, ValueError):
        ent = 450.0
    or_low = ent - or_sz / 2
    or_high = ent + or_sz / 2
    rs = str(row.get("qqq_vs_spy_strength", "") or "neutral")
    spy_ok = "above" in rs.lower() or str(row.get("qqq_stronger_than_spy", "")).lower() == "true"
    spy_status = "SPY confirms QQQ" if spy_ok else "SPY mixed or weak"
    tradeable = direction in ("Long", "Short") and regime.lower() not in ("chop", "mean reversion")
    return ReplayScenario(
        scenario_id=f"hist_{row.get('date', idx)}_{idx}",
        ticker="QQQ",
        time=str(row.get("entry_time", "09:45 ET")),
        trend=regime,
        vwap_status="Context from historical tag",
        spy_status=spy_status,
        volume_rvol="See environment research",
        or_high=round(or_high, 2),
        or_low=round(or_low, 2),
        environment_label=regime,
        tradeable=tradeable,
        direction=direction if tradeable else "No Trade",
        risk_dollars=100.0,
        invalidation="Stop beyond OR boundary",
        explanation=f"Historical {direction} in {regime}. Review tags before copying.",
        source="historical",
    )


def load_replay_scenarios() -> List[ReplayScenario]:
    """Use backtest/environment CSV rows when available; else sample scenarios."""
    scenarios: List[ReplayScenario] = list(SAMPLE_REPLAY_SCENARIOS)
    path = ENV_TRADES_FILE if ENV_TRADES_FILE.is_file() else BACKTEST_TRADES_FILE
    if path.is_file():
        try:
            df = pd.read_csv(path)
            for i, row in df.iterrows():
                scenarios.append(_row_to_replay(row, i))
        except Exception:  # noqa: BLE001
            pass
    return scenarios


def pick_replay_scenario(scenarios: List[ReplayScenario]) -> Optional[ReplayScenario]:
    if not scenarios:
        return None
    return random.choice(scenarios)


def grade_replay_answers(
    scenario: ReplayScenario,
    tradeable_answer: str,
    direction_answer: str,
    risk_answer: str,
    invalidation_answer: str,
) -> Tuple[GradeLabel, int, str]:
    """
    Grade replay practice. Returns (label, points 0-100, feedback).
    """
    points = 0
    notes: List[str] = []

    expected_tradeable = "Yes" if scenario.tradeable else "No"
    if tradeable_answer == expected_tradeable:
        points += 25
        notes.append("Tradeable call: correct.")
    else:
        notes.append(f"Tradeable call: expected **{expected_tradeable}**.")

    dir_norm = direction_answer.strip().lower()
    exp_dir = scenario.direction.strip().lower()
    if dir_norm == exp_dir or (exp_dir == "no trade" and dir_norm in ("no trade", "watch")):
        points += 25
        notes.append("Direction: correct.")
    elif exp_dir == "no trade" and dir_norm == "watch":
        points += 15
        notes.append("Direction: partially correct (watch vs no trade).")
    else:
        notes.append(f"Direction: expected **{scenario.direction}**.")

    try:
        risk_val = float(re.sub(r"[^\d.]", "", risk_answer) or "0")
    except ValueError:
        risk_val = -1.0
    if not scenario.tradeable and risk_val == 0:
        points += 25
        notes.append("Risk: correct (no trade = no risk).")
    elif scenario.tradeable and 25 <= risk_val <= 500:
        points += 25
        notes.append("Risk: reasonable plan stated.")
    elif scenario.tradeable and risk_val > 0:
        points += 15
        notes.append("Risk: partial — check your dollar risk plan.")
    else:
        notes.append("Risk: state dollars you are willing to lose.")

    inv_text = invalidation_answer.strip().lower()
    if len(inv_text) >= 8:
        key_words = ["or", "vwap", "stop", "break", "close", "below", "above"]
        if any(w in inv_text for w in key_words):
            points += 25
            notes.append("Invalidation: good answer.")
        else:
            points += 15
            notes.append("Invalidation: partial — mention OR, VWAP, or stop.")
    else:
        notes.append("Invalidation: describe what cancels the trade.")

    if points >= 85:
        label: GradeLabel = "Correct"
    elif points >= 55:
        label = "Partially correct"
    else:
        label = "Incorrect"

    feedback = " ".join(notes) + f" {scenario.explanation}"
    return label, points, feedback


def record_replay_result(state: ProgressState, label: GradeLabel) -> ProgressState:
    state.replay_attempts += 1
    if label == "Correct":
        state.replay_correct += 1
    elif label == "Partially correct":
        state.replay_partial += 1
    save_progress(state)
    return state


# ---------------------------------------------------------------------------
# Trader score
# ---------------------------------------------------------------------------


def quiz_accuracy_pct(state: ProgressState) -> float:
    if state.quiz_attempts == 0:
        return 0.0
    return 100.0 * state.quiz_correct / state.quiz_attempts


def replay_accuracy_pct(state: ProgressState) -> float:
    if state.replay_attempts == 0:
        return 0.0
    full = state.replay_correct + 0.5 * state.replay_partial
    return 100.0 * full / state.replay_attempts


def risk_mgmt_accuracy_pct(state: ProgressState) -> float:
    if state.risk_calc_attempts == 0:
        return 0.0
    return 100.0 * state.risk_calc_correct / state.risk_calc_attempts


def no_trade_discipline_pct(state: ProgressState) -> float:
    if state.no_trade_discipline_total == 0:
        return 0.0
    return 100.0 * state.no_trade_discipline_correct / state.no_trade_discipline_total


def compute_trader_score(state: ProgressState) -> Tuple[float, str]:
    """
    Weighted skill score 0-100 and label.
    """
    quiz = quiz_accuracy_pct(state)
    replay = replay_accuracy_pct(state)
    risk_m = risk_mgmt_accuracy_pct(state) if state.risk_calc_attempts else quiz * 0.5
    discipline = no_trade_discipline_pct(state) if state.no_trade_discipline_total else replay * 0.5
    journal_bonus = min(10.0, state.journal_entries * 2.0)

    if state.quiz_attempts + state.replay_attempts < 5:
        raw = 15.0 + journal_bonus
    else:
        raw = (
            0.30 * quiz
            + 0.30 * replay
            + 0.20 * risk_m
            + 0.15 * discipline
            + 0.05 * min(100.0, state.completed_modules * 10)
            + journal_bonus * 0.5
        )

    score = round(min(100.0, max(0.0, raw)), 1)
    label = SKILL_LABELS[0][1]
    for threshold, name in SKILL_LABELS:
        if score >= threshold:
            label = name
    return score, label


# ---------------------------------------------------------------------------
# Journal
# ---------------------------------------------------------------------------


def append_journal_entry(
    module: str,
    scenario: str,
    user_answer: str,
    correct_answer: str,
    score: str,
    notes: str,
    lesson_learned: str,
) -> Path:
    row = {
        "date": date.today().isoformat(),
        "module": module,
        "scenario": scenario,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "score": score,
        "notes": notes,
        "lesson_learned": lesson_learned,
    }
    exists = JOURNAL_FILE.is_file()
    with JOURNAL_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=JOURNAL_COLUMNS)
        if not exists:
            w.writeheader()
        w.writerow(row)
    return JOURNAL_FILE


def load_journal_df() -> pd.DataFrame:
    if not JOURNAL_FILE.is_file():
        return pd.DataFrame(columns=JOURNAL_COLUMNS)
    try:
        return pd.read_csv(JOURNAL_FILE)
    except Exception:  # noqa: BLE001
        return pd.DataFrame(columns=JOURNAL_COLUMNS)


def record_journal_completion(state: ProgressState) -> ProgressState:
    state.journal_entries += 1
    state = mark_module_complete(state, 10)
    save_progress(state)
    return state


# ---------------------------------------------------------------------------
# Risk calculator practice
# ---------------------------------------------------------------------------


def grade_risk_practice(
    account: float,
    risk_pct: float,
    entry: float,
    stop: float,
    target: float,
    direction: risk.Direction,
    user_shares: int,
    user_r: float,
) -> Tuple[bool, Dict[str, float], str]:
    max_risk = risk.max_dollar_risk(account, risk_pct)
    rps = risk.risk_per_share(entry, stop, direction)
    rps_reward = risk.reward_per_share(entry, target, direction)
    shares = risk.position_size(max_risk, rps)
    r_mult = risk.r_multiple(rps_reward, rps)

    shares_ok = user_shares == shares
    r_ok = abs(user_r - r_mult) < 0.15 if r_mult > 0 else user_r == 0
    ok = shares_ok and r_ok

    msg = (
        f"Correct size: **{shares}** shares. Correct R: **{r_mult:.2f}**. "
        f"Max risk: **${max_risk:,.2f}**."
    )
    if not ok:
        msg = (
            f"Your shares: {user_shares}, correct: **{shares}**. "
            f"Your R: {user_r:.2f}, correct: **{r_mult:.2f}**. "
            "Adjust entry, stop, target, or account risk and try again."
        )

    details = {
        "max_risk_dollars": max_risk,
        "risk_per_share": rps,
        "reward_per_share": rps_reward,
        "shares": float(shares),
        "r_multiple": r_mult,
    }
    return ok, details, msg


def record_risk_practice(state: ProgressState, ok: bool) -> ProgressState:
    state.risk_calc_attempts += 1
    if ok:
        state.risk_calc_correct += 1
    if state.risk_calc_correct >= 3 and 7 not in state.completed_modules:
        state = mark_module_complete(state, 7)
    save_progress(state)
    return state


# ---------------------------------------------------------------------------
# Paper simulator grading
# ---------------------------------------------------------------------------


def grade_paper_choice(scenario: PaperTradeScenario, choice: str) -> Tuple[bool, str]:
    ok = choice.strip().lower() == scenario.correct_choice.strip().lower()
    if ok:
        return True, scenario.explanation
    return False, f"Best choice: **{scenario.correct_choice}**. {scenario.explanation}"


def record_paper_trade(state: ProgressState, scenario: PaperTradeScenario, choice: str, ok: bool) -> ProgressState:
    state.simulated_trades_logged += 1
    state.no_trade_discipline_total += 1
    if scenario.correct_choice in ("No Trade", "Watch") and choice in ("No Trade", "Watch"):
        state.no_trade_discipline_correct += 1
    elif ok:
        state.no_trade_discipline_correct += 1
    if ok:
        if 9 not in state.completed_modules:
            state = mark_module_complete(state, 9)
    save_progress(state)
    return state


# ---------------------------------------------------------------------------
# Legacy Stage 3H helpers (app.py compatibility)
# ---------------------------------------------------------------------------


def _mc_options(correct: str, distractors: List[str], count: int = 4) -> Tuple[List[str], int]:
    opts = list(dict.fromkeys([correct] + [d for d in distractors if d and d != correct]))
    while len(opts) < count:
        for filler in ("unknown", "mixed", "neutral"):
            if filler not in opts:
                opts.append(filler)
            if len(opts) >= count:
                break
    opts = opts[:count]
    if correct not in opts:
        opts[-1] = correct
    return opts, opts.index(correct)


def build_quiz(setup: TrainingSetup) -> TrainingQuiz:
    """Multiple-choice questions for one historical setup (Stage 3H)."""
    regime_opts, regime_idx = _mc_options(
        setup.regime or "unknown",
        ["Trend Up", "Trend Down", "Chop", "Mean Reversion", "Gap Up Continuation", "Gap Down Continuation"],
    )
    rs_opts, rs_idx = _mc_options(
        setup.relative_strength or "unknown",
        ["QQQ stronger", "QQQ weaker", "neutral"],
    )
    qual_opts, qual_idx = _mc_options(
        setup.or_candle_quality or "mixed",
        ["good", "bad", "mixed"],
    )
    action_opts, act_idx = _mc_options(
        setup.recommended_action or "watch",
        ["trade", "watch", "avoid"],
    )

    questions = [
        TrainingQuestion(
            question_id="regime",
            prompt="What is the market regime?",
            options=regime_opts,
            correct_index=regime_idx,
            explanation=f"The tagged regime was **{setup.regime}**.",
        ),
        TrainingQuestion(
            question_id="relative_strength",
            prompt="Is QQQ stronger or weaker than SPY?",
            options=rs_opts,
            correct_index=rs_idx,
            explanation=f"Relative strength was **{setup.relative_strength}**.",
        ),
        TrainingQuestion(
            question_id="or_quality",
            prompt="Is the OR candle quality good or bad?",
            options=qual_opts,
            correct_index=qual_idx,
            explanation=(
                f"OR candle **{setup.or_candle_type}** with body "
                f"{setup.or_body_percent if setup.or_body_percent is not None else 'n/a'}% → "
                f"**{setup.or_candle_quality}** quality."
            ),
        ),
        TrainingQuestion(
            question_id="action",
            prompt="Is this a trade, watch, or avoid?",
            options=action_opts,
            correct_index=act_idx,
            explanation=f"Recommended review action: **{setup.recommended_action}**. {setup.explanation}",
        ),
    ]
    return TrainingQuiz(setup=setup, questions=questions)


def pick_random_setup(setups: List[TrainingSetup]) -> Optional[TrainingSetup]:
    if not setups:
        return None
    return random.choice(setups)


def grade_answer(question: TrainingQuestion, selected_index: int) -> Tuple[bool, str]:
    ok = selected_index == question.correct_index
    msg = (
        question.explanation
        if ok
        else f"Correct answer: **{question.options[question.correct_index]}**. {question.explanation}"
    )
    return ok, msg


def append_training_log(rows: List[Dict[str, Any]]) -> Path:
    exists = TRAINING_LOG_FILE.is_file()
    fieldnames = list(LOG_COLUMNS)
    if exists:
        with TRAINING_LOG_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                fieldnames = list(dict.fromkeys(list(reader.fieldnames) + LOG_COLUMNS))
    with TRAINING_LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            w.writeheader()
        for row in rows:
            if not row.get("timestamp_utc"):
                row["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
            w.writerow({k: row.get(k, "") for k in fieldnames})
    return TRAINING_LOG_FILE


# ---------------------------------------------------------------------------
# 5-layer simulator (replay, checklist, coach, skills, scenario library)
# ---------------------------------------------------------------------------

try:
    import fathers_hand_simulator as _fh_sim
except ImportError:  # pragma: no cover
    _fh_sim = None  # type: ignore[assignment]

if _fh_sim is not None:
    SIM_DISCLAIMER = _fh_sim.SIM_DISCLAIMER
    FullScenario = _fh_sim.FullScenario
    SkillScores = _fh_sim.SkillScores
    CHECKLIST_ITEMS = _fh_sim.CHECKLIST_ITEMS
    ensure_simulator_files = _fh_sim.ensure_simulator_files
    load_full_scenarios = _fh_sim.load_scenarios
    pick_full_scenario = _fh_sim.pick_scenario
    scenario_library_stats = _fh_sim.scenario_library_stats
    grade_replay_decision = _fh_sim.grade_replay_decision
    save_replay_attempt = _fh_sim.save_replay_attempt
    grade_checklist = _fh_sim.grade_checklist
    save_checklist_attempt = _fh_sim.save_checklist_attempt
    generate_coach_report = _fh_sim.generate_coach_report
    load_coach_reports = _fh_sim.load_coach_reports
    compute_skill_scores = _fh_sim.compute_skill_scores
    save_skill_history = _fh_sim.save_skill_history
    load_skill_history = _fh_sim.load_skill_history
    trader_level_from_score = _fh_sim.trader_level_from_score
    export_all_logs = _fh_sim.export_all_logs
    import_historical_ohlcv = _fh_sim.import_historical_ohlcv
    convert_historical_to_scenarios = _fh_sim.convert_historical_to_scenarios
    tag_orb_examples = _fh_sim.tag_orb_examples

try:
    import fathers_hand_modules as _fh_mod
except ImportError:  # pragma: no cover
    _fh_mod = None  # type: ignore[assignment]

if _fh_mod is not None:
    ensure_module_files = _fh_mod.ensure_module_files
    MARKET_ENVIRONMENT_OPTIONS = _fh_mod.MARKET_ENVIRONMENT_OPTIONS
    grade_market_environment = _fh_mod.grade_market_environment
    save_market_context = _fh_mod.save_market_context
    grade_futures_context = _fh_mod.grade_futures_context
    save_futures_context = _fh_mod.save_futures_context
    grade_market_structure = _fh_mod.grade_market_structure
    save_structure = _fh_mod.save_structure
    pick_pattern_drill = _fh_mod.pick_pattern_drill
    grade_pattern = _fh_mod.grade_pattern
    save_pattern = _fh_mod.save_pattern
    grade_trend_day = _fh_mod.grade_trend_day
    save_trend_day = _fh_mod.save_trend_day
    grade_trade_management = _fh_mod.grade_trade_management
    save_trade_management = _fh_mod.save_trade_management
    MASTER_SKILL_WEIGHTS = _fh_mod.MASTER_SKILL_WEIGHTS

try:
    import fathers_hand_scenario_engine as _fh_eng
except ImportError:  # pragma: no cover
    _fh_eng = None  # type: ignore[assignment]

if _fh_eng is not None:
    pick_scenario_for_market = _fh_eng.pick_scenario_for_market
    generate_scenario = _fh_eng.generate_scenario
    scenario_library_capacity = _fh_eng.library_capacity
    TRAINING_MARKET_CHOICES = _fh_eng.TRAINING_MARKET_CHOICES
