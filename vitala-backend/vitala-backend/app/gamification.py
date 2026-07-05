"""Pure gamification logic — no database, no I/O.

The daily-quest generator is a 1:1 port of the frontend's mulberry32 PRNG so
that, for a given (username, date, focus), the server produces the EXACT same
five quests the React app would. That's why XP totals can't be forged: the
client and server independently agree on which quests exist today.
"""
from .game_data import QUEST_POOL, BADGES

_MASK = 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    return (a * b) & _MASK


def _hash_str(s: str) -> int:
    """FNV-1a 32-bit hash (matches the JS implementation)."""
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = _imul(h, 16777619)
    return h & _MASK


def _mulberry32(seed: int):
    a = seed & _MASK

    def rng() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & _MASK
        t = a
        t = _imul(t ^ (t >> 15), (t | 1) & _MASK)
        t = ((t + _imul(t ^ (t >> 7), (t | 61) & _MASK)) & _MASK) ^ t
        t &= _MASK
        return ((t ^ (t >> 14)) & _MASK) / 4294967296.0

    return rng


def level_from_xp(xp: int) -> dict:
    """Total XP -> level info. Level 1->2 costs 120 XP, +60 per level after."""
    lvl, need, floor = 1, 120, 0
    while xp >= floor + need:
        floor += need
        lvl += 1
        need = 120 + (lvl - 1) * 60
    return {"level": lvl, "into": xp - floor, "need": need, "floor": floor}


def daily_quests(username: str, date_key: str, focus: list[str]) -> list[dict]:
    """Five quests for the day, weighted toward the user's focus areas."""
    rng = _mulberry32(_hash_str(f"{username}|{date_key}"))
    weighted = []
    for q in QUEST_POOL:
        weighted.append(q)
        if focus and q["cat"] in focus:
            weighted.append(q)
            weighted.append(q)
    seen, pick, guard = set(), [], 0
    while len(pick) < 5 and guard < 400:
        guard += 1
        q = weighted[int(rng() * len(weighted))]
        if q["id"] not in seen:
            seen.add(q["id"])
            pick.append(q)
    return pick


def build_stats(prog, learning=None) -> dict:
    """Shape a UserProgress row (+ optional learning counts) into the dict the
    badge tests expect."""
    learning = learning or {}
    return {
        "total_xp": prog.xp,
        "level": level_from_xp(prog.xp)["level"],
        "streak": prog.streak,
        "longest_streak": prog.longest_streak,
        "total_quests": prog.total_quests,
        "cat": dict(prog.cat_counts or {}),
        "perfect_days": prog.perfect_days,
        "modules_completed": learning.get("modules_completed", 0),
        "perfect_quizzes": learning.get("perfect_quizzes", 0),
    }


def evaluate_badges(stats: dict) -> list[str]:
    """Return the ids of every badge currently satisfied."""
    return [b["id"] for b in BADGES if b["test"](stats)]


def bmi(height_cm, weight_kg):
    if not height_cm or not weight_kg:
        return None
    h = height_cm / 100.0
    return round(weight_kg / (h * h), 1)
