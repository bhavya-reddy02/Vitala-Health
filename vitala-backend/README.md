# Vitala Frontend

The interactive React app for Vitala. It talks to the FastAPI backend, so your
account, XP, streaks, badges and leaderboard position all live in PostgreSQL and
Redis — nothing is stored only in the browser except your login token.

## Before you start

Two things must be true:

1. **The backend is running.** Start it first (in the `vitala-backend` folder):
   ```bash
   docker compose up --build
   ```
   Leave that terminal running. The API should be reachable at http://localhost:8000.

2. **Node.js 18+ is installed.** Check with `node -v`. If it's missing, install the
   LTS version from https://nodejs.org.

## Run the frontend

Open a **second** terminal (keep the backend one running) and, inside this
`vitala-frontend` folder:

```bash
npm install      # first time only — downloads React & Vite
npm run dev
```

Then open the URL it prints — usually:

**http://localhost:5173**

Sign up, complete the onboarding, and you're in. Everything you do is saved to the
database through the API, so you can refresh, log out, and log back in and your
progress is still there.

## The order that matters

```
Terminal 1:  cd vitala-backend   →  docker compose up --build     (the database + API)
Terminal 2:  cd vitala-frontend  →  npm install && npm run dev     (the app you click)
Browser:     http://localhost:5173
```

## Troubleshooting

**"Can't reach the server" on the login screen**
The backend isn't running (or is still starting). Make sure `docker compose up` is
running in the other terminal and http://localhost:8000/docs opens.

**A CORS error in the browser console**
The backend only allows the frontend origins listed in its `CORS_ORIGINS` setting,
which already includes `http://localhost:5173`. If Vite starts on a different port
(it will tell you), add that origin to `CORS_ORIGINS` in `docker-compose.yml` and
restart the backend.

**The API is on a different address**
Copy `.env.example` to `.env` and set `VITE_API_URL` to wherever the backend runs,
then restart `npm run dev`.

## How it connects (for the write-up)

- `src/api.js` — a tiny `fetch` wrapper that attaches the JWT and points at
  `VITE_API_URL`.
- `src/App.jsx` — the UI. Instead of computing XP/streaks locally, it calls the API:
  `POST /auth/signup|login`, `PUT /profile`, `GET /quests/today`,
  `POST /quests/complete`, `GET /leaderboard`. The server returns the authoritative
  state and the UI just renders it.
- The login token is kept in `localStorage` so a refresh stays logged in; logout
  calls `POST /auth/logout`, which deletes the session from Redis.
