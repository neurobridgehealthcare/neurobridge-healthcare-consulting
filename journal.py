"""
Append completed signal snapshots to signals.csv.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SIGNALS_FILE = Path(__file__).resolve().parent / "signals.csv"

# Stable column order for the CSV header
COLUMNS: List[str] = [
    "saved_at_utc",
    "account_size",
    "risk_percent",
    "or_high",
    "or_low",
    "qqq_price",
    "direction",
    "vwap_aligned",
    "spy_confirmed",
    "volume_confirmed",
    "entry",
    "stop",
    "target",
    "or_midpoint",
    "or_size",
    "risk_per_share",
    "max_dollar_risk",
    "position_size_shares",
    "reward_per_share",
    "r_multiple",
    "setup_score",
    "decision",
    "warnings",
]


def save_signal(row: Dict[str, Any]) -> Path:
    """
    Append one row to signals.csv (creates file with header if needed).
    """
    file_exists = SIGNALS_FILE.is_file()
    with SIGNALS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        payload = {k: row.get(k, "") for k in COLUMNS}
        if "saved_at_utc" not in row or not row["saved_at_utc"]:
            payload["saved_at_utc"] = datetime.now(timezone.utc).isoformat()
        writer.writerow(payload)
    return SIGNALS_FILE
