"""/chat — the RAG health assistant."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..security import get_current_user
from ..serializers import serialize_profile
from ..config import settings
from .. import models, schemas

router = APIRouter(prefix="/chat", tags=["assistant"])

DISCLAIMER = ("Vitala offers general wellbeing information, not medical advice. "
              "For anything concerning, please speak with a qualified professional.")


@router.get("/history")
def history(limit: int = 50, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(models.ChatMessage)
            .filter_by(user_id=user.id)
            .order_by(models.ChatMessage.id.desc())
            .limit(limit).all())
    rows = list(reversed(rows))
    return {
        "messages": [{"role": r.role, "content": r.content, "citations": r.citations or []} for r in rows],
        "disclaimer": DISCLAIMER,
        "configured": settings.llm_ready(),
    }


@router.post("")
def chat(body: schemas.ChatIn, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not settings.llm_ready():
        raise HTTPException(status_code=503, detail="The assistant isn't configured yet. Set LLM_PROVIDER=ollama (free/local) or add an ANTHROPIC_API_KEY, then restart the backend.")

    msg = (body.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Message is empty")

    # A little recent history gives the assistant conversational memory.
    recent = (db.query(models.ChatMessage)
              .filter_by(user_id=user.id)
              .order_by(models.ChatMessage.id.desc())
              .limit(6).all())
    hist = [{"role": r.role, "content": r.content} for r in reversed(recent)]

    profile = serialize_profile(user.profile) or {}

    # Imported here so the app still starts if the RAG deps aren't installed yet.
    from ..rag.assistant import answer
    try:
        result = answer(profile, msg, literacy=body.literacy or "standard", history=hist)
    except Exception as e:
        if settings.llm_provider == "ollama":
            hint = "Make sure Ollama is running and the model has been pulled."
        elif settings.llm_provider == "gemini":
            hint = "Check your GOOGLE_API_KEY and that GEMINI_MODEL is available on your key."
        else:
            hint = "Check the API key and that CHAT_MODEL is available on your account."
        raise HTTPException(status_code=502, detail=f"The assistant couldn't respond right now ({type(e).__name__}). {hint}")

    db.add(models.ChatMessage(user_id=user.id, role="user", content=msg, citations=[]))
    db.add(models.ChatMessage(user_id=user.id, role="assistant", content=result["answer"], citations=result["citations"]))
    db.commit()

    return {"answer": result["answer"], "citations": result["citations"], "disclaimer": DISCLAIMER}
