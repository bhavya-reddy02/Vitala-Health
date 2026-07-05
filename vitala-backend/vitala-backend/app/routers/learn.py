"""/learn — Phase 3 health-literacy modules, quizzes, and progress.

Completing the cards or a quiz awards XP through the same gamification engine
(level, badges, leaderboard) that quests use.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..redis_client import update_leaderboard
from ..security import get_current_user
from ..serializers import serialize_state, learning_counts
from ..gamification import level_from_xp, build_stats, evaluate_badges
from ..game_data import BADGE_BY_ID
from ..learn_data import MODULES, MODULE_BY_ID, module_summary, module_detail
from .. import models, schemas

router = APIRouter(prefix="/learn", tags=["learning"])


def _get_or_create(db: Session, user: models.User, module_id: str) -> models.LearningProgress:
    lp = (db.query(models.LearningProgress)
          .filter_by(user_id=user.id, module_id=module_id).first())
    if lp is None:
        lp = models.LearningProgress(user_id=user.id, module_id=module_id)
        db.add(lp)
        db.flush()
    return lp


def _finalize(db: Session, user: models.User, before_level: int):
    """Shared: unlock any new badges, bump the leaderboard, detect level-ups."""
    db.flush()
    prog = user.progress
    learn = learning_counts(user, db)
    stats = build_stats(prog, learn)
    earned = {bu.badge_id for bu in user.badge_unlocks}
    newly = [bid for bid in evaluate_badges(stats) if bid not in earned]
    for bid in newly:
        db.add(models.BadgeUnlock(user_id=user.id, badge_id=bid))
    after_level = level_from_xp(prog.xp)["level"]
    db.commit()
    db.refresh(user)
    update_leaderboard(user.username, prog.xp)
    new_badges = [{"id": BADGE_BY_ID[b]["id"], "name": BADGE_BY_ID[b]["name"],
                   "tier": BADGE_BY_ID[b]["tier"], "emoji": BADGE_BY_ID[b]["emoji"],
                   "desc": BADGE_BY_ID[b]["desc"]} for b in newly]
    return after_level > before_level, after_level, new_badges


@router.get("")
def list_modules(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """All modules with the user's per-module status + overall progress."""
    rows = {r.module_id: r for r in db.query(models.LearningProgress).filter_by(user_id=user.id).all()}
    modules = []
    for m in MODULES:
        r = rows.get(m["id"])
        modules.append({
            **module_summary(m),
            "status": {
                "cards_completed": bool(r and r.cards_completed),
                "quiz_completed": bool(r and r.quiz_completed),
                "best_score": (r.best_score if r else 0),
            },
        })
    completed = sum(1 for m in modules if m["status"]["cards_completed"] and m["status"]["quiz_completed"])
    return {"modules": modules, "completed": completed, "total": len(MODULES)}


@router.get("/{module_id}")
def get_module(module_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = MODULE_BY_ID.get(module_id)
    if not m:
        raise HTTPException(status_code=404, detail="Module not found")
    r = (db.query(models.LearningProgress).filter_by(user_id=user.id, module_id=module_id).first())
    return {
        **module_detail(m),
        "status": {
            "cards_completed": bool(r and r.cards_completed),
            "quiz_completed": bool(r and r.quiz_completed),
            "best_score": (r.best_score if r else 0),
        },
    }


@router.post("/{module_id}/read")
def complete_reading(module_id: str, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = MODULE_BY_ID.get(module_id)
    if not m:
        raise HTTPException(status_code=404, detail="Module not found")

    prog = user.progress
    before_level = level_from_xp(prog.xp)["level"]
    lp = _get_or_create(db, user, module_id)

    awarded = 0
    if not lp.cards_completed:            # award reading XP only the first time
        lp.cards_completed = True
        awarded = m["xp_read"]
        lp.xp_awarded += awarded
        prog.xp += awarded

    level_up, new_level, new_badges = _finalize(db, user, before_level)
    return {"awardedXp": awarded, "levelUp": level_up, "newLevel": new_level,
            "newBadges": new_badges, "state": serialize_state(user, db)}


@router.post("/{module_id}/quiz")
def submit_quiz(module_id: str, body: schemas.QuizSubmitIn,
                user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = MODULE_BY_ID.get(module_id)
    if not m:
        raise HTTPException(status_code=404, detail="Module not found")

    # --- grade server-side ---
    results, correct = [], 0
    for q in m["quiz"]:
        chosen = body.answers.get(q["id"], -1)
        is_correct = (chosen == q["answer"])
        if is_correct:
            correct += 1
        results.append({
            "id": q["id"], "correct": is_correct,
            "your": chosen, "answer": q["answer"], "explanation": q["explanation"],
        })
    total = len(m["quiz"])
    score = round(correct / total * 100) if total else 0

    prog = user.progress
    before_level = level_from_xp(prog.xp)["level"]
    lp = _get_or_create(db, user, module_id)
    lp.attempts += 1
    lp.best_score = max(lp.best_score, score)

    awarded = 0
    if not lp.quiz_completed:             # award quiz XP once, scaled by this score
        lp.quiz_completed = True
        awarded = round(m["xp_quiz"] * score / 100)
        lp.xp_awarded += awarded
        prog.xp += awarded

    level_up, new_level, new_badges = _finalize(db, user, before_level)
    return {
        "score": score, "correct": correct, "total": total, "results": results,
        "bestScore": lp.best_score,
        "awardedXp": awarded, "levelUp": level_up, "newLevel": new_level,
        "newBadges": new_badges, "state": serialize_state(user, db),
    }
