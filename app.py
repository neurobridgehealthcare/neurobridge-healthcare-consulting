"""
EdgeOne ORB — Streamlit dashboard (Manual, Live Data, Paper, Backtest).
"""

from __future__ import annotations

import copy
from datetime import date, time, timedelta
from pathlib import Path
from typing import cast

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

import adaptive_environment
import backtester
import broker
import data_provider
import environment_engine
import fathers_hand
import journal
import live_trade_scoring
import optimizer
import paper_simulation
import risk
import scored_paper_journal
import scoring

st.set_page_config(page_title="EdgeOne ORB", layout="wide")

load_dotenv(Path(__file__).resolve().parent / ".env")

st.title("EdgeOne ORB")
st.caption(
    "QQQ ORB — Manual / Live Data (2A) / Paper (2B) / Backtest (3A) / Optimizer (3B) / "
    "Environment (3C) / Adaptive filter (3D) / Trade scoring (3E–3G) / Father's Hand (3H) / "
    "Paper simulation (3I)"
)

mode = st.radio(
    "Mode",
    ["Manual Mode", "Live Data Mode"],
    horizontal=True,
    help="Manual: type all fields yourself. Live: pull QQQ/SPY intraday data from Alpaca (read-only).",
)

yes_no_options = ("Yes", "No")


def yn_to_bool(label: str, key: str) -> bool:
    return st.selectbox(label, yes_no_options, index=0, key=key) == "Yes"


# --- Defaults (used until Manual inputs or Live snapshot assign values) ---
account_size = 100_000.0
risk_percent = 1.0
or_high = 450.0
or_low = 448.0
current_qqq = 450.5
direction = cast(risk.Direction, "Long")
vwap_aligned = True
spy_confirmed = True
volume_confirmed = True
entry = 450.25
stop = 449.50
target = 452.00

if mode == "Manual Mode":
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Account & opening range")
        account_size = st.number_input(
            "Account size ($)", min_value=0.0, value=100_000.0, step=1_000.0, key="m_acct"
        )
        risk_percent = st.number_input(
            "Risk percent (per trade)",
            min_value=0.0,
            max_value=100.0,
            value=1.0,
            step=0.1,
            key="m_riskpct",
        )
        or_high = st.number_input("OR high (QQQ)", value=450.0, step=0.01, format="%.2f", key="m_orh")
        or_low = st.number_input("OR low (QQQ)", value=448.0, step=0.01, format="%.2f", key="m_orl")
        current_qqq = st.number_input(
            "Current QQQ price", value=450.5, step=0.01, format="%.2f", key="m_qqq"
        )

    with col_b:
        st.subheader("Setup & trade plan")
        direction = cast(
            risk.Direction,
            st.selectbox("Direction", ["Long", "Short", "None"], index=0, key="m_dir"),
        )
        vwap_aligned = yn_to_bool("VWAP aligned", "m_vwap")
        spy_confirmed = yn_to_bool("SPY confirmed", "m_spy")
        volume_confirmed = yn_to_bool("Volume confirmed", "m_vol")
        entry = st.number_input("Entry", value=450.25, step=0.01, format="%.2f", key="m_ent")
        stop = st.number_input("Stop", value=449.50, step=0.01, format="%.2f", key="m_stp")
        target = st.number_input("Target", value=452.00, step=0.01, format="%.2f", key="m_tgt")

else:
    # --- Live Data Mode ---
    st.subheader("Live market data (Alpaca)")
    _, btn_col = st.columns([4, 1])
    with btn_col:
        refresh = st.button("Refresh market data")

    cache_key = "live_market_cache_v1"
    if refresh or cache_key not in st.session_state:
        with st.spinner("Loading QQQ / SPY from Alpaca…"):
            snap, err = data_provider.fetch_live_snapshot()
        st.session_state[cache_key] = {"snap": snap, "err": err}

    bundle = st.session_state[cache_key]
    live_snap = bundle["snap"]
    live_err = bundle["err"]

    if live_err:
        st.warning(live_err)
        st.caption("Enter opening range and QQQ price manually until live data is available.")
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Account & opening range (fallback)")
            account_size = st.number_input(
                "Account size ($)", min_value=0.0, value=100_000.0, step=1_000.0, key="l_acct"
            )
            risk_percent = st.number_input(
                "Risk percent (per trade)",
                min_value=0.0,
                max_value=100.0,
                value=1.0,
                step=0.1,
                key="l_riskpct",
            )
            or_high = st.number_input(
                "OR high (QQQ)", value=450.0, step=0.01, format="%.2f", key="l_orh"
            )
            or_low = st.number_input(
                "OR low (QQQ)", value=448.0, step=0.01, format="%.2f", key="l_orl"
            )
            current_qqq = st.number_input(
                "Current QQQ price", value=450.5, step=0.01, format="%.2f", key="l_qqq"
            )
        with col_b:
            st.subheader("Setup & trade plan")
            direction = cast(
                risk.Direction,
                st.selectbox("Direction", ["Long", "Short", "None"], index=0, key="l_dir"),
            )
            vwap_aligned = yn_to_bool("VWAP aligned", "l_vwap")
            spy_confirmed = yn_to_bool("SPY confirmed", "l_spy")
            volume_confirmed = yn_to_bool("Volume confirmed", "l_vol")
            entry = st.number_input("Entry", value=450.25, step=0.01, format="%.2f", key="l_ent")
            stop = st.number_input("Stop", value=449.50, step=0.01, format="%.2f", key="l_stp")
            target = st.number_input("Target", value=452.00, step=0.01, format="%.2f", key="l_tgt")
    else:
        assert live_snap is not None
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Account & opening range (from Alpaca)")
            account_size = st.number_input(
                "Account size ($)", min_value=0.0, value=100_000.0, step=1_000.0, key="lv_acct"
            )
            risk_percent = st.number_input(
                "Risk percent (per trade)",
                min_value=0.0,
                max_value=100.0,
                value=1.0,
                step=0.1,
                key="lv_riskpct",
            )
            or_high = float(live_snap.or_high)
            or_low = float(live_snap.or_low)
            current_qqq = float(live_snap.qqq_last)
            st.metric("OR high (9:30–9:45 ET)", f"{or_high:.2f}")
            st.metric("OR low (9:30–9:45 ET)", f"{or_low:.2f}")
            st.metric("Current QQQ (last bar close)", f"{current_qqq:.2f}")
            st.caption(
                f"Trading date (ET): **{live_snap.trading_date}** — "
                f"latest bar **{live_snap.latest_bar_time_et.strftime('%Y-%m-%d %H:%M %Z')}**"
            )

        with col_b:
            st.subheader("Setup & trade plan")
            direction = cast(
                risk.Direction,
                st.selectbox("Direction", ["Long", "Short", "None"], index=0, key="lv_dir"),
            )
            st.markdown("**VWAP & SPY (from live data)**")
            st.write(
                f"- QQQ last **{live_snap.qqq_vs_vwap}** session VWAP "
                f"({live_snap.qqq_last:.2f} vs VWAP {live_snap.qqq_vwap:.2f})"
            )
            st.write(
                f"- SPY last {live_snap.spy_last:.2f} vs SPY VWAP {live_snap.spy_vwap:.2f} — "
                f"confirms **Long**: {'Yes' if live_snap.spy_confirms_long else 'No'}, "
                f"confirms **Short**: {'Yes' if live_snap.spy_confirms_short else 'No'}"
            )

            if direction == "Long":
                vwap_aligned = live_snap.qqq_vs_vwap == "above"
                spy_confirmed = live_snap.spy_confirms_long
            elif direction == "Short":
                vwap_aligned = live_snap.qqq_vs_vwap == "below"
                spy_confirmed = live_snap.spy_confirms_short
            else:
                vwap_aligned = False
                spy_confirmed = False

            st.info(
                f"For scoring: **VWAP aligned** = {'Yes' if vwap_aligned else 'No'}, "
                f"**SPY confirmed** = {'Yes' if spy_confirmed else 'No'} "
                f"(based on direction **{direction}**)."
            )
            volume_confirmed = yn_to_bool("Volume confirmed (manual)", "lv_vol")
            entry = st.number_input("Entry", value=current_qqq, step=0.01, format="%.2f", key="lv_ent")
            stop = st.number_input("Stop", value=or_low, step=0.01, format="%.2f", key="lv_stp")
            target = st.number_input("Target", value=or_high + 1.0, step=0.01, format="%.2f", key="lv_tgt")

        st.divider()
        st.subheader("Recent intraday bars (today, regular session)")
        cqqq, cspy = st.columns(2)
        with cqqq:
            st.markdown("**QQQ**")
            st.dataframe(
                pd.DataFrame(data_provider.bars_for_display(live_snap.qqq_session_bars)),
                use_container_width=True,
                height=320,
            )
        with cspy:
            st.markdown("**SPY**")
            st.dataframe(
                pd.DataFrame(data_provider.bars_for_display(live_snap.spy_session_bars)),
                use_container_width=True,
                height=320,
            )

# --- Calculations (shared) ---
mid = risk.or_midpoint(or_high, or_low)
size_or = risk.or_size(or_high, or_low)
max_risk = risk.max_dollar_risk(account_size, risk_percent)
r_each = risk.risk_per_share(entry, stop, direction)
reward_each = risk.reward_per_share(entry, target, direction)
shares = risk.position_size(max_risk, r_each)
r_mult = risk.r_multiple(reward_each, r_each)

score = scoring.setup_score(
    direction=direction,
    current_price=current_qqq,
    or_high=or_high,
    or_low=or_low,
    vwap_aligned=vwap_aligned,
    spy_confirmed=spy_confirmed,
    volume_confirmed=volume_confirmed,
    entry=entry,
    stop=stop,
    target=target,
)

warnings = scoring.build_warnings(
    direction=direction,
    r_mult=r_mult,
    vwap_aligned=vwap_aligned,
    spy_confirmed=spy_confirmed,
    volume_confirmed=volume_confirmed,
    entry=entry,
    stop=stop,
)

decision = scoring.trade_decision(score, r_mult)

st.divider()
st.subheader("Calculated values")

c1, c2, c3, c4 = st.columns(4)
c1.metric("OR midpoint", f"{mid:.2f}")
c2.metric("OR size", f"{size_or:.2f}")
c3.metric("Risk per share", f"{r_each:.2f}")
c4.metric("Max dollar risk", f"{max_risk:,.2f}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Position size (shares)", str(shares))
c6.metric("Reward per share", f"{reward_each:.2f}")
c7.metric("R multiple", f"{r_mult:.2f}")
c8.metric("Setup score", f"{score} / 100")

st.metric("Decision", decision)

if warnings:
    st.warning("Warnings:\n- " + "\n- ".join(warnings))
else:
    st.success("No warning flags from the checklist.")

TRADE_ALLOWED = "TRADE ALLOWED"
PAPER_ACCT_CACHE_KEY = "paper_account_snapshot_v2"

st.divider()
if decision == TRADE_ALLOWED:
    st.subheader("Stage 2B: Paper trading (Alpaca)")
    st.warning(
        "This submits a simulated paper trade only. No live money is used. "
        "Confirm below, then click **Send Paper Trade**."
    )
    keys_ok = data_provider.load_alpaca_keys_from_env() is not None
    if not keys_ok:
        st.info("Alpaca keys not found. Add them to a `.env` file before submitting a paper order.")

    account_snapshot = None
    acct_err: str | None = None
    if keys_ok:
        if st.button("Refresh paper account", key="refresh_paper_account"):
            st.session_state.pop(PAPER_ACCT_CACHE_KEY, None)
        if PAPER_ACCT_CACHE_KEY not in st.session_state:
            with st.spinner("Loading paper account…"):
                st.session_state[PAPER_ACCT_CACHE_KEY] = broker.fetch_paper_account_snapshot()
        account_snapshot, acct_err = st.session_state[PAPER_ACCT_CACHE_KEY]

        if account_snapshot is not None:
            st.markdown("**Alpaca paper account**")
            ap1, ap2, ap3 = st.columns(3)
            ap1.metric("Buying power", f"${account_snapshot.buying_power:,.2f}")
            ap2.metric("Cash", f"${account_snapshot.cash:,.2f}")
            ap3.metric("Portfolio value", f"${account_snapshot.portfolio_value:,.2f}")
        elif acct_err:
            st.warning(acct_err)

    max_bp_usage_pct = st.number_input(
        "Max buying power usage percent (paper cap)",
        min_value=0.0,
        max_value=100.0,
        value=25.0,
        step=1.0,
        help="Max notional (entry × shares) as a percent of Alpaca paper buying power before capping size.",
        key="paper_max_bp_usage_pct",
    )

    sizing = None
    if account_snapshot is not None and entry > 0:
        sizing = broker.compute_paper_order_sizing(
            risk_based_shares=shares,
            entry_price=float(entry),
            buying_power=account_snapshot.buying_power,
            max_buying_power_usage_percent=max_bp_usage_pct,
        )
        st.markdown("**Paper order sizing**")
        sz1, sz2, sz3, sz4 = st.columns(4)
        sz1.metric("Risk-based position size", str(sizing.risk_based_size))
        sz2.metric("Buying-power capped size", str(sizing.buying_power_cap_size))
        sz3.metric("Final paper order size", str(sizing.final_order_size))
        sz4.metric("Estimated order cost", f"${sizing.estimated_order_cost:,.2f}")
        st.caption(
            f"Max allowed trade value (before share floor): **${sizing.max_allowed_trade_value:,.2f}** "
            f"({max_bp_usage_pct:.1f}% of buying power)."
        )
        if sizing.risk_based_size > 0 and sizing.final_order_size < sizing.risk_based_size:
            st.info(
                "Final size is **smaller** than the risk-based size because of the buying-power cap. "
                "Raise max usage %, add paper buying power, or tighten risk if you need more shares."
            )

    if not keys_ok:
        pass  # message already shown
    elif direction not in ("Long", "Short"):
        st.info("Choose **Long** or **Short** to enable a paper order (direction **None** cannot be sent).")
    elif shares <= 0:
        st.info("**Risk-based position size** is zero — adjust account risk, stop, or entry before paper sizing.")
    elif account_snapshot is None:
        st.info("Load the paper account above (fix any error) to enable capped order sizing.")
    elif entry <= 0:
        st.info("**Entry** must be greater than zero to estimate order cost.")

    if sizing is not None and sizing.final_order_size < 1:
        st.warning("Final paper order size is below 1 share.")

    if sizing is not None and account_snapshot is not None:
        if sizing.estimated_order_cost > account_snapshot.buying_power + 1e-6:
            st.error(
                "Estimated order cost exceeds paper buying power. "
                "Lower max usage %, entry, or risk-based size — order will not be sent."
            )

    confirm_paper = st.checkbox(
        "I confirm I want to submit this simulated paper-only order.",
        value=False,
        key="paper_trade_confirm",
    )

    cost_ok = (
        sizing is not None
        and account_snapshot is not None
        and sizing.estimated_order_cost <= account_snapshot.buying_power + 1e-6
    )
    can_send_paper = (
        keys_ok
        and account_snapshot is not None
        and sizing is not None
        and sizing.final_order_size >= 1
        and cost_ok
        and direction in ("Long", "Short")
        and shares > 0
        and confirm_paper
    )

    if st.button("Send Paper Trade", disabled=not can_send_paper, key="send_paper_trade"):
        if sizing is None or account_snapshot is None:
            st.error("Sizing or account data is missing. Refresh the paper account and try again.")
        else:
            with st.spinner("Submitting paper order to Alpaca…"):
                result = broker.submit_paper_market_order_qqq(
                    qty=sizing.final_order_size,
                    direction=direction,
                )
            if result.ok:
                broker.append_paper_order_csv(
                    {
                        "symbol": "QQQ",
                        "direction": direction,
                        "qty": sizing.final_order_size,
                        "order_id": result.order_id,
                        "status": result.status,
                        "submitted_at": result.submitted_at,
                        "entry": entry,
                        "stop": stop,
                        "target": target,
                        "setup_score": score,
                        "r_multiple": round(r_mult, 4),
                        "max_buying_power_usage_percent": max_bp_usage_pct,
                        "buying_power": account_snapshot.buying_power,
                        "cash": account_snapshot.cash,
                        "portfolio_value": account_snapshot.portfolio_value,
                        "risk_based_size": sizing.risk_based_size,
                        "buying_power_cap_size": sizing.buying_power_cap_size,
                        "final_order_size": sizing.final_order_size,
                        "estimated_order_cost": round(sizing.estimated_order_cost, 4),
                    }
                )
                st.success(
                    f"{result.message} Submitted **{sizing.final_order_size}** share(s). "
                    f"Order ID: **{result.order_id}** (status: {result.status}). "
                    f"Logged to `paper_orders.csv`."
                )
            else:
                st.error(result.message)

st.divider()
if st.button("Save signal to signals.csv"):
    path = journal.save_signal(
        {
            "account_size": account_size,
            "risk_percent": risk_percent,
            "or_high": or_high,
            "or_low": or_low,
            "qqq_price": current_qqq,
            "direction": direction,
            "vwap_aligned": vwap_aligned,
            "spy_confirmed": spy_confirmed,
            "volume_confirmed": volume_confirmed,
            "entry": entry,
            "stop": stop,
            "target": target,
            "or_midpoint": mid,
            "or_size": size_or,
            "risk_per_share": r_each,
            "max_dollar_risk": max_risk,
            "position_size_shares": shares,
            "reward_per_share": reward_each,
            "r_multiple": r_mult,
            "setup_score": score,
            "decision": decision,
            "warnings": " | ".join(warnings),
        }
    )
    st.success(f"Saved to {path}")

# --- Stage 3A: Historical Backtesting (separate from live / paper execution) ---
st.divider()
st.subheader("Stage 3A: Historical Backtesting")
st.caption(
    "Replay QQQ ORB setups on past 1-minute data (Alpaca). Results export to `backtest_trades.csv`. "
    "Not predictive of future performance."
)

bt_c1, bt_c2, bt_c3 = st.columns(3)
with bt_c1:
    bt_start = st.date_input("Start date", value=date.today() - timedelta(days=30), key="bt_start")
with bt_c2:
    bt_end = st.date_input("End date", value=date.today(), key="bt_end")
with bt_c3:
    st.write("")  # spacer
    run_bt = st.button("Run Backtest", key="bt_run", type="primary")

with st.expander("Backtest strategy parameters", expanded=True):
    p1, p2, p3 = st.columns(3)
    with p1:
        bt_acct = st.number_input("Backtest account size ($)", min_value=1_000.0, value=100_000.0, step=5_000.0, key="bt_acct")
        bt_risk = st.number_input("Risk percent (per trade)", min_value=0.1, max_value=100.0, value=1.0, step=0.1, key="bt_risk")
        bt_r_target = st.number_input("R target (reward = R × risk)", min_value=0.5, max_value=10.0, value=2.0, step=0.5, key="bt_rt")
    with p2:
        stop_labels = {"Opposite OR side": "opposite_or", "OR midpoint": "midpoint", "Fixed % off entry": "fixed_pct"}
        bt_stop_label = st.selectbox("Stop style", list(stop_labels.keys()), index=0, key="bt_stop")
        bt_stop = cast(backtester.StopStyle, stop_labels[bt_stop_label])
        bt_fixed_pct = st.number_input(
            "Fixed stop % (only if stop style is Fixed %)",
            min_value=0.05,
            max_value=20.0,
            value=0.5,
            step=0.05,
            key="bt_fixed",
        )
        bt_max_tr = st.number_input("Max trades per day", min_value=1, max_value=10, value=1, step=1, key="bt_maxtr")
    with p3:
        bt_vwap = st.checkbox("VWAP filter (QQQ vs session VWAP)", value=True, key="bt_vwap")
        bt_spy = st.checkbox("SPY confirmation (SPY vs session VWAP)", value=True, key="bt_spy")
        bt_vol = st.checkbox("Volume confirmation (vs OR-period avg)", value=False, key="bt_vol")
        # Relative Volume filter
        bt_use_rvol = st.checkbox(
            "Use Relative Volume Filter",
            value=False,
            key="bt_use_rvol",
            disabled=not bt_vol,
        )
        bt_min_rvol = st.number_input(
            "Minimum RVOL",
            min_value=0.1,
            value=1.5,
            step=0.1,
            format="%.2f",
            key="bt_min_rvol",
            disabled=not (bt_vol and bt_use_rvol),
        )
        # Daily trend alignment filter
        bt_daily_trend = st.checkbox(
            "Daily trend filter (QQQ above daily 20 EMA)",
            value=False,
            key="bt_daily_trend",
        )
        dir_labels = {"Both": "both", "Long only": "long", "Short only": "short"}
        bt_dir_label = st.selectbox("Directions", list(dir_labels.keys()), index=0, key="bt_dir")
        bt_dir = cast(backtester.DirectionFilter, dir_labels[bt_dir_label])

    # Opening range size filter
    or_sz_c1, or_sz_c2, or_sz_c3 = st.columns(3)
    with or_sz_c1:
        bt_or_size_en = st.checkbox("Enable OR Size Filter", value=False, key="bt_or_size_en")
    with or_sz_c2:
        bt_or_min = st.number_input(
            "Minimum OR Size ($)",
            min_value=0.01,
            value=1.00,
            step=0.05,
            format="%.2f",
            key="bt_or_min",
            disabled=not bt_or_size_en,
        )
    with or_sz_c3:
        bt_or_max = st.number_input(
            "Maximum OR Size ($)",
            min_value=0.01,
            value=6.00,
            step=0.05,
            format="%.2f",
            key="bt_or_max",
            disabled=not bt_or_size_en,
        )

    # Intraday entry cutoff (Stage 3A)
    ec_c1, ec_c2 = st.columns(2)
    with ec_c1:
        bt_entry_cutoff_en = st.checkbox("Enable Entry Cutoff Time", value=False, key="bt_entry_cutoff_en")
    with ec_c2:
        bt_entry_cutoff_time = st.time_input(
            "No new entries after",
            value=time(11, 0),
            step=60,
            key="bt_entry_cutoff_time",
            disabled=not bt_entry_cutoff_en,
        )

    # Stage 3D adaptive environment filter
    bt_favorable_env = st.checkbox(
        "Trade only favorable environments",
        value=False,
        key="bt_favorable_env",
        help="Requires Stage 3C Environment Research rules (built automatically after 3C run).",
    )

bt_progress = st.empty()
if run_bt:
    cfg = backtester.BacktestConfig(
        start_date=bt_start,
        end_date=bt_end,
        account_size=float(bt_acct),
        risk_percent=float(bt_risk),
        r_target=float(bt_r_target),
        stop_style=bt_stop,
        fixed_stop_percent=float(bt_fixed_pct),
        max_trades_per_day=int(bt_max_tr),
        vwap_filter=bt_vwap,
        spy_confirmation=bt_spy,
        volume_confirmation=bt_vol,
        direction_filter=bt_dir,
        daily_trend_qqq_ema20_filter=bt_daily_trend,
        or_size_filter_enabled=bt_or_size_en,
        or_size_min=float(bt_or_min),
        or_size_max=float(bt_or_max),
        use_rvol_filter=bt_use_rvol,
        min_rvol=float(bt_min_rvol),
        enable_entry_cutoff=bt_entry_cutoff_en,
        entry_cutoff_time=f"{bt_entry_cutoff_time.hour:02d}:{bt_entry_cutoff_time.minute:02d}",
        favorable_environments_only=bt_favorable_env,
    )

    adaptive_rules = st.session_state.get("adaptive_rules")
    if bt_favorable_env and adaptive_rules is None:
        adaptive_rules = adaptive_environment.load_adaptive_rules_from_disk()
    if bt_favorable_env and adaptive_rules is None:
        st.warning(
            "Adaptive rules not found. Run **Stage 3C Environment Research** first, "
            "then re-run the backtest."
        )

    def _bt_prog(msg: str) -> None:
        bt_progress.info(msg)

    with st.spinner("Backtest running…"):
        bt_res = backtester.run_backtest(
            cfg,
            progress=_bt_prog,
            adaptive_rules=adaptive_rules if bt_favorable_env else None,
        )
    bt_progress.empty()
    st.session_state["bt_last_result"] = bt_res
    st.session_state["bt_last_start"] = bt_start
    st.session_state["bt_last_end"] = bt_end

bt_res = st.session_state.get("bt_last_result")
if bt_res is not None:
    if bt_res.error:
        st.error(bt_res.error)
    else:
        s = bt_res.summary
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total trades", f"{int(s['total_trades'])}")
        m2.metric("Win rate", f"{s['win_rate']:.1%}")
        m3.metric("Average R", f"{s['avg_r']:.2f}")
        m4.metric("Total P/L ($)", f"{s['total_pnl']:,.2f}")
        m5, m6, m7, m8 = st.columns(4)
        m5.metric("Expectancy ($/trade)", f"{s['expectancy']:,.2f}")
        m6.metric("Profit factor", f"{s['profit_factor']:.2f}")
        m7.metric("Largest drawdown ($)", f"{s['max_drawdown']:,.2f}")
        m8.metric("Avg OR size ($)", f"{s['avg_or_size']:.2f}")

        if bt_res.trades:
            eq_series = pd.Series([t.pnl for t in bt_res.trades]).cumsum()
            st.markdown("**Cumulative equity (by trade sequence)**")
            st.line_chart(pd.DataFrame({"equity": eq_series}))

            st.markdown("**Histogram of R multiples** (0.1R bins)")
            r_rounded = [round(t.r_multiple, 1) for t in bt_res.trades]
            r_df = pd.DataFrame({"R": r_rounded})
            hist_counts = r_df.groupby("R").size().reset_index(name="count")
            st.bar_chart(hist_counts.set_index("R"))

            st.caption(f"Trades written to `{backtester.BACKTEST_TRADES_FILE.name}` in the project folder.")
        else:
            st.info("No trades matched the rules in this date range (try wider dates or relax filters).")

# --- Stage 3B: QQQ Parameter Optimizer (research only; uses Stage 3A engine) ---
st.divider()
st.subheader("Stage 3B: QQQ Optimizer")
st.warning(
    "**Research only.** This optimizer searches parameter combinations ranked by **robustness**, "
    "not raw profit alone. Walk-forward validation splits data 70% train / 30% test. "
    "Results are **not** predictive of future QQQ performance. **No live trading** from the optimizer."
)

opt_c1, opt_c2, opt_c3 = st.columns(3)
with opt_c1:
    opt_start = st.date_input(
        "Optimizer start date",
        value=date.today() - timedelta(days=365),
        key="opt_start",
    )
with opt_c2:
    opt_end = st.date_input("Optimizer end date", value=date.today(), key="opt_end")
with opt_c3:
    st.write("")
    run_opt = st.button("Run Optimizer", key="opt_run", type="primary")

opt_quick = st.checkbox(
    "Quick Optimizer Mode",
    value=True,
    help="Runs ~8 starter combinations for fast results. Turn off for the full grid (7,680+ combos).",
    key="opt_quick",
)

with st.expander("Optimizer grid options", expanded=not opt_quick):
    if opt_quick:
        st.info(
            "Quick mode searches **8** combinations: Both direction, R=2.0, max trades 1/2, "
            "RVOL 1.25/1.50, opposite OR stop, VWAP+SPY+volume+RVOL on, entry cutoff off/11:00."
        )
    opt_inc_daily = st.checkbox(
        "Include daily trend filter in search (On / Off)",
        value=False,
        key="opt_inc_daily",
        disabled=opt_quick,
    )
    opt_inc_or = st.checkbox(
        "Include OR size filter in search (On / Off)",
        value=False,
        key="opt_inc_or",
        disabled=opt_quick,
    )
    opt_grid_n = optimizer.count_parameter_grid(
        opt_inc_daily, opt_inc_or, quick_mode=opt_quick
    )
    st.caption(
        f"Grid size: **{opt_grid_n:,}** combination{'s' if opt_grid_n == 1 else 's'} "
        + (
            "(quick starter search)."
            if opt_quick
            else "(volume + RVOL always on; full parameter sweep)."
        )
    )

if "opt_market_cache" not in st.session_state:
    st.session_state["opt_market_cache"] = {}

opt_progress = st.empty()
opt_progress_bar = st.progress(0, text="Ready")
if run_opt:
    import re

    def _opt_prog(msg: str) -> None:
        opt_progress.markdown(msg)
        match = re.search(r"\*\*(Training|Testing)\*\* (\d+)/(\d+)", msg)
        if match:
            phase, idx_s, total_s = match.group(1), match.group(2), match.group(3)
            idx, total = int(idx_s), int(total_s)
            pct = min(100, int(idx / total * 100)) if total else 0
            opt_progress_bar.progress(pct, text=f"{phase} {idx}/{total}")
        elif msg.startswith("Done"):
            opt_progress_bar.progress(100, text="Complete")

    opt_progress_bar.progress(0, text="Starting optimizer…")
    with st.spinner("Optimizer running (walk-forward)…"):
        opt_res = optimizer.run_optimizer(
            opt_start,
            opt_end,
            quick_mode=opt_quick,
            include_daily_trend=opt_inc_daily,
            include_or_size_filter=opt_inc_or,
            progress=_opt_prog,
            session_cache=st.session_state["opt_market_cache"],
        )
    opt_progress_bar.progress(100, text="Complete")
    st.session_state["opt_last_result"] = opt_res

opt_res = st.session_state.get("opt_last_result")
if opt_res is not None:
    if opt_res.error:
        st.error(opt_res.error)
    elif not opt_res.rows:
        st.info("No optimizer results returned.")
    else:
        if opt_res.train_start and opt_res.test_start:
            mode_label = "Quick" if opt_res.quick_mode else "Full"
            st.caption(
                f"**{mode_label} grid** · Train: **{opt_res.train_start}** → **{opt_res.train_end}** · "
                f"Test: **{opt_res.test_start}** → **{opt_res.test_end}** · "
                f"Grid: **{opt_res.grid_size:,}** configs"
                + (f" · **{opt_res.skipped_count}** skipped" if opt_res.skipped_count else "")
            )

        st.markdown("**Top 20 parameter sets** (ranked by walk-forward final score)")
        st.dataframe(optimizer.results_table_df(opt_res.rows, limit=20), use_container_width=True)

        def _show_best(label: str, m: optimizer.OptimizerRunMetrics | None) -> None:
            if m is None:
                st.write(f"*{label}: not available*")
                return
            ts = m.test_summary
            st.markdown(f"**{label}**")
            st.code(m.params_label, language=None)
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Final score", f"{m.final_score:.1f}")
            b2.metric("Test P/L ($)", f"{ts.get('total_pnl', 0):,.2f}")
            b3.metric("Test profit factor", f"{ts.get('profit_factor', 0):.2f}")
            b4.metric("Test trades", f"{int(ts.get('total_trades', 0))}")

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            _show_best("Best overall (walk-forward)", opt_res.best_overall)
        with bc2:
            _show_best("Best conservative (test PF ≥ 1.3, lower DD)", opt_res.best_conservative)
        with bc3:
            _show_best("Best aggressive (highest test P/L)", opt_res.best_aggressive)

        pick_labels = {
            "Best overall": opt_res.best_overall,
            "Best conservative": opt_res.best_conservative,
            "Best aggressive": opt_res.best_aggressive,
        }
        pick_key = st.selectbox(
            "Equity curve for",
            list(pick_labels.keys()),
            key="opt_eq_pick",
        )
        picked = pick_labels.get(pick_key)
        if picked and picked.test_trades:
            eq = pd.Series([t.pnl for t in picked.test_trades]).cumsum()
            st.markdown(f"**Out-of-sample equity curve** ({pick_key}, test period)")
            st.line_chart(pd.DataFrame({"equity": eq}))
        elif picked and picked.train_trades:
            eq = pd.Series([t.pnl for t in picked.train_trades]).cumsum()
            st.markdown(f"**In-sample equity curve** ({pick_key}, train period — no test trades)")
            st.line_chart(pd.DataFrame({"equity": eq}))

        st.caption(
            f"Exported: `{optimizer.OPTIMIZER_RESULTS_FILE.name}` · "
            f"`{optimizer.BEST_CONFIG_FILE.name}` (best overall params)."
        )

# --- Stage 3C: Market Environment Intelligence (research layer) ---
st.divider()
st.subheader("Stage 3C: Environment Research")
st.caption(
    "Identify **when** QQQ ORB setups are most favorable — time of day, premarket structure, "
    "OR quality, regime, and QQQ vs SPY strength. Rule-based only (no ML)."
)
st.warning(
    "**Research only.** Environment tags describe past conditions; they are not predictive "
    "of future QQQ performance."
)

bt_for_env = st.session_state.get("bt_last_result")
env_c1, env_c2, env_c3 = st.columns(3)
with env_c1:
    env_start = st.date_input(
        "Environment analysis start",
        value=st.session_state.get("bt_last_start", date.today() - timedelta(days=365)),
        key="env_start",
    )
with env_c2:
    env_end = st.date_input(
        "Environment analysis end",
        value=st.session_state.get("bt_last_end", date.today()),
        key="env_end",
    )
with env_c3:
    st.write("")
    run_env = st.button("Run Environment Research", key="env_run", type="primary")

if bt_for_env is not None and bt_for_env.trades:
    st.caption(
        f"Using **{len(bt_for_env.trades)}** trades from the latest Stage 3A backtest. "
        "Run Stage 3A first to refresh trade sample."
    )
else:
    st.info("Run **Stage 3A Historical Backtesting** first to generate trades for environment analysis.")

if "env_market_cache" not in st.session_state:
    st.session_state["env_market_cache"] = {}

env_progress = st.empty()
if run_env:
    src = st.session_state.get("bt_last_result")
    if src is None or not src.trades or src.error:
        st.error("No Stage 3A trades available. Run a backtest in Stage 3A first.")
    else:
        trades_copy = copy.deepcopy(src.trades)

        def _env_prog(msg: str) -> None:
            env_progress.info(msg)

        with st.spinner("Environment research running…"):
            env_res = environment_engine.run_environment_research(
                trades_copy,
                env_start,
                env_end,
                progress=_env_prog,
                session_cache=st.session_state["env_market_cache"],
            )
        st.session_state["env_last_result"] = env_res
        if env_res is not None and not env_res.error and env_res.trades:
            st.session_state["adaptive_rules"] = adaptive_environment.build_adaptive_rules(env_res)

env_res = st.session_state.get("env_last_result")
if env_res is not None:
    if env_res.error:
        st.error(env_res.error)
    elif env_res.trades:
        st.markdown("**Performance by time bucket**")
        st.dataframe(pd.DataFrame(env_res.by_time_bucket), use_container_width=True)

        st.markdown("**Performance by regime**")
        st.dataframe(pd.DataFrame(env_res.by_regime), use_container_width=True)

        st.markdown("**Performance by premarket trend**")
        st.dataframe(pd.DataFrame(env_res.by_premarket_trend), use_container_width=True)

        st.markdown("**Performance by OR candle quality**")
        st.dataframe(pd.DataFrame(env_res.by_or_candle), use_container_width=True)

        st.markdown("**Performance by QQQ/SPY relative strength**")
        st.dataframe(pd.DataFrame(env_res.by_relative_strength), use_container_width=True)

        st.markdown("**Best environment combinations** (time bucket × regime, min 3 trades)")
        if env_res.best_combinations:
            st.dataframe(pd.DataFrame(env_res.best_combinations), use_container_width=True)
        else:
            st.caption("Not enough trades for combination ranking.")

        st.caption(
            f"Exported: `{environment_engine.ENVIRONMENT_TRADES_FILE.name}` · "
            f"`{environment_engine.ENVIRONMENT_SUMMARY_FILE.name}` · "
            f"`{environment_engine.BEST_ENVIRONMENT_RULES_FILE.name}`"
        )

# --- Stage 3D: Adaptive Environment Filter Engine ---
st.divider()
st.subheader("Stage 3D: Adaptive Environment Filter")
st.caption(
    "Rule-based scoring from Stage 3C research — tags current conditions as "
    "**FAVORABLE**, **NEUTRAL**, or **AVOID** using historical expectancy, profit factor, "
    "and robustness (not a forecast)."
)

if "adaptive_rules" not in st.session_state:
    st.session_state["adaptive_rules"] = adaptive_environment.load_adaptive_rules_from_disk()

adaptive_rules = st.session_state.get("adaptive_rules")
env_res_for_3d = st.session_state.get("env_last_result")

d3_c1, d3_c2 = st.columns(2)
with d3_c1:
    assess_date = st.date_input(
        "Assess session date",
        value=date.today(),
        key="d3_assess_date",
    )
with d3_c2:
    assess_time = st.time_input(
        "Assess entry time (ET)",
        value=time(10, 15),
        key="d3_assess_time",
    )

if st.button("Refresh adaptive rules from Stage 3C", key="d3_refresh_rules"):
    if env_res_for_3d and env_res_for_3d.trades and not env_res_for_3d.error:
        st.session_state["adaptive_rules"] = adaptive_environment.build_adaptive_rules(env_res_for_3d)
        st.success("Adaptive rules rebuilt from latest Stage 3C results.")
    else:
        st.warning("Run Stage 3C Environment Research first.")

if adaptive_rules is None:
    st.info(
        "No adaptive rules loaded. Run **Stage 3C Environment Research** to build "
        "`adaptive_environment_rules.json`."
    )
else:
    st.caption(
        f"Rules built from **{adaptive_rules.source_trades}** trades · "
        f"min sample **{adaptive_rules.min_sample_size}** · "
        f"updated **{adaptive_rules.built_at or 'n/a'}**"
    )

    d3_progress = st.empty()

    if st.button("Assess environment", key="d3_assess", type="primary"):
        if "env_market_cache" not in st.session_state:
            st.session_state["env_market_cache"] = {}

        def _d3_prog(msg: str) -> None:
            d3_progress.info(msg)

        with st.spinner("Assessing environment…"):
            environment_engine.clear_day_context_cache()
            bundle, err = environment_engine.load_environment_bundle_for_session(
                assess_date,
                progress=_d3_prog,
                session_cache=st.session_state["env_market_cache"],
            )
            if err or bundle is None:
                st.error(err or "Could not load market data for assessment.")
            else:
                assessment = adaptive_environment.assess_session(
                    bundle, assess_date, assess_time, adaptive_rules
                )
                st.session_state["d3_last_assessment"] = assessment
        d3_progress.empty()

    assessment = st.session_state.get("d3_last_assessment")
    if assessment is not None:
        label = assessment.environment_label
        if label == "FAVORABLE":
            st.success(f"**{label}** — score {assessment.environment_score:.1f}")
        elif label == "AVOID":
            st.error(f"**{label}** — score {assessment.environment_score:.1f}")
        else:
            st.warning(f"**{label}** — score {assessment.environment_score:.1f}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Environment score", f"{assessment.environment_score:.1f}")
        m2.metric("Confidence", f"{assessment.confidence:.0%}")
        m3.metric("Hist. expectancy ($/trade)", f"{assessment.historical_expectancy:,.2f}")
        m4.metric("Hist. win rate", f"{assessment.historical_win_rate:.1%}")

        st.markdown("**Trade recommendation**")
        st.write(assessment.recommendation)

        if assessment.warnings:
            for w in assessment.warnings:
                st.warning(w)

        if assessment.session_features is not None:
            st.markdown("**Calculated session features (debug)**")
            st.dataframe(
                pd.DataFrame(assessment.session_features.debug_table()),
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("**Detected environment tags (scoring inputs)**")
        st.json(assessment.tags)

        if assessment.dimension_contributions:
            st.markdown("**Dimension contributions**")
            st.json(assessment.dimension_contributions)

    st.caption(
        f"Exported: `{adaptive_environment.ADAPTIVE_RULES_FILE.name}` · "
        f"`{adaptive_environment.ENVIRONMENT_SCORES_FILE.name}`"
    )

# --- Stage 3E / 3F / 3G: Live Trade Scoring, Blocking, Paper Journal ---
st.divider()
st.subheader("Stage 3E: Live Trade Scoring")
st.caption(
    "Combines **Stage 3D environment score** with live setup quality (VWAP, SPY, RVOL, OR quality, "
    "relative strength, time bucket, stop/OR geometry). Research and paper logging only — "
    "**no live orders**."
)

d3_assessment = st.session_state.get("d3_last_assessment")
env_score_3e = 50.0
env_label_3e = "NEUTRAL"
or_quality_3e: str | None = None
time_bucket_3e: str | None = None
relative_strength_3e: str | None = None
env_tags_3e: dict = {}

if d3_assessment is not None:
    env_score_3e = float(d3_assessment.environment_score)
    env_label_3e = str(d3_assessment.environment_label)
    env_tags_3e = dict(d3_assessment.tags or {})
    if d3_assessment.session_features is not None:
        sf = d3_assessment.session_features
        or_quality_3e = sf.or_candle_quality
        time_bucket_3e = sf.time_bucket
        relative_strength_3e = sf.relative_strength
    st.info(
        f"Using Stage 3D assessment — **{env_label_3e}** ({env_score_3e:.1f}). "
        "Run **Assess environment** above to refresh."
    )
else:
    from zoneinfo import ZoneInfo

    from datetime import datetime as _dt

    _now_et = _dt.now(ZoneInfo("America/New_York"))
    time_bucket_3e = environment_engine.entry_time_bucket(_now_et.time())
    st.warning(
        "No Stage 3D assessment in session — environment score defaults to **50 (NEUTRAL)**. "
        "Run Stage 3D **Assess environment** for accurate environment scoring."
    )

e3_prog = st.empty()
e3_prog.caption("Ready to score current setup from Manual/Live inputs above.")

with st.expander("Stage 3F: Trade blocking thresholds", expanded=True):
    bf1, bf2, bf3, bf4 = st.columns(4)
    with bf1:
        min_env_score = st.number_input(
            "Min environment score",
            min_value=0.0,
            max_value=100.0,
            value=45.0,
            step=1.0,
            key="e3_min_env",
        )
    with bf2:
        min_trade_score = st.number_input(
            "Min trade score",
            min_value=0.0,
            max_value=100.0,
            value=60.0,
            step=1.0,
            key="e3_min_trade",
        )
    with bf3:
        min_rvol_3e = st.number_input(
            "Min RVOL (0 = skip check)",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.05,
            key="e3_min_rvol",
        )
    with bf4:
        max_or_size_3e = st.number_input(
            "Max OR size ($)",
            min_value=0.5,
            max_value=50.0,
            value=8.0,
            step=0.25,
            key="e3_max_or",
        )

e3_rvol_col1, e3_rvol_col2 = st.columns(2)
with e3_rvol_col1:
    use_manual_rvol = st.checkbox(
        "Override session RVOL (optional)",
        value=False,
        key="e3_rvol_override",
    )
with e3_rvol_col2:
    manual_rvol_val = st.number_input(
        "Session RVOL",
        min_value=0.0,
        max_value=10.0,
        value=1.25,
        step=0.05,
        disabled=not use_manual_rvol,
        key="e3_rvol_val",
    )

session_rvol_3e: float | None = manual_rvol_val if use_manual_rvol else None

score_inp = live_trade_scoring.build_score_input_from_context(
    environment_score=env_score_3e,
    environment_label=env_label_3e,
    vwap_aligned=vwap_aligned,
    spy_confirmed=spy_confirmed,
    volume_confirmed=volume_confirmed,
    session_rvol=session_rvol_3e,
    or_candle_quality=or_quality_3e,
    relative_strength=relative_strength_3e,
    time_bucket=time_bucket_3e,
    entry=entry,
    stop=stop,
    or_size=size_or,
    direction=direction,
    r_multiple=r_mult,
)

trade_score_result = live_trade_scoring.compute_live_trade_score(score_inp)
block_thresholds = live_trade_scoring.TradeBlockThresholds(
    min_environment_score=float(min_env_score),
    min_trade_score=float(min_trade_score),
    min_rvol=float(min_rvol_3e) if min_rvol_3e > 0 else 0.0,
    max_or_size=float(max_or_size_3e),
)
if block_thresholds.min_rvol <= 0:
    block_thresholds.min_rvol = 0.0
trade_score_result = live_trade_scoring.apply_trade_blocking(
    trade_score_result, score_inp, block_thresholds
)

e3m1, e3m2, e3m3 = st.columns(3)
e3m1.metric("Trade score", f"{trade_score_result.trade_score:.1f} / 100")
e3m2.metric("Trade label", trade_score_result.label)
if trade_score_result.blocked:
    e3m3.metric("Block decision", live_trade_scoring.BLOCK_DECISION)
    st.error(f"**{live_trade_scoring.BLOCK_DECISION}** — setup blocked by Stage 3F thresholds.")
else:
    e3m3.metric("Block decision", live_trade_scoring.ALLOW_DECISION)
    st.success(f"**{live_trade_scoring.ALLOW_DECISION}** — passes blocking thresholds (paper/research only).")

st.markdown("**Score reasons**")
for reason in trade_score_result.reasons:
    st.write(f"- {reason}")

if trade_score_result.risk_warnings:
    st.markdown("**Risk warnings / block reasons**")
    for w in trade_score_result.risk_warnings:
        st.warning(w)

if trade_score_result.component_scores:
    with st.expander("Component breakdown"):
        st.json(trade_score_result.component_scores)

st.markdown("**Stage 3G: Paper journal (scored log)**")
st.caption(
    "Logs a research paper trade to CSV — separate from Alpaca **Send Paper Trade** (Stage 2B)."
)
paper_notes_3g = st.text_area(
    "User notes (optional)",
    value="",
    key="e3_paper_notes",
    placeholder="Why you took or passed on this setup…",
)
if st.button("Log Paper Trade From Current Score", key="e3_log_paper", type="primary"):
    try:
        entry_time_str = ""
        if d3_assessment and d3_assessment.session_features and d3_assessment.session_features.entry_time:
            entry_time_str = d3_assessment.session_features.entry_time.isoformat()
        elif time_bucket_3e:
            entry_time_str = time_bucket_3e

        path = scored_paper_journal.append_scored_paper_trade(
            {
                "ticker": "QQQ",
                "direction": direction,
                "entry_time": entry_time_str,
                "entry": entry,
                "stop": stop,
                "target": target,
                "environment_score": round(env_score_3e, 2),
                "environment_label": env_label_3e,
                "trade_score": trade_score_result.trade_score,
                "trade_label": trade_score_result.label,
                "allow_block_decision": trade_score_result.block_decision,
                "environment_tags_json": scored_paper_journal.format_tags_json(env_tags_3e),
                "reason_list": " | ".join(trade_score_result.reasons),
                "risk_warnings": " | ".join(trade_score_result.risk_warnings),
                "user_notes": paper_notes_3g,
                "or_size": round(size_or, 4),
                "r_multiple": round(r_mult, 4),
            }
        )
        st.success(f"Scored paper trade logged to `{path.name}`.")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not log paper trade: {exc}")

st.caption(f"Journal file: `{scored_paper_journal.SCORED_PAPER_TRADES_FILE.name}`")

# --- Stage 3H: Father's Hand Training ---
st.divider()
st.subheader("Stage 3H: Father's Hand Training")
st.caption(
    "Review historical ORB setups from environment/backtest CSVs. Answer multiple-choice "
    "questions and get immediate grading with explanations."
)

if "fh_training_setups" not in st.session_state:
    with st.spinner("Loading training setups…"):
        st.session_state["fh_training_setups"] = fathers_hand.load_training_setups()

fh_setups = st.session_state.get("fh_training_setups") or []
if not fh_setups:
    st.info(
        "No training setups found. Run **Stage 3C Environment Research** (or Stage 3A backtest) "
        "to populate `environment_trades.csv` or `backtest_trades.csv`."
    )
else:
    st.caption(f"**{len(fh_setups)}** setups available for training.")

    fh_c1, fh_c2 = st.columns(2)
    with fh_c1:
        if st.button("Load new training setup", key="fh_new_setup", type="primary"):
            picked = fathers_hand.pick_random_setup(fh_setups)
            if picked is not None:
                st.session_state["fh_current_quiz"] = fathers_hand.build_quiz(picked)
                st.session_state.pop("fh_graded", None)
    with fh_c2:
        if st.button("Reload setup library", key="fh_reload"):
            st.session_state["fh_training_setups"] = fathers_hand.load_training_setups()
            st.session_state.pop("fh_current_quiz", None)
            st.session_state.pop("fh_graded", None)
            st.rerun()

    fh_quiz: fathers_hand.TrainingQuiz | None = st.session_state.get("fh_current_quiz")
    if fh_quiz is None and fh_setups:
        st.info("Click **Load new training setup** to begin.")
    elif fh_quiz is not None:
        setup = fh_quiz.setup
        st.markdown(
            f"**Setup** — date `{setup.date}` · direction **{setup.direction}** · "
            f"OR candle **{setup.or_candle_type}** · body "
            f"{setup.or_body_percent if setup.or_body_percent is not None else 'n/a'}%"
        )
        st.caption("Answers are hidden until you submit. Historical P/L is revealed after grading.")

        fh_answers: dict[str, int | None] = {}
        for q in fh_quiz.questions:
            choice = st.radio(
                q.prompt,
                options=["— select —", *q.options],
                key=f"fh_ans_{setup.setup_id}_{q.question_id}",
                index=0,
            )
            if choice == "— select —":
                fh_answers[q.question_id] = None
            else:
                fh_answers[q.question_id] = q.options.index(choice)

        if st.button("Submit answers & grade", key="fh_grade"):
            if any(v is None for v in fh_answers.values()):
                st.warning("Answer all four questions before submitting.")
            else:
                log_rows: list[dict] = []
                correct_count = 0
                for q in fh_quiz.questions:
                    sel = int(fh_answers[q.question_id])
                    ok, explanation = fathers_hand.grade_answer(q, sel)
                    if ok:
                        correct_count += 1
                        st.success(f"**{q.prompt}** — Correct. {explanation}")
                    else:
                        st.error(f"**{q.prompt}** — Incorrect. {explanation}")
                    log_rows.append(
                        {
                            "setup_date": setup.date,
                            "direction": setup.direction,
                            "question_id": q.question_id,
                            "question_text": q.prompt,
                            "user_answer": q.options[sel],
                            "correct_answer": q.options[q.correct_index],
                            "is_correct": ok,
                            "explanation": explanation,
                            "setup_pnl": setup.pnl if setup.pnl is not None else "",
                            "setup_r": setup.r_multiple if setup.r_multiple is not None else "",
                        }
                    )
                try:
                    log_path = fathers_hand.append_training_log(log_rows)
                    st.caption(f"Attempt saved to `{log_path.name}`.")
                except Exception as exc:  # noqa: BLE001
                    st.warning(f"Could not save training log: {exc}")

                st.metric("Score", f"{correct_count} / {len(fh_quiz.questions)}")
                if setup.pnl is not None and setup.r_multiple is not None:
                    st.info(
                        f"Historical outcome: P/L **${setup.pnl:,.2f}**, R **{setup.r_multiple:.2f}**."
                    )
                st.session_state["fh_graded"] = True

    st.caption(f"Training log: `{fathers_hand.TRAINING_LOG_FILE.name}`")

# --- Stage 3I: Paper Simulation Report ---
st.divider()
st.subheader("Stage 3I: Paper Simulation Report")
st.caption(
    "Simulate compounding account growth if you had followed the EdgeOne strategy over a date range. "
    "Uses historical replay, environment scoring, and trade scoring. **Research only — no live orders.**"
)

sim3i_default_start = date.today() - timedelta(days=90)
sim_c1, sim_c2, sim_c3, sim_c4 = st.columns(4)
with sim_c1:
    sim_start_balance = st.number_input(
        "Starting account ($)",
        min_value=100.0,
        value=1_000.0,
        step=100.0,
        key="sim3i_balance",
    )
with sim_c2:
    sim_start_date = st.date_input(
        "Start date",
        value=sim3i_default_start,
        key="sim3i_start",
    )
with sim_c3:
    sim_end_date = st.date_input(
        "End date",
        value=date.today(),
        key="sim3i_end",
    )
with sim_c4:
    sim_risk_pct = st.number_input(
        "Risk per trade (%)",
        min_value=0.1,
        max_value=100.0,
        value=1.0,
        step=0.1,
        key="sim3i_risk",
    )

sim_preset = st.selectbox(
    "Strategy preset",
    ["Current Best EdgeOne Setup", "Custom"],
    key="sim3i_preset",
)

sim_mode = st.selectbox(
    "Simulation mode",
    ["STRICT", "MODERATE", "RELAXED"],
    index=1,
    key="sim3i_mode",
    help=(
        "**STRICT** — production 3F thresholds (env 45, trade 60, RVOL 1.0). "
        "**MODERATE** — env 40, trade 55, RVOL 1.2. "
        "**RELAXED** — env 30, trade 50, RVOL 1.0."
    ),
)

sim_custom_cfg: backtester.BacktestConfig | None = None
if sim_preset == "Custom":
    with st.expander("Custom strategy parameters", expanded=True):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            sim_r_target = st.number_input("R target", min_value=0.5, max_value=10.0, value=2.0, step=0.5, key="sim3i_rt")
            sim_max_tr = st.number_input("Max trades/day", min_value=1, max_value=10, value=2, step=1, key="sim3i_maxtr")
            sim_dir_labels = {"Both": "both", "Long only": "long", "Short only": "short"}
            sim_dir_label = st.selectbox("Directions", list(sim_dir_labels.keys()), index=0, key="sim3i_dir")
            sim_dir = cast(backtester.DirectionFilter, sim_dir_labels[sim_dir_label])
        with sc2:
            sim_stop_labels = {"Opposite OR side": "opposite_or", "OR midpoint": "midpoint", "Fixed % off entry": "fixed_pct"}
            sim_stop_label = st.selectbox("Stop style", list(sim_stop_labels.keys()), index=0, key="sim3i_stop")
            sim_stop = cast(backtester.StopStyle, sim_stop_labels[sim_stop_label])
            sim_fixed_pct = st.number_input("Fixed stop %", min_value=0.05, max_value=20.0, value=0.5, step=0.05, key="sim3i_fixed")
            sim_vwap = st.checkbox("VWAP filter", value=True, key="sim3i_vwap")
            sim_spy = st.checkbox("SPY confirmation", value=True, key="sim3i_spy")
        with sc3:
            sim_vol = st.checkbox("Volume confirmation", value=True, key="sim3i_vol")
            sim_use_rvol = st.checkbox("Relative volume filter", value=True, key="sim3i_rvol", disabled=not sim_vol)
            sim_min_rvol = st.number_input(
                "Minimum RVOL",
                min_value=0.1,
                value=1.5,
                step=0.1,
                format="%.2f",
                key="sim3i_min_rvol",
                disabled=not (sim_vol and sim_use_rvol),
            )
            sim_daily_trend = st.checkbox("Daily trend filter (QQQ 20 EMA)", value=False, key="sim3i_trend")
            sim_or_size_en = st.checkbox("OR size filter", value=False, key="sim3i_or_en")
            sim_or_min = st.number_input("Min OR size ($)", min_value=0.01, value=1.0, step=0.25, key="sim3i_or_min", disabled=not sim_or_size_en)
            sim_or_max = st.number_input("Max OR size ($)", min_value=0.01, value=6.0, step=0.25, key="sim3i_or_max", disabled=not sim_or_size_en)

    sim_custom_cfg = backtester.BacktestConfig(
        start_date=sim_start_date,
        end_date=sim_end_date,
        account_size=float(sim_start_balance),
        risk_percent=float(sim_risk_pct),
        r_target=float(sim_r_target),
        stop_style=sim_stop,
        fixed_stop_percent=float(sim_fixed_pct),
        max_trades_per_day=int(sim_max_tr),
        vwap_filter=sim_vwap,
        spy_confirmation=sim_spy,
        volume_confirmation=sim_vol,
        direction_filter=sim_dir,
        daily_trend_qqq_ema20_filter=sim_daily_trend,
        or_size_filter_enabled=sim_or_size_en,
        or_size_min=float(sim_or_min),
        or_size_max=float(sim_or_max),
        use_rvol_filter=sim_use_rvol,
        min_rvol=float(sim_min_rvol),
        enable_entry_cutoff=False,
        favorable_environments_only=False,
    )

sim3i_progress = st.empty()
run_sim3i = st.button("Run paper simulation", key="sim3i_run", type="primary")

if run_sim3i:
    if sim_preset == "Current Best EdgeOne Setup":
        bt_cfg = paper_simulation.current_best_edgeone_backtest_config(
            sim_start_date,
            sim_end_date,
            float(sim_start_balance),
            float(sim_risk_pct),
        )
        preset_label = "Current Best EdgeOne Setup"
    else:
        bt_cfg = sim_custom_cfg
        preset_label = "Custom"
        if bt_cfg is None:
            st.error("Custom configuration is missing.")
            bt_cfg = paper_simulation.current_best_edgeone_backtest_config(
                sim_start_date, sim_end_date, float(sim_start_balance), float(sim_risk_pct)
            )

    def _sim_prog(msg: str) -> None:
        sim3i_progress.info(msg)

    adaptive_rules_sim = st.session_state.get("adaptive_rules")
    if adaptive_rules_sim is None:
        adaptive_rules_sim = adaptive_environment.load_adaptive_rules_from_disk()

    with st.spinner("Running paper simulation…"):
        sim_result = paper_simulation.run_paper_simulation(
            starting_balance=float(sim_start_balance),
            start_date=sim_start_date,
            end_date=sim_end_date,
            risk_percent=float(sim_risk_pct),
            backtest_cfg=bt_cfg,
            preset_label=preset_label,
            simulation_mode=sim_mode,
            progress=_sim_prog,
            adaptive_rules=adaptive_rules_sim,
        )

    st.session_state["sim3i_result"] = sim_result
    if sim_result.error:
        st.error(sim_result.error)
    else:
        try:
            export_paths = paper_simulation.write_simulation_exports(sim_result)
            st.session_state["sim3i_exports"] = export_paths
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Simulation finished but export failed: {exc}")

sim3i_result: paper_simulation.PaperSimulationResult | None = st.session_state.get("sim3i_result")

if sim3i_result is not None and not sim3i_result.error:
    rs = sim3i_result.replay_stats
    s = sim3i_result.summary

    st.markdown("**Replay pipeline summary**")
    rp1, rp2, rp3, rp4, rp5 = st.columns(5)
    rp1.metric("Tradable sessions", str(rs.tradable_session_days))
    rp2.metric("Candidate setups", str(rs.candidate_setups))
    rp3.metric("Blocked setups", str(rs.candidate_setups - rs.approved_setups))
    rp4.metric("Approved setups", str(rs.approved_setups))
    rp5.metric("Executed trades", str(rs.executed_paper_trades))

    with st.expander("Filter debug breakdown", expanded=rs.executed_paper_trades == 0):
        dbg1, dbg2, dbg3 = st.columns(3)
        dbg1.metric("Blocked: environment score", str(rs.blocked_environment_score))
        dbg1.metric("Blocked: trade score", str(rs.blocked_trade_score))
        dbg2.metric("Blocked: RVOL", str(rs.blocked_rvol))
        dbg2.metric("Blocked: OR size", str(rs.blocked_or_size))
        dbg3.metric("Blocked: R multiple", str(rs.blocked_r_multiple))
        dbg3.metric("Blocked: buying power", str(rs.blocked_buying_power))
        st.caption(
            f"Mode **{rs.simulation_mode}** · Stage 3A replay account **${rs.signal_replay_account_used:,.0f}** "
            f"(signal discovery only; P/L uses ${sim_start_balance:,.0f}) · "
            f"Strategy replay min RVOL **{rs.strategy_replay_min_rvol:.2f}**"
        )
        if rs.candidate_setups == 0:
            st.warning(
                "Stage 3A replay returned **0 candidates**. Common causes: date range has no Alpaca bars, "
                "filters too strict (RVOL/VWAP/SPY), or no OR breakouts in range. "
                "Try a longer range or **MODERATE/RELAXED** simulation mode."
            )
        elif rs.approved_setups == 0:
            st.warning(
                "Candidates were found but **all were blocked** by Stage 3D/3E/3F filters. "
                "Try **MODERATE** or **RELAXED** simulation mode."
            )

    if rs.low_trade_count_warning and rs.executed_paper_trades > 0:
        st.warning(
            f"Only **{rs.executed_paper_trades}** trades executed (fewer than 10). "
            "Results may not be statistically meaningful — widen the date range or use a looser simulation mode."
        )
    elif rs.executed_paper_trades == 0:
        st.warning("No paper trades executed after filtering. See debug breakdown above.")

    if sim3i_result.summary.number_of_trades == 0:
        st.info("No executed trades to chart or journal — adjust settings and re-run.")
    else:
        st.success(
            f"Simulation: **${s.starting_balance:,.2f}** → **${s.ending_balance:,.2f}** "
            f"({s.total_return_pct:+.2f}%) over **{int(s.number_of_trades)}** trades."
        )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Starting balance", f"${s.starting_balance:,.2f}")
    m2.metric("Ending balance", f"${s.ending_balance:,.2f}")
    m3.metric("Total return", f"{s.total_return_pct:.2f}%")
    m4.metric("Total P/L", f"${s.total_pnl:,.2f}")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Trades", str(int(s.number_of_trades)))
    m6.metric("Win rate", f"{s.win_rate:.1%}")
    m7.metric("Profit factor", f"{s.profit_factor:.2f}")
    m8.metric("Expectancy", f"${s.expectancy:,.2f}")

    m9, m10, m11, m12 = st.columns(4)
    m9.metric("Max drawdown", f"${s.max_drawdown:,.2f}")
    m10.metric("Best trade", f"${s.best_trade_pnl:,.2f}")
    m11.metric("Worst trade", f"${s.worst_trade_pnl:,.2f}")
    m12.metric("Avg monthly return", f"{s.average_monthly_return_pct:.2f}%")
    st.metric("Average weekly return", f"{s.average_weekly_return_pct:.2f}%")

    if sim3i_result.monthly:
        st.markdown("**Monthly breakdown**")
        monthly_df = pd.DataFrame([{
            "month": r.month,
            "starting_balance": r.starting_balance,
            "ending_balance": r.ending_balance,
            "P/L": r.pnl,
            "return_pct": r.return_pct,
            "number_of_trades": r.number_of_trades,
            "win_rate": r.win_rate,
        } for r in sim3i_result.monthly])
        st.dataframe(monthly_df, use_container_width=True, hide_index=True)

    if sim3i_result.trades:
        st.markdown("**Trade journal** (edit **notes** column, then save exports)")
        journal_df = paper_simulation.trades_to_dataframe(sim3i_result.trades)
        edited_journal = st.data_editor(
            journal_df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "notes": st.column_config.TextColumn("notes", help="Your review notes for this trade"),
            },
            disabled=[c for c in journal_df.columns if c != "notes"],
            key="sim3i_journal_editor",
        )

        if st.button("Save journal notes to CSV exports", key="sim3i_save_notes"):
            updated_trades = paper_simulation.apply_notes_from_editor(sim3i_result.trades, edited_journal)
            sim3i_result.trades = updated_trades
            st.session_state["sim3i_result"] = sim3i_result
            try:
                paths = paper_simulation.write_simulation_exports(sim3i_result)
                st.session_state["sim3i_exports"] = paths
                st.success("Exports updated with your notes.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not save exports: {exc}")

    if sim3i_result.balance_curve:
        st.markdown("**Account balance curve**")
        st.line_chart(pd.DataFrame(sim3i_result.balance_curve).set_index("date"))

    if sim3i_result.monthly_pnl_chart:
        st.markdown("**Monthly P/L**")
        st.bar_chart(pd.DataFrame(sim3i_result.monthly_pnl_chart).set_index("month"))

    if sim3i_result.drawdown_curve:
        st.markdown("**Drawdown curve**")
        st.line_chart(
            pd.DataFrame(sim3i_result.drawdown_curve).set_index("date")[["drawdown_dollars"]]
        )

    exports = st.session_state.get("sim3i_exports", {})
    if exports:
        st.caption(
            f"Exported: `{paper_simulation.TRADES_FILE.name}` · "
            f"`{paper_simulation.MONTHLY_FILE.name}` · "
            f"`{paper_simulation.SUMMARY_FILE.name}` · "
            f"Google Sheets: `{paper_simulation.SHEETS_TRADES_FILE.name}`"
        )
elif sim3i_result is not None and sim3i_result.error:
    st.error(sim3i_result.error)
    if sim3i_result.summary.number_of_trades == 0:
        st.info("No trades to display. Adjust dates or strategy filters and run again.")
