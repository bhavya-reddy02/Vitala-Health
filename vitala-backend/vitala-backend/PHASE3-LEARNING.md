# Vitala — Phase 3: Health-literacy features

Phase 3 adds a **Learn** section: bite-sized educational modules, each with content
cards and a short quiz. Completing them earns XP through the *same* gamification
engine as quests — so levels, badges and the leaderboard all update together.

## What's new

**Learn tab (frontend)**
- A grid of learning modules, each showing your status (Read ✓ / Quiz ✓ / best score)
  and the XP on offer, plus an overall "health-literacy progress" bar.
- Open a module to **read the content cards** (a simple stepper), then **take the quiz**.
- Quizzes are graded, show which answers were right/wrong with a short explanation,
  and let you retake to improve your score.
- A "Keep learning" card on the dashboard links straight in.

**Six modules** (in `app/learn_data.py`): Hydration, Moving more, Sleep, Eating for
energy, Managing stress, and Understanding health info. Each has 3 cards + a 3-question
quiz. Add or edit modules there — no code changes needed.

**XP tied to gamification**
- Reading a module's cards awards its `xp_read` (once).
- Completing its quiz awards `xp_quiz` scaled by your score (once). Retakes update your
  best score but don't pay XP again — so it's not farmable.
- XP flows into your level and the Redis leaderboard, exactly like quests.

**Four new badges** (Phase 3): Curious Mind (first module), Scholar (3 modules),
Quiz Whiz (100% on a quiz), Well Read (all modules).

## How it works (for the write-up)

- **Quizzes are graded on the server.** The API sends questions and options to the
  browser but *never* the correct answers; you submit your choices to
  `POST /learn/{id}/quiz` and the server grades and returns the results. That stops
  the answers being read from the page source.
- **Progress is tracked per module** in a new `learning_progress` table
  (cards done, quiz done, best score, attempts, XP awarded), created automatically on
  startup — no data loss to your existing tables.
- **XP awards are idempotent**: reading and quiz XP are each granted only once, guarded
  by flags in that table.

## Endpoints added

| Method | Path                      | Purpose                                   |
|--------|---------------------------|-------------------------------------------|
| GET    | `/learn`                  | all modules + your status + overall total |
| GET    | `/learn/{id}`             | one module: cards + quiz (no answers)     |
| POST   | `/learn/{id}/read`        | mark cards read, award reading XP         |
| POST   | `/learn/{id}/quiz`        | grade answers, award quiz XP, results     |

## Running it

Nothing new to install. From your existing setup:

```bash
cd vitala-backend
docker compose up --build      # creates the learning_progress table on startup
```

Then the frontend as usual (`cd vitala-frontend && npm install && npm run dev`) and
open the **Learn** tab.

> Note: if you're on an older database from before Phase 3, the new table is added
> automatically — your existing accounts, XP and quests are untouched. (If you ever
> want a clean slate: `docker compose down -v`.)

## Adding your own module

Append a new entry to `MODULES` in `app/learn_data.py` following the same shape
(`id`, `topic`, `title`, `icon`, `description`, `xp_read`, `xp_quiz`, `cards`, `quiz`),
then restart the backend. It appears in the Learn tab automatically.
