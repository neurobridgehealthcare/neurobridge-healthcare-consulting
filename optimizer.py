"""
Stage 3B — QQQ ORB parameter optimizer with walk-forward validation.

Research tool only. Uses Stage 3A backtester replay on pre-loaded market data.
Not for live trading. Past performance does not guarantee future results.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import backtester
from backtester import (
    BacktestConfig,
    BacktestMarketData,
    BacktestResult,
    BacktestTrade,
    DirectionFilter,
    StopStyle,
    list_tradable_session_dates,
    load_backtest_market_data,
    run_backtest_with_data,
)

PROJECT_DIR = Path(__file__).resolve().parent
OPTIMIZER_RESULTS_FILE = PROJECT_DIR / "optimizer_results.csv"
BEST_CONFIG_FILE = PROJECT_DIR / "best_config.json"

ProgressCb = Optional[Callable[[str], None]]

# In-process cache so repeated optimizer runs skip Alpaca downloads.
_MARKET_DATA_CACHE: Dict[Tuple[str, str, bool, bool], BacktestMarketData] = {}

# Fixed optimizer defaults (grid always uses volume + RVOL per spec)
OPT_ACCOUNT_SIZE = 100_000.0
OPT_RISK_PERCENT = 1.0
OPT_OR_SIZE_MIN = 1.0
OPT_OR_SIZE_MAX = 6.0


@dataclass
class OptimizerParams:
    """One parameter combination in the search grid."""

    direction_filter: DirectionFilter
    r_target: float
    max_trades_per_day: int
    min_rvol: float
    stop_style: StopStyle
    fixed_stop_percent: float
    vwap_filter: bool
    spy_confirmation: bool
    daily_trend_qqq_ema20_filter: bool
    or_size_filter_enabled: bool
    enable_entry_cutoff: bool
    entry_cutoff_time: str

    def label(self) -> str:
        cutoff = "off" if not self.enable_entry_cutoff else self.entry_cutoff_time
        stop = self.stop_style
        if self.stop_style == "fixed_pct":
            stop = f"fixed_{self.fixed_stop_percent:.2f}pct"
        return (
            f"dir={self.direction_filter}|R={self.r_target}|maxTr={self.max_trades_per_day}|"
            f"rvol={self.min_rvol:.2f}|stop={stop}|vwap={'Y' if self.vwap_filter else 'N'}|"
            f"spy={'Y' if self.spy_confirmation else 'N'}|trend={'Y' if self.daily_trend_qqq_ema20_filter else 'N'}|"
            f"orSz={'Y' if self.or_size_filter_enabled else 'N'}|cut={cutoff}"
        )

    def to_backtest_config(self, start: date, end: date) -> BacktestConfig:
        return BacktestConfig(
            start_date=start,
            end_date=end,
            account_size=OPT_ACCOUNT_SIZE,
            risk_percent=OPT_RISK_PERCENT,
            r_target=self.r_target,
            stop_style=self.stop_style,
            fixed_stop_percent=self.fixed_stop_percent,
            max_trades_per_day=self.max_trades_per_day,
            vwap_filter=self.vwap_filter,
            spy_confirmation=self.spy_confirmation,
            volume_confirmation=True,
            direction_filter=self.direction_filter,
            daily_trend_qqq_ema20_filter=self.daily_trend_qqq_ema20_filter,
            or_size_filter_enabled=self.or_size_filter_enabled,
            or_size_min=OPT_OR_SIZE_MIN,
            or_size_max=OPT_OR_SIZE_MAX,
            use_rvol_filter=True,
            min_rvol=self.min_rvol,
            enable_entry_cutoff=self.enable_entry_cutoff,
            entry_cutoff_time=self.entry_cutoff_time,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizerRunMetrics:
    params: OptimizerParams
    train_robustness: float = 0.0
    test_robustness: float = 0.0
    final_score: float = 0.0
    train_summary: Dict[str, float] = field(default_factory=dict)
    test_summary: Dict[str, float] = field(default_factory=dict)
    consistency_ratio: float = 0.0
    train_trades: List[BacktestTrade] = field(default_factory=list)
    test_trades: List[BacktestTrade] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def params_label(self) -> str:
        return self.params.label()


@dataclass
class OptimizerResult:
    rows: List[OptimizerRunMetrics] = field(default_factory=list)
    best_overall: Optional[OptimizerRunMetrics] = None
    best_conservative: Optional[OptimizerRunMetrics] = None
    best_aggressive: Optional[OptimizerRunMetrics] = None
    train_start: Optional[date] = None
    train_end: Optional[date] = None
    test_start: Optional[date] = None
    test_end: Optional[date] = None
    grid_size: int = 0
    quick_mode: bool = False
    skipped_count: int = 0
    error: Optional[str] = None


def count_parameter_grid(
    include_daily_trend: bool = False,
    include_or_size_filter: bool = False,
    quick_mode: bool = False,
) -> int:
    """Return grid size; ``quick_mode=True`` uses the small starter search only."""
    if quick_mode:
        return len(iter_quick_parameter_grid())
    return len(iter_parameter_grid(include_daily_trend, include_or_size_filter))


def build_parameter_grid(
    include_daily_trend: bool = False,
    include_or_size_filter: bool = False,
    quick_mode: bool = False,
) -> List[OptimizerParams]:
    if quick_mode:
        return iter_quick_parameter_grid()
    return iter_parameter_grid(include_daily_trend, include_or_size_filter)


def iter_quick_parameter_grid() -> List[OptimizerParams]:
    """Small starter grid (~8 combos) for fast optimizer smoke tests."""
    combos: List[OptimizerParams] = []
    for max_tr, rvol, (cut_en, cut_time) in itertools.product(
        [1, 2],
        [1.25, 1.50],
        [(False, "11:00"), (True, "11:00")],
    ):
        combos.append(
            OptimizerParams(
                direction_filter="both",
                r_target=2.0,
                max_trades_per_day=max_tr,
                min_rvol=rvol,
                stop_style="opposite_or",
                fixed_stop_percent=0.5,
                vwap_filter=True,
                spy_confirmation=True,
                daily_trend_qqq_ema20_filter=False,
                or_size_filter_enabled=False,
                enable_entry_cutoff=cut_en,
                entry_cutoff_time=cut_time,
            )
        )
    return combos


def iter_parameter_grid(
    include_daily_trend: bool = False,
    include_or_size_filter: bool = False,
) -> List[OptimizerParams]:
    directions: List[DirectionFilter] = ["long", "short", "both"]
    r_targets = [1.5, 2.0, 2.5, 3.0]
    max_trades = [1, 2]
    min_rvols = [1.10, 1.25, 1.50, 1.75, 2.00]
    vwap_opts = [True, False]
    spy_opts = [True, False]
    daily_trend_opts = [False, True] if include_daily_trend else [False]
    or_size_opts = [False, True] if include_or_size_filter else [False]
    cutoff_opts: List[Tuple[bool, str]] = [
        (False, "11:00"),
        (True, "10:30"),
        (True, "11:00"),
        (True, "11:30"),
    ]

    stop_combos: List[Tuple[StopStyle, float]] = [("opposite_or", 0.5)]
    for pct in (0.25, 0.35, 0.50):
        stop_combos.append(("fixed_pct", pct))

    combos: List[OptimizerParams] = []
    for (
        direction,
        r_tgt,
        max_tr,
        rvol,
        (stop_style, fixed_pct),
        vwap,
        spy,
        daily_tr,
        or_sz,
        (cut_en, cut_time),
    ) in itertools.product(
        directions,
        r_targets,
        max_trades,
        min_rvols,
        stop_combos,
        vwap_opts,
        spy_opts,
        daily_trend_opts,
        or_size_opts,
        cutoff_opts,
    ):
        combos.append(
            OptimizerParams(
                direction_filter=direction,
                r_target=r_tgt,
                max_trades_per_day=max_tr,
                min_rvol=rvol,
                stop_style=stop_style,
                fixed_stop_percent=fixed_pct,
                vwap_filter=vwap,
                spy_confirmation=spy,
                daily_trend_qqq_ema20_filter=daily_tr,
                or_size_filter_enabled=or_sz,
                enable_entry_cutoff=cut_en,
                entry_cutoff_time=cut_time,
            )
        )
    return combos


def list_tradable_session_dates(
    market: BacktestMarketData,
    start: date,
    end: date,
) -> List[date]:
    """Calendar dates with enough QQQ + SPY session bars for replay."""
    return backtester.list_tradable_session_dates(market, start, end)


def split_train_test_dates(
    session_dates: List[date],
    train_fraction: float = 0.70,
) -> Tuple[List[date], List[date]]:
    if len(session_dates) < 10:
        return session_dates, []
    split_idx = max(1, int(len(session_dates) * train_fraction))
    if split_idx >= len(session_dates):
        split_idx = len(session_dates) - 1
    return session_dates[:split_idx], session_dates[split_idx:]


def equity_stability_r2(pnls: List[float]) -> float:
    """R² of cumulative equity vs trade index (1.0 = perfectly linear growth)."""
    if len(pnls) < 3:
        return 0.0
    cum: List[float] = []
    running = 0.0
    for p in pnls:
        running += p
        cum.append(running)
    n = len(cum)
    x_mean = (n - 1) / 2.0
    y_mean = sum(cum) / n
    ss_tot = sum((y - y_mean) ** 2 for y in cum)
    if ss_tot < 1e-12:
        return 1.0 if cum[-1] >= 0 else 0.0
    ss_xy = sum((i - x_mean) * (cum[i] - y_mean) for i in range(n))
    ss_xx = sum((i - x_mean) ** 2 for i in range(n))
    if ss_xx < 1e-12:
        return 0.0
    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    ss_res = sum((cum[i] - (intercept + slope * i)) ** 2 for i in range(n))
    return max(0.0, min(1.0, 1.0 - ss_res / ss_tot))


def compute_robustness_score(summary: Dict[str, float], trades: List[BacktestTrade]) -> float:
    """
    Rank parameter sets by robustness — not raw P/L alone.
    Rewards PF, expectancy, P/L, stable equity; penalizes low sample, weak PF, large DD.
    """
    n = int(summary.get("total_trades", 0))
    if n < 1:
        return -1000.0

    pf = float(summary.get("profit_factor", 0.0))
    exp = float(summary.get("expectancy", 0.0))
    pnl = float(summary.get("total_pnl", 0.0))
    max_dd = abs(float(summary.get("max_drawdown", 0.0)))

    score = 0.0

    # Sample size — need enough trades to matter
    if n < 30:
        score -= (30 - n) * 3.0
    else:
        score += min(n - 30, 170) * 0.08

    # Profit factor
    if pf < 1.2:
        score -= (1.2 - min(pf, 1.2)) * 60.0
    else:
        score += min(pf, 4.0) * 12.0

    # Expectancy per trade
    if exp <= 0:
        score -= 25.0
    else:
        score += min(exp / 75.0, 8.0) * 4.0

    # Total P/L (capped) with penalty when profit comes from very few trades
    pnl_component = min(max(pnl, -50_000.0) / 5000.0, 15.0)
    score += pnl_component
    if n < 30 and pnl > 0:
        score -= (pnl / max(n, 1)) * 0.015

    # Drawdown penalty (relative to gross activity)
    if max_dd > 0:
        dd_pen = min(max_dd / max(abs(pnl), 500.0), 3.0) * 18.0
        score -= dd_pen

    # Equity curve stability
    pnls = [t.pnl for t in trades]
    score += equity_stability_r2(pnls) * 20.0

    return score


def compute_walk_forward_final_score(
    train_score: float,
    test_score: float,
    train_summary: Dict[str, float],
    test_summary: Dict[str, float],
) -> Tuple[float, float]:
    """
    Combine train + test robustness; reject configs that fail out-of-sample.
    Returns (final_score, consistency_ratio).
    """
    test_n = int(test_summary.get("total_trades", 0))
    test_pf = float(test_summary.get("profit_factor", 0.0))
    test_exp = float(test_summary.get("expectancy", 0.0))

    if test_n < 8:
        return -1000.0, 0.0
    if test_pf < 1.0:
        return -800.0, 0.0
    if test_exp <= 0:
        return -600.0, 0.0

    consistency = test_score / max(train_score, 1.0)
    if train_score > 0 and consistency < 0.25:
        return -500.0, consistency
    if train_score <= 0 and test_score <= 0:
        return -400.0, consistency

    final = test_score * 0.55 + train_score * 0.25 + min(consistency, 1.25) * 25.0
    if test_pf < 1.2:
        final -= (1.2 - test_pf) * 40.0
    return final, consistency


def get_cached_market_data(
    start_date: date,
    end_date: date,
    *,
    need_daily_ema: bool = False,
    need_rvol: bool = True,
    progress: ProgressCb = None,
    session_cache: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[BacktestMarketData], Optional[str]]:
    """
    Load Alpaca data once per (date range, flags) and reuse across parameter combos.
    ``session_cache`` (e.g. Streamlit session_state dict) persists across app reruns.
    """
    cache_key = (
        start_date.isoformat(),
        end_date.isoformat(),
        need_daily_ema,
        need_rvol,
    )
    if session_cache is not None and cache_key in session_cache:
        if progress:
            progress("Using cached market data (session)…")
        return session_cache[cache_key], None

    if cache_key in _MARKET_DATA_CACHE:
        if progress:
            progress("Using cached market data (memory)…")
        market = _MARKET_DATA_CACHE[cache_key]
        if session_cache is not None:
            session_cache[cache_key] = market
        return market, None

    market, err = load_backtest_market_data(
        start_date,
        end_date,
        need_daily_ema=need_daily_ema,
        need_rvol=need_rvol,
        progress=progress,
    )
    if err or market is None:
        return market, err

    _MARKET_DATA_CACHE[cache_key] = market
    if session_cache is not None:
        session_cache[cache_key] = market
    return market, None


def _replay_period(
    params: OptimizerParams,
    market: BacktestMarketData,
    start: date,
    end: date,
) -> BacktestResult:
    cfg = params.to_backtest_config(start, end)
    return run_backtest_with_data(cfg, market, write_csv=False)


def _format_progress(
    phase: str,
    idx: int,
    total: int,
    params: OptimizerParams,
    extra: str = "",
) -> str:
    pct = int((idx / total) * 100) if total else 0
    msg = (
        f"**{phase}** {idx}/{total} ({pct}%)  \n"
        f"`{params.label()}`"
    )
    if extra:
        msg += f"  \n{extra}"
    return msg


def run_optimizer(
    start_date: date,
    end_date: date,
    *,
    quick_mode: bool = True,
    include_daily_trend: bool = False,
    include_or_size_filter: bool = False,
    train_fraction: float = 0.70,
    top_n: int = 20,
    progress: ProgressCb = None,
    session_cache: Optional[Dict[str, Any]] = None,
) -> OptimizerResult:
    """
    Walk-forward optimizer: rank on training robustness, validate top N on test period.
    """
    grid = build_parameter_grid(
        include_daily_trend, include_or_size_filter, quick_mode=quick_mode
    )
    grid_size = len(grid)
    if end_date < start_date:
        return OptimizerResult(
            error="End date must be on or after start date.",
            grid_size=grid_size,
            quick_mode=quick_mode,
        )

    need_daily = (not quick_mode and include_daily_trend) or any(
        p.daily_trend_qqq_ema20_filter for p in grid
    )
    market, err = get_cached_market_data(
        start_date,
        end_date,
        need_daily_ema=need_daily,
        need_rvol=True,
        progress=progress,
        session_cache=session_cache,
    )
    if err or market is None:
        return OptimizerResult(
            error=err or "Could not load market data.",
            grid_size=grid_size,
            quick_mode=quick_mode,
        )

    session_dates = list_tradable_session_dates(market, start_date, end_date)
    train_dates, test_dates = split_train_test_dates(session_dates, train_fraction)
    if not train_dates:
        return OptimizerResult(
            error="Not enough session dates in range.",
            grid_size=grid_size,
            quick_mode=quick_mode,
        )
    if len(test_dates) < 5:
        return OptimizerResult(
            error="Not enough test-session dates (need wider date range for 30% holdout).",
            grid_size=grid_size,
            quick_mode=quick_mode,
        )

    train_start, train_end = train_dates[0], train_dates[-1]
    test_start, test_end = test_dates[0], test_dates[-1]

    train_runs: List[OptimizerRunMetrics] = []
    partial_rows: List[OptimizerRunMetrics] = []
    skipped = 0
    total = grid_size

    for idx, params in enumerate(grid):
        if progress:
            progress(_format_progress("Training", idx + 1, total, params, "Running train replay…"))
        try:
            train_res = _replay_period(params, market, train_start, train_end)
            train_score = compute_robustness_score(train_res.summary, train_res.trades)
            row = OptimizerRunMetrics(
                params=params,
                train_robustness=train_score,
                train_summary=train_res.summary,
                train_trades=train_res.trades,
            )
            train_runs.append(row)
            partial_rows.append(row)
            write_optimizer_results_csv(partial_rows)
            if progress:
                progress(
                    _format_progress(
                        "Training",
                        idx + 1,
                        total,
                        params,
                        f"Train score **{train_score:.1f}** · trades **{int(train_res.summary.get('total_trades', 0))}**",
                    )
                )
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            if progress:
                progress(
                    _format_progress(
                        "Training",
                        idx + 1,
                        total,
                        params,
                        f"Skipped (error): {exc}",
                    )
                )
            continue

    if not train_runs:
        return OptimizerResult(
            error="All parameter combinations failed during training.",
            grid_size=grid_size,
            quick_mode=quick_mode,
            skipped_count=skipped,
        )

    train_runs.sort(key=lambda r: r.train_robustness, reverse=True)
    validate_n = min(top_n, len(train_runs))
    if quick_mode:
        validate_n = len(train_runs)
    candidates = train_runs[:validate_n]

    if progress:
        progress(f"Walk-forward validation on top **{len(candidates)}** configs…")

    validated: List[OptimizerRunMetrics] = []
    for vidx, cand in enumerate(candidates):
        if progress:
            progress(
                _format_progress(
                    "Testing",
                    vidx + 1,
                    len(candidates),
                    cand.params,
                    "Running out-of-sample replay…",
                )
            )
        try:
            test_res = _replay_period(cand.params, market, test_start, test_end)
            test_score = compute_robustness_score(test_res.summary, test_res.trades)
            final, consistency = compute_walk_forward_final_score(
                cand.train_robustness,
                test_score,
                cand.train_summary,
                test_res.summary,
            )
            row = OptimizerRunMetrics(
                params=cand.params,
                train_robustness=cand.train_robustness,
                test_robustness=test_score,
                final_score=final,
                train_summary=cand.train_summary,
                test_summary=test_res.summary,
                consistency_ratio=consistency,
                train_trades=cand.train_trades,
                test_trades=test_res.trades,
            )
            validated.append(row)
            write_optimizer_results_csv(validated)
            if progress:
                progress(
                    _format_progress(
                        "Testing",
                        vidx + 1,
                        len(candidates),
                        cand.params,
                        f"Test score **{test_score:.1f}** · final **{final:.1f}**",
                    )
                )
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            if progress:
                progress(
                    _format_progress(
                        "Testing",
                        vidx + 1,
                        len(candidates),
                        cand.params,
                        f"Skipped (error): {exc}",
                    )
                )
            continue

    if not validated:
        return OptimizerResult(
            error="All walk-forward validations failed.",
            rows=partial_rows,
            grid_size=grid_size,
            quick_mode=quick_mode,
            skipped_count=skipped,
            train_start=train_start,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
        )

    validated.sort(key=lambda r: r.final_score, reverse=True)
    passing = [r for r in validated if r.final_score > -400]

    best_overall = passing[0] if passing else (validated[0] if validated else None)

    conservative_pool = [
        r
        for r in passing
        if float(r.test_summary.get("profit_factor", 0)) >= 1.3
        and float(r.test_summary.get("max_drawdown", 0)) > -15_000
    ]
    conservative_pool.sort(
        key=lambda r: (
            r.test_robustness,
            -abs(float(r.test_summary.get("max_drawdown", 0))),
        ),
        reverse=True,
    )
    best_conservative = conservative_pool[0] if conservative_pool else best_overall

    aggressive_pool = [
        r
        for r in passing
        if float(r.test_summary.get("profit_factor", 0)) >= 1.15
        and int(r.test_summary.get("total_trades", 0)) >= 8
    ]
    aggressive_pool.sort(
        key=lambda r: float(r.test_summary.get("total_pnl", 0)),
        reverse=True,
    )
    best_aggressive = aggressive_pool[0] if aggressive_pool else best_overall

    result = OptimizerResult(
        rows=validated,
        best_overall=best_overall,
        best_conservative=best_conservative,
        best_aggressive=best_aggressive,
        train_start=train_start,
        train_end=train_end,
        test_start=test_start,
        test_end=test_end,
        grid_size=grid_size,
        quick_mode=quick_mode,
        skipped_count=skipped,
    )

    write_optimizer_results_csv(validated)
    if best_overall is not None:
        write_best_config_json(best_overall, result)

    if progress:
        progress(
            f"Done — **{len(validated)}** validated · **{skipped}** skipped · "
            f"results saved to `{OPTIMIZER_RESULTS_FILE.name}`"
        )

    return result


def metrics_to_row(m: OptimizerRunMetrics) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "params": m.params_label,
        "final_score": round(m.final_score, 4),
        "train_robustness": round(m.train_robustness, 4),
        "test_robustness": round(m.test_robustness, 4),
        "consistency_ratio": round(m.consistency_ratio, 4),
    }
    for prefix, summary in (("train_", m.train_summary), ("test_", m.test_summary)):
        for key in (
            "total_trades",
            "win_rate",
            "avg_r",
            "total_pnl",
            "expectancy",
            "profit_factor",
            "max_drawdown",
        ):
            val = summary.get(key, 0.0)
            row[f"{prefix}{key}"] = round(val, 4) if isinstance(val, float) else val
    p = m.params
    row.update(
        {
            "direction_filter": p.direction_filter,
            "r_target": p.r_target,
            "max_trades_per_day": p.max_trades_per_day,
            "min_rvol": p.min_rvol,
            "stop_style": p.stop_style,
            "fixed_stop_percent": p.fixed_stop_percent,
            "vwap_filter": p.vwap_filter,
            "spy_confirmation": p.spy_confirmation,
            "daily_trend_filter": p.daily_trend_qqq_ema20_filter,
            "or_size_filter": p.or_size_filter_enabled,
            "entry_cutoff_enabled": p.enable_entry_cutoff,
            "entry_cutoff_time": p.entry_cutoff_time,
        }
    )
    if m.error:
        row["error"] = m.error
    return row


def write_optimizer_results_csv(
    rows: List[OptimizerRunMetrics],
    path: Path = OPTIMIZER_RESULTS_FILE,
) -> Path:
    if not rows:
        with path.open("w", newline="", encoding="utf-8") as f:
            f.write("")
        return path
    dict_rows = [metrics_to_row(r) for r in rows]
    fieldnames = list(dict_rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(dict_rows)
    return path


def write_best_config_json(
    best: OptimizerRunMetrics,
    result: OptimizerResult,
    path: Path = BEST_CONFIG_FILE,
) -> Path:
    payload = {
        "warning": "Research only — not predictive of future performance. Do not auto-trade.",
        "params": best.params.to_dict(),
        "params_label": best.params_label,
        "final_score": best.final_score,
        "train_robustness": best.train_robustness,
        "test_robustness": best.test_robustness,
        "consistency_ratio": best.consistency_ratio,
        "train_period": {
            "start": result.train_start.isoformat() if result.train_start else None,
            "end": result.train_end.isoformat() if result.train_end else None,
        },
        "test_period": {
            "start": result.test_start.isoformat() if result.test_start else None,
            "end": result.test_end.isoformat() if result.test_end else None,
        },
        "train_summary": {k: round(v, 4) if isinstance(v, float) else v for k, v in best.train_summary.items()},
        "test_summary": {k: round(v, 4) if isinstance(v, float) else v for k, v in best.test_summary.items()},
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


def results_table_df(rows: List[OptimizerRunMetrics], limit: int = 20):
    import pandas as pd

    data = [metrics_to_row(r) for r in rows[:limit]]
    return pd.DataFrame(data)
