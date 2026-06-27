"""
Father's Hand — gamification layer (XP, levels, streaks, badges, boss battles).

Training only. No live trading. No profit promises.
Sits on top of existing simulator logic — does not replace it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import fathers_hand_simulator as fhs

PROJECT_DIR = Path(__file__).resolve().parent
GAME_PROGRESS_FILE = PROJECT_DIR / "fathers_hand_game_progress.json"
BADGES_FILE = PROJECT_DIR / "fathers_hand_badges.json"

DAILY_SCENARIO_GOAL = 3

PLAYER_LEVELS: List[Tuple[int, str, int]] = [
    (1, "New Blood", 0),
    (2, "Chart Rookie", 250),
    (3, "Setup Spotter", 750),
    (4, "Risk Apprentice", 1500),
    (5, "VWAP Operator", 3000),
    (6, "ORB Specialist", 5000),
    (7, "Trend Day Hunter", 8000),
    (8, "Discipline Trader", 12000),
    (9, "Market Operator", 18000),
    (10, "Elite-in-Training", 25000),
]

CAREER_RANKS: List[Dict[str, Any]] = [
    {"rank": "Training Desk Intern", "xp": 0, "skill": 0, "discipline": 0, "scenarios": 0},
    {"rank": "Junior Chart Reader", "xp": 250, "skill": 20, "discipline": 15, "scenarios": 5},
    {"rank": "Setup Analyst", "xp": 750, "skill": 35, "discipline": 25, "scenarios": 15},
    {"rank": "Risk Desk Trainee", "xp": 1500, "skill": 45, "discipline": 35, "scenarios": 30},
    {"rank": "Execution Apprentice", "xp": 3000, "skill": 55, "discipline": 45, "scenarios": 50},
    {"rank": "Market Operator", "xp": 5000, "skill": 65, "discipline": 55, "scenarios": 75},
    {"rank": "Senior Simulator Trader", "xp": 8000, "skill": 75, "discipline": 65, "scenarios": 100},
    {"rank": "Elite-in-Training", "xp": 12000, "skill": 85, "discipline": 75, "scenarios": 150},
]

BOSS_TYPES: List[Dict[str, str]] = [
    {"id": "fakeout_king", "name": "The Fakeout King", "setup": "fakeout", "badge": "Fakeout Survivor"},
    {"id": "chop_monster", "name": "The Chop Monster", "setup": "no-trade chop", "badge": "No-Trade Master"},
    {"id": "late_entry_trap", "name": "The Late Entry Trap", "setup": "gap fill", "badge": "Risk Protector"},
    {"id": "overconfidence_beast", "name": "The Overconfidence Beast", "setup": "fakeout", "badge": "No-Trade Master"},
    {"id": "trend_day_test", "name": "The Trend Day Test", "setup": "trend day up", "badge": "Trend Reader"},
]

BOSS_INTERVAL = 20
BOSS_PASS_SCORE = 80
BOSS_BONUS_XP = 150

SKILL_TREE_BRANCHES: List[Dict[str, str]] = [
    {"id": "chart_reading", "name": "Chart Reading", "score_key": "chart_reading"},
    {"id": "trend_reading", "name": "Trend Reading", "score_key": "structure_reading"},
    {"id": "vwap", "name": "VWAP", "score_key": "chart_reading"},
    {"id": "opening_range", "name": "Opening Range", "score_key": "pattern_recognition"},
    {"id": "risk_management", "name": "Risk Management", "score_key": "risk_management"},
    {"id": "no_trade_discipline", "name": "No-Trade Discipline", "score_key": "discipline"},
    {"id": "trade_management", "name": "Trade Management", "score_key": "trade_management"},
    {"id": "market_context", "name": "Market Context", "score_key": "market_context"},
]

BADGE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "first_scenario": {"name": "First Scenario Completed", "check": "scenarios_1"},
    "scenarios_10": {"name": "10 Scenarios Completed", "check": "scenarios_10"},
    "scenarios_50": {"name": "50 Scenarios Completed", "check": "scenarios_50"},
    "scenarios_100": {"name": "100 Scenarios Completed", "check": "scenarios_100"},
    "trend_reader": {"name": "Trend Reader", "check": "trend_correct"},
    "vwap_specialist": {"name": "VWAP Specialist", "check": "vwap_correct"},
    "orb_hunter": {"name": "ORB Hunter", "check": "orb_setup"},
    "fakeout_survivor": {"name": "Fakeout Survivor", "check": "boss_fakeout"},
    "no_trade_master": {"name": "No-Trade Master", "check": "no_trade_pass"},
    "risk_protector": {"name": "Risk Protector", "check": "risk_good"},
    "journal_builder": {"name": "Journal Builder", "check": "journal_note"},
    "streak_7": {"name": "7-Day Streak", "check": "streak_7"},
    "streak_30": {"name": "30-Day Streak", "check": "streak_30"},
    "boss_slayer": {"name": "Boss Slayer", "check": "boss_win"},
}


@dataclass
class GameProgress:
    user_id: str = "default"
    xp: int = 0
    scenarios_completed: int = 0
    boss_battles_won: int = 0
    boss_battles_failed: int = 0
    boss_pending: bool = False
    current_streak: int = 0
    longest_streak: int = 0
    last_training_date: str = ""
    scenarios_today: int = 0
    lessons_today: int = 0
    replays_today: int = 0
    career_rank: str = "Training Desk Intern"
    last_xp_breakdown: List[str] = field(default_factory=list)
    last_xp_total: int = 0
    last_badges_earned: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "xp": self.xp,
            "scenarios_completed": self.scenarios_completed,
            "boss_battles_won": self.boss_battles_won,
            "boss_battles_failed": self.boss_battles_failed,
            "boss_pending": self.boss_pending,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_training_date": self.last_training_date,
            "scenarios_today": self.scenarios_today,
            "lessons_today": self.lessons_today,
            "replays_today": self.replays_today,
            "career_rank": self.career_rank,
            "last_xp_breakdown": self.last_xp_breakdown,
            "last_xp_total": self.last_xp_total,
            "last_badges_earned": self.last_badges_earned,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameProgress":
        return cls(
            user_id=str(data.get("user_id", "default")),
            xp=int(data.get("xp", 0)),
            scenarios_completed=int(data.get("scenarios_completed", 0)),
            boss_battles_won=int(data.get("boss_battles_won", 0)),
            boss_battles_failed=int(data.get("boss_battles_failed", 0)),
            boss_pending=bool(data.get("boss_pending", False)),
            current_streak=int(data.get("current_streak", 0)),
            longest_streak=int(data.get("longest_streak", 0)),
            last_training_date=str(data.get("last_training_date", "")),
            scenarios_today=int(data.get("scenarios_today", 0)),
            lessons_today=int(data.get("lessons_today", 0)),
            replays_today=int(data.get("replays_today", 0)),
            career_rank=str(data.get("career_rank", "Training Desk Intern")),
            last_xp_breakdown=list(data.get("last_xp_breakdown", [])),
            last_xp_total=int(data.get("last_xp_total", 0)),
            last_badges_earned=list(data.get("last_badges_earned", [])),
        )


def _today_iso() -> str:
    return date.today().isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_game_files() -> None:
    """Auto-create game JSON files if missing."""
    if not GAME_PROGRESS_FILE.is_file():
        GAME_PROGRESS_FILE.write_text(
            json.dumps(GameProgress().to_dict(), indent=2),
            encoding="utf-8",
        )
    if not BADGES_FILE.is_file():
        BADGES_FILE.write_text(
            json.dumps({"earned": []}, indent=2),
            encoding="utf-8",
        )


def load_game_progress(user_id: str = "default") -> GameProgress:
    ensure_game_files()
    try:
        data = json.loads(GAME_PROGRESS_FILE.read_text(encoding="utf-8"))
        gp = GameProgress.from_dict(data)
        if gp.user_id != user_id:
            gp.user_id = user_id
        _reset_daily_if_needed(gp)
        return gp
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return GameProgress(user_id=user_id)


def save_game_progress(gp: GameProgress) -> None:
    GAME_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    GAME_PROGRESS_FILE.write_text(json.dumps(gp.to_dict(), indent=2), encoding="utf-8")


def load_badges() -> List[Dict[str, str]]:
    ensure_game_files()
    try:
        data = json.loads(BADGES_FILE.read_text(encoding="utf-8"))
        return list(data.get("earned", []))
    except (json.JSONDecodeError, OSError, TypeError):
        return []


def save_badges(earned: List[Dict[str, str]]) -> None:
    BADGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    BADGES_FILE.write_text(json.dumps({"earned": earned}, indent=2), encoding="utf-8")


def _reset_daily_if_needed(gp: GameProgress) -> None:
    today = _today_iso()
    if gp.last_training_date != today:
        gp.scenarios_today = 0
        gp.lessons_today = 0
        gp.replays_today = 0


def player_level(xp: int) -> Tuple[int, str, int, int]:
    """Return level number, title, xp at level start, xp needed for next level."""
    level_num, title, xp_floor = PLAYER_LEVELS[0]
    for num, name, threshold in PLAYER_LEVELS:
        if xp >= threshold:
            level_num, title, xp_floor = num, name, threshold
    next_threshold = PLAYER_LEVELS[-1][2]
    for num, name, threshold in PLAYER_LEVELS:
        if threshold > xp:
            next_threshold = threshold
            break
    return level_num, title, xp_floor, next_threshold


def level_progress_pct(xp: int) -> float:
    _, _, floor_xp, next_xp = player_level(xp)
    if next_xp <= floor_xp:
        return 1.0
    return min(1.0, (xp - floor_xp) / (next_xp - floor_xp))


def skill_branch_level(score: float) -> str:
    if score < 15:
        return "Locked"
    if score < 40:
        return "Beginner"
    if score < 60:
        return "Developing"
    if score < 80:
        return "Strong"
    return "Advanced"


def build_skill_tree(user_id: str = "default") -> List[Dict[str, Any]]:
    scores = fhs.compute_skill_scores(user_id)
    score_map = {
        "chart_reading": scores.chart_reading,
        "structure_reading": scores.structure_reading,
        "pattern_recognition": scores.pattern_recognition,
        "risk_management": scores.risk_management,
        "discipline": scores.discipline,
        "trade_management": scores.trade_management,
        "market_context": scores.market_context,
    }
    tree = []
    for branch in SKILL_TREE_BRANCHES:
        raw = score_map.get(branch["score_key"], 0.0)
        tree.append({
            "id": branch["id"],
            "name": branch["name"],
            "score": round(raw, 1),
            "level": skill_branch_level(raw),
        })
    return tree


def career_rank_for(
    xp: int,
    overall_skill: float,
    discipline: float,
    scenarios: int,
) -> str:
    best = CAREER_RANKS[0]["rank"]
    for req in CAREER_RANKS:
        if (
            xp >= req["xp"]
            and overall_skill >= req["skill"]
            and discipline >= req["discipline"]
            and scenarios >= req["scenarios"]
        ):
            best = req["rank"]
    return best


def next_unlock(gp: GameProgress, user_id: str = "default") -> str:
    _, title, _, next_xp = player_level(gp.xp)
    xp_needed = max(0, next_xp - gp.xp)
    if xp_needed > 0:
        lvl_num, next_title, _, _ = player_level(next_xp)
        return f"Level {lvl_num}: {next_title} ({xp_needed} XP)"

    if gp.boss_pending:
        boss = current_boss_type(gp)
        return f"Boss Battle: {boss['name']}"

    earned_ids = {b["id"] for b in load_badges()}
    if "scenarios_10" not in earned_ids and gp.scenarios_completed < 10:
        return f"Badge: 10 Scenarios ({10 - gp.scenarios_completed} to go)"
    if gp.scenarios_completed % BOSS_INTERVAL != 0:
        remaining = BOSS_INTERVAL - (gp.scenarios_completed % BOSS_INTERVAL)
        return f"Boss Battle unlocks in {remaining} scenarios"

    scores = fhs.compute_skill_scores(user_id)
    for req in CAREER_RANKS:
        if req["rank"] == gp.career_rank:
            continue
        if gp.xp < req["xp"]:
            return f"Rank Up: {req['rank']} ({req['xp'] - gp.xp} XP)"
    return "Keep training — next mission awaits."


def current_boss_type(gp: GameProgress) -> Dict[str, str]:
    idx = (gp.scenarios_completed // BOSS_INTERVAL) % len(BOSS_TYPES)
    if gp.boss_battles_won > 0:
        idx = (gp.boss_battles_won) % len(BOSS_TYPES)
    return BOSS_TYPES[idx]


def boss_is_unlocked(gp: GameProgress) -> bool:
    return gp.boss_pending or (
        gp.scenarios_completed > 0
        and gp.scenarios_completed % BOSS_INTERVAL == 0
        and gp.scenarios_completed > gp.boss_battles_won * BOSS_INTERVAL
    )


def pick_boss_scenario(boss: Dict[str, str]) -> fhs.FullScenario:
    """Pick a scenario matching the boss battle setup type."""
    import random

    import fathers_hand_scenario_engine as fhe

    setup = boss.get("setup", "fakeout")
    markets = fhe.markets_for_mode(fhe.DEFAULT_MARKET_MODE)
    for market in markets:
        for _ in range(30):
            s = fhe.pick_scenario_for_market(market, prefer_csv=True)
            if setup.lower() in s.setup_type.lower() or setup.lower() in s.tags.lower():
                return s
    return fhe.pick_scenario_for_mode(fhe.DEFAULT_MARKET_MODE)


def _checklist_field_correct(
    scenario: fhs.FullScenario,
    answers: Dict[str, str],
    field_key: str,
) -> bool:
    key = scenario.checklist_answer_key()
    expected = fhs._canonical_checklist_answer(field_key, key.get(field_key, ""))
    user = fhs._canonical_checklist_answer(field_key, answers.get(field_key, ""))
    return fhs._normalize_checklist_answer(user) == fhs._normalize_checklist_answer(expected)


def calculate_xp(
    scenario: fhs.FullScenario,
    result: Dict[str, Any],
    is_boss: bool = False,
) -> Tuple[int, List[str]]:
    """Compute XP delta and human-readable breakdown lines."""
    xp = 0
    lines: List[str] = []

    xp += 25
    lines.append("+25 XP — scenario completed")

    checklist_pct = float(result.get("checklist_pct", 0))
    answers = result.get("checklist_answers", {})
    if checklist_pct >= 100:
        xp += 25
        lines.append("+25 XP — full checklist")

    correct_dir = bool(result.get("correct_direction", False))
    user_choice = str(result.get("user_choice", ""))
    best = scenario.best_choice
    grade = str(result.get("grade", ""))
    confidence = int(result.get("confidence", 5))
    user_note = str(result.get("user_note", ""))
    score = int(result.get("score", 0))

    if correct_dir or grade in ("Excellent", "Good"):
        xp += 50
        lines.append("+50 XP — correct trade / no-trade decision")

    if _checklist_field_correct(scenario, answers, "trend"):
        xp += 25
        lines.append("+25 XP — correct trend read")

    if _checklist_field_correct(scenario, answers, "vwap"):
        xp += 25
        lines.append("+25 XP — correct VWAP read")

    if _checklist_field_correct(scenario, answers, "risk_reward"):
        xp += 25
        lines.append("+25 XP — correct risk/reward read")

    if best in ("No Trade", "Watch") and user_choice in ("No Trade", "Watch") and best == user_choice:
        xp += 50
        lines.append("+50 XP — correct no-trade pass")

    if len(user_note.strip()) >= 40:
        xp += 25
        lines.append("+25 XP — useful journal note")

    if best in ("No Trade", "Watch") and user_choice in ("Long", "Short"):
        xp -= 25
        lines.append("-25 XP — overtrading bad setup")

    if user_choice in ("Long", "Short") and float(result.get("stop", 0)) <= 0:
        xp -= 25
        lines.append("-25 XP — missing stop loss")

    if confidence >= 8 and grade in ("Poor", "Risky", "Best answer was No Trade"):
        xp -= 25
        lines.append("-25 XP — confidence too high on poor setup")

    if is_boss and score >= BOSS_PASS_SCORE:
        xp += BOSS_BONUS_XP
        lines.append(f"+{BOSS_BONUS_XP} XP — Boss Battle victory bonus")

    return xp, lines


def _has_badge(badge_id: str) -> bool:
    return any(b.get("id") == badge_id for b in load_badges())


def _award_badge(badge_id: str, name: str) -> bool:
    if _has_badge(badge_id):
        return False
    earned = load_badges()
    earned.append({"id": badge_id, "name": name, "earned_at": _now_iso()})
    save_badges(earned)
    return True


def check_and_award_badges(
    gp: GameProgress,
    scenario: fhs.FullScenario,
    result: Dict[str, Any],
    is_boss: bool = False,
    boss_passed: bool = False,
) -> List[str]:
    """Return list of newly earned badge names."""
    new_badges: List[str] = []
    answers = result.get("checklist_answers", {})
    user_choice = str(result.get("user_choice", ""))
    user_note = str(result.get("user_note", ""))

    checks: List[Tuple[str, str, bool]] = [
        ("first_scenario", "First Scenario Completed", gp.scenarios_completed >= 1),
        ("scenarios_10", "10 Scenarios Completed", gp.scenarios_completed >= 10),
        ("scenarios_50", "50 Scenarios Completed", gp.scenarios_completed >= 50),
        ("scenarios_100", "100 Scenarios Completed", gp.scenarios_completed >= 100),
        ("trend_reader", "Trend Reader", _checklist_field_correct(scenario, answers, "trend")),
        ("vwap_specialist", "VWAP Specialist", _checklist_field_correct(scenario, answers, "vwap")),
        ("orb_hunter", "ORB Hunter", "orb" in scenario.setup_type.lower()),
        ("no_trade_master", "No-Trade Master", (
            scenario.best_choice in ("No Trade", "Watch")
            and user_choice in ("No Trade", "Watch")
            and scenario.best_choice == user_choice
        )),
        ("risk_protector", "Risk Protector", _checklist_field_correct(scenario, answers, "risk_reward")),
        ("journal_builder", "Journal Builder", len(user_note.strip()) >= 40),
        ("streak_7", "7-Day Streak", gp.current_streak >= 7),
        ("streak_30", "30-Day Streak", gp.current_streak >= 30),
    ]

    if is_boss and boss_passed:
        boss = current_boss_type(gp)
        checks.append(("fakeout_survivor", boss.get("badge", "Fakeout Survivor"), True))
        checks.append(("boss_slayer", "Boss Slayer", True))

    for badge_id, name, condition in checks:
        if condition and _award_badge(badge_id, name):
            new_badges.append(name)

    return new_badges


def _update_streak(gp: GameProgress) -> None:
    today = _today_iso()
    yesterday = date.fromisoformat(today).toordinal() - 1

    training_day = gp.scenarios_today >= DAILY_SCENARIO_GOAL or (
        gp.lessons_today >= 1 and gp.replays_today >= 1
    )

    if not training_day:
        return

    if gp.last_training_date:
        try:
            last_ord = date.fromisoformat(gp.last_training_date).toordinal()
        except ValueError:
            last_ord = 0
        if last_ord == date.fromisoformat(today).toordinal():
            return
        if last_ord == yesterday:
            gp.current_streak += 1
        elif last_ord < yesterday:
            gp.current_streak = 1
    else:
        gp.current_streak = 1

    gp.longest_streak = max(gp.longest_streak, gp.current_streak)
    gp.last_training_date = today


def process_scenario_completion(
    scenario: fhs.FullScenario,
    result: Dict[str, Any],
    user_id: str = "default",
    is_boss: bool = False,
) -> Dict[str, Any]:
    """
    Award XP, update streaks, check badges, update career rank.
    Called after existing save logic — does not replace it.
    """
    gp = load_game_progress(user_id)
    _reset_daily_if_needed(gp)

    score = int(result.get("score", 0))
    boss_passed = is_boss and score >= BOSS_PASS_SCORE

    xp_delta, xp_lines = calculate_xp(scenario, result, is_boss=is_boss and boss_passed)
    gp.xp = max(0, gp.xp + xp_delta)
    gp.scenarios_completed += 1
    gp.scenarios_today += 1
    gp.replays_today += 1

    if is_boss:
        if boss_passed:
            gp.boss_battles_won += 1
            gp.boss_pending = False
        else:
            gp.boss_battles_failed += 1
    elif gp.scenarios_completed % BOSS_INTERVAL == 0:
        gp.boss_pending = True

    _update_streak(gp)

    new_badges = check_and_award_badges(gp, scenario, result, is_boss=is_boss, boss_passed=boss_passed)
    gp.last_xp_breakdown = xp_lines
    gp.last_xp_total = xp_delta
    gp.last_badges_earned = new_badges

    scores = fhs.compute_skill_scores(user_id)
    gp.career_rank = career_rank_for(
        gp.xp,
        scores.overall_trader_score,
        scores.discipline,
        gp.scenarios_completed,
    )

    old_level = player_level(gp.xp - xp_delta)[0]
    new_level = player_level(gp.xp)[0]
    rank_up = new_level > old_level

    save_game_progress(gp)

    coach = fhs.generate_coach_report(user_id)
    skill_changes = _skill_change_summary(result, scenario)

    return {
        "xp_earned": xp_delta,
        "xp_breakdown": xp_lines,
        "badges_earned": new_badges,
        "level": player_level(gp.xp),
        "rank_up": rank_up,
        "career_rank": gp.career_rank,
        "streak": gp.current_streak,
        "scenarios_today": gp.scenarios_today,
        "daily_goal_met": gp.scenarios_today >= DAILY_SCENARIO_GOAL,
        "coach_message": coach.get("coach_message", ""),
        "recommended_drill": coach.get("recommended_drill", ""),
        "skill_changes": skill_changes,
        "boss_passed": boss_passed,
        "boss_failed": is_boss and not boss_passed,
        "game_progress": gp,
    }


def _skill_change_summary(result: Dict[str, Any], scenario: fhs.FullScenario) -> List[str]:
    lines: List[str] = []
    user = str(result.get("user_choice", ""))
    best = scenario.best_choice
    missed = result.get("checklist_missed", [])

    if best in ("No Trade", "Watch") and user in ("No Trade", "Watch"):
        lines.append("Your No-Trade Discipline increased.")
    elif result.get("correct_direction"):
        lines.append("Your Trade Selection improved.")
    else:
        lines.append("Review your weakest skill branch for the next drill.")

    missed_fields = {m.get("item", "").lower() for m in missed}
    if any("vwap" in f for f in missed_fields):
        lines.append("VWAP branch needs attention.")
    if any("trend" in f for f in missed_fields):
        lines.append("Trend Reading branch needs attention.")
    if any("opening range" in f or "or" in f for f in missed_fields):
        lines.append("Opening Range branch needs attention.")

    return lines


def record_lesson_activity(user_id: str = "default") -> GameProgress:
    """Call when user completes a lesson/quiz — counts toward daily streak."""
    gp = load_game_progress(user_id)
    _reset_daily_if_needed(gp)
    gp.lessons_today += 1
    _update_streak(gp)
    save_game_progress(gp)
    return gp


def build_game_feedback_text(feedback: Dict[str, Any]) -> str:
    """Plain-language post-scenario game summary."""
    parts: List[str] = []
    xp = feedback.get("xp_earned", 0)
    sign = "+" if xp >= 0 else ""
    parts.append(f"You earned {sign}{xp} XP.")

    for line in feedback.get("skill_changes", [])[:2]:
        parts.append(line)

    for badge in feedback.get("badges_earned", []):
        parts.append(f"Badge unlocked: {badge}")

    if feedback.get("rank_up"):
        lvl = feedback.get("level", (1, "", 0, 0))
        parts.append(f"Rank Up! You reached Level {lvl[0]}: {lvl[1]}.")

    if feedback.get("boss_passed"):
        parts.append("Boss Battle cleared. Mission complete.")
    elif feedback.get("boss_failed"):
        parts.append("Boss Battle failed. Next drill recommended.")

    drill = feedback.get("recommended_drill", "")
    if drill:
        parts.append(f"Next drill: {drill}")

    return " ".join(parts)


def daily_mission_text(gp: GameProgress) -> str:
    remaining = max(0, DAILY_SCENARIO_GOAL - gp.scenarios_today)
    if remaining == 0:
        return "Daily mission complete! Streak maintained."
    return f"Daily mission: Complete {remaining} more scenario{'s' if remaining != 1 else ''}."


def home_stats(user_id: str = "default") -> Dict[str, Any]:
    gp = load_game_progress(user_id)
    lvl_num, lvl_title, _, next_xp = player_level(gp.xp)
    return {
        "level_num": lvl_num,
        "level_title": lvl_title,
        "xp": gp.xp,
        "xp_to_next": max(0, next_xp - gp.xp),
        "level_progress": level_progress_pct(gp.xp),
        "streak": gp.current_streak,
        "career_rank": gp.career_rank,
        "next_unlock": next_unlock(gp, user_id),
        "boss_unlocked": boss_is_unlocked(gp),
        "daily_mission": daily_mission_text(gp),
        "scenarios_today": gp.scenarios_today,
    }
