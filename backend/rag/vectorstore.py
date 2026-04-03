# Vector store management: supports FAISS and ChromaDB
# Supports runtime switching via explicit db/path params
import os
from langchain.schema import Document
from rag.config import FAISS_INDEX_PATH, CHROMA_DB_PATH
from rag.embeddings import get_embeddings

# Cache both stores independently
_stores: dict = {}


def build_vectorstore(chunks: list[Document], vector_db: str):
    """Build and persist a vector store from document chunks."""
    embeddings = get_embeddings()

    if vector_db == "faiss":
        from langchain_community.vectorstores import FAISS
        store = FAISS.from_documents(chunks, embeddings)
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        store.save_local(FAISS_INDEX_PATH)
        print(f"[VectorStore] FAISS index saved to {FAISS_INDEX_PATH}")

    elif vector_db == "chroma":
        from langchain_community.vectorstores import Chroma
        store = Chroma.from_documents(
            chunks, embeddings, persist_directory=CHROMA_DB_PATH
        )
        print(f"[VectorStore] ChromaDB saved to {CHROMA_DB_PATH}")
    else:
        raise ValueError(f"Unknown vector_db: {vector_db}")

    _stores[vector_db] = store
    return store


def load_vectorstore(vector_db: str):
    """Load a vector store from disk (cached per db type)."""
    if vector_db in _stores:
        return _stores[vector_db]

    embeddings = get_embeddings()

    if vector_db == "faiss":
        from langchain_community.vectorstores import FAISS
        if os.path.exists(FAISS_INDEX_PATH):
            store = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
            )
            print("[VectorStore] FAISS index loaded.")
            _stores[vector_db] = store
            return store
        print("[VectorStore] No FAISS index found. Ingest first.")

    elif vector_db == "chroma":
        from langchain_community.vectorstores import Chroma
        if os.path.exists(CHROMA_DB_PATH):
            store = Chroma(
                persist_directory=CHROMA_DB_PATH, embedding_function=embeddings
            )
            print("[VectorStore] ChromaDB loaded.")
            _stores[vector_db] = store
            return store
        print("[VectorStore] No ChromaDB found. Ingest first.")

    return None
