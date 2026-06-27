"""
Setup score (0–100) and trade decision for EdgeOne ORB.
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from risk import Direction, r_multiple as calc_r


def _clean_or_break_points(
    direction: Direction, current_price: float, or_high: float, or_low: float
) -> int:
    """20 pts if price is on the correct side of the OR for the chosen direction."""
    if direction == "Long" and current_price > or_high:
        return 20
    if direction == "Short" and current_price < or_low:
        return 20
    return 0


def _time_quality_points(now: datetime | None = None) -> int:
    """
    10 pts max based on US/Eastern clock (no extra inputs).
    Assumes regular session 9:30–16:00 ET.
    """
    tz = ZoneInfo("America/New_York")
    t = (now or datetime.now(tz)).astimezone(tz)
    if t.weekday() >= 5:
        return 0
    minutes = t.hour * 60 + t.minute
    open_m, close_m = 9 * 60 + 30, 16 * 60
    if not (open_m <= minutes < close_m):
        return 0
    # First 30 minutes after open: full points
    if minutes < 10 * 60:
        return 10
    # First hour: strong
    if minutes < 10 * 60 + 30:
        return 8
    # Late morning
    if minutes < 12 * 60:
        return 5
    # Afternoon
    return 2


def _risk_reward_quality_points(reward_each: float, risk_each: float) -> int:
    """Up to 20 pts from R-multiple quality."""
    r = calc_r(reward_each, risk_each)
    if r >= 3.0:
        return 20
    if r >= 2.5:
        return 17
    if r >= 2.0:
        return 14
    if r >= 1.5:
        return 10
    if r >= 1.0:
        return 5
    return 0


def setup_score(
    direction: Direction,
    current_price: float,
    or_high: float,
    or_low: float,
    vwap_aligned: bool,
    spy_confirmed: bool,
    volume_confirmed: bool,
    entry: float,
    stop: float,
    target: float,
) -> int:
    from risk import reward_per_share, risk_per_share

    pts = 0
    pts += _clean_or_break_points(direction, current_price, or_high, or_low)
    if vwap_aligned:
        pts += 15
    if spy_confirmed:
        pts += 15
    if volume_confirmed:
        pts += 15

    risk_each = risk_per_share(entry, stop, direction)
    reward_each = reward_per_share(entry, target, direction)
    pts += _risk_reward_quality_points(reward_each, risk_each)
    pts += _time_quality_points()

    warn = build_warnings(
        direction=direction,
        r_mult=calc_r(reward_each, risk_each),
        vwap_aligned=vwap_aligned,
        spy_confirmed=spy_confirmed,
        volume_confirmed=volume_confirmed,
        entry=entry,
        stop=stop,
    )
    if not warn:
        pts += 5

    return max(0, min(100, pts))


def build_warnings(
    direction: Direction,
    r_mult: float,
    vwap_aligned: bool,
    spy_confirmed: bool,
    volume_confirmed: bool,
    entry: float,
    stop: float,
) -> List[str]:
    """Human-readable warning strings (used for UI and 'no warning signs' score)."""
    out: List[str] = []

    if r_mult < 1.5:
        out.append("R multiple is below 1.5")
    if not vwap_aligned:
        out.append("VWAP is not aligned")
    if not spy_confirmed:
        out.append("SPY is not confirmed")
    if not volume_confirmed:
        out.append("Volume is not confirmed")
    if stop == entry:
        out.append("Stop equals entry")
    if direction == "None":
        out.append("Direction is None")
    if direction == "Long" and stop >= entry:
        out.append("Long setup: stop should be below entry")
    if direction == "Short" and stop <= entry:
        out.append("Short setup: stop should be above entry")

    return out


def trade_decision(score: int, r_mult: float) -> str:
    if r_mult < 1.5:
        return "NO TRADE"
    if score >= 75:
        return "TRADE ALLOWED"
    if score >= 65:
        return "WATCH ONLY"
    return "NO TRADE"
