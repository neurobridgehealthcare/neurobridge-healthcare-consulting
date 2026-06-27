"""
Alpaca market data helpers for EdgeOne ORB (Stage 2A — read-only, no orders).

Uses environment variables:
  ALPACA_API_KEY
  ALPACA_SECRET_KEY
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UTC = timezone.utc

# Exact message requested when keys are missing
MISSING_KEYS_MESSAGE = "Alpaca keys not found. Add them to a .env file."

SESSION_OPEN = time(9, 30)
SESSION_CLOSE = time(16, 0)
OR_END = time(9, 45)


@dataclass
class LiveMarketSnapshot:
    """Computed fields for Live Data Mode (QQQ + SPY, regular session today ET)."""

    trading_date: date
    qqq_bars: int
    spy_bars: int
    or_high: float
    or_low: float
    or_midpoint: float
    or_size: float
    qqq_last: float
    qqq_vwap: float
    spy_last: float
    spy_vwap: float
    qqq_vs_vwap: str  # "above" | "below" | "at"
    spy_confirms_long: bool
    spy_confirms_short: bool
    latest_bar_time_et: datetime
    # For Streamlit tables (same objects Alpaca returned; not serialized to CSV)
    qqq_session_bars: List[Any] = field(default_factory=list, repr=False)
    spy_session_bars: List[Any] = field(default_factory=list, repr=False)


def load_alpaca_keys_from_env() -> Optional[Tuple[str, str]]:
    key = os.environ.get("ALPACA_API_KEY", "").strip()
    secret = os.environ.get("ALPACA_SECRET_KEY", "").strip()
    if not key or not secret:
        return None
    return key, secret


def _to_et(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.astimezone(NY)


def _session_bounds_et(trading_date: date) -> Tuple[datetime, datetime]:
    """Regular session [9:30, 16:00) in Eastern for a calendar date."""
    start = datetime.combine(trading_date, SESSION_OPEN, tzinfo=NY)
    end = datetime.combine(trading_date, SESSION_CLOSE, tzinfo=NY)
    return start, end


def _pick_trading_date_et(now_et: datetime) -> date:
    """Use today's Eastern calendar date as the session label (per Stage 2A spec)."""
    return now_et.date()


def _filter_bars_for_session(
    bars: List, trading_date: date
) -> List:
    """Keep 1‑minute bars whose bar *open* time falls on trading_date during RTH."""
    out = []
    for bar in bars:
        et = _to_et(bar.timestamp)
        if et.date() != trading_date:
            continue
        t = et.time()
        if SESSION_OPEN <= t < SESSION_CLOSE:
            out.append(bar)
    out.sort(key=lambda b: b.timestamp)
    return out


def _opening_range_bars(session_bars: List) -> List:
    """First 15 minutes of RTH: [9:30, 9:45) by bar open time."""
    out = []
    for bar in session_bars:
        et = _to_et(bar.timestamp)
        t = et.time()
        if SESSION_OPEN <= t < OR_END:
            out.append(bar)
    return out


def _typical_price(bar) -> float:
    return (bar.high + bar.low + bar.close) / 3.0


def _cumulative_vwap(session_bars: List) -> float:
    """
    Session VWAP from first RTH bar through the last bar in session_bars.
    If no volume, returns last close as a fallback.
    """
    if not session_bars:
        return 0.0
    num = 0.0
    den = 0.0
    for bar in session_bars:
        tp = _typical_price(bar)
        v = float(bar.volume or 0.0)
        num += tp * v
        den += v
    if den <= 0:
        return float(session_bars[-1].close)
    return num / den


def _price_vs_vwap(last: float, vwap: float) -> str:
    eps = 1e-6
    if last > vwap + eps:
        return "above"
    if last < vwap - eps:
        return "below"
    return "at"


def fetch_live_snapshot() -> Tuple[Optional[LiveMarketSnapshot], Optional[str]]:
    """
    Pull today's QQQ/SPY minute bars and compute OR, VWAPs, and confirmation flags.

    Returns (snapshot, None) on success, or (None, user-facing error message).
    Never raises for missing keys or empty data — callers show the message in UI.
    """
    keys = load_alpaca_keys_from_env()
    if keys is None:
        return None, MISSING_KEYS_MESSAGE

    api_key, secret_key = keys

    try:
        from alpaca.common.exceptions import APIError
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame
    except ImportError as exc:  # pragma: no cover
        return None, f"Alpaca packages are not installed: {exc}"

    now_et = datetime.now(NY)
    trading_date = _pick_trading_date_et(now_et)
    sess_start_et, sess_end_et = _session_bounds_et(trading_date)

    # Before today's regular open: no same-day OR yet
    if now_et < sess_start_et:
        return None, (
            "The U.S. stock market is not open yet for today (Eastern). "
            "Live opening-range data is available after 9:30 AM ET."
        )

    # Request window: session start through now (capped at official close)
    end_et = min(now_et, sess_end_et)
    if end_et <= sess_start_et:
        return None, "Not enough intraday data for today yet. Try again after the open."

    start_utc = sess_start_et.astimezone(UTC)
    # Alpaca's `end` is exclusive; nudge forward so the current minute bar is included.
    end_utc = (end_et + timedelta(minutes=2)).astimezone(UTC)

    try:
        client = StockHistoricalDataClient(api_key, secret_key)
        request = StockBarsRequest(
            symbol_or_symbols=["QQQ", "SPY"],
            timeframe=TimeFrame.Minute,
            start=start_utc,
            end=end_utc,
        )
        bar_set = client.get_stock_bars(request)
    except APIError as exc:
        return None, f"Alpaca market data error: {exc}"
    except Exception as exc:  # noqa: BLE001 — beginner-friendly surface for Streamlit
        return None, f"Could not load market data: {exc}"

    raw_by_symbol: Dict[str, List] = {}
    if bar_set is None or not getattr(bar_set, "data", None):
        return None, (
            "No intraday bars returned for today. The market may be closed, "
            "or your data subscription may not include these symbols."
        )

    for sym, lst in bar_set.data.items():
        raw_by_symbol[str(sym)] = list(lst)

    qqq_raw = raw_by_symbol.get("QQQ", [])
    spy_raw = raw_by_symbol.get("SPY", [])
    qqq_session = _filter_bars_for_session(qqq_raw, trading_date)
    spy_session = _filter_bars_for_session(spy_raw, trading_date)

    if not qqq_session:
        return None, (
            "No QQQ intraday bars for today's regular session. "
            "The market may be closed or data is not available yet."
        )
    if not spy_session:
        return None, (
            "No SPY intraday bars for today's regular session. "
            "The market may be closed or data is not available yet."
        )

    or_bars = _opening_range_bars(qqq_session)
    if not or_bars:
        return None, (
            "Not enough data to compute the QQQ opening range (9:30–9:45 AM ET). "
            "Wait until a few minutes after the open, or check whether the session has started."
        )

    highs = [float(b.high) for b in or_bars]
    lows = [float(b.low) for b in or_bars]
    or_high = max(highs)
    or_low = min(lows)
    or_mid = (or_high + or_low) / 2.0
    or_sz = or_high - or_low

    qqq_last = float(qqq_session[-1].close)
    spy_last = float(spy_session[-1].close)
    latest_et = _to_et(qqq_session[-1].timestamp)

    qqq_vwap = _cumulative_vwap(qqq_session)
    spy_vwap = _cumulative_vwap(spy_session)

    qqq_rel = _price_vs_vwap(qqq_last, qqq_vwap)
    spy_confirms_long = spy_last > spy_vwap
    spy_confirms_short = spy_last < spy_vwap

    snap = LiveMarketSnapshot(
        trading_date=trading_date,
        qqq_bars=len(qqq_session),
        spy_bars=len(spy_session),
        or_high=or_high,
        or_low=or_low,
        or_midpoint=or_mid,
        or_size=or_sz,
        qqq_last=qqq_last,
        qqq_vwap=qqq_vwap,
        spy_last=spy_last,
        spy_vwap=spy_vwap,
        qqq_vs_vwap=qqq_rel,
        spy_confirms_long=spy_confirms_long,
        spy_confirms_short=spy_confirms_short,
        latest_bar_time_et=latest_et,
        qqq_session_bars=qqq_session,
        spy_session_bars=spy_session,
    )
    return snap, None


def bars_for_display(
    bars: List, max_rows: int = 30
) -> List[dict]:
    """Lightweight rows for Streamlit tables (most recent last)."""
    rows: List[dict] = []
    tail = bars[-max_rows:] if len(bars) > max_rows else bars
    for bar in tail:
        et = _to_et(bar.timestamp)
        rows.append(
            {
                "Time (ET)": et.strftime("%H:%M"),
                "Open": float(bar.open),
                "High": float(bar.high),
                "Low": float(bar.low),
                "Close": float(bar.close),
                "Volume": float(bar.volume or 0),
            }
        )
    return rows
