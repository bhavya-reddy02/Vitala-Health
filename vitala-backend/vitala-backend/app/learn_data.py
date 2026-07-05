"""Health-literacy content: bite-sized learning modules, each with a few
educational cards and a short quiz. Kept as data so it's easy to extend and
mirrors how quests/badges are defined.

Each module:
  id, topic, title, icon, description, xp_read, xp_quiz, cards[], quiz[]
Each card:   { heading, body }
Each quiz Q: { id, question, options[], answer(index), explanation }
"""

PASS_MARK = 60  # % needed to "pass" (quiz still completes below this; XP scales with score)

MODULES = [
    {
        "id": "mod_hydration", "topic": "hydration", "title": "Hydration essentials",
        "icon": "💧", "description": "Why water matters and how to stay topped up.",
        "xp_read": 20, "xp_quiz": 40,
        "cards": [
            {"heading": "Why water matters",
             "body": "Water supports energy, concentration, temperature control and digestion. You lose it all day through breathing, sweating and using the toilet, so it needs topping up regularly."},
            {"heading": "How much do you need?",
             "body": "Needs vary with body size, activity and the weather, so there's no single magic number. Drinking with each meal, sipping across the day, and drinking more when it's hot or during exercise covers most people."},
            {"heading": "A simple self-check",
             "body": "Urine colour is a rough guide: pale straw usually means you're well hydrated, while darker colour can be a sign to drink more. Thirst is an early cue — try not to wait until you're very thirsty."},
        ],
        "quiz": [
            {"id": "h1", "question": "What's a simple everyday sign you may need to drink more?",
             "options": ["Pale, light-coloured urine", "Darker-coloured urine", "Feeling too full", "Cold hands"],
             "answer": 1, "explanation": "Darker urine can indicate you need more fluids; pale straw usually means you're well hydrated."},
            {"id": "h2", "question": "Which statement about daily water needs is most accurate?",
             "options": ["Everyone needs exactly 2 litres", "Needs vary with activity, size and weather", "You only need water when exercising", "Thirst means you've already had too much"],
             "answer": 1, "explanation": "Fluid needs differ from person to person and day to day."},
            {"id": "h3", "question": "When should you usually drink more than normal?",
             "options": ["When it's cold and you're resting", "In hot weather or during exercise", "Only with meals", "Never change your amount"],
             "answer": 1, "explanation": "Heat and exercise increase fluid loss through sweat."},
        ],
    },
    {
        "id": "mod_movement", "topic": "movement", "title": "Moving more",
        "icon": "🏃", "description": "How everyday activity boosts body and mind.",
        "xp_read": 20, "xp_quiz": 40,
        "cards": [
            {"heading": "Movement is medicine",
             "body": "Regular activity supports heart and lung health, strength, mood and sleep, and helps manage long-term health risks. Everyday movement like walking, housework and taking the stairs all counts."},
            {"heading": "A general weekly target",
             "body": "A widely used guide for adults is around 150 minutes of moderate activity a week — anything that raises your heart rate a little — plus muscle-strengthening on two or more days. Build up to it gradually."},
            {"heading": "Start small, stay consistent",
             "body": "If you're new to exercise, short walks and gentle stretching are great first steps. Consistency matters more than intensity — a little, often, beats a lot occasionally."},
        ],
        "quiz": [
            {"id": "m1", "question": "Roughly how much moderate activity a week is a common general target for adults?",
             "options": ["About 20 minutes", "About 150 minutes", "About 10 hours", "None is needed"],
             "answer": 1, "explanation": "Around 150 minutes of moderate activity per week is a widely used guide."},
            {"id": "m2", "question": "What matters most when starting out?",
             "options": ["Training as hard as possible", "Consistency over intensity", "Only long gym sessions count", "Avoiding all rest"],
             "answer": 1, "explanation": "Doing a little regularly is more sustainable than occasional intense bursts."},
            {"id": "m3", "question": "Which of these counts as helpful everyday movement?",
             "options": ["Taking the stairs and brisk walking", "Only structured gym workouts", "Sitting for long periods", "Sleeping more"],
             "answer": 0, "explanation": "Everyday activity like walking and stairs adds up meaningfully."},
        ],
    },
    {
        "id": "mod_sleep", "topic": "sleep", "title": "Sleep well",
        "icon": "😴", "description": "Habits that help you rest and recover.",
        "xp_read": 20, "xp_quiz": 40,
        "cards": [
            {"heading": "Why sleep counts",
             "body": "Good sleep supports memory, mood, immune function and appetite control. Quality matters as much as quantity, and most adults feel best with roughly 7 to 9 hours."},
            {"heading": "Build a rhythm",
             "body": "Going to bed and waking at similar times helps your body clock. A calm wind-down in the last half hour — dimming lights and stepping away from screens — signals that it's time to rest."},
            {"heading": "Common disruptors",
             "body": "Caffeine can linger for many hours, so it's best avoided later in the day. Large meals, alcohol and bright screens near bedtime can also make sleep lighter or harder to reach."},
        ],
        "quiz": [
            {"id": "s1", "question": "How many hours of sleep suit most adults?",
             "options": ["3 to 4 hours", "7 to 9 hours", "12 or more hours", "It doesn't matter"],
             "answer": 1, "explanation": "Most adults function best on roughly 7 to 9 hours, though it varies."},
            {"id": "s2", "question": "Which habit best supports good sleep?",
             "options": ["A consistent bed and wake time", "Strong coffee before bed", "Bright screens right up to sleep", "A large late-night meal"],
             "answer": 0, "explanation": "A regular schedule helps your internal clock keep steady."},
            {"id": "s3", "question": "Why avoid caffeine later in the day?",
             "options": ["It has no effect", "It can stay in the body for hours and disturb sleep", "It always improves sleep", "It replaces the need for water"],
             "answer": 1, "explanation": "Caffeine can linger for many hours and make sleep lighter or harder to reach."},
        ],
    },
    {
        "id": "mod_nutrition", "topic": "nutrition", "title": "Eating for energy",
        "icon": "🥗", "description": "Simple, balanced eating without the fuss.",
        "xp_read": 20, "xp_quiz": 40,
        "cards": [
            {"heading": "It's about the pattern",
             "body": "Healthy eating is about your overall pattern, not any single food. A varied, balanced diet gives your body the energy and nutrients it needs. Small, sustainable changes beat strict short-term diets."},
            {"heading": "Build a balanced plate",
             "body": "Fill much of your plate with vegetables and fruit, include wholegrain starchy foods, and add a protein source like beans, fish, eggs or lean meat. Eating a range of colours helps cover different nutrients."},
            {"heading": "Easy swaps",
             "body": "Foods high in added sugar, salt and saturated fat are fine occasionally but best not in large amounts. Swapping sugary drinks for water and choosing fruit for snacks are simple, effective changes."},
        ],
        "quiz": [
            {"id": "n1", "question": "What best describes healthy eating?",
             "options": ["Cutting out entire food groups", "Your overall balanced pattern over time", "Never eating treats again", "Only counting calories"],
             "answer": 1, "explanation": "It's the overall pattern that matters, not perfection at any single meal."},
            {"id": "n2", "question": "Which is a simple, effective swap?",
             "options": ["Sugary drink for water", "Water for a sugary drink", "Vegetables for sweets", "Skipping meals"],
             "answer": 0, "explanation": "Swapping sugary drinks for water cuts added sugar with little effort."},
            {"id": "n3", "question": "A balanced plate is mostly built around…",
             "options": ["Vegetables, fruit, wholegrains and protein", "Only protein", "Only starchy foods", "Mostly sugary snacks"],
             "answer": 0, "explanation": "Variety across these groups covers a broad range of nutrients."},
        ],
    },
    {
        "id": "mod_stress", "topic": "mindfulness", "title": "Managing stress",
        "icon": "🧘", "description": "Everyday ways to calm a busy mind.",
        "xp_read": 20, "xp_quiz": 40,
        "cards": [
            {"heading": "Stress is normal",
             "body": "Some stress is a normal part of life and can even help in short bursts. It becomes a problem when it's intense or ongoing, affecting sleep, mood and concentration."},
            {"heading": "What genuinely helps",
             "body": "Regular activity, good sleep and staying connected to others are among the most effective supports for mental wellbeing. Short breaks and time outdoors help the nervous system settle."},
            {"heading": "A breathing reset",
             "body": "Slow breathing calms the body's stress response. Try breathing in gently for about four counts and out for about six, repeated for a minute or two, whenever things feel overwhelming."},
        ],
        "quiz": [
            {"id": "t1", "question": "Which is a well-supported way to manage stress?",
             "options": ["Regular activity, sleep and social connection", "Skipping sleep to get more done", "Avoiding people entirely", "Ignoring it completely"],
             "answer": 0, "explanation": "Activity, sleep and connection are among the most effective supports."},
            {"id": "t2", "question": "A simple breathing reset is roughly…",
             "options": ["In for 4, out for 6", "Hold your breath as long as possible", "Breathe as fast as you can", "Only breathe through your mouth"],
             "answer": 0, "explanation": "Slow breathing — in for about four, out for about six — calms the stress response."},
            {"id": "t3", "question": "When is stress most likely to become a problem?",
             "options": ["In short, occasional bursts", "When it's intense or ongoing", "Only during exercise", "It never causes problems"],
             "answer": 1, "explanation": "Ongoing or intense stress is what tends to affect health and wellbeing."},
        ],
    },
    {
        "id": "mod_literacy", "topic": "literacy", "title": "Understanding health info",
        "icon": "🧠", "description": "Read health information with a confident, critical eye.",
        "xp_read": 25, "xp_quiz": 45,
        "cards": [
            {"heading": "Spot reliable sources",
             "body": "Trustworthy health information usually comes from recognised health services, professional bodies and peer-reviewed research. Be cautious with claims that promise quick fixes, sell a product, or have no named source."},
            {"heading": "Understanding 'risk'",
             "body": "Health advice often talks about risk, not certainty. 'Increases risk' means something becomes more likely on average — not that it will definitely happen. Relative changes ('50% higher') can sound dramatic even when the actual chance stays small."},
            {"heading": "Know when to seek help",
             "body": "General information can guide healthy habits, but it can't replace personal advice. Persistent, severe or worrying symptoms are always worth discussing with a qualified professional, who can consider your full situation."},
        ],
        "quiz": [
            {"id": "l1", "question": "Which is usually the most reliable source of health information?",
             "options": ["A recognised health service or peer-reviewed research", "A random social media post", "An advert selling a supplement", "An unnamed website promising a quick cure"],
             "answer": 0, "explanation": "Recognised health bodies and peer-reviewed research are more dependable than anonymous or sales-driven claims."},
            {"id": "l2", "question": "If something 'increases your risk', it means…",
             "options": ["It will definitely happen", "It becomes more likely on average", "It's completely safe", "The risk is always huge"],
             "answer": 1, "explanation": "Risk is about likelihood, not certainty; a relative increase can still be a small actual chance."},
            {"id": "l3", "question": "When should you seek personalised advice from a professional?",
             "options": ["For persistent, severe or worrying symptoms", "Never — general info is enough", "Only after trying every online remedy", "Only in an emergency"],
             "answer": 0, "explanation": "General information can't replace advice tailored to your own situation."},
        ],
    },
]

MODULE_BY_ID = {m["id"]: m for m in MODULES}
TOTAL_MODULES = len(MODULES)


def module_summary(m: dict) -> dict:
    """Public metadata (no quiz answers)."""
    return {
        "id": m["id"], "topic": m["topic"], "title": m["title"], "icon": m["icon"],
        "description": m["description"], "xp_read": m["xp_read"], "xp_quiz": m["xp_quiz"],
        "num_cards": len(m["cards"]), "num_questions": len(m["quiz"]),
    }


def module_detail(m: dict) -> dict:
    """Full content for studying — cards plus quiz questions WITHOUT the answers."""
    return {
        **module_summary(m),
        "cards": m["cards"],
        "quiz": [{"id": q["id"], "question": q["question"], "options": q["options"]} for q in m["quiz"]],
    }
