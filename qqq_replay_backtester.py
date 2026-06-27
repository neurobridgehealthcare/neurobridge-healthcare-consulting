"""
QQQ Replay Backtester — simple TradingView-style replay simulator.

Run: streamlit run qqq_replay_backtester.py

Training only. No live trading. No real orders. No profit promises.
"""

from __future__ import annotations

import streamlit as st

import qqq_replay_engine as engine

st.set_page_config(
    page_title="QQQ Replay Backtester",
    page_icon="📈",
    layout="wide",
)

engine.ensure_files()

DISCLAIMER = (
    "**Training only.** See chart → place trade → reveal outcome → learn. "
    "No live orders. No profit promises."
)


def _init() -> None:
    defaults = {
        "qr_scenario": None,
        "qr_candles_1m": None,
        "qr_revealed": False,
        "qr_outcome": None,
        "qr_market": engine.DEFAULT_MARKET,
        "qr_timeframe": "5m",
        "qr_chart_wide": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init()


def _load_random(market: str) -> None:
    sc = engine.pick_scenario(market)
    candles = engine.load_candles_1m(sc.scenario_id)
    st.session_state["qr_scenario"] = sc
    st.session_state["qr_candles_1m"] = candles
    st.session_state["qr_revealed"] = False
    st.session_state["qr_outcome"] = None
    st.session_state["qr_market"] = market


def _reset_current() -> None:
    st.session_state["qr_revealed"] = False
    st.session_state["qr_outcome"] = None


st.title("QQQ Replay Backtester")
st.markdown("#### See chart. Place trade. Reveal outcome. Repeat.")
st.caption("Training only · No live orders · No profit promises")

# Top controls
c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1, 1])
with c1:
    market = st.selectbox(
        "Market",
        engine.MARKETS,
        index=engine.MARKETS.index(st.session_state.get("qr_market", engine.DEFAULT_MARKET)),
        key="qr_market_sel",
    )
with c2:
    timeframe = st.selectbox("Timeframe", engine.TIMEFRAMES, key="qr_tf_sel")
with c3:
    if st.button("New Scenario", type="primary", use_container_width=True):
        _load_random(market)
        st.rerun()
with c4:
    reveal_clicked = st.button("Reveal Outcome", use_container_width=True)
with c5:
    if st.button("Reset Current Scenario", use_container_width=True):
        _reset_current()
        st.rerun()

if st.session_state.get("qr_scenario") is None:
    _load_random(market)

scenario: engine.ReplayScenario = st.session_state["qr_scenario"]
candles_1m = st.session_state.get("qr_candles_1m")
if candles_1m is None:
    candles_1m = engine.load_candles_1m(scenario.scenario_id)
    st.session_state["qr_candles_1m"] = candles_1m

agg = engine.aggregate_timeframe(candles_1m, timeframe)
visible = engine.visible_candles(
    agg,
    scenario.replay_cutoff_time,
    revealed=st.session_state.get("qr_revealed", False),
    end_time=scenario.outcome_end_time,
)

chart_col, plan_col = st.columns([1.6, 1])

with chart_col:
    wide = st.session_state.get("qr_chart_wide", True)
    if st.button("Toggle chart width"):
        st.session_state["qr_chart_wide"] = not wide
        st.rerun()

    ent = float(st.session_state.get("qr_entry", 0))
    stp = float(st.session_state.get("qr_stop", 0))
    tgt = float(st.session_state.get("qr_target", 0))
    plan_for_chart = None
    if ent > 0 or stp > 0 or tgt > 0 or st.session_state.get("qr_revealed"):
        plan_for_chart = engine.TradePlan(
            direction=st.session_state.get("qr_dir", "Long"),
            entry=ent,
            stop_loss=stp,
            take_profit=tgt,
            risk_amount=float(st.session_state.get("qr_risk", 0)),
            notes=st.session_state.get("qr_notes", ""),
        )

    phase = "revealed" if st.session_state.get("qr_revealed") else f"cutoff {scenario.replay_cutoff_time}"
    fig = engine.build_chart(
        visible,
        scenario,
        plan=plan_for_chart,
        full_width=wide,
        title=f"{scenario.market} · {scenario.date} · {scenario.setup_type} · {timeframe} · {phase}",
    )
    if fig:
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True},
        )
    else:
        st.warning("Install plotly: pip install plotly")

    st.caption(
        f"Cutoff: **{scenario.replay_cutoff_time}** · Outcome window ends **{scenario.outcome_end_time}** · "
        f"Difficulty: {scenario.difficulty}"
    )

with plan_col:
    st.subheader("Trade Plan")
    direction = st.radio(
        "Direction",
        ["Long", "Short", "No Trade"],
        horizontal=True,
        key="qr_dir",
    )

    entry = st.number_input("Entry price", value=0.0, format="%.4f", key="qr_entry")
    stop = st.number_input("Stop loss", value=0.0, format="%.4f", key="qr_stop")
    target = st.number_input("Take profit", value=0.0, format="%.4f", key="qr_target")
    risk_amt = st.number_input("Risk amount ($)", value=100.0, min_value=0.0, key="qr_risk")
    notes = st.text_area("Notes", key="qr_notes", height=80)

    plan = engine.TradePlan(
        direction=direction,
        entry=entry,
        stop_loss=stop,
        take_profit=target,
        risk_amount=risk_amt,
        notes=notes,
    )
    ok, warnings, rr = engine.validate_trade_plan(plan)
    if direction in ("Long", "Short") and entry > 0 and stop > 0 and target > 0:
        risk_unit = abs(entry - stop)
        reward_unit = abs(target - entry)
        m1, m2, m3 = st.columns(3)
        m1.metric("Risk / unit", f"{risk_unit:.4f}")
        m2.metric("Reward / unit", f"{reward_unit:.4f}")
        m3.metric("R : R", f"{rr:.1f} : 1")
    for w in warnings:
        st.warning(w)

    if reveal_clicked:
        if not ok and direction != "No Trade":
            st.error("Fix trade plan errors before revealing.")
        elif direction == "No Trade" and not notes.strip():
            st.error("Notes required for No Trade.")
        else:
            outcome = engine.run_backtest(candles_1m, scenario, plan)
            engine.save_result(scenario, timeframe, plan, outcome, rr)
            st.session_state["qr_revealed"] = True
            st.session_state["qr_outcome"] = outcome
            st.rerun()

st.markdown("---")

outcome: engine.BacktestOutcome | None = st.session_state.get("qr_outcome")
if outcome:
    st.subheader("Result")
    r = outcome.result
    if r == "WIN":
        st.success(f"**{r}** · {outcome.explanation}")
    elif r == "LOSS":
        st.error(f"**{r}** · {outcome.explanation}")
    elif r == "AMBIGUOUS":
        st.warning(f"**{r}** · {outcome.explanation}")
    elif r == "NO TRADE":
        st.info(f"**{r}** · {outcome.explanation}")
    else:
        st.info(f"**{r}** · {outcome.explanation}")

    if r != "NO TRADE":
        r1, r2, r3, r4, r5 = st.columns(5)
        r1.metric("Exit price", f"{outcome.exit_price:.4f}")
        r2.metric("R multiple", f"{outcome.r_multiple:.2f}R")
        r3.metric("Simulated P/L", f"${outcome.simulated_pnl:,.2f}")
        r4.metric("Trigger time", outcome.trigger_time or "—")
        r5.metric("Setup", scenario.setup_type)

    if st.session_state.get("qr_revealed"):
        st.caption(f"Hidden outcome: {scenario.hidden_outcome}")

st.subheader("Trade log")
log = engine.load_results(limit=15)
if not log.empty:
    st.dataframe(log.iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.caption("Complete a scenario to populate the log.")

st.caption(DISCLAIMER)
