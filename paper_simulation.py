"""
Stage 3I — Paper simulation report.

Replays EdgeOne ORB strategy on historical data with compounding account balance,
per-trade environment + trade scores, and CSV exports. Research only — no live orders.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

import pandas as pd

import adaptive_environment
import backtester
import environment_engine
import live_trade_scoring
from backtester import BacktestConfig, BacktestTrade, compute_opening_range_rvol
from live_trade_scoring import LiveTradeScoreInput, LiveTradeScoreResult, TradeBlockThresholds
from risk import Direction

PROJECT_DIR = Path(__file__).resolve().parent
TRADES_FILE = PROJECT_DIR / "paper_simulation_trades.csv"
MONTHLY_FILE = PROJECT_DIR / "paper_simulation_monthly.csv"
SUMMARY_FILE = PROJECT_DIR / "paper_simulation_summary.csv"
SHEETS_TRADES_FILE = PROJECT_DIR / "paper_simulation_trades_google_sheets.csv"

# Stage 3A replay skips signals when shares × entry > account_size. Small accounts ($1k + QQQ)
# would block every trade — use a floor for signal discovery only; P/L uses real balance.
SIGNAL_REPLAY_ACCOUNT_FLOOR = 100_000.0

SimulationModeName = Literal["STRICT", "MODERATE", "RELAXED"]
ProgressCb = Optional[Callable[[str], None]]


@dataclass(frozen=True)
class SimulationModeThresholds:
    name: SimulationModeName
    min_environment_score: float
    min_trade_score: float
    min_rvol: float
    max_or_size: float


SIMULATION_MODES: Dict[SimulationModeName, SimulationModeThresholds] = {
    "STRICT": SimulationModeThresholds("STRICT", 45.0, 60.0, 1.0, 8.0),
    "MODERATE": SimulationModeThresholds("MODERATE", 40.0, 55.0, 1.2, 8.0),
    "RELAXED": SimulationModeThresholds("RELAXED", 30.0, 50.0, 1.0, 10.0),
}


def get_simulation_mode(name: str) -> SimulationModeThresholds:
    key = name.upper() if isinstance(name, str) else "STRICT"
    if key not in SIMULATION_MODES:
        key = "STRICT"
    return SIMULATION_MODES[key]  # type: ignore[index]


def current_best_edgeone_backtest_config(
    start_date: date,
    end_date: date,
    account_size: float,
    risk_percent: float,
) -> BacktestConfig:
    """Preset from spec: Both, max 2/day, R=2, opposite OR, filters on, RVOL 1.50."""
    return BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        account_size=account_size,
        risk_percent=risk_percent,
        r_target=2.0,
        stop_style="opposite_or",
        fixed_stop_percent=0.5,
        max_trades_per_day=2,
        vwap_filter=True,
        spy_confirmation=True,
        volume_confirmation=True,
        direction_filter="both",
        daily_trend_qqq_ema20_filter=False,
        or_size_filter_enabled=False,
        use_rvol_filter=True,
        min_rvol=1.50,
        enable_entry_cutoff=False,
        favorable_environments_only=False,
    )


@dataclass
class SimulationReplayStats:
    tradable_session_days: int = 0
    candidate_setups: int = 0
    blocked_environment_score: int = 0
    blocked_trade_score: int = 0
    blocked_rvol: int = 0
    blocked_or_size: int = 0
    blocked_r_multiple: int = 0
    blocked_buying_power: int = 0
    blocked_other: int = 0
    approved_setups: int = 0
    executed_paper_trades: int = 0
    signal_replay_account_used: float = 0.0
    strategy_replay_min_rvol: float = 0.0
    simulation_mode: str = "STRICT"
    low_trade_count_warning: bool = False

    def to_display_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SimulatedTradeRow:
    trade_id: str
    date: str
    time: str
    ticker: str
    direction: str
    entry: float
    stop: float
    target: float
    exit: float
    exit_reason: str
    result: str
    r_multiple: float
    shares: int
    pnl: float
    account_balance_after: float
    environment_score: float
    environment_label: str
    trade_score: float
    trade_label: str
    notes: str = ""


@dataclass
class MonthlySimRow:
    month: str
    starting_balance: float
    ending_balance: float
    pnl: float
    return_pct: float
    number_of_trades: int
    win_rate: float


@dataclass
class PaperSimulationSummary:
    starting_balance: float
    ending_balance: float
    total_return_pct: float
    total_pnl: float
    number_of_trades: int
    win_rate: float
    profit_factor: float
    expectancy: float
    max_drawdown: float
    best_trade_pnl: float
    worst_trade_pnl: float
    average_weekly_return_pct: float
    average_monthly_return_pct: float
    start_date: str
    end_date: str
    risk_percent: float
    preset_label: str
    simulation_mode: str = "STRICT"


@dataclass
class PaperSimulationResult:
    summary: PaperSimulationSummary
    trades: List[SimulatedTradeRow] = field(default_factory=list)
    monthly: List[MonthlySimRow] = field(default_factory=list)
    balance_curve: List[Dict[str, Any]] = field(default_factory=list)
    drawdown_curve: List[Dict[str, Any]] = field(default_factory=list)
    monthly_pnl_chart: List[Dict[str, Any]] = field(default_factory=list)
    replay_stats: SimulationReplayStats = field(default_factory=SimulationReplayStats)
    error: Optional[str] = None


@dataclass
class CandidateEvaluation:
    env_score: float
    env_label: str
    trade_score: float
    trade_label: str
    session_rvol: Optional[float]
    score_input: LiveTradeScoreInput
    score_result: LiveTradeScoreResult
    block_categories: List[str]
    approved: bool


def _signal_replay_account(starting_balance: float) -> float:
    return max(float(starting_balance), SIGNAL_REPLAY_ACCOUNT_FLOOR)


def _risk_per_share(entry: float, stop: float, direction: str) -> float:
    if direction == "Long":
        return max(0.0, entry - stop)
    if direction == "Short":
        return max(0.0, stop - entry)
    return 0.0


def _position_shares(balance: float, risk_percent: float, risk_per_share: float) -> int:
    if risk_per_share <= 0 or balance <= 0:
        return 0
    max_risk = balance * (risk_percent / 100.0)
    return int(max_risk // risk_per_share)


def _affordable_shares(balance: float, entry: float) -> int:
    if entry <= 0 or balance <= 0:
        return 0
    return int(balance // entry)


def _trade_pnl(direction: str, entry: float, exit_price: float, shares: int) -> float:
    if shares <= 0:
        return 0.0
    if direction == "Long":
        return (exit_price - entry) * shares
    if direction == "Short":
        return (entry - exit_price) * shares
    return 0.0


def _result_label(pnl: float) -> str:
    if pnl > 0:
        return "win"
    if pnl < 0:
        return "loss"
    return "breakeven"


def cast_direction(value: str) -> Direction:
    if value == "Long":
        return "Long"
    if value == "Short":
        return "Short"
    return "None"


def _score_candidate(
    trade: BacktestTrade,
    bundle: environment_engine.EnvironmentMarketBundle,
    rules: adaptive_environment.AdaptiveEnvironmentRules,
    market: backtester.BacktestMarketData,
    volume_confirmation: bool,
) -> CandidateEvaluation:
    """Historical environment + trade score (no live session state required)."""
    env_score = 50.0
    env_label = "NEUTRAL"
    or_quality: Optional[str] = None
    time_bucket: Optional[str] = None
    rel_strength: Optional[str] = None

    try:
        features = environment_engine.compute_session_environment_features(
            bundle, trade.date, trade.entry_time
        )
        tags = features.tags_for_scoring()
        assessment = adaptive_environment.assess_environment(
            tags, rules, session_features=features
        )
        env_score = float(assessment.environment_score)
        env_label = str(assessment.environment_label)
        or_quality = features.or_candle_quality
        time_bucket = features.time_bucket
        rel_strength = features.relative_strength
    except Exception:  # noqa: BLE001
        or_quality = None
        time_bucket = trade.time_bucket
        rel_strength = trade.qqq_vs_spy_strength

    session_rvol: Optional[float] = None
    try:
        session_rvol = compute_opening_range_rvol(trade.date, market.or_vol_by_date)
    except Exception:  # noqa: BLE001
        pass

    direction = cast_direction(trade.direction)
    vwap_ok = trade.VWAP_alignment in ("Yes", "yes", "True", "true")
    if trade.VWAP_alignment == "n/a":
        vwap_ok = True
    spy_ok = trade.SPY_confirmation in ("Yes", "yes", "True", "true")
    if trade.SPY_confirmation == "n/a":
        spy_ok = True

    score_inp = live_trade_scoring.build_score_input_from_context(
        environment_score=env_score,
        environment_label=env_label,
        vwap_aligned=vwap_ok,
        spy_confirmed=spy_ok,
        volume_confirmed=volume_confirmation,
        session_rvol=session_rvol,
        or_candle_quality=or_quality,
        relative_strength=rel_strength,
        time_bucket=time_bucket,
        entry=trade.entry,
        stop=trade.stop,
        or_size=trade.OR_size,
        direction=direction,
        r_multiple=float(trade.r_multiple),
    )
    score_res = live_trade_scoring.compute_live_trade_score(score_inp)

    return CandidateEvaluation(
        env_score=env_score,
        env_label=env_label,
        trade_score=score_res.trade_score,
        trade_label=score_res.label,
        session_rvol=session_rvol,
        score_input=score_inp,
        score_result=score_res,
        block_categories=[],
        approved=False,
    )


def _apply_simulation_mode_filter(
    evaluation: CandidateEvaluation,
    mode: SimulationModeThresholds,
) -> CandidateEvaluation:
    """Stage 3D/3E/3F-style gates for paper simulation (rule-based, no live state)."""
    thresholds = TradeBlockThresholds(
        min_environment_score=mode.min_environment_score,
        min_trade_score=mode.min_trade_score,
        min_rvol=mode.min_rvol,
        max_or_size=mode.max_or_size,
    )
    blocked_result = live_trade_scoring.apply_trade_blocking(
        evaluation.score_result,
        evaluation.score_input,
        thresholds,
    )

    categories: List[str] = []
    inp = evaluation.score_input

    if inp.environment_score < mode.min_environment_score:
        categories.append("environment_score")
    if blocked_result.trade_score < mode.min_trade_score:
        categories.append("trade_score")
    if mode.min_rvol > 0 and inp.session_rvol is not None and inp.session_rvol < mode.min_rvol:
        categories.append("rvol")
    if inp.or_size > mode.max_or_size:
        categories.append("or_size")
    if inp.r_multiple < 1.5:
        categories.append("r_multiple")
    if inp.direction == "None":
        categories.append("other")

    evaluation.score_result = blocked_result
    evaluation.trade_score = blocked_result.trade_score
    evaluation.trade_label = blocked_result.label
    evaluation.block_categories = categories
    evaluation.approved = len(categories) == 0
    return evaluation


def _increment_block_stats(stats: SimulationReplayStats, categories: List[str]) -> None:
    if not categories:
        return
    primary = categories[0]
    if primary == "environment_score":
        stats.blocked_environment_score += 1
    elif primary == "trade_score":
        stats.blocked_trade_score += 1
    elif primary == "rvol":
        stats.blocked_rvol += 1
    elif primary == "or_size":
        stats.blocked_or_size += 1
    elif primary == "r_multiple":
        stats.blocked_r_multiple += 1
    else:
        stats.blocked_other += 1


def _compute_drawdown(balance_points: List[Tuple[date, float]]) -> Tuple[float, List[Dict[str, Any]]]:
    if not balance_points:
        return 0.0, []
    peak = balance_points[0][1]
    max_dd = 0.0
    curve: List[Dict[str, Any]] = []
    for d, bal in balance_points:
        peak = max(peak, bal)
        dd = bal - peak
        max_dd = min(max_dd, dd)
        dd_pct = (dd / peak * 100.0) if peak > 0 else 0.0
        curve.append({"date": d.isoformat(), "drawdown_dollars": round(dd, 2), "drawdown_pct": round(dd_pct, 2)})
    return float(max_dd), curve


def _monthly_breakdown(
    trades: List[SimulatedTradeRow],
    starting_balance: float,
) -> List[MonthlySimRow]:
    if not trades:
        return []

    by_month: Dict[str, List[SimulatedTradeRow]] = {}
    for t in trades:
        month = t.date[:7]
        by_month.setdefault(month, []).append(t)

    rows: List[MonthlySimRow] = []
    balance = starting_balance
    for month in sorted(by_month.keys()):
        month_trades = by_month[month]
        start_bal = balance
        month_pnl = sum(t.pnl for t in month_trades)
        balance += month_pnl
        wins = sum(1 for t in month_trades if t.pnl > 0)
        ret_pct = (month_pnl / start_bal * 100.0) if start_bal > 0 else 0.0
        rows.append(
            MonthlySimRow(
                month=month,
                starting_balance=round(start_bal, 2),
                ending_balance=round(balance, 2),
                pnl=round(month_pnl, 2),
                return_pct=round(ret_pct, 2),
                number_of_trades=len(month_trades),
                win_rate=round(wins / len(month_trades), 4) if month_trades else 0.0,
            )
        )
    return rows


def _period_return_averages(
    trades: List[SimulatedTradeRow],
    starting_balance: float,
) -> Tuple[float, float]:
    if not trades or starting_balance <= 0:
        return 0.0, 0.0

    monthly = _monthly_breakdown(trades, starting_balance)
    monthly_returns = [m.return_pct for m in monthly]
    avg_monthly = sum(monthly_returns) / len(monthly_returns) if monthly_returns else 0.0

    ordered = sorted(trades, key=lambda x: (x.date, x.time))
    running = starting_balance
    week_start_balance: Dict[str, float] = {}
    week_end_balance: Dict[str, float] = {}
    for t in ordered:
        d = date.fromisoformat(t.date)
        week_key = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
        if week_key not in week_start_balance:
            week_start_balance[week_key] = running
        running = t.account_balance_after
        week_end_balance[week_key] = running

    weekly_returns: List[float] = []
    for wk in sorted(week_start_balance.keys()):
        sb = week_start_balance[wk]
        eb = week_end_balance.get(wk, sb)
        if sb > 0:
            weekly_returns.append((eb - sb) / sb * 100.0)

    avg_weekly = sum(weekly_returns) / len(weekly_returns) if weekly_returns else 0.0
    return round(avg_weekly, 2), round(avg_monthly, 2)


def _build_summary(
    trades: List[SimulatedTradeRow],
    starting_balance: float,
    start_date: date,
    end_date: date,
    risk_percent: float,
    preset_label: str,
    simulation_mode: str,
) -> PaperSimulationSummary:
    ending = trades[-1].account_balance_after if trades else starting_balance
    total_pnl = ending - starting_balance
    total_ret = (total_pnl / starting_balance * 100.0) if starting_balance > 0 else 0.0

    pnls = [t.pnl for t in trades]
    wins = sum(1 for p in pnls if p > 0)
    losses = [p for p in pnls if p < 0]
    gains = [p for p in pnls if p > 0]
    gross_win = sum(gains) if gains else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    pf = (gross_win / gross_loss) if gross_loss > 1e-9 else (999.0 if gross_win > 0 else 0.0)

    balance_points = [(date.fromisoformat(t.date), t.account_balance_after) for t in trades]
    if trades:
        first_d = date.fromisoformat(trades[0].date)
        balance_points.insert(0, (first_d, starting_balance))
    max_dd, _ = _compute_drawdown(balance_points)

    avg_weekly, avg_monthly = _period_return_averages(trades, starting_balance)

    return PaperSimulationSummary(
        starting_balance=round(starting_balance, 2),
        ending_balance=round(ending, 2),
        total_return_pct=round(total_ret, 2),
        total_pnl=round(total_pnl, 2),
        number_of_trades=len(trades),
        win_rate=round(wins / len(trades), 4) if trades else 0.0,
        profit_factor=round(pf, 4),
        expectancy=round(total_pnl / len(trades), 2) if trades else 0.0,
        max_drawdown=round(max_dd, 2),
        best_trade_pnl=round(max(pnls), 2) if pnls else 0.0,
        worst_trade_pnl=round(min(pnls), 2) if pnls else 0.0,
        average_weekly_return_pct=avg_weekly,
        average_monthly_return_pct=avg_monthly,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        risk_percent=risk_percent,
        preset_label=preset_label,
        simulation_mode=simulation_mode,
    )


def _build_env_bundle_from_market(
    market: backtester.BacktestMarketData,
    start_date: date,
    end_date: date,
    progress: ProgressCb = None,
) -> environment_engine.EnvironmentMarketBundle:
    """Prefer full bundle (premarket/gap); fall back to session-only market data."""
    bundle, err = environment_engine.load_environment_market_bundle(
        start_date, end_date, progress=progress
    )
    if bundle is not None:
        return bundle
    if progress and err:
        progress(f"Environment bundle partial load ({err}) — using session bars only for scoring.")
    return environment_engine.EnvironmentMarketBundle(
        market=market,
        premarket_qqq={},
        prev_close_qqq={},
        spy_lookup=market.spy_lookup,
    )


def run_paper_simulation(
    *,
    starting_balance: float,
    start_date: date,
    end_date: date,
    risk_percent: float,
    backtest_cfg: BacktestConfig,
    preset_label: str = "Current Best EdgeOne Setup",
    simulation_mode: str = "STRICT",
    progress: ProgressCb = None,
    adaptive_rules: Optional[adaptive_environment.AdaptiveEnvironmentRules] = None,
) -> PaperSimulationResult:
    """Run historical simulation: 3A replay → 3D/3E score → 3F mode filter → compounding P/L."""
    mode = get_simulation_mode(simulation_mode)
    empty_summary = _build_summary(
        [], starting_balance, start_date, end_date, risk_percent, preset_label, mode.name
    )
    stats = SimulationReplayStats(
        simulation_mode=mode.name,
        strategy_replay_min_rvol=float(backtest_cfg.min_rvol),
    )

    if end_date < start_date:
        return PaperSimulationResult(
            summary=empty_summary,
            replay_stats=stats,
            error="End date must be on or after start date.",
        )

    if progress:
        progress("Loading market data for simulation…")

    market, err = backtester.load_backtest_market_data(
        start_date,
        end_date,
        need_daily_ema=backtest_cfg.daily_trend_qqq_ema20_filter,
        need_rvol=backtest_cfg.volume_confirmation and backtest_cfg.use_rvol_filter,
        progress=progress,
    )
    if err or market is None:
        return PaperSimulationResult(
            summary=empty_summary,
            replay_stats=stats,
            error=err or "Could not load market data.",
        )

    tradable_days = backtester.list_tradable_session_dates(market, start_date, end_date)
    stats.tradable_session_days = len(tradable_days)

    signal_account = _signal_replay_account(starting_balance)
    stats.signal_replay_account_used = signal_account

    if progress:
        progress(
            f"Running Stage 3A replay on {stats.tradable_session_days} tradable sessions "
            f"(signal account ${signal_account:,.0f} — fixes small-account share cap)…"
        )

    replay_cfg = BacktestConfig(
        **{
            **asdict(backtest_cfg),
            "account_size": signal_account,
            "start_date": start_date,
            "end_date": end_date,
        }
    )
    bt_result = backtester.run_backtest_with_data(replay_cfg, market, write_csv=False)

    stats.candidate_setups = len(bt_result.trades)
    if not bt_result.trades:
        if progress:
            progress(
                "Replay found 0 candidate setups — check date range, Alpaca data, or strategy filters "
                f"(tradable days: {stats.tradable_session_days}, replay min RVOL: {stats.strategy_replay_min_rvol})."
            )
        summary = _build_summary([], starting_balance, start_date, end_date, risk_percent, preset_label, mode.name)
        return PaperSimulationResult(summary=summary, replay_stats=stats, error=None)

    if progress:
        progress("Loading environment data for Stage 3D scoring…")

    env_bundle = _build_env_bundle_from_market(market, start_date, end_date, progress=progress)

    if progress:
        progress("Enriching candidates with OR / regime / relative-strength tags…")
    environment_engine.enrich_trades(bt_result.trades, env_bundle, progress=progress)

    rules = adaptive_rules or adaptive_environment.load_adaptive_rules_from_disk()
    if rules is None:
        rules = adaptive_environment.AdaptiveEnvironmentRules()

    if progress:
        progress(f"Applying {mode.name} simulation filters (env + trade score + RVOL + OR size)…")

    balance = float(starting_balance)
    simulated: List[SimulatedTradeRow] = []
    total = len(bt_result.trades)

    for i, trade in enumerate(bt_result.trades):
        if progress and (i == 0 or (i + 1) % 10 == 0 or i + 1 == total):
            progress(f"Scoring candidate {i + 1}/{total}…")

        evaluation = _score_candidate(
            trade,
            env_bundle,
            rules,
            market,
            backtest_cfg.volume_confirmation,
        )
        evaluation = _apply_simulation_mode_filter(evaluation, mode)

        if not evaluation.approved:
            _increment_block_stats(stats, evaluation.block_categories)
            continue

        stats.approved_setups += 1

        risk_each = _risk_per_share(trade.entry, trade.stop, trade.direction)
        risk_shares = _position_shares(balance, risk_percent, risk_each)
        affordable = _affordable_shares(balance, trade.entry)
        shares = min(risk_shares, affordable) if affordable > 0 else risk_shares

        if shares <= 0:
            stats.blocked_buying_power += 1
            continue

        pnl = _trade_pnl(trade.direction, trade.entry, trade.exit_price, shares)
        balance += pnl
        stats.executed_paper_trades += 1

        entry_tm = trade.entry_time.isoformat() if trade.entry_time else ""
        trade_id = f"{trade.date.isoformat()}_{entry_tm}_{trade.direction}_{i}"

        simulated.append(
            SimulatedTradeRow(
                trade_id=trade_id,
                date=trade.date.isoformat(),
                time=entry_tm,
                ticker="QQQ",
                direction=trade.direction,
                entry=round(trade.entry, 4),
                stop=round(trade.stop, 4),
                target=round(trade.target, 4),
                exit=round(trade.exit_price, 4),
                exit_reason=trade.exit_reason,
                result=_result_label(pnl),
                r_multiple=round(float(trade.r_multiple), 4),
                shares=shares,
                pnl=round(pnl, 2),
                account_balance_after=round(balance, 2),
                environment_score=round(evaluation.env_score, 2),
                environment_label=evaluation.env_label,
                trade_score=round(evaluation.trade_score, 2),
                trade_label=evaluation.trade_label,
                notes="",
            )
        )

    stats.low_trade_count_warning = stats.executed_paper_trades < 10

    summary = _build_summary(
        simulated, starting_balance, start_date, end_date, risk_percent, preset_label, mode.name
    )
    monthly = _monthly_breakdown(simulated, starting_balance)

    balance_curve: List[Dict[str, Any]] = [{"date": start_date.isoformat(), "balance": starting_balance}]
    for t in simulated:
        balance_curve.append({"date": t.date, "balance": t.account_balance_after})

    _, drawdown_curve = _compute_drawdown(
        [(date.fromisoformat(p["date"]), float(p["balance"])) for p in balance_curve]
    )

    monthly_pnl_chart = [{"month": m.month, "pnl": m.pnl} for m in monthly]

    if progress:
        progress(
            f"Done — {stats.candidate_setups} candidates, {stats.approved_setups} approved, "
            f"{stats.executed_paper_trades} executed, ending ${summary.ending_balance:,.2f}."
        )

    return PaperSimulationResult(
        summary=summary,
        trades=simulated,
        monthly=monthly,
        balance_curve=balance_curve,
        drawdown_curve=drawdown_curve,
        monthly_pnl_chart=monthly_pnl_chart,
        replay_stats=stats,
    )


def trades_to_dataframe(trades: List[SimulatedTradeRow]) -> pd.DataFrame:
    cols = [
        "date",
        "time",
        "ticker",
        "direction",
        "entry",
        "stop",
        "target",
        "exit",
        "result",
        "r_multiple",
        "pnl",
        "account_balance_after",
        "environment_score",
        "trade_score",
        "notes",
    ]
    rows = []
    for t in trades:
        rows.append(
            {
                "date": t.date,
                "time": t.time,
                "ticker": t.ticker,
                "direction": t.direction,
                "entry": t.entry,
                "stop": t.stop,
                "target": t.target,
                "exit": t.exit,
                "result": t.result,
                "r_multiple": t.r_multiple,
                "pnl": t.pnl,
                "account_balance_after": t.account_balance_after,
                "environment_score": t.environment_score,
                "trade_score": t.trade_score,
                "notes": t.notes,
            }
        )
    return pd.DataFrame(rows, columns=cols)


def apply_notes_from_editor(
    trades: List[SimulatedTradeRow],
    edited_df: pd.DataFrame,
) -> List[SimulatedTradeRow]:
    if edited_df is None or edited_df.empty or len(edited_df) != len(trades):
        return trades
    if "notes" not in edited_df.columns:
        return trades
    for i, t in enumerate(trades):
        val = edited_df.iloc[i].get("notes", "")
        t.notes = "" if pd.isna(val) else str(val)
    return trades


def write_simulation_exports(result: PaperSimulationResult) -> Dict[str, Path]:
    paths: Dict[str, Path] = {}

    trade_df = trades_to_dataframe(result.trades)
    trade_df.to_csv(TRADES_FILE, index=False, encoding="utf-8")
    paths["trades"] = TRADES_FILE

    sheets_content = trade_df.to_csv(index=False)
    SHEETS_TRADES_FILE.write_text("\ufeff" + sheets_content, encoding="utf-8")
    paths["sheets_trades"] = SHEETS_TRADES_FILE

    monthly_rows = [asdict(m) for m in result.monthly]
    pd.DataFrame(monthly_rows).to_csv(MONTHLY_FILE, index=False, encoding="utf-8")
    paths["monthly"] = MONTHLY_FILE

    summary_row = {**asdict(result.summary), **result.replay_stats.to_display_dict()}
    pd.DataFrame([summary_row]).to_csv(SUMMARY_FILE, index=False, encoding="utf-8")
    paths["summary"] = SUMMARY_FILE

    return paths
