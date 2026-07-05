"""The health companion: retrieve grounding context from Chroma, engineer a
prompt tailored to the user, and call the LLM — returning the answer plus the
sources it was grounded in.

Default provider is Hugging Face (free Inference API with a token).
Other supported providers: gemini, anthropic, ollama.
"""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..config import settings
from .store import get_store

# --- prompt engineering: tone tailored to the user's health literacy ---
LITERACY = {
    "simple":   "Write for someone new to health topics: very plain everyday words, short sentences, no jargon.",
    "standard": "Write in clear, friendly language with a little helpful detail.",
    "detailed": "You may use more precise terms and give fuller explanations, while staying accessible.",
}

SYSTEM_TEMPLATE = """You are Vitala's friendly health companion inside a wellbeing app.

Follow these rules strictly:
- SCOPE: only answer questions about health, wellbeing, medical or hospital information that appears in the CONTEXT, and about how to use the Vitala app. If asked about anything else (for example coding, maths, politics, or general trivia), politely reply that you can only help with health and hospital-related topics, and invite a health question instead.
- You give GENERAL wellbeing information only. You are not a doctor; never diagnose conditions or recommend specific medicines or doses.
- Answer using ONLY the CONTEXT below. If the context does not cover the question, say you don't have reliable information on that and gently suggest speaking with a qualified health professional. Never invent medical facts.
- If the person mentions urgent or emergency symptoms (for example chest pain, trouble breathing, fainting, or thoughts of self-harm), calmly and clearly tell them to seek immediate help from emergency services or a professional.
- {literacy}
- Gently personalise to the user's main goal ({goal}) and focus areas ({focus}). Be warm, encouraging, practical and brief.
- When you give health guidance, finish with a short one-line reminder that this is general information, not medical advice.

CONTEXT:
{context}"""


def build_llm():
    """Pick the LLM backend from settings.

    Default is Hugging Face (free Inference API, needs HUGGINGFACEHUB_API_TOKEN).
    Uses Qwen/Qwen2.5-72B-Instruct — one of the best open-source instruction
    models available on the HF Inference API.

    Other providers:
      - gemini   → Google Gemini (needs GOOGLE_API_KEY)
      - anthropic → Claude      (needs ANTHROPIC_API_KEY)
      - ollama    → local model (no key needed)
    """
    # ── Hugging Face (default) ──────────────────────────────────────────
    if settings.llm_provider == "huggingface":
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
        endpoint = HuggingFaceEndpoint(
            repo_id=settings.huggingface_model,
            huggingfacehub_api_token=settings.huggingfacehub_api_token,
            task="text-generation",
            temperature=0.3,
            max_new_tokens=700,
            repetition_penalty=1.1,
        )
        return ChatHuggingFace(llm=endpoint)

    # ── Gemini ──────────────────────────────────────────────────────────
    if settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.3,
            max_output_tokens=700,
        )

    # ── Ollama (local) ──────────────────────────────────────────────────
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.3,
            num_predict=700,
        )

    # ── Anthropic (Claude) ──────────────────────────────────────────────
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model=settings.chat_model,
        api_key=settings.anthropic_api_key,
        temperature=0.3,
        max_tokens=700,
        timeout=60,
    )


def retrieve(query: str, embeddings=None, k: int = 4, threshold: float = 0.15):
    """Fetch the most relevant knowledge chunks and format them + citations."""
    store = get_store(embeddings)
    pairs = store.similarity_search_with_relevance_scores(query, k=k)
    kept = [(d, s) for d, s in pairs if s is None or s >= threshold]
    if not kept and pairs:
        kept = pairs[:1]  # fall back to the single closest match
    docs = [d for d, _ in kept]

    context = "\n\n".join(
        f"[{i + 1}] {d.metadata.get('title', '')}\n{d.page_content}" for i, d in enumerate(docs)
    )
    citations, seen = [], set()
    for d in docs:
        title = d.metadata.get("title")
        if title and title not in seen:
            seen.add(title)
            citations.append({"title": title, "source": d.metadata.get("source")})
    return context, citations


def answer(profile: dict | None, message: str, literacy: str = "standard",
           history: list | None = None, embeddings=None, llm=None) -> dict:
    context, citations = retrieve(message, embeddings)

    goal = (profile or {}).get("goal") or "general wellbeing"
    focus = ", ".join((profile or {}).get("focus") or []) or "general health"
    system = SYSTEM_TEMPLATE.format(
        literacy=LITERACY.get(literacy, LITERACY["standard"]),
        goal=goal, focus=focus,
        context=context or "(no relevant information was found in the knowledge base)",
    )

    messages = [SystemMessage(system)]
    for m in (history or []):
        messages.append(HumanMessage(m["content"]) if m["role"] == "user" else AIMessage(m["content"]))
    messages.append(HumanMessage(message))

    llm = llm or build_llm()
    resp = llm.invoke(messages)
    text = resp.content if isinstance(resp.content, str) else str(resp.content)
    return {"answer": text.strip(), "citations": citations}