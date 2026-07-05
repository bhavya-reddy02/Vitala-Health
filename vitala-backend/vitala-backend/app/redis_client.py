"""Redis is used for two things in Vitala:

1. Sessions  — every issued JWT has a matching `session:{jti}` key with a TTL.
   Deleting that key (logout / revocation) instantly invalidates the token,
   which a plain stateless JWT can't do on its own.

2. Leaderboard — a single sorted set (`leaderboard:xp`) keyed by username and
   scored by total XP, so top-N and a user's rank are O(log n) lookups.
"""
import redis

from .config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

LEADERBOARD_KEY = "leaderboard:xp"


def update_leaderboard(username: str, xp: int) -> None:
    """Set a player's score to their current total XP."""
    redis_client.zadd(LEADERBOARD_KEY, {username: xp})
