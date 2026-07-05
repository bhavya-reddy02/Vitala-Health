"""Vitala API — entrypoint.

Run locally:   uvicorn app.main:app --reload
Interactive docs:  http://localhost:8000/docs
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from . import models  # noqa: F401  (import so tables are registered on Base)
from .routers import auth, profile, quests, leaderboard, chat, learn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Postgres may still be starting; retry table creation a few times.
    last_err = None
    for _ in range(15):
        try:
            Base.metadata.create_all(bind=engine)
            last_err = None
            break
        except Exception as e:  # pragma: no cover
            last_err = e
            time.sleep(2)
    if last_err:
        raise last_err

    # Build the RAG knowledge index (first boot downloads the small embedding
    # model, then it's cached; later boots skip since the index is persisted).
    try:
        from .rag.store import ensure_index
        n = ensure_index()
        print(f"[vitala] knowledge index ready" + (f" — indexed {n} chunks" if n else " (already built)"))
    except Exception as e:  # pragma: no cover
        print(f"[vitala] WARNING: knowledge index not built yet: {e}")

    yield


app = FastAPI(title="Vitala API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(quests.router)
app.include_router(leaderboard.router)
app.include_router(chat.router)
app.include_router(learn.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "vitala-api", "version": "1.0.0"}


@app.get("/test-gemini", tags=["health"])
def test_gemini():
    try:
        from google import genai
        client = genai.Client(api_key=settings.google_api_key)
        interaction = client.interactions.create(
            model="gemini-3.5-flash",
            input="Explain how AI works in a few words"
        )
        return {"status": "ok", "output": interaction.output_text}
    except Exception as e:
        return {"status": "error", "message": str(e)}
