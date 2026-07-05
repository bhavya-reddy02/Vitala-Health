"""/leaderboard — top players + the caller's rank, straight from Redis."""
from fastapi import APIRouter, Depends, Query

from ..redis_client import redis_client, LEADERBOARD_KEY
from ..security import get_current_user
from .. import models

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("")
def leaderboard(
    limit: int = Query(10, ge=1, le=100),
    user: models.User = Depends(get_current_user),
):
    top = redis_client.zrevrange(LEADERBOARD_KEY, 0, limit - 1, withscores=True)
    rows = [
        {"rank": i + 1, "username": name, "xp": int(score)}
        for i, (name, score) in enumerate(top)
    ]

    rank = redis_client.zrevrank(LEADERBOARD_KEY, user.username)
    score = redis_client.zscore(LEADERBOARD_KEY, user.username)
    me = {
        "username": user.username,
        "rank": (rank + 1) if rank is not None else None,
        "xp": int(score) if score is not None else 0,
    }
    return {"top": rows, "me": me}
