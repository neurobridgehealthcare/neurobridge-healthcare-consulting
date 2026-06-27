"""
Stage 3A — Historical ORB backtester (QQQ + SPY 1-minute bars via Alpaca).

Modular layout:
  1) Data retrieval
  2) Signal generation (OR + breakout + filters)
  3) Trade simulation (intrabar stop vs target: stop priority if both hit)
  4) Analytics + CSV export

Not for live trading. Past performance does not guarantee future results.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple
from zoneinfo import ZoneInfo

import pandas as pd

from data_provider import MISSING_KEYS_MESSAGE, load_alpaca_keys_from_env

NY = ZoneInfo("America/New_York")
UTC = timezone.utc
SESSION_OPEN = time(9, 30)
SESSION_CLOSE = time(16, 0)
OR_END = time(9, 45)

StopStyle = Literal["opposite_or", "midpoint", "fixed_pct"]
DirectionFilter = Literal["long", "short", "both"]

BACKTEST_TRADES_FILE = Path(__file__).resolve().parent / "backtest_trades.csv"

CSV_COLUMNS = [
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
    "VWAP_alignment",
    "SPY_confirmation",
]


# ---------------------------------------------------------------------------
# 1) Data retrieval
# ---------------------------------------------------------------------------


def _to_et(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.astimezone(NY)


def _norm_utc_minute(ts: datetime) -> datetime:
    t = ts if ts.tzinfo else ts.replace(tzinfo=UTC)
    t = t.astimezone(UTC).replace(second=0, microsecond=0)
    return t


def _session_bars_for_date(bars: List[Any], d: date) -> List[Any]:
    out: List[Any] = []
    for bar in bars:
        et = _to_et(bar.timestamp)
        if et.date() != d:
            continue
        tm = et.time()
        if SESSION_OPEN <= tm < SESSION_CLOSE:
            out.append(bar)
    out.sort(key=lambda b: b.timestamp)
    return out


def _or_window_bars(session: List[Any]) -> List[Any]:
    out: List[Any] = []
    for bar in session:
        et = _to_et(bar.timestamp)
        tm = et.time()
        if SESSION_OPEN <= tm < OR_END:
            out.append(bar)
    return out


def fetch_intraday_range(
    start_date: date,
    end_date: date,
) -> Tuple[Dict[str, List[Any]], Optional[str]]:
    """
    Pull QQQ and SPY 1-minute bars for all regular sessions between start_date and end_date (inclusive, Eastern calendar days).
    """
    keys = load_alpaca_keys_from_env()
    if keys is None:
        return {}, MISSING_KEYS_MESSAGE
    if end_date < start_date:
        return {}, "End date must be on or after start date."

    api_key, secret_key = keys
    try:
        from alpaca.common.exceptions import APIError
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame

        start_et = datetime.combine(start_date, SESSION_OPEN, tzinfo=NY)
        end_et = datetime.combine(end_date, SESSION_CLOSE, tzinfo=NY) + timedelta(minutes=2)
        start_utc = start_et.astimezone(UTC)
        end_utc = end_et.astimezone(UTC)

        client = StockHistoricalDataClient(api_key, secret_key)
        req = StockBarsRequest(
            symbol_or_symbols=["QQQ", "SPY"],
            timeframe=TimeFrame.Minute,
            start=start_utc,
            end=end_utc,
        )
        bar_set = client.get_stock_bars(req)
    except APIError as exc:
        return {}, f"Alpaca market data error: {exc}"
    except Exception as exc:  # noqa: BLE001
        return {}, f"Could not load historical bars: {exc}"

    out: Dict[str, List[Any]] = {"QQQ": [], "SPY": []}
    if bar_set is None or not getattr(bar_set, "data", None):
        return out, None
    for sym, lst in bar_set.data.items():
        out[str(sym)] = sorted(list(lst), key=lambda b: b.timestamp)
    return out, None


def fetch_daily_qqq_range(start_date: date, end_date: date) -> Tuple[List[Any], Optional[str]]:
    # Daily trend alignment filter — fetch QQQ daily closes for EMA vs intraday session close.
    """
    Pull QQQ daily bars for calendar range [start_date, end_date] (inclusive, Eastern dates).
    Used for the optional daily trend alignment filter (20 EMA on daily closes).
    """
    keys = load_alpaca_keys_from_env()
    if keys is None:
        return [], MISSING_KEYS_MESSAGE
    if end_date < start_date:
        return [], "End date must be on or after start date."

    api_key, secret_key = keys
    try:
        from alpaca.common.exceptions import APIError
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame

        start_et = datetime.combine(start_date, time(0, 0), tzinfo=NY)
        end_et = datetime.combine(end_date, time(23, 59), tzinfo=NY) + timedelta(days=1)
        start_utc = start_et.astimezone(UTC)
        end_utc = end_et.astimezone(UTC)

        client = StockHistoricalDataClient(api_key, secret_key)
        req = StockBarsRequest(
            symbol_or_symbols="QQQ",
            timeframe=TimeFrame.Day,
            start=start_utc,
            end=end_utc,
        )
        bar_set = client.get_stock_bars(req)
    except APIError as exc:
        return [], f"Alpaca market data error: {exc}"
    except Exception as exc:  # noqa: BLE001
        return [], f"Could not load QQQ daily bars: {exc}"

    if bar_set is None or not getattr(bar_set, "data", None):
        return [], None
    lst: Optional[List[Any]] = bar_set.data.get("QQQ")
    if lst is None and bar_set.data:
        lst = next(iter(bar_set.data.values()))
    if not lst:
        return [], None
    return sorted(list(lst), key=lambda b: b.timestamp), None


def build_qqq_daily_ema20_prev_by_day(daily_bars: List[Any]) -> Dict[date, Optional[float]]:
    """Map session date -> prior session's 20 EMA of QQQ daily closes (warmup via longer history)."""
    # Daily trend alignment filter — daily closes + 20 EMA, shifted so day D uses EMA through D-1.
    if not daily_bars:
        return {}
    rows: List[Tuple[date, float]] = []
    for bar in daily_bars:
        et = _to_et(bar.timestamp)
        rows.append((et.date(), float(bar.close)))
    df = pd.DataFrame(rows, columns=["d", "close"]).sort_values("d").drop_duplicates("d", keep="last")
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema_prev"] = df["ema20"].shift(1)
    out: Dict[date, Optional[float]] = {}
    for _, row in df.iterrows():
        v = row["ema_prev"]
        if v is None or not math.isfinite(float(v)):
            out[row["d"]] = None
        else:
            out[row["d"]] = float(v)
    return out


def build_spy_lookup(spy_bars: List[Any]) -> Dict[datetime, Any]:
    """Minute-aligned UTC timestamp -> SPY bar."""
    lu: Dict[datetime, Any] = {}
    for bar in spy_bars:
        lu[_norm_utc_minute(bar.timestamp)] = bar
    return lu


# ---------------------------------------------------------------------------
# 2) Session math (VWAP, OR)
# ---------------------------------------------------------------------------


def _typical(bar: Any) -> float:
    return (float(bar.high) + float(bar.low) + float(bar.close)) / 3.0


def cumulative_vwap_series(session: List[Any]) -> List[float]:
    """Session VWAP after each bar (same index as session)."""
    out: List[float] = []
    num = 0.0
    den = 0.0
    for bar in session:
        tp = _typical(bar)
        v = float(bar.volume or 0.0)
        num += tp * v
        den += v
        if den > 0:
            out.append(num / den)
        else:
            out.append(float(bar.close))
    return out


def compute_or_levels(or_bars: List[Any]) -> Optional[Tuple[float, float, float, float]]:
    if not or_bars:
        return None
    highs = [float(b.high) for b in or_bars]
    lows = [float(b.low) for b in or_bars]
    or_high = max(highs)
    or_low = min(lows)
    mid = (or_high + or_low) / 2.0
    size = or_high - or_low
    return or_high, or_low, mid, size


def avg_volume(bars: List[Any]) -> float:
    if not bars:
        return 0.0
    return sum(float(b.volume or 0) for b in bars) / len(bars)


def sum_qqq_or_volume_by_date(qqq_bars: List[Any]) -> Dict[date, float]:
    """Total QQQ volume in the opening-range window (9:30–9:45 ET) per session date."""
    # Relative Volume filter
    sums: Dict[date, float] = defaultdict(float)
    for bar in qqq_bars:
        et = _to_et(bar.timestamp)
        tm = et.time()
        if SESSION_OPEN <= tm < OR_END:
            sums[et.date()] += float(bar.volume or 0)
    return dict(sums)


def compute_opening_range_rvol(
    session_date: date,
    or_vol_by_date: Dict[date, float],
    max_prior_sessions: int = 20,
) -> Optional[float]:
    """OR-window total volume today vs mean over prior sessions (up to ``max_prior_sessions``)."""
    # Relative Volume filter
    today = or_vol_by_date.get(session_date)
    if today is None or today <= 0:
        return None
    prior_dates = sorted(d for d in or_vol_by_date if d < session_date)
    window = prior_dates[-max_prior_sessions:]
    if not window:
        return None
    vols = [float(or_vol_by_date[pd]) for pd in window]
    avg = sum(vols) / len(vols)
    if avg <= 0 or not math.isfinite(avg):
        return None
    r = float(today) / avg
    return r if math.isfinite(r) else None


# ---------------------------------------------------------------------------
# 3) Stop / target from config
# ---------------------------------------------------------------------------


def compute_long_stop_target(
    entry: float,
    or_high: float,
    or_low: float,
    or_mid: float,
    stop_style: StopStyle,
    fixed_stop_percent: float,
    r_target: float,
) -> Tuple[float, float, float]:
    """Returns (stop, target, risk_per_share)."""
    if stop_style == "opposite_or":
        stop = or_low
    elif stop_style == "midpoint":
        stop = or_mid
    else:
        stop = entry * (1.0 - max(0.01, fixed_stop_percent) / 100.0)
    risk = max(entry - stop, 1e-9)
    target = entry + r_target * risk
    return stop, target, risk


def compute_short_stop_target(
    entry: float,
    or_high: float,
    or_low: float,
    or_mid: float,
    stop_style: StopStyle,
    fixed_stop_percent: float,
    r_target: float,
) -> Tuple[float, float, float]:
    """Returns (stop, target, risk_per_share)."""
    if stop_style == "opposite_or":
        stop = or_high
    elif stop_style == "midpoint":
        stop = or_mid
    else:
        stop = entry * (1.0 + max(0.01, fixed_stop_percent) / 100.0)
    risk = max(stop - entry, 1e-9)
    target = entry - r_target * risk
    return stop, target, risk


# ---------------------------------------------------------------------------
# 4) Trade simulation
# ---------------------------------------------------------------------------


@dataclass
class BacktestTrade:
    date: date
    direction: str
    entry: float
    stop: float
    target: float
    shares: int
    exit_price: float
    exit_reason: str
    pnl: float
    r_multiple: float
    OR_size: float
    VWAP_alignment: str
    SPY_confirmation: str
    entry_time: Optional[time] = None
    # Stage 3C environment features (filled by environment_engine.enrich_trades)
    time_bucket: Optional[str] = None
    premarket_trend: Optional[str] = None
    gap_percent: Optional[float] = None
    or_body_percent: Optional[float] = None
    or_close_location: Optional[float] = None
    regime: Optional[str] = None
    qqq_vs_spy_strength: Optional[str] = None
    qqq_stronger_than_spy: Optional[bool] = None
    or_candle_type: Optional[str] = None


def simulate_long_from_bar(
    session: List[Any],
    start_idx: int,
    entry: float,
    stop: float,
    target: float,
    shares: int,
    or_size: float,
    vwap_tag: str,
    spy_tag: str,
    d: date,
) -> Tuple[BacktestTrade, int]:
    """Exit simulation starts after ``start_idx``. Returns (trade, last_bar_index_used)."""
    risk = entry - stop
    last_idx = min(start_idx, len(session) - 1)
    if risk <= 0:
        exit_p = float(session[last_idx].close)
        entry_tm = _to_et(session[start_idx].timestamp).time()
        return (
            BacktestTrade(
                date=d,
                direction="Long",
                entry=entry,
                stop=stop,
                target=target,
                shares=shares,
                exit_price=exit_p,
                exit_reason="invalid_stop",
                pnl=0.0,
                r_multiple=0.0,
                OR_size=or_size,
                VWAP_alignment=vwap_tag,
                SPY_confirmation=spy_tag,
                entry_time=entry_tm,
            ),
            last_idx,
        )

    exit_price = entry
    exit_reason = "end_of_day"
    exit_idx = len(session) - 1
    for j in range(start_idx + 1, len(session)):
        bar = session[j]
        lo, hi, op = float(bar.low), float(bar.high), float(bar.open)
        if op <= stop:
            exit_price = op
            exit_reason = "stop_hit"
            exit_idx = j
            break
        if lo <= stop:
            exit_price = stop
            exit_reason = "stop_hit"
            exit_idx = j
            break
        if op >= target:
            exit_price = op
            exit_reason = "target_hit"
            exit_idx = j
            break
        if hi >= target:
            exit_price = target
            exit_reason = "target_hit"
            exit_idx = j
            break
    else:
        last = session[-1]
        exit_price = float(last.close)
        exit_reason = "end_of_day"
        exit_idx = len(session) - 1

    pnl = (exit_price - entry) * shares
    r_mult = (exit_price - entry) / risk
    entry_bar = session[start_idx]
    entry_tm = _to_et(entry_bar.timestamp).time()
    return (
        BacktestTrade(
            date=d,
            direction="Long",
            entry=entry,
            stop=stop,
            target=target,
            shares=shares,
            exit_price=exit_price,
            exit_reason=exit_reason,
            pnl=pnl,
            r_multiple=r_mult,
            OR_size=or_size,
            VWAP_alignment=vwap_tag,
            SPY_confirmation=spy_tag,
            entry_time=entry_tm,
        ),
        exit_idx,
    )


def simulate_short_from_bar(
    session: List[Any],
    start_idx: int,
    entry: float,
    stop: float,
    target: float,
    shares: int,
    or_size: float,
    vwap_tag: str,
    spy_tag: str,
    d: date,
) -> Tuple[BacktestTrade, int]:
    risk = stop - entry
    last_idx = min(start_idx, len(session) - 1)
    if risk <= 0:
        exit_p = float(session[last_idx].close)
        entry_tm = _to_et(session[start_idx].timestamp).time()
        return (
            BacktestTrade(
                date=d,
                direction="Short",
                entry=entry,
                stop=stop,
                target=target,
                shares=shares,
                exit_price=exit_p,
                exit_reason="invalid_stop",
                pnl=0.0,
                r_multiple=0.0,
                OR_size=or_size,
                VWAP_alignment=vwap_tag,
                SPY_confirmation=spy_tag,
                entry_time=entry_tm,
            ),
            last_idx,
        )

    exit_price = entry
    exit_reason = "end_of_day"
    exit_idx = len(session) - 1
    for j in range(start_idx + 1, len(session)):
        bar = session[j]
        lo, hi, op = float(bar.low), float(bar.high), float(bar.open)
        if op >= stop:
            exit_price = op
            exit_reason = "stop_hit"
            exit_idx = j
            break
        if hi >= stop:
            exit_price = stop
            exit_reason = "stop_hit"
            exit_idx = j
            break
        if op <= target:
            exit_price = op
            exit_reason = "target_hit"
            exit_idx = j
            break
        if lo <= target:
            exit_price = target
            exit_reason = "target_hit"
            exit_idx = j
            break
    else:
        last = session[-1]
        exit_price = float(last.close)
        exit_reason = "end_of_day"
        exit_idx = len(session) - 1

    pnl = (entry - exit_price) * shares
    r_mult = (entry - exit_price) / risk
    entry_tm = _to_et(session[start_idx].timestamp).time()
    return (
        BacktestTrade(
            date=d,
            direction="Short",
            entry=entry,
            stop=stop,
            target=target,
            shares=shares,
            exit_price=exit_price,
            exit_reason=exit_reason,
            pnl=pnl,
            r_multiple=r_mult,
            OR_size=or_size,
            VWAP_alignment=vwap_tag,
            SPY_confirmation=spy_tag,
            entry_time=entry_tm,
        ),
        exit_idx,
    )


def aligned_spy_vwap_series(session: List[Any], spy_session: List[Any]) -> List[Optional[float]]:
    """SPY session VWAP at each QQQ session minute (aligned by bar open UTC)."""
    idx_by_ts = {_norm_utc_minute(b.timestamp): i for i, b in enumerate(spy_session)}
    spy_vwap = cumulative_vwap_series(spy_session)
    out: List[Optional[float]] = []
    for qb in session:
        ix = idx_by_ts.get(_norm_utc_minute(qb.timestamp))
        if ix is None:
            out.append(None)
        else:
            out.append(spy_vwap[ix])
    return out


# ---------------------------------------------------------------------------
# 5) Signal + day replay
# ---------------------------------------------------------------------------


@dataclass
class BacktestConfig:
    start_date: date
    end_date: date
    account_size: float
    risk_percent: float
    r_target: float
    stop_style: StopStyle
    fixed_stop_percent: float
    max_trades_per_day: int
    vwap_filter: bool
    spy_confirmation: bool
    volume_confirmation: bool
    direction_filter: DirectionFilter
    daily_trend_qqq_ema20_filter: bool = False
    or_size_filter_enabled: bool = False
    or_size_min: float = 1.0
    or_size_max: float = 6.0
    use_rvol_filter: bool = False
    min_rvol: float = 1.5
    enable_entry_cutoff: bool = False
    entry_cutoff_time: str = "11:00"
    favorable_environments_only: bool = False


ProgressCb = Optional[Callable[[str], None]]


@dataclass
class BacktestResult:
    trades: List[BacktestTrade] = field(default_factory=list)
    summary: Dict[str, float] = field(default_factory=dict)
    equity_curve: List[Tuple[date, float]] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class BacktestMarketData:
    """Pre-loaded bars and derived series for repeated replays (Stage 3B optimizer)."""

    qqq_all: List[Any]
    spy_all: List[Any]
    spy_lookup: Dict[datetime, Any]
    ema_prev_by_day: Dict[date, Optional[float]] = field(default_factory=dict)
    or_vol_by_date: Dict[date, float] = field(default_factory=dict)
    loaded_from: date = field(default_factory=date.today)
    loaded_to: date = field(default_factory=date.today)
    qqq_by_date: Dict[date, List[Any]] = field(default_factory=dict)
    spy_by_date: Dict[date, List[Any]] = field(default_factory=dict)


def _build_session_index(bars: List[Any]) -> Dict[date, List[Any]]:
    """Index RTH session bars by calendar date (speeds optimizer replays)."""
    by_date: Dict[date, List[Any]] = defaultdict(list)
    for bar in bars:
        et = _to_et(bar.timestamp)
        tm = et.time()
        if SESSION_OPEN <= tm < SESSION_CLOSE:
            by_date[et.date()].append(bar)
    for d in by_date:
        by_date[d].sort(key=lambda b: b.timestamp)
    return dict(by_date)


def load_backtest_market_data(
    start_date: date,
    end_date: date,
    *,
    need_daily_ema: bool = False,
    need_rvol: bool = False,
    progress: ProgressCb = None,
) -> Tuple[Optional[BacktestMarketData], Optional[str]]:
    """Fetch intraday (and optional daily) data once for many backtest replays."""
    if progress:
        progress("Loading historical data…")
    intraday_start = start_date
    if need_rvol:
        intraday_start = start_date - timedelta(days=60)
    raw, err = fetch_intraday_range(intraday_start, end_date)
    if err:
        return None, err

    qqq_all = raw.get("QQQ", [])
    spy_all = raw.get("SPY", [])
    if not qqq_all or not spy_all:
        return None, "No QQQ or SPY bars returned for this range (check dates / market calendar)."

    spy_lookup = build_spy_lookup(spy_all)
    ema_prev_by_day: Dict[date, Optional[float]] = {}
    if need_daily_ema:
        if progress:
            progress("Loading QQQ daily bars for trend filter…")
        daily_warm_start = start_date - timedelta(days=180)
        daily_qqq, derr = fetch_daily_qqq_range(daily_warm_start, end_date)
        if derr:
            return None, derr
        if not daily_qqq:
            return None, "No QQQ daily bars returned for the trend filter (check dates / API access)."
        ema_prev_by_day = build_qqq_daily_ema20_prev_by_day(daily_qqq)

    or_vol_by_date: Dict[date, float] = {}
    if need_rvol:
        or_vol_by_date = sum_qqq_or_volume_by_date(qqq_all)

    qqq_by_date = _build_session_index(qqq_all)
    spy_by_date = _build_session_index(spy_all)

    return (
        BacktestMarketData(
            qqq_all=qqq_all,
            spy_all=spy_all,
            spy_lookup=spy_lookup,
            ema_prev_by_day=ema_prev_by_day,
            or_vol_by_date=or_vol_by_date,
            loaded_from=intraday_start,
            loaded_to=end_date,
            qqq_by_date=qqq_by_date,
            spy_by_date=spy_by_date,
        ),
        None,
    )


def run_backtest_with_data(
    cfg: BacktestConfig,
    market: BacktestMarketData,
    *,
    write_csv: bool = False,
    env_bundle: Any = None,
    adaptive_rules: Any = None,
) -> BacktestResult:
    """Replay ``cfg`` on pre-loaded market data (no API fetch)."""
    all_trades: List[BacktestTrade] = []
    cur = cfg.start_date
    while cur <= cfg.end_date:
        if market.qqq_by_date:
            session = market.qqq_by_date.get(cur, [])
            spy_sess = market.spy_by_date.get(cur, [])
        else:
            session = _session_bars_for_date(market.qqq_all, cur)
            spy_sess = _session_bars_for_date(market.spy_all, cur)
        if len(session) >= 20 and spy_sess:
            ema_prev = market.ema_prev_by_day.get(cur) if cfg.daily_trend_qqq_ema20_filter else None
            session_rvol: Optional[float] = None
            if cfg.volume_confirmation and cfg.use_rvol_filter:
                session_rvol = compute_opening_range_rvol(cur, market.or_vol_by_date)
            all_trades.extend(
                replay_single_day(
                    cur,
                    session,
                    spy_sess,
                    market.spy_lookup,
                    cfg,
                    ema_prev,
                    session_rvol,
                    env_bundle,
                    adaptive_rules,
                )
            )
        cur += timedelta(days=1)

    summary = compute_summary(all_trades)
    eq_pts = equity_curve_points(all_trades)
    if write_csv:
        write_backtest_trades_csv(all_trades)
    return BacktestResult(trades=all_trades, summary=summary, equity_curve=eq_pts, error=None)


def list_tradable_session_dates(
    market: BacktestMarketData,
    start: date,
    end: date,
) -> List[date]:
    """Session dates between ``start`` and ``end`` with enough QQQ + SPY bars."""
    if market.qqq_by_date and market.spy_by_date:
        out: List[date] = []
        cur = start
        while cur <= end:
            session = market.qqq_by_date.get(cur, [])
            spy_sess = market.spy_by_date.get(cur, [])
            if len(session) >= 20 and spy_sess:
                out.append(cur)
            cur += timedelta(days=1)
        return out
    out = []
    cur = start
    while cur <= end:
        session = _session_bars_for_date(market.qqq_all, cur)
        spy_sess = _session_bars_for_date(market.spy_all, cur)
        if len(session) >= 20 and spy_sess:
            out.append(cur)
        cur += timedelta(days=1)
    return out


def _position_shares(account_size: float, risk_pct: float, risk_per_share: float) -> int:
    if risk_per_share <= 0:
        return 0
    max_risk = account_size * (risk_pct / 100.0)
    return int(max_risk // risk_per_share)


def _spy_bar_at(spy_lookup: Dict[datetime, Any], qqq_bar: Any) -> Optional[Any]:
    return spy_lookup.get(_norm_utc_minute(qqq_bar.timestamp))


def parse_entry_cutoff_hhmm(value: str) -> Optional[time]:
    """Parse ``entry_cutoff_time`` (``HH:MM``) for Eastern-time bar comparisons."""
    if not value or not isinstance(value, str):
        return None
    parts = value.strip().split(":")
    if len(parts) < 2:
        return None
    try:
        h = int(parts[0])
        m = int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return None
        return time(h, m)
    except ValueError:
        return None


def replay_single_day(
    d: date,
    session: List[Any],
    spy_session: List[Any],
    spy_lookup: Dict[datetime, Any],
    cfg: BacktestConfig,
    qqq_daily_ema_prev: Optional[float] = None,
    session_rvol: Optional[float] = None,
    env_bundle: Any = None,
    adaptive_rules: Any = None,
) -> List[BacktestTrade]:
    """Replay one session: OR, signals, optional multiple trades per day."""
    trades: List[BacktestTrade] = []
    or_bars = _or_window_bars(session)
    or_levels = compute_or_levels(or_bars)
    if or_levels is None:
        return trades
    or_high, or_low, or_mid, or_size = or_levels
    if or_size <= 0:
        return trades

    # Opening range size filter — optional band on |OR_high - OR_low| before scanning for entries.
    if cfg.or_size_filter_enabled:
        or_span = abs(float(or_high) - float(or_low))
        eff_min = min(float(cfg.or_size_min), float(cfg.or_size_max))
        eff_max = max(float(cfg.or_size_min), float(cfg.or_size_max))
        if not (math.isfinite(or_span) and math.isfinite(eff_min) and math.isfinite(eff_max)):
            return trades
        if or_span < eff_min or or_span > eff_max:
            return trades

    vwap_qqq = cumulative_vwap_series(session)
    spy_vwap_align = aligned_spy_vwap_series(session, spy_session)
    avg_or_vol = avg_volume(or_bars)

    or_end_idx = len(or_bars) - 1
    start_scan = or_end_idx + 1
    if start_scan >= len(session):
        return trades

    trades_today = 0
    scan_from = start_scan

    cutoff_et: Optional[time] = None
    if cfg.enable_entry_cutoff:
        cutoff_et = parse_entry_cutoff_hhmm(cfg.entry_cutoff_time)

    while trades_today < cfg.max_trades_per_day and scan_from < len(session):
        signal_idx = -1
        chosen: Optional[str] = None

        for i in range(scan_from, len(session)):
            bar = session[i]
            et = _to_et(bar.timestamp)
            if et.time() >= SESSION_CLOSE:
                break

            # Intraday entry cutoff (Eastern): no new entries after configured clock (existing exits unchanged).
            if cutoff_et is not None and et.time() > cutoff_et:
                continue

            spy_b = _spy_bar_at(spy_lookup, bar)
            if spy_b is None:
                continue

            cl = float(bar.close)
            spy_cl = float(spy_b.close)
            sv = spy_vwap_align[i]
            if sv is None:
                continue

            vq = vwap_qqq[i]
            vol_ok = True
            if cfg.volume_confirmation:
                if cfg.use_rvol_filter:
                    # Relative Volume filter — session RVOL vs configured minimum (see run_backtest warmup).
                    if session_rvol is not None and math.isfinite(session_rvol):
                        vol_ok = session_rvol >= float(cfg.min_rvol)
                    else:
                        vol_ok = True
                else:
                    vol_ok = float(bar.volume or 0) >= 1.1 * avg_or_vol if avg_or_vol > 0 else True

            vwap_long_ok = (not cfg.vwap_filter) or (cl > vq)
            vwap_short_ok = (not cfg.vwap_filter) or (cl < vq)
            spy_long_ok = (not cfg.spy_confirmation) or (spy_cl > sv)
            spy_short_ok = (not cfg.spy_confirmation) or (spy_cl < sv)

            # Daily trend alignment filter — optional; running session close vs prior day's 20 EMA level.
            trend_long_ok = True
            trend_short_ok = True
            if cfg.daily_trend_qqq_ema20_filter and qqq_daily_ema_prev is not None:
                if math.isfinite(qqq_daily_ema_prev):
                    trend_long_ok = cl > qqq_daily_ema_prev
                    trend_short_ok = cl < qqq_daily_ema_prev

            long_sig = trend_long_ok and cl > or_high and vwap_long_ok and spy_long_ok and vol_ok
            short_sig = trend_short_ok and cl < or_low and vwap_short_ok and spy_short_ok and vol_ok

            take_long = long_sig and cfg.direction_filter in ("long", "both")
            take_short = short_sig and cfg.direction_filter in ("short", "both")
            if take_long and take_short:
                take_short = False
            if take_long:
                chosen = "Long"
                signal_idx = i
                break
            if take_short:
                chosen = "Short"
                signal_idx = i
                break

        if signal_idx < 0 or chosen is None:
            break

        # Stage 3D — optional adaptive environment gate (FAVORABLE only).
        if cfg.favorable_environments_only and adaptive_rules is not None and env_bundle is not None:
            try:
                from adaptive_environment import is_favorable_entry

                entry_tm = _to_et(session[signal_idx].timestamp).time()
                if not is_favorable_entry(env_bundle, d, entry_tm, adaptive_rules):
                    scan_from = signal_idx + 1
                    continue
            except Exception:  # noqa: BLE001
                scan_from = signal_idx + 1
                continue

        entry = float(session[signal_idx].close)
        vwap_tag = "n/a" if not cfg.vwap_filter else "Yes"
        spy_tag = "n/a" if not cfg.spy_confirmation else "Yes"

        if chosen == "Long":
            stop, target, risk = compute_long_stop_target(
                entry, or_high, or_low, or_mid, cfg.stop_style, cfg.fixed_stop_percent, cfg.r_target
            )
        else:
            stop, target, risk = compute_short_stop_target(
                entry, or_high, or_low, or_mid, cfg.stop_style, cfg.fixed_stop_percent, cfg.r_target
            )

        sh = _position_shares(cfg.account_size, cfg.risk_percent, risk)
        if sh <= 0:
            scan_from = signal_idx + 1
            continue

        est_cost = sh * entry
        if est_cost > cfg.account_size:
            scan_from = signal_idx + 1
            continue

        if chosen == "Long":
            tr, exi = simulate_long_from_bar(
                session, signal_idx, entry, stop, target, sh, or_size, vwap_tag, spy_tag, d
            )
        else:
            tr, exi = simulate_short_from_bar(
                session, signal_idx, entry, stop, target, sh, or_size, vwap_tag, spy_tag, d
            )

        trades.append(tr)
        trades_today += 1
        scan_from = exi + 1

    return trades


# ---------------------------------------------------------------------------
# 6) Analytics + CSV + orchestration
# ---------------------------------------------------------------------------


def compute_summary(trades: List[BacktestTrade]) -> Dict[str, float]:
    """Totals and ratios for the Streamlit summary panel."""
    if not trades:
        return {
            "total_trades": 0.0,
            "win_rate": 0.0,
            "avg_r": 0.0,
            "total_pnl": 0.0,
            "expectancy": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "avg_or_size": 0.0,
        }

    pnls = [t.pnl for t in trades]
    rs = [t.r_multiple for t in trades]
    wins = sum(1 for p in pnls if p > 0)
    losses = [p for p in pnls if p < 0]
    gains = [p for p in pnls if p > 0]

    gross_win = sum(gains) if gains else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    pf = (gross_win / gross_loss) if gross_loss > 1e-9 else (999.0 if gross_win > 0 else 0.0)

    eq = 0.0
    peak = 0.0
    max_dd = 0.0
    for p in pnls:
        eq += p
        peak = max(peak, eq)
        max_dd = min(max_dd, eq - peak)

    return {
        "total_trades": float(len(trades)),
        "win_rate": wins / len(trades) if trades else 0.0,
        "avg_r": sum(rs) / len(rs) if rs else 0.0,
        "total_pnl": sum(pnls),
        "expectancy": sum(pnls) / len(trades),
        "profit_factor": pf,
        "max_drawdown": float(max_dd),
        "avg_or_size": sum(t.OR_size for t in trades) / len(trades),
    }


def equity_curve_points(trades: List[BacktestTrade]) -> List[Tuple[date, float]]:
    running = 0.0
    out: List[Tuple[date, float]] = []
    for t in trades:
        running += t.pnl
        out.append((t.date, running))
    return out


def write_backtest_trades_csv(trades: List[BacktestTrade], path: Path = BACKTEST_TRADES_FILE) -> Path:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for t in trades:
            w.writerow(
                {
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
                    "VWAP_alignment": t.VWAP_alignment,
                    "SPY_confirmation": t.SPY_confirmation,
                }
            )
    return path


def run_backtest(
    cfg: BacktestConfig,
    progress: ProgressCb = None,
    adaptive_rules: Any = None,
    env_bundle: Any = None,
) -> BacktestResult:
    """
    Full pipeline: download bars, replay each session day, analytics, write ``backtest_trades.csv``.
    """
    need_rvol = cfg.volume_confirmation and cfg.use_rvol_filter
    market, err = load_backtest_market_data(
        cfg.start_date,
        cfg.end_date,
        need_daily_ema=cfg.daily_trend_qqq_ema20_filter,
        need_rvol=need_rvol,
        progress=progress,
    )
    if err:
        return BacktestResult(error=err)
    assert market is not None

    bundle = env_bundle
    if cfg.favorable_environments_only and adaptive_rules is not None and bundle is None:
        if progress:
            progress("Loading environment data for adaptive filter…")
        try:
            from environment_engine import load_environment_market_bundle

            bundle, _ = load_environment_market_bundle(cfg.start_date, cfg.end_date, progress=progress)
        except Exception:  # noqa: BLE001
            bundle = None

    if progress:
        progress("Running historical replay…")

    result = run_backtest_with_data(
        cfg,
        market,
        write_csv=False,
        env_bundle=bundle,
        adaptive_rules=adaptive_rules,
    )

    if progress:
        progress("Generating statistics…")

    write_backtest_trades_csv(result.trades)
    return result
