# Vitala — Free assistant with Ollama (no API key)

Ollama runs a language model **on your own machine**, so the health coach works for
free with no API key and no per-message cost. The rest of Phase 2 is unchanged:
LangChain still retrieves from the ChromaDB knowledge base, and answers are still
grounded and restricted to health / hospital / app topics.

The LLM is now a **switch** in `docker-compose.yml`:

```
LLM_PROVIDER: ollama        # free, local (default)
# LLM_PROVIDER: anthropic   # hosted Claude (needs ANTHROPIC_API_KEY)
```

Ollama runs as its own container in the stack, so `docker compose up` starts it
alongside Postgres, Redis, and the API — nothing extra to install.

---

## Steps

### 1. Start the stack (now includes Ollama)

```bash
cd vitala-backend
docker compose up --build
```

First run downloads the Ollama image and the embedding model, so give it a few
minutes. Wait for `Application startup complete`.

### 2. Pull a model into Ollama (one time)

The Ollama container starts empty — you download a model into it once. In a second
terminal:

```bash
docker compose exec ollama ollama pull llama3.2
```

`llama3.2` is a small 3B model that runs on a normal laptop CPU and is a good match
here because the RAG knowledge base supplies the facts. The download (~2 GB) is
saved in a Docker volume, so you only do it once.

Lighter / heavier options (set `OLLAMA_MODEL` in `docker-compose.yml` to match, then
restart):

| Model            | Size  | Notes                                   |
|------------------|-------|-----------------------------------------|
| `llama3.2:1b`    | ~1 GB | fastest, weakest — for low-spec laptops |
| `llama3.2`       | ~2 GB | **default** — good balance              |
| `qwen2.5:3b`     | ~2 GB | strong small alternative                |
| `llama3.1:8b`    | ~5 GB | better quality if your machine can handle it |

### 3. Use it

Start the frontend (`cd vitala-frontend && npm run dev`), open
http://localhost:5173 → **Coach** tab, and ask a health or hospital question.
No API key needed. Answers are generated locally by Ollama and grounded in the
knowledge base, with source chips shown underneath.

---

## Making it hospital-specific

The assistant only answers from the documents in `app/rag/knowledge/`. To make it
answer about a particular hospital:

1. Open `app/rag/knowledge/hospital-info.md` and replace the placeholders with your
   hospital's real details (departments, visiting hours, appointments, contacts).
   You can add more `.md` files too (one per topic).
2. Rebuild the index:
   ```bash
   docker compose exec api python -m app.rag.ingest --reset
   ```
3. Ask the Coach — it will now answer from your hospital documents, and politely
   decline anything outside health/hospital/app topics.

---

## Switching back to Claude later

Set `LLM_PROVIDER: anthropic` in `docker-compose.yml`, put `ANTHROPIC_API_KEY=sk-ant-...`
in a `.env` file, and `docker compose up --build`. Everything else stays the same.

---

## Notes and troubleshooting

- **First answer is slow / times out.** A local model on CPU takes longer than a
  hosted API, and the very first request also loads the model into memory. Give it
  time, or use a smaller model (`llama3.2:1b`).
- **"couldn't respond … make sure Ollama is running and the model has been pulled".**
  You haven't run the `ollama pull` step (step 2), or the model name in
  `OLLAMA_MODEL` doesn't match what you pulled.
- **Faster responses.** If your machine has a supported GPU, running Ollama natively
  (install from https://ollama.com, then `ollama pull llama3.2`) can use it. In that
  case remove the `ollama` service + its `depends_on` from `docker-compose.yml` and
  set `OLLAMA_BASE_URL: http://host.docker.internal:11434` so the API reaches the
  Ollama on your host.
- **Quality.** Small local models are weaker writers than Claude, but because
  answers are grounded in your knowledge base, they stay factual and on-topic.
