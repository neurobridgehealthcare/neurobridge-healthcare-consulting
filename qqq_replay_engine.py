"""
QQQ Replay Backtester — synthetic scenario + candle engine.

Training only. No live trading. No real orders.
"""

from __future__ import annotations

import csv
import hashlib
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
SCENARIOS_FILE = PROJECT_DIR / "qqq_replay_scenarios.csv"
CANDLES_FILE = PROJECT_DIR / "qqq_replay_candles.csv"
RESULTS_FILE = PROJECT_DIR / "qqq_replay_results.csv"

MARKETS = ["QQQ", "SPY", "NQ", "ES"]
DEFAULT_MARKET = "QQQ"
TIMEFRAMES = ["1m", "5m", "15m", "1h", "1d"]

SETUP_TYPES = [
    "ORB long",
    "ORB short",
    "trend day up",
    "trend day down",
    "fakeout",
    "chop",
    "VWAP reclaim",
    "VWAP rejection",
]

SCENARIO_COLUMNS = [
    "scenario_id",
    "market",
    "date",
    "replay_cutoff_time",
    "outcome_end_time",
    "previous_day_high",
    "previous_day_low",
    "weekly_high",
    "weekly_low",
    "opening_range_high",
    "opening_range_low",
    "vwap",
    "setup_type",
    "hidden_outcome",
    "difficulty",
]

CANDLE_COLUMNS = [
    "scenario_id",
    "bar_time",
    "minute_offset",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

RESULT_COLUMNS = [
    "timestamp",
    "scenario_id",
    "market",
    "timeframe",
    "direction",
    "entry",
    "stop_loss",
    "take_profit",
    "risk_amount",
    "reward_risk",
    "result",
    "r_multiple",
    "simulated_pnl",
    "trigger_time",
    "notes",
]

ResultLabel = Literal["WIN", "LOSS", "NO HIT", "AMBIGUOUS", "NO TRADE"]

MARKET_BASES = {
    "QQQ": 480.0,
    "SPY": 520.0,
    "NQ": 18500.0,
    "ES": 5200.0,
}

SCENARIO_TARGETS = {
    "QQQ": 200,
    "SPY": 150,
    "NQ": 100,
    "ES": 50,
}

RTH_OPEN = "09:30"
RTH_CLOSE = "16:00"
SESSION_MINUTES = 390  # 9:30 to 16:00


@dataclass
class ReplayScenario:
    scenario_id: str
    market: str
    date: str
    replay_cutoff_time: str
    outcome_end_time: str
    previous_day_high: float
    previous_day_low: float
    weekly_high: float
    weekly_low: float
    opening_range_high: float
    opening_range_low: float
    vwap: float
    setup_type: str
    hidden_outcome: str
    difficulty: str

    def to_row(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "ReplayScenario":
        def _f(k: str, default: str = "") -> str:
            v = row.get(k, default)
            return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)

        def _float(k: str) -> float:
            try:
                return float(row.get(k, 0) or 0)
            except (TypeError, ValueError):
                return 0.0

        return cls(
            scenario_id=_f("scenario_id"),
            market=_f("market", "QQQ"),
            date=_f("date"),
            replay_cutoff_time=_f("replay_cutoff_time", "10:00"),
            outcome_end_time=_f("outcome_end_time", "16:00"),
            previous_day_high=_float("previous_day_high"),
            previous_day_low=_float("previous_day_low"),
            weekly_high=_float("weekly_high"),
            weekly_low=_float("weekly_low"),
            opening_range_high=_float("opening_range_high"),
            opening_range_low=_float("opening_range_low"),
            vwap=_float("vwap"),
            setup_type=_f("setup_type"),
            hidden_outcome=_f("hidden_outcome"),
            difficulty=_f("difficulty", "beginner"),
        )


@dataclass
class TradePlan:
    direction: str
    entry: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    notes: str


@dataclass
class BacktestOutcome:
    result: ResultLabel
    exit_price: float
    r_multiple: float
    simulated_pnl: float
    trigger_time: str
    trigger_minute: Optional[int]
    explanation: str


def _rng(scenario_id: str) -> random.Random:
    digest = hashlib.sha256(scenario_id.encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def _tick(market: str, base: float) -> float:
    if market in ("NQ", "ES"):
        return 0.25 if market == "NQ" else 0.25
    return 0.01


def _round_px(price: float, market: str) -> float:
    if market in ("NQ", "ES"):
        return round(price, 2)
    return round(price, 2)


def time_to_minute_offset(time_str: str) -> int:
    """Convert HH:MM session time to minutes from 9:30 open."""
    parts = time_str.strip().split(":")
    h, m = int(parts[0]), int(parts[1])
    open_mins = 9 * 60 + 30
    return max(0, h * 60 + m - open_mins)


def minute_offset_to_time(offset: int) -> str:
    total = 9 * 60 + 30 + offset
    return f"{total // 60}:{total % 60:02d}"


def _ensure_csv(path: Path, columns: List[str]) -> None:
    if not path.is_file():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=columns).writeheader()


def ensure_files() -> None:
    _ensure_csv(SCENARIOS_FILE, SCENARIO_COLUMNS)
    _ensure_csv(CANDLES_FILE, CANDLE_COLUMNS)
    _ensure_csv(RESULTS_FILE, RESULT_COLUMNS)
    if not SCENARIOS_FILE.is_file() or _count_scenarios() < 500:
        generate_library()


def _count_scenarios() -> int:
    if not SCENARIOS_FILE.is_file():
        return 0
    try:
        return sum(1 for _ in SCENARIOS_FILE.open(encoding="utf-8")) - 1
    except OSError:
        return 0


def _build_scenario(idx: int, market: str, setup: str, rng: random.Random) -> ReplayScenario:
    base = MARKET_BASES.get(market, 480.0)
    tick = _tick(market, base)
    or_size = base * rng.uniform(0.003, 0.012)
    mid = base + rng.uniform(-or_size, or_size)
    or_high = _round_px(mid + or_size / 2, market)
    or_low = _round_px(mid - or_size / 2, market)
    pdh = _round_px(mid + or_size * rng.uniform(0.5, 1.2), market)
    pdl = _round_px(mid - or_size * rng.uniform(0.5, 1.2), market)
    wh = _round_px(pdh + or_size * rng.uniform(0.2, 0.8), market)
    wl = _round_px(pdl - or_size * rng.uniform(0.2, 0.8), market)
    vwap = _round_px(or_low + (or_high - or_low) * rng.uniform(0.35, 0.65), market)

    yr = rng.randint(2023, 2025)
    mo = rng.randint(1, 12)
    dy = rng.randint(1, 28)
    cutoff = rng.choice(["09:45", "10:00", "10:15", "10:30"])

    outcomes = {
        "ORB long": "Breakout holds above OR high; trend continues toward session highs.",
        "ORB short": "Breakdown below OR low; sellers control through midday.",
        "trend day up": "Steady trend day up; pullbacks are shallow.",
        "trend day down": "Trend day down; rallies fail at VWAP.",
        "fakeout": "Break above OR fails; price reverses back into range.",
        "chop": "Range-bound chop; no clean follow-through.",
        "VWAP reclaim": "Price reclaims VWAP and holds; buyers step in.",
        "VWAP rejection": "VWAP rejection; lower highs form.",
    }

    return ReplayScenario(
        scenario_id=f"qr_{market.lower()}_{idx:04d}",
        market=market,
        date=f"{yr}-{mo:02d}-{dy:02d}",
        replay_cutoff_time=cutoff,
        outcome_end_time="16:00",
        previous_day_high=pdh,
        previous_day_low=pdl,
        weekly_high=wh,
        weekly_low=wl,
        opening_range_high=or_high,
        opening_range_low=or_low,
        vwap=vwap,
        setup_type=setup,
        hidden_outcome=outcomes.get(setup, "Session unfolds after cutoff."),
        difficulty=rng.choice(["beginner", "intermediate", "advanced"]),
    )


def _generate_candles(scenario: ReplayScenario, rng: random.Random) -> pd.DataFrame:
    """Generate 1-minute session candles aligned with setup type."""
    market = scenario.market
    base = (scenario.opening_range_high + scenario.opening_range_low) / 2
    tick = _tick(market, base)
    setup = scenario.setup_type.lower()
    rows: List[Dict[str, Any]] = []
    price = (scenario.opening_range_high + scenario.opening_range_low) / 2
    cutoff = time_to_minute_offset(scenario.replay_cutoff_time)
    end = min(SESSION_MINUTES, time_to_minute_offset(scenario.outcome_end_time))

    for minute in range(end + 1):
        drift = tick * rng.uniform(-0.4, 0.4)
        if minute <= 15:
            if "long" in setup or "up" in setup:
                drift = tick * rng.uniform(0.05, 0.5)
            elif "short" in setup or "down" in setup:
                drift = -tick * rng.uniform(0.05, 0.5)
        elif minute <= cutoff:
            drift = tick * rng.uniform(-0.3, 0.3)
        else:
            if "long" in setup or "up" in setup or "reclaim" in setup:
                drift = tick * rng.uniform(0.02, 0.35)
            elif "short" in setup or "down" in setup or "rejection" in setup:
                drift = -tick * rng.uniform(0.02, 0.35)
            elif "fakeout" in setup:
                drift = -tick * rng.uniform(0.1, 0.4) if minute > cutoff + 10 else tick * 0.2
            else:
                drift = tick * rng.uniform(-0.25, 0.25)

        o = price
        h = o + abs(drift) + tick * rng.uniform(0.2, 1.0)
        l = o - abs(drift) - tick * rng.uniform(0.2, 1.0)
        c = o + drift
        h, l = max(h, o, c), min(l, o, c)
        vol = int(rng.uniform(500, 5000) * (1.4 if minute <= 15 else 1.0))
        price = _round_px(c, market)

        rows.append({
            "scenario_id": scenario.scenario_id,
            "bar_time": minute_offset_to_time(minute),
            "minute_offset": minute,
            "open": _round_px(o, market),
            "high": _round_px(h, market),
            "low": _round_px(l, market),
            "close": price,
            "volume": vol,
        })

    return pd.DataFrame(rows)


def generate_library(min_total: int = 500) -> None:
    scenarios: List[ReplayScenario] = []
    candles: List[pd.DataFrame] = []
    idx = 0

    for market, count in SCENARIO_TARGETS.items():
        setups = list(SETUP_TYPES)
        rng = random.Random(hash(market) % 99999)
        rng.shuffle(setups)
        for j in range(count):
            setup = setups[j % len(setups)]
            s = _build_scenario(idx, market, setup, rng)
            scenarios.append(s)
            candles.append(_generate_candles(s, _rng(s.scenario_id)))
            idx += 1

    while len(scenarios) < min_total:
        market = random.choice(MARKETS)
        setup = random.choice(SETUP_TYPES)
        s = _build_scenario(idx, market, setup, random.Random(idx))
        scenarios.append(s)
        candles.append(_generate_candles(s, _rng(s.scenario_id)))
        idx += 1

    with SCENARIOS_FILE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SCENARIO_COLUMNS)
        w.writeheader()
        for s in scenarios:
            w.writerow(s.to_row())

    combined = pd.concat(candles, ignore_index=True)[CANDLE_COLUMNS]
    combined.to_csv(CANDLES_FILE, index=False)


def load_scenarios(market: Optional[str] = None) -> List[ReplayScenario]:
    ensure_files()
    df = pd.read_csv(SCENARIOS_FILE)
    if market:
        df = df[df["market"].astype(str).str.upper() == market.upper()]
    return [ReplayScenario.from_row(row) for _, row in df.iterrows()]


def pick_scenario(market: Optional[str] = None) -> ReplayScenario:
    pool = load_scenarios(market)
    if not pool:
        ensure_files()
        pool = load_scenarios(market)
    return random.choice(pool)


def load_candles_1m(scenario_id: str) -> pd.DataFrame:
    ensure_files()
    if not CANDLES_FILE.is_file():
        return pd.DataFrame(columns=CANDLE_COLUMNS)
    df = pd.read_csv(CANDLES_FILE)
    out = df[df["scenario_id"].astype(str) == scenario_id].sort_values("minute_offset")
    if out.empty:
        sc = next((s for s in load_scenarios() if s.scenario_id == scenario_id), None)
        if sc:
            out = _generate_candles(sc, _rng(scenario_id))
        else:
            return pd.DataFrame(columns=CANDLE_COLUMNS)
    return out


def aggregate_timeframe(candles_1m: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if candles_1m.empty:
        return candles_1m
    if timeframe == "1m":
        return candles_1m.copy()

    df = candles_1m.copy()
    if timeframe == "1d":
        return pd.DataFrame([{
            "bar_time": df["bar_time"].iloc[0],
            "minute_offset": int(df["minute_offset"].iloc[0]),
            "open": float(df["open"].iloc[0]),
            "high": float(df["high"].max()),
            "low": float(df["low"].min()),
            "close": float(df["close"].iloc[-1]),
            "volume": int(df["volume"].sum()),
        }])

    mins = {"5m": 5, "15m": 15, "1h": 60}[timeframe]
    df["bucket"] = df["minute_offset"] // mins
    agg = df.groupby("bucket", as_index=False).agg(
        bar_time=("bar_time", "first"),
        minute_offset=("minute_offset", "min"),
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    )
    return agg


def visible_candles(
    candles: pd.DataFrame,
    cutoff_time: str,
    revealed: bool,
    end_time: str = "16:00",
) -> pd.DataFrame:
    cutoff = time_to_minute_offset(cutoff_time)
    if revealed:
        end = time_to_minute_offset(end_time)
        return candles[candles["minute_offset"] <= end].copy()
    return candles[candles["minute_offset"] <= cutoff].copy()


def validate_trade_plan(plan: TradePlan) -> Tuple[bool, List[str], float]:
    warnings: List[str] = []
    d = plan.direction.strip()
    rr = 0.0

    if d == "No Trade":
        if not plan.notes.strip():
            warnings.append("Notes are required for No Trade.")
        return len(warnings) == 0, warnings, rr

    if d not in ("Long", "Short"):
        warnings.append("Choose Long, Short, or No Trade.")
        return False, warnings, rr

    if plan.entry <= 0 or plan.stop_loss <= 0 or plan.take_profit <= 0:
        warnings.append("Entry, stop loss, and take profit are required.")
        return False, warnings, rr

    if d == "Long":
        if plan.stop_loss >= plan.entry:
            warnings.append("Stop must be below entry on a long.")
        if plan.take_profit <= plan.entry:
            warnings.append("Take profit must be above entry on a long.")
    else:
        if plan.stop_loss <= plan.entry:
            warnings.append("Stop must be above entry on a short.")
        if plan.take_profit >= plan.entry:
            warnings.append("Take profit must be below entry on a short.")

    risk = abs(plan.entry - plan.stop_loss)
    reward = abs(plan.take_profit - plan.entry)
    rr = reward / risk if risk > 0 else 0.0
    if risk > 0 and rr < 2.0:
        warnings.append(f"Reward:risk is {rr:.1f}:1 — aim for at least 2:1.")

    ok = len([w for w in warnings if "aim for" not in w]) == 0
    return ok, warnings, round(rr, 2)


def run_backtest(
    candles_1m: pd.DataFrame,
    scenario: ReplayScenario,
    plan: TradePlan,
) -> BacktestOutcome:
    if plan.direction.strip() == "No Trade":
        return BacktestOutcome(
            result="NO TRADE",
            exit_price=0.0,
            r_multiple=0.0,
            simulated_pnl=0.0,
            trigger_time="",
            trigger_minute=None,
            explanation="No trade taken — capital preserved for a clearer setup.",
        )

    direction = plan.direction.strip()
    cutoff = time_to_minute_offset(scenario.replay_cutoff_time)
    end = time_to_minute_offset(scenario.outcome_end_time)
    future = candles_1m[
        (candles_1m["minute_offset"] > cutoff) & (candles_1m["minute_offset"] <= end)
    ].sort_values("minute_offset")

    risk = abs(plan.entry - plan.stop_loss)
    reward = abs(plan.take_profit - plan.entry)
    r_win = reward / risk if risk > 0 else 0.0

    for _, row in future.iterrows():
        low = float(row["low"])
        high = float(row["high"])
        minute = int(row["minute_offset"])
        t = str(row["bar_time"])

        if direction == "Long":
            stop_hit = low <= plan.stop_loss
            target_hit = high >= plan.take_profit
        else:
            stop_hit = high >= plan.stop_loss
            target_hit = low <= plan.take_profit

        if stop_hit and target_hit:
            return BacktestOutcome(
                result="AMBIGUOUS",
                exit_price=plan.entry,
                r_multiple=0.0,
                simulated_pnl=0.0,
                trigger_time=t,
                trigger_minute=minute,
                explanation=(
                    f"Both stop ({plan.stop_loss}) and target ({plan.take_profit}) "
                    f"were touched in the same candle at {t}. Real fill order is unknown."
                ),
            )
        if stop_hit:
            pnl = -plan.risk_amount if plan.risk_amount > 0 else -risk
            return BacktestOutcome(
                result="LOSS",
                exit_price=plan.stop_loss,
                r_multiple=-1.0,
                simulated_pnl=round(pnl, 2),
                trigger_time=t,
                trigger_minute=minute,
                explanation=f"Stop loss hit first at {t}.",
            )
        if target_hit:
            pnl = plan.risk_amount * r_win if plan.risk_amount > 0 else reward
            return BacktestOutcome(
                result="WIN",
                exit_price=plan.take_profit,
                r_multiple=round(r_win, 2),
                simulated_pnl=round(pnl, 2),
                trigger_time=t,
                trigger_minute=minute,
                explanation=f"Take profit hit first at {t}.",
            )

    return BacktestOutcome(
        result="NO HIT",
        exit_price=float(future.iloc[-1]["close"]) if not future.empty else plan.entry,
        r_multiple=0.0,
        simulated_pnl=0.0,
        trigger_time=str(future.iloc[-1]["bar_time"]) if not future.empty else "",
        trigger_minute=int(future.iloc[-1]["minute_offset"]) if not future.empty else None,
        explanation="Neither stop nor target was hit before the outcome window ended.",
    )


def save_result(
    scenario: ReplayScenario,
    timeframe: str,
    plan: TradePlan,
    outcome: BacktestOutcome,
    reward_risk: float,
) -> None:
    _ensure_csv(RESULTS_FILE, RESULT_COLUMNS)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_id": scenario.scenario_id,
        "market": scenario.market,
        "timeframe": timeframe,
        "direction": plan.direction,
        "entry": plan.entry,
        "stop_loss": plan.stop_loss,
        "take_profit": plan.take_profit,
        "risk_amount": plan.risk_amount,
        "reward_risk": reward_risk,
        "result": outcome.result,
        "r_multiple": outcome.r_multiple,
        "simulated_pnl": outcome.simulated_pnl,
        "trigger_time": outcome.trigger_time,
        "notes": plan.notes,
    }
    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RESULT_COLUMNS, extrasaction="ignore")
        w.writerow(row)


def load_results(limit: int = 20) -> pd.DataFrame:
    ensure_files()
    if not RESULTS_FILE.is_file():
        return pd.DataFrame(columns=RESULT_COLUMNS)
    try:
        df = pd.read_csv(RESULTS_FILE)
        return df.tail(limit)
    except Exception:  # noqa: BLE001
        return pd.DataFrame(columns=RESULT_COLUMNS)


def build_chart(
    candles: pd.DataFrame,
    scenario: ReplayScenario,
    plan: Optional[TradePlan] = None,
    full_width: bool = True,
    title: str = "",
) -> Any:
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:  # pragma: no cover
        return None

    if candles.empty:
        return None

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.75, 0.25],
    )

    fig.add_trace(
        go.Candlestick(
            x=candles["bar_time"],
            open=candles["open"],
            high=candles["high"],
            low=candles["low"],
            close=candles["close"],
            name="Price",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=1, col=1,
    )

    colors = ["#9e9e9e", "#ff9800", "#2196f3", "#4caf50", "#f44336", "#8bc34a"]
    levels = [
        (scenario.previous_day_high, "PDH", colors[0]),
        (scenario.previous_day_low, "PDL", colors[0]),
        (scenario.weekly_high, "Weekly High", colors[0]),
        (scenario.weekly_low, "Weekly Low", colors[0]),
        (scenario.opening_range_high, "OR High", colors[1]),
        (scenario.opening_range_low, "OR Low", colors[1]),
        (scenario.vwap, "VWAP", colors[2]),
    ]
    for price, label, color in levels:
        if price and price > 0:
            fig.add_hline(
                y=price, line_color=color, line_dash="dash",
                annotation_text=label, annotation_position="right",
                row=1, col=1,
            )

    if plan and plan.entry > 0:
        fig.add_hline(y=plan.entry, line_color=colors[3], annotation_text="Entry", row=1, col=1)
    if plan and plan.stop_loss > 0:
        fig.add_hline(y=plan.stop_loss, line_color=colors[4], annotation_text="Stop", row=1, col=1)
    if plan and plan.take_profit > 0:
        fig.add_hline(y=plan.take_profit, line_color=colors[5], annotation_text="Target", row=1, col=1)

    fig.add_trace(
        go.Bar(x=candles["bar_time"], y=candles["volume"], name="Volume", marker_color="#78909c"),
        row=2, col=1,
    )

    fig.update_layout(
        title=title or f"{scenario.market} · {scenario.date} · {scenario.setup_type}",
        xaxis_rangeslider_visible=False,
        height=620 if full_width else 480,
        margin=dict(l=40, r=20, t=50, b=40),
        dragmode="pan",
        hovermode="x unified",
        showlegend=False,
    )
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False, row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig
