# Vitala — Assistant with Google Gemini (fast + free tier)

Gemini is a hosted model with a **free tier**, so the health coach is fast and
costs nothing to try — no local model, no GPU needed. Your RAG pipeline (LangChain
+ ChromaDB grounding, citations, health/hospital-only scope) is exactly the same;
only the model provider changes.

The provider is a switch in `docker-compose.yml`:

```
LLM_PROVIDER: gemini        # default now
```

---

## Steps

### 1. Get a free Gemini API key

1. Go to https://aistudio.google.com/app/apikey (sign in with a Google account).
2. Click **Create API key**. It looks like `AIza...`. Copy it.

The free tier is enough for development and demos.

### 2. Give the key to the backend

In the **`vitala-backend`** folder, create a file named exactly **`.env`** with one line:

```
GOOGLE_API_KEY=AIza-your-key-here
```

`docker-compose.yml` already reads it, and `LLM_PROVIDER` is already set to `gemini`.
(Don't commit or share this file.)

### 3. Start the backend

```bash
cd vitala-backend
docker compose up --build
```

Note: the slow Ollama service no longer starts by default, so this is lighter than
before. Wait for `Application startup complete`.

### 4. Use it

Start the frontend (`cd vitala-frontend && npm run dev`), open
http://localhost:5173 → **Coach** tab, and ask a health or hospital question.
Answers come back in a second or two, grounded in the knowledge base with source
chips, and adapt to the Simple / Standard / In-depth switch.

---

## Choosing the model

Default is `gemini-2.0-flash` (fast, free tier). To change it, edit `GEMINI_MODEL`
in `docker-compose.yml` and restart. If a model name is ever rejected, pick a
current one from your key's list at https://aistudio.google.com — common fast
choices are `gemini-2.0-flash` and `gemini-1.5-flash`.

```
GEMINI_MODEL: gemini-2.0-flash
```

Then:

```bash
docker compose up -d
```

---

## Switching providers later (one line)

| Want                         | Set in docker-compose.yml        | Key needed (in .env)          |
|------------------------------|----------------------------------|-------------------------------|
| Fast + free tier (default)   | `LLM_PROVIDER: gemini`           | `GOOGLE_API_KEY=...`          |
| Fast, paid                   | `LLM_PROVIDER: anthropic`        | `ANTHROPIC_API_KEY=...`       |
| Free, local (slow on laptop) | `LLM_PROVIDER: ollama`           | none; run `docker compose --profile ollama up` and `docker compose exec ollama ollama pull llama3.2` |

Everything else — retrieval, grounding, citations, the medical-safety prompt — is
identical across all three. That pluggable LLM backend is a good design point to
note in your write-up.

---

## Troubleshooting

- **Coach says "not switched on yet"** → the `.env` `GOOGLE_API_KEY` is missing or the
  backend wasn't restarted. Recreate `.env`, then `docker compose up --build`.
- **"couldn't respond … check your GOOGLE_API_KEY and GEMINI_MODEL"** → the key is
  invalid/over quota, or the model name isn't available on your key. Try
  `gemini-1.5-flash`, then restart.
- **Make hospital answers specific** → edit `app/rag/knowledge/hospital-info.md` with
  your hospital's real details, then
  `docker compose exec api python -m app.rag.ingest --reset`.
