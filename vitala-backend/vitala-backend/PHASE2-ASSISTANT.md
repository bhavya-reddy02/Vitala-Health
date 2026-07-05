# Vitala — Phase 2: the AI Health Coach (Claude + RAG)

Phase 2 adds a personal health assistant to Vitala. It uses **Claude** for the
language, **LangChain** to orchestrate retrieval, and **ChromaDB** as the vector
store holding a vetted wellbeing knowledge base. Answers are *grounded* in that
knowledge (so the assistant doesn't make up health facts) and *tailored* to each
user's goal, focus areas, and chosen reading level.

```
  User asks a question (Coach tab)
        │
        ▼
   FastAPI /chat
        │  1. embed the question (local model, no extra key)
        ▼
   ChromaDB  ──► most relevant wellbeing snippets  ─┐
        │                                           │ 2. build a tailored,
        ▼                                           │    grounded prompt
   Claude (Anthropic API)  ◄─────────────────────────┘
        │  3. answer, grounded only in the retrieved snippets
        ▼
   Answer + the sources it used  ──►  saved to PostgreSQL (chat history)
```

Only the **LLM** needs an API key. Turning text into vectors (embeddings) runs
locally with a small model, so there's just one key to manage.

---

## 1. Get a Claude API key

1. Go to https://console.anthropic.com → sign in → **API Keys** → create a key.
2. It looks like `sk-ant-...`. Copy it.

(You'll need a little credit on the Anthropic account for it to answer.)

## 2. Give the key to the backend

In the **`vitala-backend`** folder, create a file named exactly **`.env`** with one line:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

`docker-compose.yml` already reads this automatically. (Don't share this file or
commit it to Git.)

## 3. Rebuild and start the backend

```bash
cd vitala-backend
docker compose up --build
```

Two things happen on this first run:

- New Python packages install (LangChain, Chroma, etc.), so the build takes a few
  minutes.
- On startup the small embedding model downloads once (~130 MB) and the knowledge
  base is indexed into Chroma. Watch for the log line:
  **`[vitala] knowledge index ready — indexed N chunks`**.

Both are one-time; later starts are fast because the model and index are stored in
Docker volumes.

## 4. Use it

Start the frontend as usual (`cd vitala-frontend && npm run dev`), open
http://localhost:5173, and click the **Coach** tab. Ask something like
"How much water should I drink?" or "How do streaks work?". You'll see:

- a grounded answer from Claude,
- little **📄 source** chips showing which knowledge documents it used,
- a **Simple / Standard / In-depth** switch that changes how answers are explained,
- a standing reminder that this is general info, not medical advice.

Your conversation is saved in PostgreSQL, so it's still there when you return.

---

## How the parts map to the stack

| Layer        | Choice                          | Where in the code                         |
|--------------|---------------------------------|-------------------------------------------|
| LLM API      | Anthropic **Claude**            | `app/rag/assistant.py` (`ChatAnthropic`)  |
| RAG framework| **LangChain**                   | `app/rag/*` (splitters, retriever, messages) |
| Vector DB    | **ChromaDB** (persisted)        | `app/rag/store.py`                         |
| Embeddings   | local fastembed (ONNX)          | `app/rag/embeddings.py`                    |
| Knowledge    | vetted wellbeing docs           | `app/rag/knowledge/*.md`                   |
| History      | PostgreSQL                      | `chat_messages` table                     |

## Prompt engineering (the anti-hallucination + personalisation bit)

The system prompt in `assistant.py`:
- restricts the model to **only** the retrieved context and tells it to admit when
  it doesn't know rather than guess,
- forbids diagnosis and specific medication/dosage advice,
- routes urgent/emergency mentions to professional help,
- adapts tone to the chosen **literacy level** (simple / standard / in-depth),
- gently personalises to the user's **goal** and **focus areas** from their profile.

## Editing the knowledge base

Add or edit Markdown files in `app/rag/knowledge/`, then rebuild the index:

```bash
docker compose exec api python -m app.rag.ingest --reset
```

## Endpoints added

| Method | Path            | Purpose                                        |
|--------|-----------------|------------------------------------------------|
| POST   | `/chat`         | ask the assistant (grounded, tailored answer)  |
| GET    | `/chat/history` | load the saved conversation                    |

## Troubleshooting

- **Coach says "not switched on yet"** → the `.env` key is missing or the backend
  wasn't restarted after adding it. Recreate `.env`, then `docker compose up --build`.
- **"couldn't respond right now"** → usually an invalid/limited API key, or the
  chosen `CHAT_MODEL` isn't available on your account. Set `CHAT_MODEL` in
  `docker-compose.yml` to a model your account supports and restart.
- **First message is slow** → the embedding model is downloading on first use; it's
  quick afterwards.
