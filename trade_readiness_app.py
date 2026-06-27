"""
Trade Readiness Simulator — standalone Streamlit practice app.

Run: streamlit run trade_readiness_app.py

Training only. No live trading. No real orders. No profit promises.
"""

from __future__ import annotations

import streamlit as st

import trade_readiness_engine as tre

st.set_page_config(
    page_title="Trade Readiness Simulator",
    page_icon="📋",
    layout="wide",
)

if "tr_progress" not in st.session_state:
    st.session_state["tr_progress"] = tre.load_progress()
if "tr_scenario" not in st.session_state:
    st.session_state["tr_scenario"] = None
if "tr_revealed" not in st.session_state:
    st.session_state["tr_revealed"] = False
if "tr_last_grade" not in st.session_state:
    st.session_state["tr_last_grade"] = None

progress: tre.ProgressState = st.session_state["tr_progress"]
score = tre.overall_trader_score(progress)
level = tre.trader_level(score)

st.title("Trade Readiness Simulator")
st.caption("Practice trade preparation · Checklist · Simulated paper money · No live orders")
st.info(tre.DISCLAIMER)

# Dashboard row
d1, d2, d3, d4, d5, d6, d7 = st.columns(7)
d1.metric("Practice balance", f"${progress.account_balance:,.2f}")
d2.metric("Total trades", progress.total_trades)
d3.metric("Win rate", f"{tre.win_rate(progress):.0f}%")
d4.metric("Average R", f"{tre.average_r(progress):.2f}")
d5.metric("Discipline", f"{progress.discipline_score:.0f}")
d6.metric("Scenarios done", len(progress.completed_scenarios))
d7.metric("Trader level", level, delta=f"{score:.0f}/100")

st.divider()

# Settings
with st.expander("Practice account settings", expanded=False):
    s1, s2 = st.columns(2)
    with s1:
        new_balance = st.number_input(
            "Starting practice balance ($)",
            min_value=100.0,
            value=float(progress.starting_balance),
            step=500.0,
        )
    with s2:
        new_risk = st.number_input(
            "Risk per trade (%)",
            min_value=0.1,
            max_value=10.0,
            value=float(progress.risk_per_trade_pct),
            step=0.1,
        )
    if st.button("Update settings"):
        progress.starting_balance = new_balance
        progress.risk_per_trade_pct = new_risk
        if progress.total_trades == 0:
            progress.account_balance = new_balance
        tre.save_progress(progress)
        st.session_state["tr_progress"] = progress
        st.success("Settings saved.")

left, right = st.columns([1.1, 0.9])

# ---------------------------------------------------------------------------
# LEFT: Scenario
# ---------------------------------------------------------------------------
with left:
    st.subheader("Scenario")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("New scenario", type="primary", key="tr_new"):
            st.session_state["tr_scenario"] = tre.pick_scenario()
            st.session_state["tr_revealed"] = False
            st.session_state["tr_last_grade"] = None
            st.rerun()
    with btn_col2:
        reveal_clicked = st.button("Reveal outcome", key="tr_reveal")
    with btn_col3:
        save_clicked = st.button("Save trade attempt", key="tr_save")

    scenario: tre.TradeScenario | None = st.session_state.get("tr_scenario")
    if scenario is None:
        st.info("Click **New scenario** to start practicing.")
    else:
        st.markdown(f"### {scenario.market} · {scenario.date} · {scenario.time}")
        st.markdown(f"**Market condition:** {scenario.market_condition_summary}")

        info1, info2 = st.columns(2)
        with info1:
            st.markdown(f"**Weekly trend:** {scenario.weekly_trend}")
            st.markdown(f"**Monthly trend:** {scenario.monthly_trend}")
            st.markdown(f"**Opening 15-min candle:** {scenario.opening_15m_candle}")
            st.markdown(f"**VWAP status:** {scenario.vwap_status}")
        with info2:
            st.markdown(f"**Volume / RVOL:** {scenario.volume_rvol}")
            st.markdown(f"**Support / resistance:** {scenario.support_resistance}")

        st.markdown("---")
        st.markdown("#### Your trade plan")
        trade_choice = st.radio(
            "Trade choice",
            ["Long", "Short", "Watch", "No Trade"],
            horizontal=True,
            key="tr_choice",
        )
        p1, p2, p3 = st.columns(3)
        with p1:
            entry = st.number_input("Entry price", value=0.0, format="%.4f", key="tr_entry")
        with p2:
            stop = st.number_input("Stop price", value=0.0, format="%.4f", key="tr_stop")
        with p3:
            target = st.number_input("Target price", value=0.0, format="%.4f", key="tr_target")
        confidence = st.slider("Confidence (1–10)", 1, 10, 5, key="tr_conf")
        notes = st.text_area("Notes", placeholder="Why this choice?", key="tr_notes")

        checklist_answers: dict[str, str] = {}
        for key in ("trend", "vwap", "volume", "regime", "relative_strength"):
            item = next((i for i in tre.CHECKLIST_ITEMS if i[0] == key), None)
            if item and item[2]:
                checklist_answers[key] = st.selectbox(
                    item[1],
                    item[2],
                    key=f"tr_chk_{key}",
                )

        if reveal_clicked:
            st.session_state["tr_revealed"] = True
            grade, score_val, feedback = tre.grade_trade_decision(
                scenario, trade_choice, entry, stop, target, confidence
            )
            chk_pct, missed = tre.grade_checklist_answers(
                scenario, checklist_answers, trade_choice, entry, stop, target
            )
            st.session_state["tr_last_grade"] = {
                "grade": grade,
                "score": score_val,
                "feedback": feedback,
                "chk_pct": chk_pct,
                "missed": missed,
                "trade_choice": trade_choice,
                "entry": entry,
                "stop": stop,
                "target": target,
                "confidence": confidence,
                "notes": notes,
                "checklist_answers": checklist_answers,
            }

        if st.session_state.get("tr_revealed"):
            st.markdown("#### Outcomes (revealed)")
            st.success(f"**By 10:30:** {scenario.outcome_1030}")
            st.info(f"**By 11:00:** {scenario.outcome_1100}")
            st.info(f"**By 12:00:** {scenario.outcome_1200}")
            st.warning(f"**At close:** {scenario.outcome_close}")
            st.markdown(f"**Best choice was:** {scenario.best_choice}")

            last = st.session_state.get("tr_last_grade")
            if last:
                g = last["grade"]
                if g in ("Excellent", "Good"):
                    st.success(f"**Grade: {g}** ({last['score']}/100) — {last['feedback']}")
                elif g == "Best answer was No Trade":
                    st.error(f"**Grade: {g}** — {last['feedback']}")
                else:
                    st.warning(f"**Grade: {g}** ({last['score']}/100) — {last['feedback']}")
                st.caption(f"Checklist score: {last['chk_pct']:.0f}%")

        if save_clicked:
            last = st.session_state.get("tr_last_grade")
            if not last:
                grade, score_val, feedback = tre.grade_trade_decision(
                    scenario, trade_choice, entry, stop, target, confidence
                )
                chk_pct, _ = tre.grade_checklist_answers(
                    scenario, checklist_answers, trade_choice, entry, stop, target
                )
            else:
                grade = last["grade"]
                score_val = last["score"]
                chk_pct = last["chk_pct"]
                trade_choice = last["trade_choice"]
                entry = last["entry"]
                stop = last["stop"]
                target = last["target"]
                confidence = last["confidence"]
                notes = last["notes"]

            progress = tre.record_attempt(
                progress,
                scenario,
                trade_choice,
                entry,
                stop,
                target,
                confidence,
                notes,
                grade,
                score_val,
                chk_pct,
            )
            st.session_state["tr_progress"] = progress
            st.success(f"Saved. Practice balance: ${progress.account_balance:,.2f}")
            st.rerun()

# ---------------------------------------------------------------------------
# RIGHT: Checklist
# ---------------------------------------------------------------------------
with right:
    st.subheader("Trade Readiness Checklist")
    st.caption("Answer each item before you decide. No trade is a valid answer.")

    for idx, (key, question, options) in enumerate(tre.CHECKLIST_ITEMS, start=1):
        st.markdown(f"**{idx}. {question}**")
        if options:
            st.radio(
                question,
                options,
                key=f"tr_rubric_{key}",
                label_visibility="collapsed",
            )
        elif key == "market":
            mkt = scenario.market if scenario else "—"
            st.text_input("Market", value=mkt, disabled=True, key=f"tr_rubric_{key}")
        elif key == "opening_candle":
            oc = scenario.opening_15m_candle if scenario else "Load a scenario first"
            st.text_area("Opening candle", value=oc, disabled=True, height=68, key=f"tr_rubric_{key}")
        elif key in ("entry_plan", "stop_plan", "target_plan"):
            st.caption("Fill these on the left side in your trade plan.")
        st.markdown("")

    if scenario and st.session_state.get("tr_revealed"):
        last = st.session_state.get("tr_last_grade")
        if last and last.get("missed"):
            st.markdown("#### Checklist feedback")
            for m in last["missed"]:
                st.warning(m)

st.divider()
st.markdown("### Performance summary")
jdf = tre.load_journal()
if jdf.empty:
    st.caption("No saved attempts yet. Reveal an outcome and save your attempt.")
else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best trade (R)", f"{progress.best_trade_r:.2f}")
    c2.metric("Worst trade (R)", f"{progress.worst_trade_r:.2f}")
    c3.metric("Checklist avg", f"{tre.checklist_completion_score(progress):.0f}%")
    c4.metric("Total P/L", f"${progress.account_balance - progress.starting_balance:,.2f}")
    st.dataframe(jdf.sort_values("timestamp", ascending=False).head(20), use_container_width=True, hide_index=True)

st.caption(
    "Files: `trade_readiness_scenarios.csv` · `trade_readiness_journal.csv` · "
    "`trade_readiness_progress.json`"
)
