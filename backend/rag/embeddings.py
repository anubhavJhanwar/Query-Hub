# HuggingFace embeddings using sentence-transformers (PyTorch backend only)
import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings
from rag.config import EMBEDDING_MODEL

_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached HuggingFace embeddings instance."""
    global _embeddings
    if _embeddings is None:
        print(f"[Embeddings] Loading model: {EMBEDDING_MODEL}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
    return _embeddings
