"""Game content, kept identical to the Vitala frontend so the server is the
source of truth without the two drifting apart."""

FOCUS_AREAS = ["hydration", "movement", "mindfulness", "nutrition", "sleep", "social"]

# id, category, title, description, xp, emoji
QUEST_POOL = [
    {"id": "q_water6",   "cat": "hydration",   "emoji": "💧", "t": "Drink 6 glasses of water",      "d": "Stay topped up through the day",   "xp": 25},
    {"id": "q_water_am", "cat": "hydration",   "emoji": "🌅", "t": "A glass of water on waking",     "d": "Rehydrate before coffee",          "xp": 15},
    {"id": "q_nocaf",    "cat": "hydration",   "emoji": "🚫", "t": "No fizzy drinks today",          "d": "Swap one for water",               "xp": 20},
    {"id": "q_walk",     "cat": "movement",    "emoji": "🚶", "t": "Walk 7,000 steps",               "d": "A long stroll counts",             "xp": 30},
    {"id": "q_stretch",  "cat": "movement",    "emoji": "🤸", "t": "5-minute stretch break",         "d": "Loosen up your shoulders & back",   "xp": 15},
    {"id": "q_stairs",   "cat": "movement",    "emoji": "🪜", "t": "Take the stairs",                "d": "Skip the lift once today",         "xp": 15},
    {"id": "q_workout",  "cat": "movement",    "emoji": "🏋️", "t": "20 minutes of exercise",        "d": "Anything that raises your pulse",   "xp": 35},
    {"id": "q_breathe",  "cat": "mindfulness", "emoji": "🌬️", "t": "3 minutes of deep breathing",   "d": "In for 4, out for 6",              "xp": 20},
    {"id": "q_mood",     "cat": "mindfulness", "emoji": "📝", "t": "Log how you're feeling",         "d": "Name today's mood",                "xp": 15},
    {"id": "q_screen",   "cat": "mindfulness", "emoji": "📵", "t": "30 min screen-free wind-down",   "d": "Before bed, lights low",           "xp": 25},
    {"id": "q_gratitude","cat": "mindfulness", "emoji": "🙏", "t": "Note one good thing",            "d": "A small win from today",           "xp": 15},
    {"id": "q_veg",      "cat": "nutrition",   "emoji": "🥦", "t": "Eat 3 portions of veg",          "d": "Colour up your plate",             "xp": 25},
    {"id": "q_fruit",    "cat": "nutrition",   "emoji": "🍎", "t": "Swap a snack for fruit",         "d": "One mindful swap",                 "xp": 15},
    {"id": "q_cook",     "cat": "nutrition",   "emoji": "🍳", "t": "Cook a meal from scratch",       "d": "You choose the recipe",            "xp": 30},
    {"id": "q_sleep8",   "cat": "sleep",       "emoji": "🛌", "t": "7+ hours in bed tonight",        "d": "Protect your wind-down",           "xp": 30},
    {"id": "q_bedtime",  "cat": "sleep",       "emoji": "⏰", "t": "Same bedtime as yesterday",      "d": "Rhythm beats willpower",           "xp": 20},
    {"id": "q_checkin",  "cat": "social",      "emoji": "💬", "t": "Message someone you care about", "d": "A quick hello counts",             "xp": 20},
    {"id": "q_sunlight", "cat": "social",      "emoji": "☀️", "t": "10 minutes of daylight",         "d": "Step outside, look up",            "xp": 15},
]

# id, name, tier, emoji, description, test(stats)->bool, target(stats)->(current, goal)
BADGES = [
    {"id": "spark",     "name": "First Steps",  "tier": "bronze", "emoji": "✨", "desc": "Complete your first quest",
     "test": lambda s: s["total_quests"] >= 1,            "target": lambda s: (s["total_quests"], 1)},
    {"id": "streak3",   "name": "Warming Up",   "tier": "bronze", "emoji": "🔥", "desc": "Hit a 3-day streak",
     "test": lambda s: s["longest_streak"] >= 3,          "target": lambda s: (s["longest_streak"], 3)},
    {"id": "week",      "name": "Week Warrior", "tier": "silver", "emoji": "🗓️", "desc": "Reach a 7-day streak",
     "test": lambda s: s["longest_streak"] >= 7,          "target": lambda s: (s["longest_streak"], 7)},
    {"id": "level5",    "name": "Rising",       "tier": "silver", "emoji": "⭐", "desc": "Reach level 5",
     "test": lambda s: s["level"] >= 5,                   "target": lambda s: (s["level"], 5)},
    {"id": "quests25",  "name": "Quest Seeker", "tier": "silver", "emoji": "🧭", "desc": "Finish 25 quests",
     "test": lambda s: s["total_quests"] >= 25,           "target": lambda s: (s["total_quests"], 25)},
    {"id": "perfect",   "name": "Flawless Day", "tier": "gold",   "emoji": "💎", "desc": "Clear every quest in a day",
     "test": lambda s: s["perfect_days"] >= 1,            "target": lambda s: (s["perfect_days"], 1)},
    {"id": "hydro",     "name": "Hydro Hero",   "tier": "gold",   "emoji": "🌊", "desc": "Complete 15 hydration quests",
     "test": lambda s: s["cat"].get("hydration", 0) >= 15, "target": lambda s: (s["cat"].get("hydration", 0), 15)},
    {"id": "zen",       "name": "Zen Mode",     "tier": "gold",   "emoji": "🧘", "desc": "Complete 15 mindfulness quests",
     "test": lambda s: s["cat"].get("mindfulness", 0) >= 15, "target": lambda s: (s["cat"].get("mindfulness", 0), 15)},
    {"id": "level10",   "name": "Seasoned",     "tier": "plat",   "emoji": "🌟", "desc": "Reach level 10",
     "test": lambda s: s["level"] >= 10,                  "target": lambda s: (s["level"], 10)},
    {"id": "month",     "name": "Unstoppable",  "tier": "plat",   "emoji": "👑", "desc": "Reach a 30-day streak",
     "test": lambda s: s["longest_streak"] >= 30,         "target": lambda s: (s["longest_streak"], 30)},
    {"id": "quests100", "name": "Centurion",    "tier": "plat",   "emoji": "🏆", "desc": "Finish 100 quests",
     "test": lambda s: s["total_quests"] >= 100,          "target": lambda s: (s["total_quests"], 100)},
    # --- Phase 3: health-literacy badges ---
    {"id": "curious",   "name": "Curious Mind",  "tier": "bronze", "emoji": "📚", "desc": "Complete your first learning module",
     "test": lambda s: s.get("modules_completed", 0) >= 1, "target": lambda s: (s.get("modules_completed", 0), 1)},
    {"id": "scholar",   "name": "Scholar",       "tier": "silver", "emoji": "🎓", "desc": "Complete 3 learning modules",
     "test": lambda s: s.get("modules_completed", 0) >= 3, "target": lambda s: (s.get("modules_completed", 0), 3)},
    {"id": "quizwhiz",  "name": "Quiz Whiz",     "tier": "gold",   "emoji": "🧠", "desc": "Score 100% on a quiz",
     "test": lambda s: s.get("perfect_quizzes", 0) >= 1,   "target": lambda s: (s.get("perfect_quizzes", 0), 1)},
    {"id": "wellread",  "name": "Well Read",     "tier": "plat",   "emoji": "📖", "desc": "Complete every learning module",
     "test": lambda s: s.get("modules_completed", 0) >= 6, "target": lambda s: (s.get("modules_completed", 0), 6)},
]

BADGE_BY_ID = {b["id"]: b for b in BADGES}
