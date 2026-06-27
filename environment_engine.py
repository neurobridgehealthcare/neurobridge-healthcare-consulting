"""
Stage 3C — Market Environment Intelligence for QQQ ORB research.

Rule-based daily/trade features: time buckets, premarket structure, OR quality,
regime classification, and QQQ vs SPY relative strength.

Research only — not for live trading.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from zoneinfo import ZoneInfo

import backtester
from backtester import (
    BacktestMarketData,
    BacktestTrade,
    compute_summary,
    fetch_daily_qqq_range,
    load_backtest_market_data,
)
from data_provider import MISSING_KEYS_MESSAGE, load_alpaca_keys_from_env

NY = ZoneInfo("America/New_York")
UTC = timezone.utc
SESSION_OPEN = time(9, 30)
SESSION_CLOSE = time(16, 0)
OR_END = time(9, 45)
PREMARKET_OPEN = time(4, 0)

PROJECT_DIR = Path(__file__).resolve().parent
ENVIRONMENT_TRADES_FILE = PROJECT_DIR / "environment_trades.csv"
ENVIRONMENT_SUMMARY_FILE = PROJECT_DIR / "environment_summary.csv"
BEST_ENVIRONMENT_RULES_FILE = PROJECT_DIR / "best_environment_rules.json"

ProgressCb = Optional[Callable[[str], None]]

TIME_BUCKETS: List[Tuple[str, time, time]] = [
    ("9:45-10:00", time(9, 45), time(10, 0)),
    ("10:00-10:30", time(10, 0), time(10, 30)),
    ("10:30-11:00", time(10, 30), time(11, 0)),
    ("11:00-12:00", time(11, 0), time(12, 0)),
]

ENV_TRADE_COLUMNS = [
    "date",
    "direction",
    "entry",
    "stop",
    "target",
    "shares",
    "exit_price",
    "exit_reason",
    "pnl",
    "r_multiple",
    "OR_size",
    "entry_time",
    "time_bucket",
    "premarket_trend",
    "gap_percent",
    "or_body_percent",
    "or_close_location",
    "or_candle_type",
    "regime",
    "qqq_vs_spy_strength",
    "qqq_stronger_than_spy",
]

_DAY_CONTEXT_CACHE: Dict[Tuple[date, str], "DayEnvironmentContext"] = {}


@dataclass
class DayEnvironmentContext:
    session_date: date
    premarket_high: Optional[float] = None
    premarket_low: Optional[float] = None
    premarket_range: Optional[float] = None
    premarket_trend: Optional[str] = None
    gap_percent: Optional[float] = None
    open_vs_premarket_mid: Optional[str] = None
    or_size: Optional[float] = None
    or_body_percent: Optional[float] = None
    or_upper_wick_percent: Optional[float] = None
    or_lower_wick_percent: Optional[float] = None
    or_close_location: Optional[float] = None
    or_candle_type: Optional[str] = None
    session_open_qqq: Optional[float] = None
    session_open_spy: Optional[float] = None
    qqq_vwap_at_entry_idx: Dict[int, float] = field(default_factory=dict)


@dataclass
class EnvironmentResearchResult:
    trades: List[BacktestTrade] = field(default_factory=list)
    by_time_bucket: List[Dict[str, Any]] = field(default_factory=list)
    by_regime: List[Dict[str, Any]] = field(default_factory=list)
    by_premarket_trend: List[Dict[str, Any]] = field(default_factory=list)
    by_or_candle: List[Dict[str, Any]] = field(default_factory=list)
    by_relative_strength: List[Dict[str, Any]] = field(default_factory=list)
    best_combinations: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


def _to_et(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.astimezone(NY)


def _norm_minute(ts: datetime) -> datetime:
    t = ts if ts.tzinfo else ts.replace(tzinfo=UTC)
    return t.astimezone(UTC).replace(second=0, microsecond=0)


def entry_time_bucket(entry_tm: Optional[time]) -> Optional[str]:
    if entry_tm is None:
        return None
    for label, start, end in TIME_BUCKETS:
        if start <= entry_tm < end:
            return label
    if time(9, 30) <= entry_tm < time(9, 45):
        return "9:30-9:45"
    if entry_tm >= time(12, 0):
        return "12:00+"
    return "other"


def _build_premarket_index(bars: List[Any]) -> Dict[date, List[Any]]:
    by_date: Dict[date, List[Any]] = {}
    for bar in bars:
        et = _to_et(bar.timestamp)
        tm = et.time()
        if PREMARKET_OPEN <= tm < SESSION_OPEN:
            by_date.setdefault(et.date(), []).append(bar)
    for d in by_date:
        by_date[d].sort(key=lambda b: b.timestamp)
    return by_date


def fetch_extended_intraday(
    start_date: date,
    end_date: date,
) -> Tuple[Dict[str, List[Any]], Optional[str]]:
    """QQQ + SPY minute bars from 4:00 ET (premarket) through session close."""
    keys = load_alpaca_keys_from_env()
    if keys is None:
        return {}, MISSING_KEYS_MESSAGE
    api_key, secret_key = keys
    try:
        from alpaca.common.exceptions import APIError
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame

        start_et = datetime.combine(start_date, PREMARKET_OPEN, tzinfo=NY) - timedelta(days=1)
        end_et = datetime.combine(end_date, SESSION_CLOSE, tzinfo=NY) + timedelta(minutes=2)
        client = StockHistoricalDataClient(api_key, secret_key)
        req = StockBarsRequest(
            symbol_or_symbols=["QQQ", "SPY"],
            timeframe=TimeFrame.Minute,
            start=start_et.astimezone(UTC),
            end=end_et.astimezone(UTC),
        )
        bar_set = client.get_stock_bars(req)
    except Exception as exc:  # noqa: BLE001
        return {}, f"Could not load extended bars: {exc}"

    out: Dict[str, List[Any]] = {"QQQ": [], "SPY": []}
    if bar_set is None or not getattr(bar_set, "data", None):
        return out, None
    for sym, lst in bar_set.data.items():
        out[str(sym)] = sorted(list(lst), key=lambda b: b.timestamp)
    return out, None


@dataclass
class EnvironmentMarketBundle:
    market: BacktestMarketData
    premarket_qqq: Dict[date, List[Any]]
    prev_close_qqq: Dict[date, float]
    spy_lookup: Dict[datetime, Any]


_ENV_MARKET_CACHE: Dict[str, EnvironmentMarketBundle] = {}


def load_environment_market_bundle(
    start_date: date,
    end_date: date,
    progress: ProgressCb = None,
    session_cache: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[EnvironmentMarketBundle], Optional[str]]:
    cache_key = f"{start_date.isoformat()}_{end_date.isoformat()}"
    if session_cache is not None and cache_key in session_cache:
        if progress:
            progress("Using cached environment market data…")
        return session_cache[cache_key], None
    if cache_key in _ENV_MARKET_CACHE:
        if progress:
            progress("Using cached environment market data (memory)…")
        bundle = _ENV_MARKET_CACHE[cache_key]
        if session_cache is not None:
            session_cache[cache_key] = bundle
        return bundle, None

    if progress:
        progress("Loading session bars for environment research…")
    market, err = load_backtest_market_data(
        start_date - timedelta(days=60),
        end_date,
        need_daily_ema=False,
        need_rvol=True,
        progress=progress,
    )
    if err or market is None:
        return None, err

    if progress:
        progress("Loading extended (premarket) bars…")
    extended, xerr = fetch_extended_intraday(start_date, end_date)
    if xerr and not extended.get("QQQ"):
        extended = {"QQQ": market.qqq_all, "SPY": market.spy_all}

    premarket_qqq = _build_premarket_index(extended.get("QQQ", []))

    if progress:
        progress("Loading QQQ daily closes for gap calculation…")
    daily, derr = fetch_daily_qqq_range(start_date - timedelta(days=30), end_date)
    prev_close: Dict[date, float] = {}
    if daily:
        daily_rows: List[Tuple[date, float]] = []
        for bar in daily:
            daily_rows.append((_to_et(bar.timestamp).date(), float(bar.close)))
        daily_rows.sort(key=lambda x: x[0])
        for i in range(1, len(daily_rows)):
            prev_close[daily_rows[i][0]] = daily_rows[i - 1][1]

    bundle = EnvironmentMarketBundle(
        market=market,
        premarket_qqq=premarket_qqq,
        prev_close_qqq=prev_close,
        spy_lookup=market.spy_lookup,
    )
    _ENV_MARKET_CACHE[cache_key] = bundle
    if session_cache is not None:
        session_cache[cache_key] = bundle
    return bundle, None


def clear_day_context_cache() -> None:
    """Reset per-day feature cache (call before a new Stage 3D assessment)."""
    _DAY_CONTEXT_CACHE.clear()


def load_environment_bundle_for_session(
    session_date: date,
    progress: ProgressCb = None,
    session_cache: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[EnvironmentMarketBundle], Optional[str]]:
    """
    Load QQQ/SPY intraday data focused on ``session_date`` for Stage 3D assessment.
    Cache key is per session date so assessments do not reuse the wrong bar window.
    """
    cache_key = f"session_{session_date.isoformat()}"
    if session_cache is not None and cache_key in session_cache:
        if progress:
            progress(f"Using cached session data for {session_date}…")
        return session_cache[cache_key], None
    if cache_key in _ENV_MARKET_CACHE:
        if progress:
            progress(f"Using cached session data for {session_date}…")
        bundle = _ENV_MARKET_CACHE[cache_key]
        if session_cache is not None:
            session_cache[cache_key] = bundle
        return bundle, None

    if progress:
        progress(f"Loading QQQ/SPY session bars for {session_date}…")
    market, err = load_backtest_market_data(
        session_date,
        session_date,
        need_daily_ema=False,
        need_rvol=False,
        progress=progress,
    )
    if err or market is None:
        return None, err

    qqq_sess = market.qqq_by_date.get(session_date, [])
    spy_sess = market.spy_by_date.get(session_date, [])
    if not qqq_sess:
        return None, (
            f"No QQQ regular-session bars for {session_date} "
            "(weekend, holiday, or data not available from Alpaca)."
        )
    if not spy_sess:
        return None, (
            f"No SPY regular-session bars for {session_date} "
            "(weekend, holiday, or data not available from Alpaca)."
        )

    if progress:
        progress(f"Loading premarket bars for {session_date}…")
    extended, _ = fetch_extended_intraday(session_date, session_date)
    if not extended.get("QQQ"):
        extended = {"QQQ": market.qqq_all, "SPY": market.spy_all}
    premarket_qqq = _build_premarket_index(extended.get("QQQ", []))

    if progress:
        progress("Loading prior close for gap calculation…")
    daily, _ = fetch_daily_qqq_range(session_date - timedelta(days=14), session_date)
    prev_close: Dict[date, float] = {}
    if daily:
        daily_rows: List[Tuple[date, float]] = []
        for bar in daily:
            daily_rows.append((_to_et(bar.timestamp).date(), float(bar.close)))
        daily_rows.sort(key=lambda x: x[0])
        for i in range(1, len(daily_rows)):
            prev_close[daily_rows[i][0]] = daily_rows[i - 1][1]

    bundle = EnvironmentMarketBundle(
        market=market,
        premarket_qqq=premarket_qqq,
        prev_close_qqq=prev_close,
        spy_lookup=market.spy_lookup,
    )
    _ENV_MARKET_CACHE[cache_key] = bundle
    if session_cache is not None:
        session_cache[cache_key] = bundle
    return bundle, None


def _compute_or_quality(or_bars: List[Any]) -> Dict[str, Optional[float]]:
    if not or_bars:
        return {
            "or_size": None,
            "or_body_percent": None,
            "or_upper_wick_percent": None,
            "or_lower_wick_percent": None,
            "or_close_location": None,
            "or_candle_type": None,
        }
    highs = [float(b.high) for b in or_bars]
    lows = [float(b.low) for b in or_bars]
    o_open = float(or_bars[0].open)
    o_close = float(or_bars[-1].close)
    o_high = max(highs)
    o_low = min(lows)
    rng = o_high - o_low
    if rng <= 0:
        return {
            "or_size": 0.0,
            "or_body_percent": None,
            "or_upper_wick_percent": None,
            "or_lower_wick_percent": None,
            "or_close_location": None,
            "or_candle_type": "neutral",
        }
    body = abs(o_close - o_open)
    top = max(o_open, o_close)
    bottom = min(o_open, o_close)
    upper = o_high - top
    lower = bottom - o_low
    candle = "bullish" if o_close > o_open else ("bearish" if o_close < o_open else "neutral")
    return {
        "or_size": rng,
        "or_body_percent": 100.0 * body / rng,
        "or_upper_wick_percent": 100.0 * upper / rng,
        "or_lower_wick_percent": 100.0 * lower / rng,
        "or_close_location": (o_close - o_low) / rng,
        "or_candle_type": candle,
    }


def _vwap_slope(session: List[Any], end_idx: int, lookback: int = 15) -> Optional[float]:
    if end_idx < 1 or not session:
        return None
    start_idx = max(0, end_idx - lookback)
    vwap_series = backtester.cumulative_vwap_series(session[: end_idx + 1])
    if len(vwap_series) < 2:
        return None
    v0 = vwap_series[start_idx]
    v1 = vwap_series[end_idx]
    if v0 <= 0:
        return None
    return (v1 - v0) / v0


def _classify_regime(
    *,
    gap_pct: Optional[float],
    qqq_vs_vwap: Optional[str],
    vwap_slope: Optional[float],
    range_expansion: Optional[float],
    close_loc_in_range: Optional[float],
    open_vs_pm_mid: Optional[str],
) -> Optional[str]:
    gap = gap_pct if gap_pct is not None else 0.0
    slope = vwap_slope if vwap_slope is not None else 0.0
    expansion = range_expansion if range_expansion is not None else 0.0
    close_loc = close_loc_in_range if close_loc_in_range is not None else 0.5

    if gap >= 0.25 and open_vs_pm_mid == "above" and qqq_vs_vwap == "above" and slope > 0:
        return "Gap Up Continuation"
    if gap <= -0.25 and open_vs_pm_mid == "below" and qqq_vs_vwap == "below" and slope < 0:
        return "Gap Down Continuation"
    if abs(gap) >= 0.2 and (
        (gap > 0 and qqq_vs_vwap == "below")
        or (gap < 0 and qqq_vs_vwap == "above")
    ):
        return "Mean Reversion"
    if slope > 0.0005 and qqq_vs_vwap == "above" and expansion > 0.3:
        return "Trend Up"
    if slope < -0.0005 and qqq_vs_vwap == "below" and expansion > 0.3:
        return "Trend Down"
    if abs(slope) < 0.0003 and 0.35 <= close_loc <= 0.65:
        return "Chop"
    if qqq_vs_vwap == "above":
        return "Trend Up"
    if qqq_vs_vwap == "below":
        return "Trend Down"
    return "Chop"


def build_day_context(
    session_date: date,
    bundle: EnvironmentMarketBundle,
) -> DayEnvironmentContext:
    cache_key = (session_date, "ctx")
    if cache_key in _DAY_CONTEXT_CACHE:
        return _DAY_CONTEXT_CACHE[cache_key]

    ctx = DayEnvironmentContext(session_date=session_date)
    market = bundle.market
    qqq_sess = market.qqq_by_date.get(session_date, [])
    spy_sess = market.spy_by_date.get(session_date, [])

    pm_bars = bundle.premarket_qqq.get(session_date, [])
    if pm_bars:
        pm_highs = [float(b.high) for b in pm_bars]
        pm_lows = [float(b.low) for b in pm_bars]
        ctx.premarket_high = max(pm_highs)
        ctx.premarket_low = min(pm_lows)
        ctx.premarket_range = ctx.premarket_high - ctx.premarket_low
        pm_open = float(pm_bars[0].open)
        pm_close = float(pm_bars[-1].close)
        if pm_close > pm_open * 1.0005:
            ctx.premarket_trend = "up"
        elif pm_close < pm_open * 0.9995:
            ctx.premarket_trend = "down"
        else:
            ctx.premarket_trend = "flat"

    if qqq_sess:
        ctx.session_open_qqq = float(qqq_sess[0].open)
        prev = bundle.prev_close_qqq.get(session_date)
        if prev and prev > 0:
            ctx.gap_percent = 100.0 * (ctx.session_open_qqq - prev) / prev
        if ctx.premarket_high is not None and ctx.premarket_low is not None:
            pm_mid = (ctx.premarket_high + ctx.premarket_low) / 2.0
            if ctx.session_open_qqq > pm_mid:
                ctx.open_vs_premarket_mid = "above"
            elif ctx.session_open_qqq < pm_mid:
                ctx.open_vs_premarket_mid = "below"
            else:
                ctx.open_vs_premarket_mid = "at"

    or_bars = backtester._or_window_bars(qqq_sess)
    or_q = _compute_or_quality(or_bars)
    ctx.or_size = or_q["or_size"]
    ctx.or_body_percent = or_q["or_body_percent"]
    ctx.or_upper_wick_percent = or_q["or_upper_wick_percent"]
    ctx.or_lower_wick_percent = or_q["or_lower_wick_percent"]
    ctx.or_close_location = or_q["or_close_location"]
    ctx.or_candle_type = or_q["or_candle_type"]

    if spy_sess:
        ctx.session_open_spy = float(spy_sess[0].open)

    _DAY_CONTEXT_CACHE[cache_key] = ctx
    return ctx


def _find_bar_index(session: List[Any], entry_tm: time) -> int:
    for i, bar in enumerate(session):
        if _to_et(bar.timestamp).time() == entry_tm:
            return i
    for i, bar in enumerate(session):
        et = _to_et(bar.timestamp)
        if et.time() >= entry_tm:
            return i
    return max(0, len(session) - 1)


def _relative_strength_at_entry(
    bundle: EnvironmentMarketBundle,
    session_date: date,
    entry_tm: Optional[time],
) -> Tuple[Optional[str], Optional[bool], Optional[bool]]:
    market = bundle.market
    qqq_sess = market.qqq_by_date.get(session_date, [])
    spy_sess = market.spy_by_date.get(session_date, [])
    if not qqq_sess or not spy_sess or entry_tm is None:
        return None, None, None
    ctx = build_day_context(session_date, bundle)
    if ctx.session_open_qqq is None or ctx.session_open_spy is None:
        return None, None, None

    q_idx = _find_bar_index(qqq_sess, entry_tm)
    q_bar = qqq_sess[q_idx]
    spy_bar = bundle.spy_lookup.get(_norm_minute(q_bar.timestamp))
    if spy_bar is None:
        return None, None, None

    q_pct = 100.0 * (float(q_bar.close) - ctx.session_open_qqq) / ctx.session_open_qqq
    s_pct = 100.0 * (float(spy_bar.close) - ctx.session_open_spy) / ctx.session_open_spy
    if abs(q_pct - s_pct) < 0.02:
        label = "neutral"
        stronger = False
        weaker = False
    elif q_pct > s_pct:
        label = "QQQ stronger"
        stronger = True
        weaker = False
    else:
        label = "QQQ weaker"
        stronger = False
        weaker = True
    return label, stronger, weaker


def _regime_at_entry(
    bundle: EnvironmentMarketBundle,
    session_date: date,
    entry_tm: Optional[time],
    ctx: DayEnvironmentContext,
) -> Optional[str]:
    qqq_sess = bundle.market.qqq_by_date.get(session_date, [])
    spy_sess = bundle.market.spy_by_date.get(session_date, [])
    if not qqq_sess or entry_tm is None:
        return None
    idx = _find_bar_index(qqq_sess, entry_tm)
    bar = qqq_sess[idx]
    cl = float(bar.close)
    vwap_series = backtester.cumulative_vwap_series(qqq_sess[: idx + 1])
    vwap = vwap_series[-1] if vwap_series else cl
    qqq_vs_vwap = "above" if cl > vwap else ("below" if cl < vwap else "at")
    slope = _vwap_slope(qqq_sess, idx)

    session_high = max(float(b.high) for b in qqq_sess[: idx + 1])
    session_low = min(float(b.low) for b in qqq_sess[: idx + 1])
    rng = session_high - session_low
    or_bars = backtester._or_window_bars(qqq_sess)
    if or_bars:
        or_high = max(float(b.high) for b in or_bars)
        or_low = min(float(b.low) for b in or_bars)
    else:
        or_high, or_low = session_high, session_low
    or_rng = max(or_high - or_low, 1e-9)
    expansion = rng / or_rng - 1.0

    close_loc = (cl - session_low) / rng if rng > 0 else 0.5

    spy_confirms = False
    if spy_sess:
        spy_bar = bundle.spy_lookup.get(_norm_minute(bar.timestamp))
        if spy_bar:
            spy_vwap = backtester.cumulative_vwap_series(spy_sess[: min(idx + 1, len(spy_sess))])
            if spy_vwap:
                spy_cl = float(spy_bar.close)
                spy_confirms = (spy_cl > spy_vwap[-1]) if qqq_vs_vwap == "above" else (spy_cl < spy_vwap[-1])

    regime = _classify_regime(
        gap_pct=ctx.gap_percent,
        qqq_vs_vwap=qqq_vs_vwap,
        vwap_slope=slope,
        range_expansion=expansion,
        close_loc_in_range=close_loc,
        open_vs_pm_mid=ctx.open_vs_premarket_mid,
    )
    if spy_confirms and regime == "Chop":
        regime = "Trend Up" if qqq_vs_vwap == "above" else "Trend Down"
    return regime


def or_quality_label_from_ctx(ctx: DayEnvironmentContext) -> Optional[str]:
    """OR candle quality bucket (matches trade-level ``_or_quality_bucket`` logic)."""
    if ctx.or_candle_type is None:
        return None
    body = ctx.or_body_percent
    if body is None:
        return ctx.or_candle_type
    if body >= 60:
        body_tag = "strong_body"
    elif body >= 35:
        body_tag = "moderate_body"
    else:
        body_tag = "weak_body"
    return f"{ctx.or_candle_type}_{body_tag}"


@dataclass
class SessionEnvironmentFeatures:
    """Calculated session tags for Stage 3D before adaptive scoring."""

    session_date: date
    entry_time: Optional[time]
    time_bucket: Optional[str] = None
    premarket_trend: Optional[str] = None
    gap_percent: Optional[float] = None
    open_vs_premarket_mid: Optional[str] = None
    or_size: Optional[float] = None
    or_body_percent: Optional[float] = None
    or_close_location: Optional[float] = None
    or_candle_type: Optional[str] = None
    or_candle_quality: Optional[str] = None
    regime: Optional[str] = None
    relative_strength: Optional[str] = None
    qqq_stronger_than_spy: Optional[bool] = None
    qqq_bars: int = 0
    spy_bars: int = 0
    premarket_bars: int = 0
    warnings: List[str] = field(default_factory=list)

    def tags_for_scoring(self) -> Dict[str, Optional[str]]:
        return {
            "time_bucket": self.time_bucket,
            "regime": self.regime,
            "premarket_trend": self.premarket_trend,
            "or_candle_quality": self.or_candle_quality,
            "relative_strength": self.relative_strength,
        }

    def debug_table(self) -> List[Dict[str, Any]]:
        rows = [
            {"feature": "session_date", "value": self.session_date.isoformat()},
            {"feature": "entry_time (ET)", "value": self.entry_time.isoformat() if self.entry_time else ""},
            {"feature": "time_bucket", "value": self.time_bucket or ""},
            {"feature": "premarket_trend", "value": self.premarket_trend or ""},
            {"feature": "gap_percent", "value": self.gap_percent if self.gap_percent is not None else ""},
            {"feature": "open_vs_premarket_mid", "value": self.open_vs_premarket_mid or ""},
            {"feature": "or_size ($)", "value": self.or_size if self.or_size is not None else ""},
            {"feature": "or_body_percent", "value": self.or_body_percent if self.or_body_percent is not None else ""},
            {"feature": "or_close_location", "value": self.or_close_location if self.or_close_location is not None else ""},
            {"feature": "or_candle_type", "value": self.or_candle_type or ""},
            {"feature": "or_candle_quality", "value": self.or_candle_quality or ""},
            {"feature": "regime", "value": self.regime or ""},
            {"feature": "relative_strength", "value": self.relative_strength or ""},
            {"feature": "qqq_stronger_than_spy", "value": self.qqq_stronger_than_spy if self.qqq_stronger_than_spy is not None else ""},
            {"feature": "qqq_session_bars", "value": self.qqq_bars},
            {"feature": "spy_session_bars", "value": self.spy_bars},
            {"feature": "premarket_bars", "value": self.premarket_bars},
        ]
        return rows


def compute_session_environment_features(
    bundle: EnvironmentMarketBundle,
    session_date: date,
    entry_tm: Optional[time],
) -> SessionEnvironmentFeatures:
    """Calculate real session tags from QQQ/SPY bars before Stage 3D scoring."""
    out = SessionEnvironmentFeatures(session_date=session_date, entry_time=entry_tm)
    out.time_bucket = entry_time_bucket(entry_tm)

    market = bundle.market
    qqq_sess = market.qqq_by_date.get(session_date, [])
    spy_sess = market.spy_by_date.get(session_date, [])
    out.qqq_bars = len(qqq_sess)
    out.spy_bars = len(spy_sess)
    out.premarket_bars = len(bundle.premarket_qqq.get(session_date, []))

    if not qqq_sess:
        out.warnings.append(f"No QQQ session bars for {session_date}.")
        return out
    if not spy_sess:
        out.warnings.append(f"No SPY session bars for {session_date}.")
    if out.premarket_bars == 0:
        out.warnings.append("No premarket QQQ bars (4:00–9:30 ET) — premarket trend unavailable.")

    try:
        ctx = build_day_context(session_date, bundle)
        out.premarket_trend = ctx.premarket_trend
        out.gap_percent = ctx.gap_percent
        out.open_vs_premarket_mid = ctx.open_vs_premarket_mid
        out.or_size = ctx.or_size
        out.or_body_percent = ctx.or_body_percent
        out.or_close_location = ctx.or_close_location
        out.or_candle_type = ctx.or_candle_type
        out.or_candle_quality = or_quality_label_from_ctx(ctx)
        if ctx.or_candle_type is None:
            out.warnings.append("OR candle quality unavailable (no 9:30–9:45 OR bars).")
        if ctx.premarket_trend is None:
            out.warnings.append("Premarket trend could not be calculated.")
        if ctx.gap_percent is None:
            out.warnings.append("Gap % unavailable (missing prior daily close).")
    except Exception as exc:  # noqa: BLE001
        out.warnings.append(f"Day context error: {exc}")

    if entry_tm is None:
        out.warnings.append("Entry time missing — regime and relative strength skipped.")
        return out

    try:
        ctx = build_day_context(session_date, bundle)
        out.regime = _regime_at_entry(bundle, session_date, entry_tm, ctx)
        if out.regime is None:
            out.warnings.append("Market regime could not be classified at entry time.")
    except Exception as exc:  # noqa: BLE001
        out.warnings.append(f"Regime calculation error: {exc}")

    try:
        strength, stronger, _ = _relative_strength_at_entry(bundle, session_date, entry_tm)
        out.relative_strength = strength
        out.qqq_stronger_than_spy = stronger
        if strength is None:
            out.warnings.append(
                "QQQ vs SPY relative strength unavailable (missing aligned SPY bar at entry)."
            )
    except Exception as exc:  # noqa: BLE001
        out.warnings.append(f"Relative strength error: {exc}")

    return out


def collect_entry_tags(
    bundle: EnvironmentMarketBundle,
    session_date: date,
    entry_tm: Optional[time],
) -> Dict[str, Optional[str]]:
    """Rule-based environment tags at a session date + entry clock time."""
    return compute_session_environment_features(bundle, session_date, entry_tm).tags_for_scoring()


def enrich_trade(
    trade: BacktestTrade,
    bundle: EnvironmentMarketBundle,
) -> BacktestTrade:
    """Attach environment features to one trade (mutates and returns trade)."""
    try:
        ctx = build_day_context(trade.date, bundle)
        trade.time_bucket = entry_time_bucket(trade.entry_time)
        trade.premarket_trend = ctx.premarket_trend
        trade.gap_percent = ctx.gap_percent
        trade.or_body_percent = ctx.or_body_percent
        trade.or_close_location = ctx.or_close_location
        trade.or_candle_type = ctx.or_candle_type
        trade.regime = _regime_at_entry(bundle, trade.date, trade.entry_time, ctx)
        strength, stronger, _ = _relative_strength_at_entry(bundle, trade.date, trade.entry_time)
        trade.qqq_vs_spy_strength = strength
        trade.qqq_stronger_than_spy = stronger
    except Exception:  # noqa: BLE001
        pass
    return trade


def enrich_trades(
    trades: List[BacktestTrade],
    bundle: EnvironmentMarketBundle,
    progress: ProgressCb = None,
) -> List[BacktestTrade]:
    total = len(trades)
    for i, trade in enumerate(trades):
        if progress and (i == 0 or (i + 1) % 10 == 0 or i + 1 == total):
            progress(f"Enriching trades {i + 1}/{total}…")
        try:
            enrich_trade(trade, bundle)
        except Exception:  # noqa: BLE001
            continue
    return trades


def _robustness_from_trades(trades: List[BacktestTrade]) -> float:
    if not trades:
        return -1000.0
    summary = compute_summary(trades)
    try:
        from optimizer import compute_robustness_score

        return compute_robustness_score(summary, trades)
    except Exception:  # noqa: BLE001
        n = len(trades)
        pf = float(summary.get("profit_factor", 0))
        exp = float(summary.get("expectancy", 0))
        return pf * 10.0 + exp * 0.1 + n * 0.05


def _group_performance(
    trades: List[BacktestTrade],
    key_fn: Callable[[BacktestTrade], Optional[str]],
    dimension: str,
) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[BacktestTrade]] = {}
    for t in trades:
        key = key_fn(t)
        label = key if key is not None else "unknown"
        buckets.setdefault(label, []).append(t)

    rows: List[Dict[str, Any]] = []
    for label, group in sorted(buckets.items()):
        summary = compute_summary(group)
        pnls = [g.pnl for g in group]
        eq = 0.0
        peak = 0.0
        max_dd = 0.0
        for p in pnls:
            eq += p
            peak = max(peak, eq)
            max_dd = min(max_dd, eq - peak)
        rows.append(
            {
                "dimension": dimension,
                "bucket": label,
                "total_trades": int(summary["total_trades"]),
                "win_rate": round(summary["win_rate"], 4),
                "total_pnl": round(summary["total_pnl"], 2),
                "expectancy": round(summary["expectancy"], 2),
                "profit_factor": round(summary["profit_factor"], 4),
                "max_drawdown": round(max_dd, 2),
                "robustness_score": round(_robustness_from_trades(group), 2),
            }
        )
    rows.sort(key=lambda r: (r["robustness_score"], r["profit_factor"]), reverse=True)
    return rows


def _or_quality_bucket(t: BacktestTrade) -> Optional[str]:
    if t.or_candle_type is None:
        return None
    body = t.or_body_percent
    if body is None:
        return t.or_candle_type
    if body >= 60:
        body_tag = "strong_body"
    elif body >= 35:
        body_tag = "moderate_body"
    else:
        body_tag = "weak_body"
    return f"{t.or_candle_type}_{body_tag}"


def build_summary_tables(trades: List[BacktestTrade]) -> EnvironmentResearchResult:
    by_time = _group_performance(trades, lambda t: t.time_bucket, "time_bucket")
    by_regime = _group_performance(trades, lambda t: t.regime, "regime")
    by_pm = _group_performance(trades, lambda t: t.premarket_trend, "premarket_trend")
    by_or = _group_performance(trades, _or_quality_bucket, "or_candle_quality")
    by_rs = _group_performance(trades, lambda t: t.qqq_vs_spy_strength, "relative_strength")

    combos: List[Dict[str, Any]] = []
    for t_bucket in {r["bucket"] for r in by_time}:
        for regime in {r["bucket"] for r in by_regime}:
            subset = [
                t
                for t in trades
                if (t.time_bucket or "unknown") == t_bucket and (t.regime or "unknown") == regime
            ]
            if len(subset) < 3:
                continue
            summary = compute_summary(subset)
            combos.append(
                {
                    "time_bucket": t_bucket,
                    "regime": regime,
                    "total_trades": int(summary["total_trades"]),
                    "profit_factor": round(summary["profit_factor"], 4),
                    "expectancy": round(summary["expectancy"], 2),
                    "total_pnl": round(summary["total_pnl"], 2),
                    "robustness_score": round(_robustness_from_trades(subset), 2),
                }
            )
    combos.sort(
        key=lambda r: (r["robustness_score"], r["profit_factor"], r["total_trades"]),
        reverse=True,
    )

    return EnvironmentResearchResult(
        trades=trades,
        by_time_bucket=by_time,
        by_regime=by_regime,
        by_premarket_trend=by_pm,
        by_or_candle=by_or,
        by_relative_strength=by_rs,
        best_combinations=combos[:25],
    )


def trade_to_env_row(t: BacktestTrade) -> Dict[str, Any]:
    return {
        "date": t.date.isoformat(),
        "direction": t.direction,
        "entry": t.entry,
        "stop": t.stop,
        "target": t.target,
        "shares": t.shares,
        "exit_price": t.exit_price,
        "exit_reason": t.exit_reason,
        "pnl": t.pnl,
        "r_multiple": t.r_multiple,
        "OR_size": t.OR_size,
        "entry_time": t.entry_time.isoformat() if t.entry_time else "",
        "time_bucket": t.time_bucket or "",
        "premarket_trend": t.premarket_trend or "",
        "gap_percent": t.gap_percent if t.gap_percent is not None else "",
        "or_body_percent": t.or_body_percent if t.or_body_percent is not None else "",
        "or_close_location": t.or_close_location if t.or_close_location is not None else "",
        "or_candle_type": t.or_candle_type or "",
        "regime": t.regime or "",
        "qqq_vs_spy_strength": t.qqq_vs_spy_strength or "",
        "qqq_stronger_than_spy": t.qqq_stronger_than_spy if t.qqq_stronger_than_spy is not None else "",
    }


def write_environment_trades_csv(
    trades: List[BacktestTrade],
    path: Path = ENVIRONMENT_TRADES_FILE,
) -> Path:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ENV_TRADE_COLUMNS)
        w.writeheader()
        for t in trades:
            w.writerow(trade_to_env_row(t))
    return path


def _collect_csv_fieldnames(rows: List[Dict[str, Any]]) -> List[str]:
    """Union of all keys across rows — supports mixed summary row shapes."""
    keys: set[str] = set()
    for row in rows:
        keys.update(row.keys())
    preferred = [
        "dimension",
        "bucket",
        "time_bucket",
        "regime",
        "total_trades",
        "win_rate",
        "total_pnl",
        "expectancy",
        "profit_factor",
        "max_drawdown",
        "robustness_score",
    ]
    ordered = [k for k in preferred if k in keys]
    rest = sorted(k for k in keys if k not in ordered)
    return ordered + rest


def write_environment_summary_csv(
    result: EnvironmentResearchResult,
    path: Path = ENVIRONMENT_SUMMARY_FILE,
) -> Path:
    rows: List[Dict[str, Any]] = []
    rows.extend(result.by_time_bucket)
    rows.extend(result.by_regime)
    rows.extend(result.by_premarket_trend)
    rows.extend(result.by_or_candle)
    rows.extend(result.by_relative_strength)
    for c in result.best_combinations:
        rows.append({"dimension": "best_combo", **c})
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fieldnames = _collect_csv_fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})
    return path


def write_best_environment_rules_json(
    result: EnvironmentResearchResult,
    path: Path = BEST_ENVIRONMENT_RULES_FILE,
) -> Path:
    payload = {
        "warning": "Research only — rule-based environment tags, not predictive of future performance.",
        "best_combinations": result.best_combinations[:10],
        "top_time_buckets": result.by_time_bucket[:5],
        "top_regimes": result.by_regime[:5],
        "top_premarket_trends": result.by_premarket_trend[:5],
        "top_or_quality": result.by_or_candle[:5],
        "top_relative_strength": result.by_relative_strength[:5],
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


def run_environment_research(
    trades: List[BacktestTrade],
    start_date: date,
    end_date: date,
    progress: ProgressCb = None,
    session_cache: Optional[Dict[str, Any]] = None,
) -> EnvironmentResearchResult:
    """Enrich trades with environment features and build summary tables."""
    if not trades:
        return EnvironmentResearchResult(error="No trades to analyze. Run Stage 3A backtest first.")

    if progress:
        progress("Loading market data for environment features…")
    bundle, err = load_environment_market_bundle(
        start_date, end_date, progress=progress, session_cache=session_cache
    )
    if err or bundle is None:
        return EnvironmentResearchResult(error=err or "Could not load environment data.")

    if progress:
        progress(f"Computing environment features for {len(trades)} trades…")
    enrich_trades(trades, bundle, progress=progress)

    if progress:
        progress("Building performance tables by environment…")
    result = build_summary_tables(trades)

    write_environment_trades_csv(trades)
    write_environment_summary_csv(result)
    write_best_environment_rules_json(result)

    if progress:
        progress(
            f"Saved `{ENVIRONMENT_TRADES_FILE.name}`, `{ENVIRONMENT_SUMMARY_FILE.name}`, "
            f"`{BEST_ENVIRONMENT_RULES_FILE.name}`"
        )
    return result
