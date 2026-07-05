"""ChromaDB vector store (persisted to disk) built from the knowledge base."""
import os
import glob

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")  # silence Chroma telemetry noise

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings
from .embeddings import get_embeddings

COLLECTION = "vitala_health"
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")


def get_store(embeddings=None) -> Chroma:
    """Open (or create) the persistent Chroma collection. Cosine space makes the
    relevance scores meaningful for the grounding threshold."""
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings or get_embeddings(),
        persist_directory=settings.chroma_dir,
        collection_metadata={"hnsw:space": "cosine"},
    )


def _load_documents() -> list[Document]:
    docs = []
    for path in sorted(glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        first_line = text.strip().split("\n", 1)[0]
        title = first_line.lstrip("# ").strip() or os.path.basename(path)
        docs.append(Document(page_content=text, metadata={"title": title, "source": os.path.basename(path)}))
    return docs


def build_index(embeddings=None, reset=False) -> int:
    """(Re)build the index. Returns the number of chunks added."""
    store = get_store(embeddings)
    if reset:
        try:
            store.delete_collection()
        except Exception:
            pass
        store = get_store(embeddings)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=120, separators=["\n## ", "\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_documents(_load_documents())
    store.add_documents(chunks)
    return len(chunks)


def ensure_index(embeddings=None) -> int:
    """Build the index only if it's empty. Returns chunks added (0 if already built)."""
    store = get_store(embeddings)
    try:
        count = store._collection.count()
    except Exception:
        count = 0
    if count == 0:
        return build_index(embeddings)
    return 0
