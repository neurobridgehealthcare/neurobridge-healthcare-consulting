"""
Procedural scenario engine — scales to 10,000+ training scenarios without a giant CSV.

Scenarios are generated on demand from (market, setup_type, seed).
Training only. No live trading.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fathers_hand_simulator import (
    SCENARIOS_FILE,
    SETUP_TYPES,
    FullScenario,
    MARKETS,
    _build_synthetic_scenario,
    _starter_featured_scenarios,
    ensure_scenario_library,
)

PROJECT_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = PROJECT_DIR / "fathers_hand_scenario_registry.json"

# Seeds available per (market, setup_type) — 10 markets × 10 setups × 1000 = 100,000 IDs
SEEDS_PER_COMBO = 1_000
GENERATION_VERSION = 2

# Primary training markets (display label → canonical ticker)
TRAINING_MARKET_CHOICES: List[Tuple[str, str]] = [
    ("QQQ", "QQQ"),
    ("SPY", "SPY"),
    ("NQ", "NQ"),
    ("XAUUSD", "Gold"),
    ("EUR/USD", "EUR/USD"),
    ("GBP/USD", "GBP/USD"),
    ("GBP/JPY", "GBP/JPY"),
    ("AUD/USD", "AUD/USD"),
    ("BTC/USD", "BTC/USD"),
    ("ETH/USD", "ETH/USD"),
]

_MARKET_ASSET: Dict[str, str] = {m: ac for m, ac in MARKETS}
_FEATURED_BY_MARKET: Dict[str, List[FullScenario]] = {}
_CSV_SCENARIOS: List[FullScenario] = []

MARKET_MODES: Dict[str, Dict[str, Any]] = {
    "My Edge Mode": {
        "markets": ["QQQ", "SPY", "NQ"],
        "description": "Primary focus: QQQ, SPY, and Nasdaq futures.",
    },
    "All Markets Mode": {
        "markets": [t for t, _ in TRAINING_MARKET_CHOICES],
        "description": "QQQ, SPY, NQ, Gold, Forex, and Crypto.",
    },
    "Forex Mode": {
        "markets": ["EUR/USD", "GBP/USD", "GBP/JPY", "AUD/USD"],
        "description": "Forex session training.",
    },
    "Futures Mode": {
        "markets": ["NQ", "XAUUSD"],
        "description": "Futures and metals.",
    },
    "Crypto Mode": {
        "markets": ["BTC/USD", "ETH/USD"],
        "description": "24h crypto training.",
    },
}

DEFAULT_MARKET_MODE = "My Edge Mode"


def _init_featured_index() -> None:
    global _FEATURED_BY_MARKET
    if _FEATURED_BY_MARKET:
        return
    for s in _starter_featured_scenarios():
        _FEATURED_BY_MARKET.setdefault(s.market.upper(), []).append(s)


def normalize_market(market: str) -> str:
    key = market.strip().upper().replace("GOLD", "XAUUSD").replace("EURUSD", "EUR/USD")
    key = key.replace("GBPUSD", "GBP/USD").replace("GBPJPY", "GBP/JPY").replace("AUDUSD", "AUD/USD")
    for ticker, _label in TRAINING_MARKET_CHOICES:
        if key == ticker.upper() or key == _label.upper():
            return ticker
    for ticker, _ in TRAINING_MARKET_CHOICES:
        if ticker.upper() == key:
            return ticker
    return market


def _market_asset_class(market: str) -> str:
    m = normalize_market(market)
    return _MARKET_ASSET.get(m, "stock_etf")


def _rng_for(market: str, setup_type: str, seed: int) -> random.Random:
    """Deterministic RNG so the same ID always yields the same scenario."""
    key = f"{GENERATION_VERSION}|{market}|{setup_type}|{seed}"
    digest = hashlib.sha256(key.encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def scenario_id_for(market: str, setup_type: str, seed: int) -> str:
    slug = normalize_market(market).lower().replace("/", "")
    setup_slug = setup_type.lower().replace(" ", "_").replace("-", "_")
    return f"gen_{slug}_{setup_slug}_{seed:05d}"


def generate_scenario(
    market: str,
    seed: int,
    setup_type: Optional[str] = None,
) -> FullScenario:
    """Build one scenario from seed. Same inputs → same scenario."""
    mkt = normalize_market(market)
    asset = _market_asset_class(mkt)
    setup = setup_type or SETUP_TYPES[seed % len(SETUP_TYPES)]
    rng = _rng_for(mkt, setup, seed)
    scenario = _build_synthetic_scenario(
        idx=seed,
        market=mkt,
        asset_class=asset,
        setup_type=setup,
        rng=rng,
    )
    scenario.scenario_id = scenario_id_for(mkt, setup, seed)
    return scenario


def _load_csv_scenarios() -> List[FullScenario]:
    global _CSV_SCENARIOS
    if _CSV_SCENARIOS:
        return _CSV_SCENARIOS
    ensure_scenario_library(250)
    if not SCENARIOS_FILE.is_file():
        return []
    try:
        import pandas as pd

        _CSV_SCENARIOS = [
            FullScenario.from_row(row)
            for _, row in pd.read_csv(SCENARIOS_FILE).iterrows()
        ]
    except Exception:  # noqa: BLE001
        _CSV_SCENARIOS = []
    return _CSV_SCENARIOS


def markets_for_mode(mode: str) -> List[str]:
    info = MARKET_MODES.get(mode, MARKET_MODES[DEFAULT_MARKET_MODE])
    return list(info["markets"])


def pick_scenario_for_market(
    market: str,
    exclude_ids: Optional[List[str]] = None,
    featured_chance: float = 0.12,
    prefer_csv: bool = True,
) -> FullScenario:
    """Pick a random scenario for a market (CSV library first, then procedural)."""
    _init_featured_index()
    mkt = normalize_market(market)
    exclude = set(exclude_ids or [])

    if prefer_csv:
        pool = [s for s in _load_csv_scenarios() if s.market == mkt and s.scenario_id not in exclude]
        if pool:
            return random.choice(pool)  # noqa: S311

    if featured_chance > 0 and mkt.upper() in _FEATURED_BY_MARKET:
        featured = [s for s in _FEATURED_BY_MARKET[mkt.upper()] if s.scenario_id not in exclude]
        if featured and random.random() < featured_chance:  # noqa: S311
            return random.choice(featured)  # noqa: S311

    for _ in range(40):
        setup = random.choice(SETUP_TYPES)  # noqa: S311
        seed = random.randint(0, SEEDS_PER_COMBO - 1)  # noqa: S311
        s = generate_scenario(mkt, seed, setup)
        if s.scenario_id not in exclude:
            return s

    return generate_scenario(mkt, random.randint(0, SEEDS_PER_COMBO - 1))  # noqa: S311


def pick_scenario_for_mode(
    mode: str = DEFAULT_MARKET_MODE,
    exclude_ids: Optional[List[str]] = None,
) -> FullScenario:
    """Pick a random scenario from markets allowed by the training mode."""
    markets = markets_for_mode(mode)
    market = random.choice(markets)  # noqa: S311
    return pick_scenario_for_market(market, exclude_ids=exclude_ids)


def pick_scenario(
    market: Optional[str] = None,
    exclude_ids: Optional[List[str]] = None,
) -> FullScenario:
    if market:
        return pick_scenario_for_market(market, exclude_ids)
    ticker = random.choice(TRAINING_MARKET_CHOICES)[0]  # noqa: S311
    return pick_scenario_for_market(ticker, exclude_ids)


def sample_scenarios(
    market: Optional[str] = None,
    setup_type: Optional[str] = None,
    limit: int = 50,
) -> List[FullScenario]:
    """Return a small preview sample without materializing the full library."""
    markets = [normalize_market(market)] if market else [t for t, _ in TRAINING_MARKET_CHOICES]
    setups = [setup_type] if setup_type else list(SETUP_TYPES)
    out: List[FullScenario] = []
    seed_step = max(1, SEEDS_PER_COMBO // max(limit, 1))
    for mkt in markets:
        for setup in setups:
            for seed in range(0, min(SEEDS_PER_COMBO, limit * seed_step), seed_step):
                out.append(generate_scenario(mkt, seed, setup))
                if len(out) >= limit:
                    return out
    return out


def library_capacity() -> Dict[str, Any]:
    n_markets = len(TRAINING_MARKET_CHOICES)
    n_setups = len(SETUP_TYPES)
    procedural = n_markets * n_setups * SEEDS_PER_COMBO
    _init_featured_index()
    featured = sum(len(v) for v in _FEATURED_BY_MARKET.values())
    return {
        "generation_version": GENERATION_VERSION,
        "seeds_per_combo": SEEDS_PER_COMBO,
        "markets": n_markets,
        "setup_types": n_setups,
        "procedural_capacity": procedural,
        "featured_scenarios": featured,
        "total_capacity": procedural + featured,
        "markets_list": [t for t, _ in TRAINING_MARKET_CHOICES],
        "setup_types_list": list(SETUP_TYPES),
    }


def library_stats() -> Dict[str, Any]:
    cap = library_capacity()
    csv_pool = _load_csv_scenarios()
    by_market: Dict[str, int] = {t: 0 for t, _ in TRAINING_MARKET_CHOICES}
    for s in csv_pool:
        by_market[s.market] = by_market.get(s.market, 0) + 1
    by_setup = {s: SEEDS_PER_COMBO * len(TRAINING_MARKET_CHOICES) for s in SETUP_TYPES}
    return {
        "total": max(len(csv_pool), cap["total_capacity"]),
        "csv_scenarios": len(csv_pool),
        "procedural": cap["procedural_capacity"],
        "featured": cap["featured_scenarios"],
        "synthetic": len(csv_pool) or cap["procedural_capacity"],
        "by_market": by_market,
        "by_setup": by_setup,
        "generation": "csv_library_plus_procedural",
        "market_modes": list(MARKET_MODES.keys()),
        "expansion_targets": {
            "csv_library": "250+ starter scenarios with OHLCV",
            "procedural_pool": f"{cap['total_capacity']:,}+",
            "historical_import": "unlimited via OHLCV pipeline",
        },
    }


def ensure_registry() -> Path:
    if not REGISTRY_FILE.is_file():
        REGISTRY_FILE.write_text(json.dumps(library_capacity(), indent=2), encoding="utf-8")
    return REGISTRY_FILE
