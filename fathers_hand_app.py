"""
Father's Hand — chart-based replay training simulator.

Run: streamlit run fathers_hand_app.py

NOT live trading. NOT financial advice. Training only.
"""

from __future__ import annotations

import streamlit as st

import fathers_hand
import fathers_hand_charts as fhc
import fathers_hand_game as fhg
import fathers_hand_modules as fhm
import fathers_hand_scenario_engine as fhe
import fathers_hand_simulator as fhs
import risk

st.set_page_config(
    page_title="Father's Hand — Chart Replay",
    page_icon="🖐️",
    layout="wide",
)

fhm.ensure_module_files()
fhe.ensure_registry()
fhs.ensure_simulator_files()
fhg.ensure_game_files()

USER_ID = "default"
MAX_RISK_DOLLARS = 500.0

STEP_LABELS = [
    "Market Mode",
    "Load Scenario",
    "Study Chart",
    "Checklist",
    "Trade Plan",
    "Submit",
    "Reveal Outcome",
    "Grade & Coaching",
]


def _init_state() -> None:
    defaults = {
        "fh_view": "home",
        "fh_train_step": 1,
        "fh_market_mode": fhe.DEFAULT_MARKET_MODE,
        "fh_train_scenario": None,
        "fh_train_candles": None,
        "fh_train_levels": None,
        "fh_train_result": None,
        "fh_coach_report": None,
        "fh_reveal_phase": "pre_reveal",
        "fh_chart_expanded": False,
        "fh_boss_mode": False,
        "fh_game_feedback": None,
        "fh_progress": fathers_hand.load_progress(),
        "fh_modules": fathers_hand.build_learning_modules(),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()
progress: fathers_hand.ProgressState = st.session_state["fh_progress"]
modules: list[fathers_hand.LessonModule] = st.session_state["fh_modules"]


def _has_active_session() -> bool:
    return (
        st.session_state.get("fh_train_scenario") is not None
        and st.session_state.get("fh_train_step", 1) < 8
    )


def _start_new_session() -> None:
    st.session_state["fh_view"] = "train"
    st.session_state["fh_train_step"] = 1
    st.session_state["fh_market_mode"] = fhe.DEFAULT_MARKET_MODE
    st.session_state["fh_train_scenario"] = None
    st.session_state["fh_train_candles"] = None
    st.session_state["fh_train_levels"] = None
    st.session_state["fh_train_result"] = None
    st.session_state["fh_coach_report"] = None
    st.session_state["fh_reveal_phase"] = "pre_reveal"
    st.session_state["fh_chart_expanded"] = False
    st.session_state["fh_boss_mode"] = False
    st.session_state["fh_game_feedback"] = None


def _start_boss_session() -> None:
    gp = fhg.load_game_progress(USER_ID)
    boss = fhg.current_boss_type(gp)
    scenario = fhg.pick_boss_scenario(boss)
    candles = fhc.get_candles(scenario)
    levels = fhc.levels_for_scenario(scenario)
    st.session_state["fh_view"] = "train"
    st.session_state["fh_train_step"] = 3
    st.session_state["fh_boss_mode"] = True
    st.session_state["fh_boss_info"] = boss
    st.session_state["fh_train_scenario"] = scenario
    st.session_state["fh_train_candles"] = candles
    st.session_state["fh_train_levels"] = levels
    st.session_state["fh_reveal_phase"] = "pre_reveal"
    st.session_state["fh_train_result"] = None
    st.session_state["fh_game_feedback"] = None


def _continue_session() -> None:
    st.session_state["fh_view"] = "train"


def _load_scenario_for_mode(mode: str) -> None:
    scenario = fhe.pick_scenario_for_mode(mode)
    candles = fhc.get_candles(scenario)
    levels = fhc.levels_for_scenario(scenario)
    st.session_state["fh_train_scenario"] = scenario
    st.session_state["fh_train_candles"] = candles
    st.session_state["fh_train_levels"] = levels
    st.session_state["fh_reveal_phase"] = "pre_reveal"


def _render_chart(
    scenario: fhs.FullScenario,
    phase: fhc.RevealPhase,
    trade_lines: fhc.TradeLines | None = None,
    key_suffix: str = "",
) -> None:
    candles = st.session_state.get("fh_train_candles")
    levels = st.session_state.get("fh_train_levels")
    if candles is None or levels is None:
        candles = fhc.get_candles(scenario)
        levels = fhc.levels_for_scenario(scenario)
        st.session_state["fh_train_candles"] = candles
        st.session_state["fh_train_levels"] = levels

    expanded = st.session_state.get("fh_chart_expanded", False)
    title = f"{scenario.market} · {scenario.date} · {scenario.setup_type}"
    if phase != "pre_reveal":
        title += f" · through {_phase_label(phase)}"

    fig = fhc.build_plotly_figure(
        candles,
        levels,
        phase=phase,
        trade_lines=trade_lines,
        show_full_width=expanded or phase != "pre_reveal",
        title=title,
    )
    if fig is None:
        st.warning("Chart unavailable. Install plotly: pip install plotly")
        return

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=f"fh_chart_{phase}_{key_suffix}",
        config={"scrollZoom": True, "displayModeBar": True},
    )


def _phase_label(phase: str) -> str:
    return {"1030": "10:30", "1100": "11:00", "1200": "12:00", "close": "close"}.get(phase, phase)


def _context_panel(scenario: fhs.FullScenario) -> None:
    with st.expander("Market context (daily / premarket)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Higher TF trend:** {scenario.higher_timeframe_trend}")
            st.write(f"**Weekly / Monthly:** {scenario.weekly_trend} / {scenario.monthly_trend}")
            st.write(f"**Prior day H/L:** {scenario.prior_day_high} / {scenario.prior_day_low}")
        with c2:
            st.write(f"**Premarket:** {scenario.premarket_trend}")
            st.write(f"**Session:** {scenario.session_type}")
            st.write(f"**15-min read:** {scenario.first_15m_candle}")
        st.caption("Future candles stay hidden until you reveal the outcome.")


def _save_attempt(scenario: fhs.FullScenario, result: dict) -> None:
    grade = result["grade"]
    score = result["score"]
    fhs.save_replay_attempt(
        scenario,
        USER_ID,
        result["user_choice"],
        result["entry"],
        result["stop"],
        result["target"],
        result["confidence"],
        grade,
        score,
        result.get("correct_direction", False),
        result.get("user_note", ""),
        target2=result.get("target2", 0.0),
        risk_amount=result.get("risk_amount", 0.0),
        risk_percent=result.get("risk_percent", 0.0),
        trade_outcome=str(result.get("trade_outcome", {}).get("result", "")),
    )
    fhs.save_checklist_attempt(
        scenario,
        USER_ID,
        result.get("checklist_answers", {}),
        result.get("checklist_pct", 0),
        result.get("checklist_missed", []),
    )
    progress = fathers_hand.record_replay_result(
        st.session_state["fh_progress"],
        "Correct" if grade in ("Excellent", "Good") else (
            "Partially correct" if grade == "Risky" else "Incorrect"
        ),
    )
    st.session_state["fh_progress"] = progress
    fathers_hand.append_journal_entry(
        module="Chart Replay",
        scenario=scenario.scenario_id,
        user_answer=result["user_choice"],
        correct_answer=scenario.best_choice,
        score=f"{grade} ({score})",
        notes=result.get("user_note", ""),
        lesson_learned=result.get("coaching", ""),
    )
    fhs.save_skill_history(USER_ID)

    game_feedback = fhg.process_scenario_completion(
        scenario,
        result,
        user_id=USER_ID,
        is_boss=st.session_state.get("fh_boss_mode", False),
    )
    st.session_state["fh_game_feedback"] = game_feedback
    result["game_feedback"] = game_feedback


def _render_stepper(step: int) -> None:
    cols = st.columns(len(STEP_LABELS))
    for i, label in enumerate(STEP_LABELS, start=1):
        with cols[i - 1]:
            if i < step:
                st.caption(f"✓ {label}")
            elif i == step:
                st.markdown(f"**→ {label}**")
            else:
                st.caption(label)


view = st.session_state.get("fh_view", "home")

# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------
if view == "home":
    stats = fhg.home_stats(USER_ID)
    gp = fhg.load_game_progress(USER_ID)

    st.title("Father's Hand")
    st.markdown("#### Train your eye. Build discipline. Master the setup.")
    st.caption("Practice only. No live orders. No profit promises.")

    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("Level", f"{stats['level_num']} · {stats['level_title']}")
    g2.metric("XP", f"{stats['xp']:,}")
    g3.metric("Streak", f"{stats['streak']}d")
    g4.metric("Rank", stats["career_rank"])
    g5.metric("Next Unlock", stats["next_unlock"][:28] + ("…" if len(stats["next_unlock"]) > 28 else ""))

    st.progress(stats["level_progress"], text=f"{stats['xp']:,} XP · {stats['xp_to_next']} to next level")
    st.caption(fhg.daily_mission_text(gp))

    st.markdown("---")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Start Training", type="primary", use_container_width=True):
            _start_new_session()
            st.rerun()
    with b2:
        if st.button("Continue Run", use_container_width=True, disabled=not _has_active_session()):
            _continue_session()
            st.rerun()
        if _has_active_session():
            step = st.session_state.get("fh_train_step", 1)
            label = "Boss Battle" if st.session_state.get("fh_boss_mode") else st.session_state.get("fh_market_mode", "?")
            st.caption(f"Resume step {step} · {label}")
    with b3:
        if st.button("View Progress", use_container_width=True):
            st.session_state["fh_view"] = "progress"
            st.rerun()

    if stats["boss_unlocked"]:
        st.markdown("---")
        boss = fhg.current_boss_type(gp)
        if st.button(f"Enter Boss Battle — {boss['name']}", type="secondary", use_container_width=True):
            _start_boss_session()
            st.rerun()

    st.caption(fathers_hand.DISCLAIMER)

# ---------------------------------------------------------------------------
# TRAINING WIZARD
# ---------------------------------------------------------------------------
elif view == "train":
    step = st.session_state.get("fh_train_step", 1)
    if st.session_state.get("fh_boss_mode"):
        boss_info = st.session_state.get("fh_boss_info", {})
        st.warning(f"**Boss Battle:** {boss_info.get('name', 'Challenge')} — score 80%+ to win.")
    _render_stepper(step)

    if st.button("← Back to Home", key="train_home"):
        st.session_state["fh_view"] = "home"
        st.rerun()

    scenario: fhs.FullScenario | None = st.session_state.get("fh_train_scenario")

    # Step 1 — Market Mode
    if step == 1:
        st.subheader("Step 1 — Choose Market Mode")
        mode = st.radio(
            "Training mode",
            list(fhe.MARKET_MODES.keys()),
            index=list(fhe.MARKET_MODES.keys()).index(
                st.session_state.get("fh_market_mode", fhe.DEFAULT_MARKET_MODE)
            ),
            key="step1_mode",
        )
        st.info(fhe.MARKET_MODES[mode]["description"])
        st.caption(f"Markets: {', '.join(fhe.markets_for_mode(mode))}")
        if st.button("Load random scenario", type="primary", key="step1_go"):
            st.session_state["fh_market_mode"] = mode
            _load_scenario_for_mode(mode)
            st.session_state["fh_train_step"] = 2
            st.rerun()

    # Step 2 — Scenario loaded
    elif step == 2 and scenario:
        st.subheader("Step 2 — Scenario Loaded")
        st.success(
            f"**{scenario.market}** · {scenario.date} · {scenario.setup_type} · "
            f"{scenario.difficulty} difficulty"
        )
        st.caption(f"Mode: {st.session_state.get('fh_market_mode', fhe.DEFAULT_MARKET_MODE)}")
        if st.button("Study chart", type="primary", key="step2_go"):
            st.session_state["fh_train_step"] = 3
            st.rerun()
        if st.button("Load different scenario", key="step2_reload"):
            _load_scenario_for_mode(st.session_state.get("fh_market_mode", fhe.DEFAULT_MARKET_MODE))
            st.rerun()

    # Step 3 — Study chart (first 15 minutes only)
    elif step == 3 and scenario:
        st.subheader("Step 3 — Study the Chart")
        st.caption("Only the first 15 minutes are visible. Outcomes stay hidden.")
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("Expand chart" if not st.session_state.get("fh_chart_expanded") else "Normal width"):
                st.session_state["fh_chart_expanded"] = not st.session_state.get("fh_chart_expanded", False)
                st.rerun()
        _render_chart(scenario, "pre_reveal", key_suffix="study")
        _context_panel(scenario)
        if st.button("Next — Checklist", type="primary", key="step3_go"):
            st.session_state["fh_train_step"] = 4
            st.rerun()

    # Step 4 — Checklist
    elif step == 4 and scenario:
        st.subheader("Step 4 — Trade Readiness Checklist")
        _render_chart(scenario, "pre_reveal", key_suffix="chk")
        checklist_answers: dict[str, str] = {}
        for field_key, label, options in fhs.CHECKLIST_ITEMS:
            st.markdown(f"**{label}**")
            checklist_answers[field_key] = st.radio(
                label, options, key=f"train_chk_{field_key}", label_visibility="collapsed",
            )
        st.session_state["fh_checklist_draft"] = checklist_answers
        if st.button("Next — Trade Plan", type="primary", key="step4_go"):
            st.session_state["fh_train_step"] = 5
            st.rerun()

    # Step 5 — Trade plan
    elif step == 5 and scenario:
        st.subheader("Step 5 — Build Your Trade Plan")
        _render_chart(scenario, "pre_reveal", key_suffix="plan")

        user_choice = st.radio(
            "Direction",
            ["Long", "Short", "Watch", "No Trade"],
            horizontal=True,
            key="train_choice",
        )

        e1, e2, e3, e4 = st.columns(4)
        with e1:
            entry = st.number_input("Entry price", value=0.0, format="%.4f", key="train_entry")
        with e2:
            stop = st.number_input("Stop loss", value=0.0, format="%.4f", key="train_stop")
        with e3:
            target1 = st.number_input("Take profit 1", value=0.0, format="%.4f", key="train_target1")
        with e4:
            target2 = st.number_input("Take profit 2 (optional)", value=0.0, format="%.4f", key="train_target2")

        r1, r2, r3 = st.columns(3)
        with r1:
            risk_amount = st.number_input("Risk amount ($)", value=0.0, min_value=0.0, key="train_risk_amt")
        with r2:
            risk_percent = st.number_input("Risk percent (%)", value=1.0, min_value=0.0, key="train_risk_pct")
        with r3:
            confidence = st.slider("Confidence (1–10)", 1, 10, 5, key="train_conf")

        user_note = st.text_area("Reason for trade or pass", key="train_note")

        ok, warnings, metrics = fhs.validate_trade_plan(
            user_choice, entry, stop, target1, target2,
            risk_amount, risk_percent, user_note, MAX_RISK_DOLLARS,
        )
        if user_choice in ("Long", "Short") and metrics["risk_per_unit"] > 0:
            st.markdown("**Risk / reward calculator**")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Risk per unit", f"{metrics['risk_per_unit']:.4f}")
            m2.metric("Reward to TP1", f"{metrics['reward_tp1']:.4f}")
            m3.metric("Reward : Risk", f"{metrics['reward_risk_ratio']:.1f} : 1")
            m4.metric("Planned R", f"{metrics['planned_r']:.1f}R")
        for w in warnings:
            st.warning(w)

        if st.button("Submit decision", type="primary", key="step5_go"):
            if not ok:
                st.error("Fix the warnings above before submitting.")
            else:
                checklist_answers = st.session_state.get("fh_checklist_draft", {})
                chk_pct, missed = fhs.grade_checklist(scenario, checklist_answers)
                candles = st.session_state.get("fh_train_candles") or fhc.get_candles(scenario)
                trade_outcome = fhc.simulate_trade_outcome(
                    candles, user_choice, entry, stop, target1, target2,
                )
                grade, score, correct_dir, feedback, breakdown = fhs.grade_replay_decision(
                    scenario, user_choice, entry, stop, target1, confidence,
                    target2=target2, trade_outcome=trade_outcome, checklist_pct=chk_pct,
                )
                result = {
                    "user_choice": user_choice,
                    "entry": entry,
                    "stop": stop,
                    "target": target1,
                    "target2": target2,
                    "risk_amount": risk_amount,
                    "risk_percent": risk_percent,
                    "confidence": confidence,
                    "user_note": user_note,
                    "checklist_answers": checklist_answers,
                    "checklist_pct": chk_pct,
                    "checklist_missed": missed,
                    "grade": grade,
                    "score": score,
                    "correct_direction": correct_dir,
                    "feedback": feedback,
                    "breakdown": breakdown,
                    "trade_outcome": trade_outcome,
                }
                result["coaching"] = fhs.generate_session_coaching(scenario, result)
                st.session_state["fh_train_result"] = result
                st.session_state["fh_train_step"] = 6
                st.rerun()

    # Step 6 — Submit (chart with entry/stop/target lines)
    elif step == 6 and scenario:
        st.subheader("Step 6 — Your Plan on the Chart")
        result = st.session_state.get("fh_train_result", {})
        lines = fhc.TradeLines(
            entry=float(result.get("entry", 0)),
            stop=float(result.get("stop", 0)),
            target1=float(result.get("target", 0)),
            target2=float(result.get("target2", 0)),
        )
        _render_chart(scenario, "pre_reveal", trade_lines=lines, key_suffix="submit")
        st.success(f"Plan submitted: **{result.get('user_choice', '?')}**")
        st.caption("Review your levels, then reveal what happened next.")
        if st.button("Reveal Outcome", type="primary", key="step6_go"):
            st.session_state["fh_train_step"] = 7
            st.session_state["fh_reveal_phase"] = "1030"
            st.rerun()

    # Step 7 — Reveal outcome
    elif step == 7 and scenario:
        st.subheader("Step 7 — Reveal Outcome")
        result = st.session_state.get("fh_train_result", {})
        lines = fhc.TradeLines(
            entry=float(result.get("entry", 0)),
            stop=float(result.get("stop", 0)),
            target1=float(result.get("target", 0)),
            target2=float(result.get("target2", 0)),
        )

        phase = st.radio(
            "Show outcome through",
            ["1030", "1100", "1200", "close"],
            format_func=_phase_label,
            horizontal=True,
            key="reveal_phase_pick",
        )
        st.session_state["fh_reveal_phase"] = phase
        _render_chart(scenario, phase, trade_lines=lines, key_suffix=f"reveal_{phase}")

        st.markdown(f"**10:30** — {scenario.outcome_1030}")
        st.markdown(f"**11:00** — {scenario.outcome_1100}")
        st.markdown(f"**12:00** — {scenario.outcome_1200}")
        st.markdown(f"**Close** — {scenario.outcome_close}")

        trade_outcome = result.get("trade_outcome", {})
        if trade_outcome.get("result") == "stop_first":
            st.error("Simulated path: **stop hit first**.")
        elif trade_outcome.get("result") == "target_first":
            st.success(f"Simulated path: **{trade_outcome.get('hit', 'target')} hit first**.")
        elif trade_outcome.get("result") == "neither":
            st.info("Simulated path: neither stop nor target hit before close.")
        elif scenario.best_choice in ("No Trade", "Watch"):
            st.info("Best answer was **no trade** or watch.")

        if st.button("Next — Grade & Coaching", type="primary", key="step7_go"):
            st.session_state["fh_train_step"] = 8
            st.rerun()

    # Step 8 — Grade, coaching, save, game feedback
    elif step == 8 and scenario:
        result = st.session_state.get("fh_train_result", {})
        breakdown = result.get("breakdown", {})
        game_fb = st.session_state.get("fh_game_feedback")

        if game_fb is None:
            report = fhs.generate_coach_report(USER_ID)
            st.session_state["fh_coach_report"] = report
            _save_attempt(scenario, result)
            game_fb = st.session_state.get("fh_game_feedback", {})
            st.rerun()

        st.subheader("Mission Complete" if not st.session_state.get("fh_boss_mode") else "Boss Battle Result")

        g = result.get("grade", "")
        if g in ("Excellent", "Good"):
            st.success(f"**Grade: {g}** ({result.get('score', 0)}/100)")
        elif g == "Best answer was No Trade":
            st.error(f"**Grade: {g}**")
        else:
            st.warning(f"**Grade: {g}** ({result.get('score', 0)}/100)")

        xp_earned = game_fb.get("xp_earned", 0)
        xp_sign = "+" if xp_earned >= 0 else ""
        st.markdown(f"### You earned {xp_sign}{xp_earned} XP")
        with st.expander("XP breakdown", expanded=False):
            for line in game_fb.get("xp_breakdown", []):
                st.write(line)

        for badge in game_fb.get("badges_earned", []):
            st.success(f"Badge unlocked: **{badge}**")

        if game_fb.get("rank_up"):
            lvl = game_fb.get("level", (1, "", 0, 0))
            st.balloons()
            st.success(f"Rank Up! Level {lvl[0]}: **{lvl[1]}**")

        if game_fb.get("boss_passed"):
            st.success("Boss Battle cleared! Bonus XP awarded.")
        elif game_fb.get("boss_failed"):
            st.error(f"Boss Battle failed (need {fhg.BOSS_PASS_SCORE}%+). {game_fb.get('recommended_drill', '')}")

        for change in game_fb.get("skill_changes", []):
            st.info(change)

        st.markdown(f"**Coach:** {result.get('coaching', game_fb.get('coach_message', ''))}")
        st.caption(f"Checklist: {result.get('checklist_pct', 0):.0f}% · Best: {scenario.best_choice}")
        st.caption(f"**Next drill:** {game_fb.get('recommended_drill', '')}")

        with st.expander("Score breakdown", expanded=False):
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Market read", breakdown.get("market_read", 0))
            b2.metric("Checklist", breakdown.get("checklist_quality", 0))
            b3.metric("Direction", breakdown.get("direction", 0))
            b4.metric("Risk/Reward", breakdown.get("risk_reward", 0))
            b5, b6, b7, b8 = st.columns(4)
            b5.metric("Entry", breakdown.get("entry_quality", 0))
            b6.metric("Stop", breakdown.get("stop_placement", 0))
            b7.metric("Target", breakdown.get("target_placement", 0))
            b8.metric("Discipline", breakdown.get("discipline", 0))

        missed = result.get("checklist_missed", [])
        if missed:
            with st.expander("Checklist review (answers revealed)"):
                for m in missed:
                    st.write(f"- **{m['item']}** — yours: {m['your_answer']} → correct: {m['correct_answer']}")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Start Training", type="primary", use_container_width=True):
                _start_new_session()
                st.rerun()
        with c2:
            if fhg.boss_is_unlocked(fhg.load_game_progress(USER_ID)):
                if st.button("Enter Boss Battle", use_container_width=True):
                    _start_boss_session()
                    st.rerun()
        with c3:
            if st.button("View Progress", use_container_width=True):
                st.session_state["fh_view"] = "progress"
                st.rerun()

    else:
        st.warning("Session data missing. Start a new simulation.")
        if st.button("Start New Simulation", type="primary"):
            _start_new_session()
            st.rerun()

# ---------------------------------------------------------------------------
# PROGRESS
# ---------------------------------------------------------------------------
elif view == "progress":
    if st.button("← Back to Home", key="prog_home"):
        st.session_state["fh_view"] = "home"
        st.rerun()

    gp = fhg.load_game_progress(USER_ID)
    stats = fhg.home_stats(USER_ID)
    scores = fhs.compute_skill_scores(USER_ID)
    strongest, weakest = fhs.strongest_weakest_skills(USER_ID)
    next_drill = fhs.recommended_drill(USER_ID)
    badges = fhg.load_badges()
    skill_tree = fhg.build_skill_tree(USER_ID)

    st.subheader("Progress")

    st.markdown("### Player")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Level", f"{stats['level_num']} · {stats['level_title']}")
    p2.metric("XP", f"{stats['xp']:,}")
    p3.metric("Career Rank", gp.career_rank)
    p4.metric("Daily Streak", f"{gp.current_streak}d (best {gp.longest_streak}d)")
    st.progress(stats["level_progress"], text=f"{stats['xp_to_next']} XP to next level")
    st.caption(fhg.daily_mission_text(gp))

    st.markdown("### Mission stats")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Scenarios completed", gp.scenarios_completed)
    m2.metric("Today", gp.scenarios_today)
    m3.metric("Strongest skill", strongest)
    m4.metric("Weakest skill", weakest)
    st.info(f"**Next recommended mission:** {next_drill}")

    if stats["boss_unlocked"]:
        boss = fhg.current_boss_type(gp)
        if st.button(f"Enter Boss Battle — {boss['name']}", key="prog_boss"):
            _start_boss_session()
            st.rerun()

    st.markdown("### Badges")
    if badges:
        badge_cols = st.columns(min(4, len(badges)))
        for i, b in enumerate(badges[:12]):
            with badge_cols[i % len(badge_cols)]:
                st.caption(f"🏅 {b.get('name', 'Badge')}")
        if len(badges) > 12:
            st.caption(f"+ {len(badges) - 12} more badges earned")
    else:
        st.caption("Complete scenarios to earn your first badge.")

    st.markdown("### Skill Tree")
    for branch in skill_tree:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.write(f"**{branch['name']}** — {branch['level']}")
        with col_b:
            st.progress(min(1.0, branch["score"] / 100.0), text=f"{branch['score']:.0f}")

    with st.expander("Career Mode", expanded=False):
        st.write(f"Current rank: **{gp.career_rank}**")
        st.caption("Promotions use XP, skill scores, discipline, and scenario count — not fake P/L.")
        for req in fhg.CAREER_RANKS:
            met = (
                gp.xp >= req["xp"]
                and scores.overall_trader_score >= req["skill"]
                and scores.discipline >= req["discipline"]
                and gp.scenarios_completed >= req["scenarios"]
            )
            icon = "✓" if met else "○"
            st.caption(
                f"{icon} {req['rank']} — {req['xp']} XP, "
                f"{req['skill']}% skill, {req['discipline']}% discipline, "
                f"{req['scenarios']} scenarios"
            )

    with st.expander("Advanced logs & study tools", expanded=False):
        st.metric("Trader rating", f"{scores.overall_trader_score:.0f}/100", delta=scores.trader_level)
        lib = fhs.scenario_library_stats()
        st.write(
            f"**{lib.get('csv_scenarios', 0)}** chart scenarios · "
            f"**{lib.get('procedural', 0):,}** procedural on demand."
        )
        if st.button("Refresh skill scores", key="prog_refresh"):
            fhs.save_skill_history(USER_ID)
            st.rerun()

    with st.expander("Lessons & Quiz", expanded=False):
        lesson_ids = [m.module_id for m in modules]
        sel = st.selectbox(
            "Module",
            lesson_ids,
            format_func=lambda i: next(m.title for m in modules if m.module_id == i),
        )
        mod = next(m for m in modules if m.module_id == sel)
        st.markdown(mod.summary)
        for line in mod.lessons:
            st.markdown(line)
        if mod.quiz:
            st.markdown("**Quiz**")
            quiz_answers: dict[str, str] = {}
            for q in mod.quiz:
                st.markdown(q.prompt)
                if q.quiz_type == "short_answer":
                    quiz_answers[q.question_id] = st.text_area("Answer", key=f"pq_{q.question_id}")
                else:
                    quiz_answers[q.question_id] = st.radio(
                        "Choose", q.options, key=f"pq_{q.question_id}", label_visibility="collapsed",
                    )
            if st.button("Submit quiz", key="prog_quiz_submit"):
                correct = sum(
                    1 for q in mod.quiz
                    if fathers_hand.grade_quiz_question(q, quiz_answers.get(q.question_id, ""))[0]
                )
                st.session_state["fh_progress"] = fathers_hand.record_quiz_result(
                    st.session_state["fh_progress"], correct, len(mod.quiz), mod.module_id, mod.title,
                )
                fhg.record_lesson_activity(USER_ID)
                st.success(f"Score: {correct}/{len(mod.quiz)}")

    with st.expander("Journal"):
        j1 = st.text_area("Why did I take this? (or skip?)", key="prog_j1")
        j2 = st.text_area("What was the setup?", key="prog_j2")
        lesson = st.text_input("One lesson learned", key="prog_lesson")
        if st.button("Save journal entry"):
            if j1.strip() or j2.strip():
                fathers_hand.append_journal_entry(
                    "Journal", "daily", j1[:300], "", "logged", j2, lesson or "",
                )
                st.session_state["fh_progress"] = fathers_hand.record_journal_completion(
                    st.session_state["fh_progress"]
                )
                fhg.record_lesson_activity(USER_ID)
                st.success("Saved.")
            else:
                st.warning("Write something first.")

    with st.expander("Risk calculator practice", expanded=False):
        acct = st.number_input("Account ($)", value=10_000.0, key="prog_acct")
        rp = st.number_input("Risk %", value=1.0, key="prog_rp")
        direction = st.selectbox("Direction", ["Long", "Short"], key="prog_dir")
        ent = st.number_input("Entry", value=450.0, key="prog_ent")
        stp = st.number_input("Stop", value=448.5, key="prog_stp")
        tgt = st.number_input("Target", value=453.0, key="prog_tgt")
        mr = risk.max_dollar_risk(acct, rp)
        rps = risk.risk_per_share(ent, stp, direction)
        shares = risk.position_size(mr, rps)
        st.write(f"Max risk: ${mr:,.2f} · Shares: {shares}")

    with st.expander("Export logs"):
        if st.button("Show log paths"):
            paths = fhs.export_all_logs()
            paths["candles"] = str(fhc.CANDLES_FILE)
            st.json(paths)
