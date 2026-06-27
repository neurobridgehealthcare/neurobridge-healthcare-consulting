"""
Stage 3G — Scored paper trade journal (research log, not Alpaca execution).
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCORED_PAPER_TRADES_FILE = Path(__file__).resolve().parent / "scored_paper_trades.csv"

COLUMNS: List[str] = [
    "timestamp_utc",
    "ticker",
    "direction",
    "entry_time",
    "entry",
    "stop",
    "target",
    "environment_score",
    "environment_label",
    "trade_score",
    "trade_label",
    "allow_block_decision",
    "environment_tags_json",
    "reason_list",
    "risk_warnings",
    "user_notes",
    "or_size",
    "r_multiple",
]


def _collect_csv_fieldnames(rows: List[Dict[str, Any]]) -> List[str]:
    keys: set[str] = set()
    for row in rows:
        keys.update(row.keys())
    ordered = [c for c in COLUMNS if c in keys]
    rest = sorted(k for k in keys if k not in ordered)
    return ordered + rest


def append_scored_paper_trade(row: Dict[str, Any]) -> Path:
    """Append one scored paper log row (creates file + header if needed)."""
    exists = SCORED_PAPER_TRADES_FILE.is_file()
    payload = {k: row.get(k, "") for k in COLUMNS}
    if not payload.get("timestamp_utc"):
        payload["timestamp_utc"] = datetime.now(timezone.utc).isoformat()

    if exists:
        with SCORED_PAPER_TRADES_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_fields = reader.fieldnames or list(COLUMNS)
        fieldnames = list(dict.fromkeys(list(existing_fields) + list(payload.keys())))
    else:
        fieldnames = list(COLUMNS)

    with SCORED_PAPER_TRADES_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow({k: payload.get(k, "") for k in fieldnames})
    return SCORED_PAPER_TRADES_FILE


def format_tags_json(tags: Optional[Dict[str, Any]]) -> str:
    if not tags:
        return ""
    return json.dumps(tags, default=str)
