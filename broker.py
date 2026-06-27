"""
Alpaca paper trading only (Stage 2B). Never submits to the live brokerage API.

Uses the same env vars as market data:
  ALPACA_API_KEY
  ALPACA_SECRET_KEY

Use API keys from the Alpaca **Paper Trading** dashboard with this module.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from data_provider import MISSING_KEYS_MESSAGE, load_alpaca_keys_from_env

PAPER_ORDERS_FILE = Path(__file__).resolve().parent / "paper_orders.csv"

PAPER_ORDER_COLUMNS = [
    "timestamp",
    "symbol",
    "direction",
    "qty",
    "order_id",
    "status",
    "submitted_at",
    "entry",
    "stop",
    "target",
    "setup_score",
    "r_multiple",
    "max_buying_power_usage_percent",
    "buying_power",
    "cash",
    "portfolio_value",
    "risk_based_size",
    "buying_power_cap_size",
    "final_order_size",
    "estimated_order_cost",
]


@dataclass
class PaperOrderResult:
    """Outcome of a paper order attempt (safe to show in the UI)."""

    ok: bool
    message: str
    order_id: Optional[str] = None
    status: Optional[str] = None
    submitted_at: Optional[str] = None


@dataclass
class PaperAccountSnapshot:
    """Key balances from ``get_account()`` (paper account only)."""

    buying_power: float
    cash: float
    portfolio_value: float


@dataclass
class PaperOrderSizing:
    """Risk-based size vs buying-power cap (whole shares)."""

    risk_based_size: int
    buying_power_cap_size: int
    final_order_size: int
    max_allowed_trade_value: float
    estimated_order_cost: float


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value))


def create_paper_trading_client():
    """
    Build an Alpaca TradingClient that **only** talks to the paper trading API.

    Returns ``None`` if API keys are missing. Never returns a live client.
    """
    keys = load_alpaca_keys_from_env()
    if keys is None:
        return None
    api_key, secret_key = keys
    from alpaca.trading.client import TradingClient

    # `paper=True` is required — it selects BaseURL.TRADING_PAPER.
    return TradingClient(api_key, secret_key, paper=True)


def fetch_paper_account_snapshot() -> Tuple[Optional[PaperAccountSnapshot], Optional[str]]:
    """
    Load Alpaca **paper** account balances (``get_account``).

    Returns ``(snapshot, None)`` on success, or ``(None, error_message)``.
    """
    client = create_paper_trading_client()
    if client is None:
        return None, MISSING_KEYS_MESSAGE

    try:
        from alpaca.common.exceptions import APIError

        acct = client.get_account()
        snap = PaperAccountSnapshot(
            buying_power=_to_float(acct.buying_power),
            cash=_to_float(acct.cash),
            portfolio_value=_to_float(acct.portfolio_value),
        )
        return snap, None
    except APIError as exc:
        return None, f"Could not load paper account (Alpaca): {exc}"
    except Exception as exc:  # noqa: BLE001
        return None, f"Could not load paper account: {exc}"


def compute_paper_order_sizing(
    *,
    risk_based_shares: int,
    entry_price: float,
    buying_power: float,
    max_buying_power_usage_percent: float,
) -> PaperOrderSizing:
    """
    Cap risk-based share count by a fraction of Alpaca **buying_power**.

    - ``max_allowed_trade_value = buying_power * (max_usage / 100)``
    - ``buying_power_cap_size = floor(max_allowed_trade_value / entry_price)``
    - ``final_order_size = min(risk_based_shares, buying_power_cap_size)``
    - ``estimated_order_cost = final_order_size * entry_price``
    """
    risk_sz = max(0, int(risk_based_shares))
    if entry_price <= 0 or buying_power <= 0:
        return PaperOrderSizing(
            risk_based_size=risk_sz,
            buying_power_cap_size=0,
            final_order_size=0,
            max_allowed_trade_value=0.0,
            estimated_order_cost=0.0,
        )

    pct = max(0.0, float(max_buying_power_usage_percent))
    max_allowed = buying_power * (pct / 100.0)
    bp_cap = int(math.floor(max_allowed / entry_price))
    bp_cap = max(0, bp_cap)
    final_sz = min(risk_sz, bp_cap)
    est_cost = final_sz * entry_price

    return PaperOrderSizing(
        risk_based_size=risk_sz,
        buying_power_cap_size=bp_cap,
        final_order_size=final_sz,
        max_allowed_trade_value=max_allowed,
        estimated_order_cost=est_cost,
    )


def submit_paper_market_order_qqq(
    *,
    qty: int,
    direction: str,
) -> PaperOrderResult:
    """
    Submit a **day** market order for **QQQ** on the **paper** account.

    - Long  → BUY
    - Short → SELL

    Does not submit when ``qty <= 0``, keys are missing, or direction is invalid.
    """
    if qty <= 0:
        return PaperOrderResult(False, "Position size must be greater than zero to submit an order.")

    if direction not in ("Long", "Short"):
        return PaperOrderResult(False, "Direction must be Long or Short to submit a stock order.")

    client = create_paper_trading_client()
    if client is None:
        return PaperOrderResult(False, MISSING_KEYS_MESSAGE)

    try:
        from alpaca.common.exceptions import APIError
        from alpaca.trading.enums import OrderSide, TimeInForce
        from alpaca.trading.requests import MarketOrderRequest

        side = OrderSide.BUY if direction == "Long" else OrderSide.SELL
        order_req = MarketOrderRequest(
            symbol="QQQ",
            qty=float(qty),
            side=side,
            time_in_force=TimeInForce.DAY,
        )
        order = client.submit_order(order_data=order_req)
    except APIError as exc:
        return PaperOrderResult(False, f"Alpaca API error: {exc}")
    except Exception as exc:  # noqa: BLE001 — surface unexpected errors in the UI
        return PaperOrderResult(False, f"Order failed: {exc}")

    oid = str(order.id) if getattr(order, "id", None) is not None else ""
    raw_status = order.status
    status_str = raw_status.value if hasattr(raw_status, "value") else str(raw_status)
    sub_at = getattr(order, "submitted_at", None)
    submitted_iso = sub_at.isoformat() if sub_at is not None else ""

    return PaperOrderResult(
        ok=True,
        message="Order submitted to Alpaca paper trading.",
        order_id=oid,
        status=status_str,
        submitted_at=submitted_iso,
    )


def append_paper_order_csv(row: Dict[str, Any]) -> Path:
    """Append one successful paper order row to ``paper_orders.csv`` (creates header if needed)."""
    file_exists = PAPER_ORDERS_FILE.is_file()
    with PAPER_ORDERS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PAPER_ORDER_COLUMNS)
        if not file_exists:
            writer.writeheader()
        payload = {k: row.get(k, "") for k in PAPER_ORDER_COLUMNS}
        if not payload.get("timestamp"):
            payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        writer.writerow(payload)
    return PAPER_ORDERS_FILE
