# Vitala API — Phase 1 Backend

The database layer for the Vitala health platform:

- **PostgreSQL** — durable user & health data (accounts, profiles, quest completions, badges)
- **Redis** — sessions (revocable JWTs) and the XP leaderboard (sorted set)
- **FastAPI** — the API that ties them together

```
  React frontend (Vitala)
          │  HTTPS + JWT
          ▼
     FastAPI  ──────────────┐
       │                    │
       ▼                    ▼
  PostgreSQL            Redis
  users                session:{jti}   (login state, TTL)
  health_profiles      leaderboard:xp  (sorted set)
  user_progress
  quest_completions
  badge_unlocks
```

FastAPI was chosen over Express so that Phase 2's RAG assistant (LangChain / LlamaIndex,
which are Python-first) lives in the same codebase.

---

## 1. Run it with Docker (recommended)

This is the easiest path — it starts Postgres, Redis, and the API together, and you
don't have to install databases on your machine.

**Install Docker Desktop**
- Windows / macOS: download from https://www.docker.com/products/docker-desktop and start it.
- Linux: install Docker Engine + the Compose plugin.

**Start everything** (from inside this `vitala-backend` folder):

```bash
docker compose up --build
```

Wait until you see `Application startup complete`. That's it:

- API:            http://localhost:8000
- **Swagger UI:**  http://localhost:8000/docs   ← try every endpoint here in the browser
- Postgres:       localhost:5432  (user `vitala`, password `vitala_pw`, db `vitala`)
- Redis:          localhost:6379

**Stop:** press `Ctrl+C`.
**Stop and wipe all data:** `docker compose down -v`.

---

## 2. Check it works

Open **http://localhost:8000/docs** and use the interactive UI, or run this from a terminal:

```bash
# 1) create an account  (copy the access_token from the response)
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"tharun","email":"tharun@example.com","password":"secret"}'

# 2) save the token in a variable
TOKEN="paste-the-access_token-here"

# 3) create the health profile
curl -X PUT http://localhost:8000/profile \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Tharun","age":24,"height_cm":178,"weight_kg":74,"goal":"active","activity":"mid","focus":["hydration","movement"]}'

# 4) see today's quests
curl http://localhost:8000/quests/today -H "Authorization: Bearer $TOKEN"

# 5) complete one (use a quest_id from step 4)
curl -X POST http://localhost:8000/quests/complete \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"quest_id":"q_water6"}'

# 6) leaderboard
curl http://localhost:8000/leaderboard -H "Authorization: Bearer $TOKEN"
```

(On Windows, the Swagger UI at `/docs` is easier than curl — click **Authorize**, paste the token, and run each call.)

---

## 3. Run it without Docker (native)

Use this only if you'd rather not use Docker.

**Prerequisites**
- Python 3.12+
- PostgreSQL 14+ running locally
- Redis running locally — note: Redis has no official Windows build, so on Windows use
  Docker (section 1), WSL2, or Memurai. macOS/Linux can install it directly.

**Set up the databases**

```sql
-- in psql, as a superuser:
CREATE ROLE vitala WITH LOGIN PASSWORD 'vitala_pw';
CREATE DATABASE vitala OWNER vitala;
```

macOS (Homebrew):  `brew install redis && brew services start redis`
Linux (apt):       `sudo apt install redis-server && sudo service redis-server start`

**Install & run the API**

```bash
cd vitala-backend
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux

uvicorn app.main:app --reload
```

The API is now at http://localhost:8000 (docs at `/docs`).

---

## 4. Project structure

```
vitala-backend/
├── docker-compose.yml      # Postgres + Redis + API
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── main.py             # FastAPI app, CORS, table creation
    ├── config.py           # settings from env
    ├── database.py         # PostgreSQL (SQLAlchemy) engine + session
    ├── redis_client.py     # Redis connection + leaderboard helper
    ├── models.py           # the database schema (5 tables)
    ├── schemas.py          # request/response shapes
    ├── security.py         # bcrypt hashing + JWT + Redis sessions
    ├── game_data.py        # quest pool + badge definitions
    ├── gamification.py     # XP curve, daily-quest PRNG, badge logic
    ├── serializers.py      # DB rows -> JSON for the frontend
    └── routers/
        ├── auth.py         # /auth/signup, /login, /logout
        ├── profile.py      # /profile  (GET + PUT)
        ├── quests.py       # /quests/today, /quests/complete
        └── leaderboard.py  # /leaderboard
```

---

## 5. Where data lives

**PostgreSQL** (the source of truth):

| Table               | Holds                                                            |
|---------------------|-----------------------------------------------------------------|
| `users`             | username, email, **bcrypt** password hash                       |
| `health_profiles`   | name, age, height, weight, goal, activity, focus areas          |
| `user_progress`     | xp, streak, longest streak, total quests, perfect days, badges  |
| `quest_completions` | one row per quest per day (unique) — the audit log              |
| `badge_unlocks`     | one row per badge a user has earned (unique)                    |

**Redis** (fast / ephemeral):

| Key                  | Type       | Purpose                                            |
|----------------------|------------|----------------------------------------------------|
| `session:{jti}`      | string+TTL | proves a JWT is still active; deleted on logout    |
| `leaderboard:xp`     | sorted set | members = usernames, scores = total XP             |

---

## 6. API reference

| Method | Path                | Auth | Purpose                                   |
|--------|---------------------|------|-------------------------------------------|
| POST   | `/auth/signup`      | —    | create account, returns JWT               |
| POST   | `/auth/login`       | —    | log in, returns JWT                        |
| POST   | `/auth/logout`      | ✓    | revoke the current session                 |
| PUT    | `/profile`          | ✓    | create/update the health profile          |
| GET    | `/profile`          | ✓    | full dashboard state                       |
| GET    | `/quests/today`     | ✓    | today's 5 quests + completion state        |
| POST   | `/quests/complete`  | ✓    | award XP, update streak/badges/leaderboard |
| GET    | `/leaderboard`      | ✓    | top players + your rank                    |

---

## 7. Connecting the Vitala frontend

The current `Vitala.jsx` saves to the browser's storage. To use this API instead, replace
those calls with `fetch`. Minimal client:

```js
const API = "http://localhost:8000";
let token = null;

async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(API + path, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
  return res.json();
}

// e.g.
const { access_token } = await api("/auth/signup", { method: "POST",
  body: { username, email, password } });
token = access_token;
const state = await api("/quests/today");
```

(The API already returns the same field names the UI uses — `xp`, `level`, `streak`,
`quests`, `badges`, etc.)

---

## 8. Before any real deployment

This is a Phase-1 dev setup. For production:

- Set a long random `JWT_SECRET` (env var) and never commit it.
- Change the Postgres password; don't expose 5432/6379 publicly.
- Put the API behind HTTPS and add rate limiting on `/auth/*`.
- Add Alembic migrations instead of `create_all` for schema changes.
- Restrict `CORS_ORIGINS` to your real frontend domain.
