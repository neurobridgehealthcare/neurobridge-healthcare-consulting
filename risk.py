"""
Risk and reward math for ORB setups (manual inputs).
Beginner-friendly: pure functions, no I/O.
"""

from __future__ import annotations

from typing import Literal

Direction = Literal["Long", "Short", "None"]


def or_midpoint(or_high: float, or_low: float) -> float:
    return (or_high + or_low) / 2.0


def or_size(or_high: float, or_low: float) -> float:
    return or_high - or_low


def max_dollar_risk(account_size: float, risk_percent: float) -> float:
    """Maximum dollars willing to lose on this trade."""
    return account_size * (risk_percent / 100.0)


def risk_per_share(entry: float, stop: float, direction: Direction) -> float:
    """
    Dollars at risk per share (always >= 0 for display).
    Invalid geometry returns 0.0 (warnings handle messaging).
    """
    if direction == "Long":
        return max(0.0, entry - stop)
    if direction == "Short":
        return max(0.0, stop - entry)
    return 0.0


def reward_per_share(entry: float, target: float, direction: Direction) -> float:
    """Dollars of profit per share if target is hit."""
    if direction == "Long":
        return max(0.0, target - entry)
    if direction == "Short":
        return max(0.0, entry - target)
    return 0.0


def position_size(max_risk_dollars: float, risk_each: float) -> int:
    """Whole shares only; 0 if risk per share is missing."""
    if risk_each <= 0:
        return 0
    return int(max_risk_dollars // risk_each)


def r_multiple(reward_each: float, risk_each: float) -> float:
    if risk_each <= 0:
        return 0.0
    return reward_each / risk_each
