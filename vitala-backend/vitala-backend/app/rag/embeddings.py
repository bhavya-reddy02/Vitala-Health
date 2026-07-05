"""Embeddings run locally (no extra API key) using fastembed's small ONNX model.

Only the LLM (Claude) needs an API key; turning text into vectors happens on the
machine. The model downloads once on first use and is then cached.
"""
from ..config import settings

_embed = None


def get_embeddings():
    global _embed
    if _embed is None:
        from langchain_community.embeddings import FastEmbedEmbeddings
        _embed = FastEmbedEmbeddings(model_name=settings.embed_model)
    return _embed
