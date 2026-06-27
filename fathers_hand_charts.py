"""
Father's Hand — chart replay engine (synthetic OHLCV + Plotly candlesticks).

Training only. No live data. No orders.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
CANDLES_FILE = PROJECT_DIR / "fathers_hand_candles.csv"

CANDLE_COLUMNS = [
    "scenario_id",
    "minute_offset",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

RevealPhase = Literal["pre_reveal", "1030", "1100", "1200", "close"]

# Minutes from RTH open (9:30) to each reveal milestone
REVEAL_MINUTES = {
    "pre_reveal": 15,
    "1030": 60,
    "1100": 90,
    "1200": 150,
    "close": 390,
}


@dataclass
class ChartLevels:
    or_high: float
    or_low: float
    vwap: float
    prior_day_high: float
    prior_day_low: float


@dataclass
class TradeLines:
    entry: float = 0.0
    stop: float = 0.0
    target1: float = 0.0
    target2: float = 0.0


def _rng_for_scenario(scenario_id: str) -> random.Random:
    digest = hashlib.sha256(scenario_id.encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def _tick_size(market: str, base: float) -> float:
    if market in ("EUR/USD", "GBP/USD", "AUD/USD"):
        return 0.0001
    if market == "GBP/JPY":
        return 0.01
    if market == "XAUUSD":
        return 0.1
    if market in ("BTC/USD", "ETH/USD"):
        return base * 0.0005
    if market == "NQ":
        return 0.25
    return 0.01 if base < 1000 else 0.05


def _round_price(price: float, market: str, base: float) -> float:
    decimals = 4 if market in ("EUR/USD", "GBP/USD", "AUD/USD") else 2
    if market == "NQ":
        decimals = 2
    if market in ("BTC/USD", "ETH/USD"):
        decimals = 2 if base > 1000 else 4
    return round(price, decimals)


def _parse_float(text: str, default: float = 0.0) -> float:
    try:
        cleaned = str(text).replace(",", "").strip()
        return float(cleaned) if cleaned else default
    except (TypeError, ValueError):
        return default


def parse_or_from_context(context: str, entry: float) -> Tuple[float, float]:
    """Extract OR high/low from support_resistance_context or estimate from entry."""
    import re

    high_m = re.search(r"OR high\s+([\d.]+)", context, re.I)
    low_m = re.search(r"OR low\s+([\d.]+)", context, re.I)
    if high_m and low_m:
        return float(high_m.group(1)), float(low_m.group(1))
    spread = entry * 0.004 if entry > 100 else entry * 0.002
    return round(entry + spread / 2, 4), round(entry - spread / 2, 4)


def levels_for_scenario(scenario: Any) -> ChartLevels:
    entry = float(getattr(scenario, "ideal_entry", 0) or 0)
    or_high = float(getattr(scenario, "or_high", 0) or 0)
    or_low = float(getattr(scenario, "or_low", 0) or 0)
    if or_high <= 0 or or_low <= 0:
        or_high, or_low = parse_or_from_context(
            getattr(scenario, "support_resistance_context", ""), entry or 100.0
        )
    vwap = float(getattr(scenario, "vwap_price", 0) or 0)
    if vwap <= 0:
        vwap_status = str(getattr(scenario, "vwap_status", "")).lower()
        mid = (or_high + or_low) / 2
        if "above" in vwap_status:
            vwap = mid - (or_high - or_low) * 0.15
        elif "below" in vwap_status:
            vwap = mid + (or_high - or_low) * 0.15
        else:
            vwap = mid
    pdh = _parse_float(getattr(scenario, "prior_day_high", ""), or_high)
    pdl = _parse_float(getattr(scenario, "prior_day_low", ""), or_low)
    market = getattr(scenario, "market", "QQQ")
    base = entry or or_high
    return ChartLevels(
        or_high=_round_price(or_high, market, base),
        or_low=_round_price(or_low, market, base),
        vwap=_round_price(vwap, market, base),
        prior_day_high=_round_price(pdh, market, base),
        prior_day_low=_round_price(pdl, market, base),
    )


def generate_session_candles(
    scenario: Any,
    rng: Optional[random.Random] = None,
) -> pd.DataFrame:
    """
    Build synthetic 1-minute candles (9:30–16:00) aligned with scenario outcome.
    First 15 minutes = visible pre-reveal window.
    """
    r = rng if rng is not None else _rng_for_scenario(scenario.scenario_id)
    market = scenario.market
    levels = levels_for_scenario(scenario)
    entry = float(scenario.ideal_entry or levels.or_high)
    stop = float(scenario.ideal_stop or levels.or_low)
    target = float(scenario.ideal_target or levels.or_high)
    base = entry if entry > 0 else (levels.or_high + levels.or_low) / 2
    tick = _tick_size(market, base)

    best = str(scenario.best_choice)
    setup = str(scenario.setup_type).lower()
    resolution = str(getattr(scenario, "outcome_resolution", "") or _infer_resolution(scenario))

    rows: List[Dict[str, Any]] = []
    price = (levels.or_high + levels.or_low) / 2
    cum_pv = 0.0
    cum_vol = 0.0

    for minute in range(REVEAL_MINUTES["close"] + 1):
        drift = 0.0
        vol_mult = 1.0

        if minute < 15:
            # Opening range — first 15 minutes
            if "long" in setup or best == "Long":
                drift = tick * r.uniform(0.1, 0.6)
            elif "short" in setup or best == "Short":
                drift = -tick * r.uniform(0.1, 0.6)
            elif best in ("No Trade", "Watch"):
                drift = tick * r.uniform(-0.3, 0.3)
            else:
                drift = tick * r.uniform(-0.2, 0.5)
            vol_mult = 1.4
        elif minute < 60:
            drift = _post_or_drift(best, resolution, minute, tick, r, bullish=True)
        elif minute < 90:
            drift = _post_or_drift(best, resolution, minute, tick, r, bullish=True) * 0.8
        elif minute < 150:
            drift = _post_or_drift(best, resolution, minute, tick, r, bullish=False) * 0.6
        else:
            drift = _post_or_drift(best, resolution, minute, tick, r, bullish=False) * 0.4

        if best == "No Trade" and minute >= 15:
            drift = tick * r.uniform(-0.35, 0.35)
            vol_mult = 0.7

        o = price
        h = o + abs(drift) + tick * r.uniform(0.2, 1.2)
        l = o - abs(drift) - tick * r.uniform(0.2, 1.2)
        c = o + drift

        # Nudge path toward ideal outcome after OR
        if minute >= 20 and best == "Long" and resolution == "target_first":
            if c < target:
                c += tick * r.uniform(0, 0.4)
        elif minute >= 20 and best == "Short" and resolution == "target_first":
            if c > target:
                c -= tick * r.uniform(0, 0.4)
        elif minute >= 20 and best in ("Long", "Short") and resolution == "stop_first":
            if best == "Long" and c > stop:
                c = stop + tick * r.uniform(-0.2, 0.1)
            if best == "Short" and c < stop:
                c = stop - tick * r.uniform(-0.2, 0.1)

        h = max(h, o, c)
        l = min(l, o, c)
        vol = int(r.uniform(800, 4000) * vol_mult)

        price = _round_price(c, market, base)
        cum_pv += price * vol
        cum_vol += vol

        rows.append({
            "scenario_id": scenario.scenario_id,
            "minute_offset": minute,
            "open": _round_price(o, market, base),
            "high": _round_price(h, market, base),
            "low": _round_price(l, market, base),
            "close": price,
            "volume": vol,
        })

    df = pd.DataFrame(rows)
    # Pin OR window to levels
    or_slice = df[df["minute_offset"] < 15]
    if not or_slice.empty:
        df.loc[df["minute_offset"] < 15, "high"] = df.loc[
            df["minute_offset"] < 15, "high"
        ].clip(upper=levels.or_high + tick)
        df.loc[df["minute_offset"] < 15, "low"] = df.loc[
            df["minute_offset"] < 15, "low"
        ].clip(lower=levels.or_low - tick)
    return df


def _infer_resolution(scenario: Any) -> str:
    best = str(scenario.best_choice)
    if best in ("No Trade", "Watch"):
        return "no_trade_best"
    if best == "Long":
        return "target_first" if "fakeout" not in str(scenario.setup_type).lower() else "stop_first"
    if best == "Short":
        return "target_first" if "fakeout" not in str(scenario.setup_type).lower() else "stop_first"
    return "neither"


def _post_or_drift(
    best: str,
    resolution: str,
    minute: int,
    tick: float,
    r: random.Random,
    bullish: bool,
) -> float:
    if best == "Long":
        if resolution == "target_first":
            return tick * r.uniform(0.05, 0.45)
        if resolution == "stop_first":
            return -tick * r.uniform(0.1, 0.5)
        return tick * r.uniform(-0.2, 0.3)
    if best == "Short":
        if resolution == "target_first":
            return -tick * r.uniform(0.05, 0.45)
        if resolution == "stop_first":
            return tick * r.uniform(0.1, 0.5)
        return tick * r.uniform(-0.3, 0.2)
    return tick * r.uniform(-0.25, 0.25)


def load_candles_for_scenario(scenario_id: str) -> pd.DataFrame:
    if not CANDLES_FILE.is_file():
        return pd.DataFrame(columns=CANDLE_COLUMNS)
    try:
        df = pd.read_csv(CANDLES_FILE)
        if df.empty:
            return df
        return df[df["scenario_id"].astype(str) == scenario_id].sort_values("minute_offset")
    except Exception:  # noqa: BLE001
        return pd.DataFrame(columns=CANDLE_COLUMNS)


def get_candles(scenario: Any) -> pd.DataFrame:
    """Load from CSV or generate on the fly."""
    stored = load_candles_for_scenario(scenario.scenario_id)
    if not stored.empty:
        return stored
    return generate_session_candles(scenario)


def candles_visible_slice(candles: pd.DataFrame, phase: RevealPhase) -> pd.DataFrame:
    max_minute = REVEAL_MINUTES.get(phase, 15)
    return candles[candles["minute_offset"] <= max_minute].copy()


def aggregate_to_15m(candles: pd.DataFrame) -> pd.DataFrame:
    """Collapse 1m candles into 15m bars for cleaner OR display."""
    if candles.empty:
        return candles
    candles = candles.copy()
    candles["bar"] = candles["minute_offset"] // 15
    agg = candles.groupby("bar", as_index=False).agg(
        minute_offset=("minute_offset", "min"),
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    )
    return agg


def simulate_trade_outcome(
    candles: pd.DataFrame,
    direction: str,
    entry: float,
    stop: float,
    target1: float,
    target2: float = 0.0,
    start_minute: int = 15,
) -> Dict[str, Any]:
    """Walk forward after submit to see if stop or target hits first."""
    if direction not in ("Long", "Short") or entry <= 0 or stop <= 0 or target1 <= 0:
        return {"result": "not_applicable", "hit": None, "minute": None}

    future = candles[candles["minute_offset"] >= start_minute].sort_values("minute_offset")
    for _, row in future.iterrows():
        low = float(row["low"])
        high = float(row["high"])
        minute = int(row["minute_offset"])
        if direction == "Long":
            if low <= stop:
                return {"result": "stop_first", "hit": "stop", "minute": minute}
            if high >= target1:
                return {"result": "target_first", "hit": "target1", "minute": minute}
            if target2 > 0 and high >= target2:
                return {"result": "target_first", "hit": "target2", "minute": minute}
        else:
            if high >= stop:
                return {"result": "stop_first", "hit": "stop", "minute": minute}
            if low <= target1:
                return {"result": "target_first", "hit": "target1", "minute": minute}
            if target2 > 0 and low <= target2:
                return {"result": "target_first", "hit": "target2", "minute": minute}
    return {"result": "neither", "hit": None, "minute": None}


def build_plotly_figure(
    candles: pd.DataFrame,
    levels: ChartLevels,
    phase: RevealPhase = "pre_reveal",
    trade_lines: Optional[TradeLines] = None,
    show_full_width: bool = True,
    title: str = "",
) -> Any:
    """Build interactive Plotly candlestick chart."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:  # pragma: no cover
        return None

    visible = candles_visible_slice(candles, phase)
    if visible.empty:
        return None

    # Use 15m aggregation when showing pre-reveal only
    if phase == "pre_reveal" and len(visible) <= 20:
        plot_df = aggregate_to_15m(visible)
    else:
        plot_df = visible

    times = [_minute_label(int(m)) for m in plot_df["minute_offset"]]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Candlestick(
            x=times,
            open=plot_df["open"],
            high=plot_df["high"],
            low=plot_df["low"],
            close=plot_df["close"],
            name="Price",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        )
    )

    _add_hline(fig, levels.or_high, "OR High", "#ff9800", "dash")
    _add_hline(fig, levels.or_low, "OR Low", "#ff9800", "dash")
    _add_hline(fig, levels.vwap, "VWAP", "#2196f3", "dot")
    _add_hline(fig, levels.prior_day_high, "Prior Day High", "#9e9e9e", "dashdot")
    _add_hline(fig, levels.prior_day_low, "Prior Day Low", "#9e9e9e", "dashdot")

    if trade_lines and trade_lines.entry > 0:
        _add_hline(fig, trade_lines.entry, "Entry", "#4caf50", "solid")
    if trade_lines and trade_lines.stop > 0:
        _add_hline(fig, trade_lines.stop, "Stop", "#f44336", "solid")
    if trade_lines and trade_lines.target1 > 0:
        _add_hline(fig, trade_lines.target1, "TP1", "#8bc34a", "solid")
    if trade_lines and trade_lines.target2 > 0:
        _add_hline(fig, trade_lines.target2, "TP2", "#cddc39", "solid")

    fig.update_layout(
        title=title or "Session replay",
        xaxis_title="Time (ET)",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=520 if show_full_width else 400,
        margin=dict(l=40, r=20, t=50, b=40),
        dragmode="pan",
        hovermode="x unified",
    )
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)
    return fig


def _add_hline(fig: Any, price: float, label: str, color: str, dash: str) -> None:
    if price and price > 0:
        fig.add_hline(
            y=price,
            line_color=color,
            line_dash=dash,
            annotation_text=label,
            annotation_position="right",
        )


def _minute_label(minute: int) -> str:
    hour = 9 + (30 + minute) // 60
    mins = (30 + minute) % 60
    return f"{hour}:{mins:02d}"


def save_candles_batch(candles_frames: List[pd.DataFrame]) -> Path:
    """Write combined candle library to CSV."""
    if not candles_frames:
        return CANDLES_FILE
    combined = pd.concat(candles_frames, ignore_index=True)
    combined = combined[CANDLE_COLUMNS]
    combined.to_csv(CANDLES_FILE, index=False)
    return CANDLES_FILE


def ensure_candles_for_scenario(scenario: Any) -> pd.DataFrame:
    """Return candles, generating and caching in memory only (CSV loaded at pick time)."""
    return get_candles(scenario)
