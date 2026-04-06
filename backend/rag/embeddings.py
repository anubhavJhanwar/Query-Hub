# HuggingFace embeddings — wraps sentence-transformers directly to avoid
# the "meta tensor" bug in langchain_huggingface on some torch versions.
import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
from rag.config import EMBEDDING_MODEL


class STEmbeddings(Embeddings):
    """Thin LangChain-compatible wrapper around SentenceTransformer."""

    def __init__(self, model_name: str):
        self._model = SentenceTransformer(model_name, device="cpu")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self._model.encode([text], convert_to_numpy=True)[0].tolist()


_embeddings = None


def get_embeddings() -> STEmbeddings:
    """Return a cached embeddings instance."""
    global _embeddings
    if _embeddings is None:
        print(f"[Embeddings] Loading model: {EMBEDDING_MODEL}")
        _embeddings = STEmbeddings(EMBEDDING_MODEL)
    return _embeddings
