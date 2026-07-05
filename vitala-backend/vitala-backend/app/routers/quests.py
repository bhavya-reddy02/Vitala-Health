"""/quests — fetch today's quests and complete them.

Completing a quest is the one place XP, streaks, perfect days, badges and the
leaderboard all change, so it runs as a single DB transaction and is the
authority on a user's score.
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..redis_client import update_leaderboard
from ..security import get_current_user
from ..serializers import serialize_state
from ..gamification import daily_quests, level_from_xp, build_stats, evaluate_badges
from ..game_data import BADGE_BY_ID
from .. import models, schemas

router = APIRouter(prefix="/quests", tags=["quests"])


@router.get("/today")
def todays_quests(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return serialize_state(user, db)


@router.post("/complete")
def complete_quest(
    body: schemas.CompleteIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prog = user.progress
    profile = user.profile
    if profile is None:
        raise HTTPException(status_code=400, detail="Create your health profile first")

    today = date.today()
    today_key = today.isoformat()
    todays = daily_quests(user.username, today_key, profile.focus or [])

    quest = next((q for q in todays if q["id"] == body.quest_id), None)
    if quest is None:
        raise HTTPException(status_code=400, detail="That quest isn't part of today's set")

    already = (
        db.query(models.QuestCompletion)
        .filter_by(user_id=user.id, quest_id=quest["id"], quest_date=today)
        .first()
    )
    if already:
        raise HTTPException(status_code=409, detail="You've already completed that quest today")

    before_level = level_from_xp(prog.xp)["level"]

    # --- award XP & counts ---
    prog.xp += quest["xp"]
    prog.total_quests += 1
    cats = dict(prog.cat_counts or {})
    cats[quest["cat"]] = cats.get(quest["cat"], 0) + 1
    prog.cat_counts = cats

    # --- streak (first completion of a new day moves it) ---
    if prog.last_active_date != today:
        if prog.last_active_date is None:
            prog.streak = 1
        else:
            gap = (today - prog.last_active_date).days
            if gap == 1:
                prog.streak += 1
            elif gap > 1:
                prog.streak = 1
        prog.last_active_date = today
        prog.longest_streak = max(prog.longest_streak, prog.streak)

    # --- record the completion, then check for a perfect day ---
    db.add(models.QuestCompletion(
        user_id=user.id, quest_id=quest["id"], quest_date=today, xp_awarded=quest["xp"],
    ))
    db.flush()

    done_count = (
        db.query(models.QuestCompletion)
        .filter_by(user_id=user.id, quest_date=today)
        .count()
    )
    pdates = list(prog.perfect_dates or [])
    if done_count == len(todays) and today_key not in pdates:
        pdates.append(today_key)
        prog.perfect_dates = pdates
        prog.perfect_days += 1

    # --- badges ---
    stats = build_stats(prog)
    earned_ids = {bu.badge_id for bu in user.badge_unlocks}
    newly = [bid for bid in evaluate_badges(stats) if bid not in earned_ids]
    for bid in newly:
        db.add(models.BadgeUnlock(user_id=user.id, badge_id=bid))

    after_level = level_from_xp(prog.xp)["level"]

    db.commit()
    db.refresh(user)

    # --- Redis leaderboard ---
    update_leaderboard(user.username, prog.xp)

    return {
        "awardedXp": quest["xp"],
        "levelUp": after_level > before_level,
        "newLevel": after_level,
        "newBadges": [
            {"id": BADGE_BY_ID[b]["id"], "name": BADGE_BY_ID[b]["name"],
             "tier": BADGE_BY_ID[b]["tier"], "emoji": BADGE_BY_ID[b]["emoji"],
             "desc": BADGE_BY_ID[b]["desc"]}
            for b in newly
        ],
        "state": serialize_state(user, db),
    }
