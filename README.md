# Vitala-Health
Gamified health &amp; wellbeing platform with an AI health coach (RAG). React + FastAPI + PostgreSQL/Redis + LangChain + ChromaDB.
<div align="center">

# 🌿 Vitala

### Level up your health.

A gamified health & wellbeing platform with an AI health coach that answers from a
vetted knowledge base — built with React, FastAPI, PostgreSQL, Redis, LangChain and ChromaDB.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)
![Postgres](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

</div>

---

## Overview

**Vitala** turns healthy habits into a game. Users complete **daily quests**, earn **XP**,
build **streaks**, unlock **badges**, work through **health-literacy learning modules** with
quizzes, and chat with an **AI health coach**. The coach uses Retrieval-Augmented Generation
(RAG) to ground every answer in a curated wellbeing knowledge base, so it stays factual and
on-topic instead of inventing medical advice.

The whole stack — API, databases and vector store — runs on any laptop with one Docker command.

## ✨ Features

- 🔐 **Authentication** — JWT sign-up / log-in, sessions in Redis
- 🎯 **Daily quests** — personalised to the user's focus areas, with XP rewards
- 🔥 **Gamification** — XP & levels, streaks, badges, and a live leaderboard
- 📚 **Health-literacy modules** — educational cards + graded quizzes that award XP
- 🤖 **AI health coach (RAG)** — grounded, cited answers tailored to reading level
- 🔄 **Pluggable LLM** — Google Gemini (free tier), Anthropic Claude, or local Ollama

## 🧱 Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| LLM | Gemini / Claude / Ollama (switchable) |
| RAG | LangChain |
| Vector DB | ChromaDB |
| Embeddings | fastembed (local ONNX, `BAAI/bge-small-en-v1.5`) |
| Database | PostgreSQL + Redis |
| Auth | JWT (bcrypt-hashed passwords) |
| Deployment | Docker + Docker Compose |

## 🚀 Quick start

> **Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop) and
> [Node.js 18+](https://nodejs.org).

**1. Clone**
```bash
git clone https://github.com/<your-username>/vitala.git
cd vitala
```

**2. Add an AI key** — create `vitala-backend/.env` (free option shown):
```
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-key-from-aistudio.google.com
```

**3. Start the backend**
```bash
cd vitala-backend
docker compose up --build
```
API -> http://localhost:8000  ·  API docs -> http://localhost:8000/docs

**4. Start the frontend** (in a second terminal)
```bash
cd vitala-frontend
npm install
npm run dev
```
Open **http://localhost:5173**, sign up, and explore.

<details>
<summary><b>Switch the AI provider (Claude / Ollama)</b></summary>

In `vitala-backend/.env`:
```
# Claude (paid):       LLM_PROVIDER=anthropic   ANTHROPIC_API_KEY=sk-ant-...
# Ollama (local/free): LLM_PROVIDER=ollama
#   then: docker compose --profile ollama up  &&  docker compose exec ollama ollama pull llama3.2
```
Then `docker compose up -d --force-recreate api`.
</details>

## 🗂️ Project structure

```
vitala/
├── vitala-backend/     # FastAPI · Postgres · Redis · LangChain + ChromaDB
│   └── app/
│       ├── routers/    # auth, profile, quests, learn, chat, leaderboard
│       ├── rag/        # AI coach + knowledge base
│       ├── game_data.py, learn_data.py
│       └── ...
└── vitala-frontend/    # React + Vite single-page app
    └── src/App.jsx
```

## 🧭 Using the app

**Home** dashboard · **Quests** · **Learn** (modules & quizzes) · **Coach** (AI assistant) ·
**Badges** · **Ranks** (leaderboard) · **Profile**.

To make the coach answer about a specific hospital, edit
`vitala-backend/app/rag/knowledge/hospital-info.md`, then
`docker compose exec api python -m app.rag.ingest --reset`.

## 🛟 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `no configuration file provided` | `cd vitala-backend` before `docker compose ...` |
| Frontend "Can't reach the server" | Start the backend first; check `/docs` loads |
| Coach "not switched on yet" | `.env` key missing -> recreate it, then `docker compose up -d --force-recreate api` |
| Gemini `ResourceExhausted` | Free-tier limit — wait a minute; or use `GEMINI_MODEL=gemini-1.5-flash` |
| Claude `credit balance is too low` | Add credit (console.anthropic.com) or switch to Gemini |
| View logs | `docker compose logs --tail 40 api` |

## 🔒 Security

Your `.env` (with the API key) is git-ignored and never committed — only `.env.example`
with placeholders is. If a key is exposed, revoke it and generate a new one.

## 📄 License

Released under the [MIT License](LICENSE).

---

<div align="center">
Built as an MSc dissertation project. Vitala provides general wellbeing information, not medical advice.
</div>
