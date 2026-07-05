"""Turn ORM rows into the response payloads the Vitala frontend expects."""
from datetime import date

from .gamification import level_from_xp, daily_quests, build_stats, bmi
from .game_data import BADGES, FOCUS_AREAS
from .learn_data import TOTAL_MODULES
from . import models


def serialize_profile(profile: "models.HealthProfile | None") -> dict | None:
    if profile is None:
        return None
    return {
        "name": profile.name,
        "age": profile.age,
        "sex": profile.sex,
        "heightCm": profile.height_cm,
        "weightKg": profile.weight_kg,
        "goal": profile.goal,
        "activity": profile.activity,
        "focus": profile.focus or [],
        "bmi": bmi(profile.height_cm, profile.weight_kg),
    }


def serialize_badges(prog, learning=None) -> list[dict]:
    """All badges with unlocked state + progress toward locked ones."""
    stats = build_stats(prog, learning)
    out = []
    for b in BADGES:
        cur, target = b["target"](stats)
        unlocked = b["test"](stats)
        out.append({
            "id": b["id"], "name": b["name"], "tier": b["tier"],
            "emoji": b["emoji"], "desc": b["desc"],
            "unlocked": unlocked,
            "current": min(cur, target), "target": target,
        })
    return out


def learning_counts(user: "models.User", db) -> dict:
    """Completed modules (cards + quiz done) and perfect quizzes for badge logic."""
    rows = db.query(models.LearningProgress).filter_by(user_id=user.id).all()
    return {
        "modules_completed": sum(1 for r in rows if r.cards_completed and r.quiz_completed),
        "perfect_quizzes": sum(1 for r in rows if r.best_score >= 100),
        "rows": {r.module_id: r for r in rows},
    }


def serialize_state(user: "models.User", db) -> dict:
    """The full dashboard payload: profile + progress + today's quests + badges."""
    prog = user.progress
    profile = user.profile
    today = date.today()
    today_key = today.isoformat()
    focus = (profile.focus if profile else []) or []

    todays = daily_quests(user.username, today_key, focus)
    done_rows = (
        db.query(models.QuestCompletion)
        .filter_by(user_id=user.id, quest_date=today)
        .all()
    )
    done_ids = {c.quest_id for c in done_rows}

    lvl = level_from_xp(prog.xp)
    earned = [bu.badge_id for bu in user.badge_unlocks]
    learn = learning_counts(user, db)

    return {
        "username": user.username,
        "profile": serialize_profile(profile),
        "xp": prog.xp,
        "level": lvl["level"],
        "xpInto": lvl["into"],
        "xpNeed": lvl["need"],
        "streak": prog.streak,
        "longestStreak": prog.longest_streak,
        "totalQuests": prog.total_quests,
        "perfectDays": prog.perfect_days,
        "badgesEarned": earned,
        "badges": serialize_badges(prog, learn),
        "quests": [{**q, "done": q["id"] in done_ids} for q in todays],
        "completedToday": list(done_ids),
        "focusAreas": FOCUS_AREAS,
        "learning": {"completed": learn["modules_completed"], "total": TOTAL_MODULES},
    }
